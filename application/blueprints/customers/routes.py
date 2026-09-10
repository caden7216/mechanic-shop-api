from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from . import customers_bp
from .schemas import customer_schema, customers_schema, login_schema
from application.models import Customer, db
from application.extensions import limiter, cache
from application.utils.util import encode_token, token_required
from application.blueprints.service_tickets.schemas import service_tickets_schema


# LOGIN - checks the email and password, hands back a token
@customers_bp.route("/login", methods=["POST"])
# Rate limited because a login route is the obvious target for someone trying
# to guess passwords. 10 tries an hour makes brute forcing impractical.
@limiter.limit("10 per hour")
def login():
    try:
        credentials = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == credentials["email"])
    customer = db.session.execute(query).scalar_one_or_none()

    if customer and customer.password == credentials["password"]:
        auth_token = encode_token(customer.id)

        return jsonify({
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token,
        }), 200

    return jsonify({"messages": "Invalid email or password"}), 401


# MY TICKETS - only works if you send the token you got from /login
@customers_bp.route("/my-tickets", methods=["GET"])
@token_required
def my_tickets(customer_id):
    # customer_id comes from the token, not the url
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalar_one_or_none()

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 404

    return service_tickets_schema.jsonify(customer.service_tickets), 200


# CREATE
@customers_bp.route("/", methods=["POST"])
# Rate limited because making accounts is easy to abuse. Without a limit
# someone could script thousands of junk customers into the database.
@limiter.limit("5 per hour")
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_customer = Customer(**data)
    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201


# READ all - with pagination
@customers_bp.route("/", methods=["GET"])
def get_customers():
    # ?page=1&per_page=10 on the end of the url. If they are not passed in we
    # fall back to page 1 with 10 per page.
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = select(Customer)
    customers = db.paginate(query, page=page, per_page=per_page)

    return jsonify({
        "customers": customers_schema.dump(customers.items),
        "page": customers.page,
        "per_page": customers.per_page,
        "total_customers": customers.total,
        "total_pages": customers.pages,
    }), 200


# READ one
@customers_bp.route("/<int:id>", methods=["GET"])
def get_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 404

    return customer_schema.jsonify(customer), 200


# UPDATE - needs a token, and you can only update your own account
@customers_bp.route("/", methods=["PUT"])
@token_required
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 404

    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# DELETE - needs a token, and you can only delete your own account
@customers_bp.route("/", methods=["DELETE"])
@token_required
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted customer {customer_id}"}), 200
