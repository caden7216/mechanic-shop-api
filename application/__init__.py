# Application Factory. create_app() builds and returns a Flask app, which
# makes it easy to create the app with different configs (like one for tests).

from flask import Flask

from .models import db
from .extensions import ma
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.service_tickets import service_tickets_bp


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")

    # hook the extensions up to this app
    db.init_app(app)
    ma.init_app(app)

    # register the blueprints. The url prefix is the plural name of the resource.
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service-tickets")

    return app
