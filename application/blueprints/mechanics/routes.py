from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema
from application.models import Mechanic, db


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
def get_mechanics():
    mechanics = db.session.execute(select(Mechanic)).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200


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
