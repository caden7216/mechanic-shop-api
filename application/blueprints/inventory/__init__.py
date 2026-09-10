from flask import Blueprint

inventory_bp = Blueprint("inventory", __name__)

# import the routes AFTER the blueprint exists, so they can attach to it
from . import routes
