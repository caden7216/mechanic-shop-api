from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from . import customers_bp
from .schemas import customer_schema, customers_schema
from application.models import Customer, db


# CREATE
@customers_bp.route("/", methods=["POST"])
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_customer = Customer(**data)
    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201


# READ all
@customers_bp.route("/", methods=["GET"])
def get_customers():
    customers = db.session.execute(select(Customer)).scalars().all()
    return customers_schema.jsonify(customers), 200


# READ one
@customers_bp.route("/<int:id>", methods=["GET"])
def get_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 404

    return customer_schema.jsonify(customer), 200


# UPDATE
@customers_bp.route("/<int:id>", methods=["PUT"])
def update_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 404

    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # copy each field from the request onto the customer
    for key, value in data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# DELETE
@customers_bp.route("/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted customer {id}"}), 200
