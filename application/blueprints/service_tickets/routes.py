from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from . import service_tickets_bp
from .schemas import service_ticket_schema, service_tickets_schema, edit_ticket_schema
from application.models import ServiceTicket, Mechanic, Customer, Inventory, db


# CREATE a ticket
@service_tickets_bp.route("/", methods=["POST"])
def create_service_ticket():
    try:
        data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # make sure the customer on the ticket actually exists
    if not db.session.get(Customer, data["customer_id"]):
        return jsonify({"message": "Invalid customer id"}), 404

    new_ticket = ServiceTicket(**data)
    db.session.add(new_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_ticket), 201


# EDIT - add and remove several mechanics in one request
@service_tickets_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
def edit_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

    if not ticket:
        return jsonify({"message": "Invalid ticket id"}), 404

    try:
        data = edit_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # add each mechanic that is not already on the ticket
    for mechanic_id in data["add_ids"]:
        mechanic = db.session.get(Mechanic, mechanic_id)

        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    # remove each mechanic that is actually on the ticket.
    # checking first matters because .remove() errors out if it is not there.
    for mechanic_id in data["remove_ids"]:
        mechanic = db.session.get(Mechanic, mechanic_id)

        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


# ADD a single part to a ticket
@service_tickets_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=["PUT"])
def add_part(ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(Inventory, part_id)

    if not ticket:
        return jsonify({"message": "Invalid ticket id"}), 404
    if not part:
        return jsonify({"message": "Invalid part id"}), 404

    if part in ticket.parts:
        return jsonify({"message": "That part is already on this ticket"}), 400

    ticket.parts.append(part)
    db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200


# ASSIGN a mechanic to a ticket
@service_tickets_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket:
        return jsonify({"message": "Invalid ticket id"}), 404
    if not mechanic:
        return jsonify({"message": "Invalid mechanic id"}), 404

    # the relationship works like a list, so just check and append
    if mechanic in ticket.mechanics:
        return jsonify({"message": "That mechanic is already on this ticket"}), 400

    ticket.mechanics.append(mechanic)
    db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200


# REMOVE a mechanic from a ticket
@service_tickets_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket:
        return jsonify({"message": "Invalid ticket id"}), 404
    if not mechanic:
        return jsonify({"message": "Invalid mechanic id"}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"message": "That mechanic is not on this ticket"}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200


# READ all tickets
@service_tickets_bp.route("/", methods=["GET"])
def get_service_tickets():
    tickets = db.session.execute(select(ServiceTicket)).scalars().all()
    return service_tickets_schema.jsonify(tickets), 200
