from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from . import inventory_bp
from .schemas import inventory_schema, inventories_schema
from application.models import Inventory, db


# CREATE
@inventory_bp.route("/", methods=["POST"])
def create_part():
    try:
        data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_part = Inventory(**data)
    db.session.add(new_part)
    db.session.commit()

    return inventory_schema.jsonify(new_part), 201


# READ all
@inventory_bp.route("/", methods=["GET"])
def get_parts():
    parts = db.session.execute(select(Inventory)).scalars().all()
    return inventories_schema.jsonify(parts), 200


# READ one
@inventory_bp.route("/<int:id>", methods=["GET"])
def get_part(id):
    part = db.session.get(Inventory, id)

    if not part:
        return jsonify({"message": "Invalid part id"}), 404

    return inventory_schema.jsonify(part), 200


# UPDATE
@inventory_bp.route("/<int:id>", methods=["PUT"])
def update_part(id):
    part = db.session.get(Inventory, id)

    if not part:
        return jsonify({"message": "Invalid part id"}), 404

    try:
        data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in data.items():
        setattr(part, key, value)

    db.session.commit()
    return inventory_schema.jsonify(part), 200


# DELETE
@inventory_bp.route("/<int:id>", methods=["DELETE"])
def delete_part(id):
    part = db.session.get(Inventory, id)

    if not part:
        return jsonify({"message": "Invalid part id"}), 404

    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted part {id}"}), 200
