from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema
from application.models import Mechanic, db
from application.extensions import cache


# CREATE
@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_mechanic = Mechanic(**data)
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201


# READ all
@mechanics_bp.route("/", methods=["GET"])
# Cached because the mechanic list barely ever changes but gets read a lot.
# The first request hits the database, then everything for the next 30 seconds
# comes straight out of the cache instead of running the query again.
@cache.cached(timeout=30)
def get_mechanics():
    mechanics = db.session.execute(select(Mechanic)).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200


# READ - mechanics ranked by how many tickets they have worked
@mechanics_bp.route("/most-tickets", methods=["GET"])
def most_tickets():
    mechanics = db.session.execute(select(Mechanic)).scalars().all()

    # the relationship gives us a list, so len() tells us how many tickets each
    # mechanic is on. reverse=True puts the busiest mechanic first.
    mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)

    # build the response by hand so we can include the ticket count
    result = []
    for mechanic in mechanics:
        result.append({
            "id": mechanic.id,
            "name": mechanic.name,
            "email": mechanic.email,
            "phone": mechanic.phone,
            "salary": mechanic.salary,
            "ticket_count": len(mechanic.service_tickets),
        })

    return jsonify(result), 200


# UPDATE
@mechanics_bp.route("/<int:id>", methods=["PUT"])
def update_mechanic(id):
    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"message": "Invalid mechanic id"}), 404

    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# DELETE
@mechanics_bp.route("/<int:id>", methods=["DELETE"])
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"message": "Invalid mechanic id"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted mechanic {id}"}), 200
