from flask import Blueprint

customers_bp = Blueprint("customers", __name__)

# import the routes AFTER the blueprint exists, so they can attach to it
from . import routes
