# Application Factory. create_app() builds and returns a Flask app, which
# makes it easy to create the app with different configs (like one for tests).

from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

from .models import db
from .extensions import ma, limiter, cache
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.service_tickets import service_tickets_bp
from .blueprints.inventory import inventory_bp

# Swagger. SWAGGER_URL is the page you visit to read the docs, and API_URL is
# the yaml file that page reads the docs out of.
SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Mechanic Shop API"},
)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")

    # hook the extensions up to this app
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # register the blueprints. The url prefix is the plural name of the resource.
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service-tickets")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    # the swagger docs live at http://127.0.0.1:5001/api/docs
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
