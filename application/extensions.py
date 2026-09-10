# Extensions live here so the blueprints can import them without importing
# the whole app (which would cause a circular import).

from flask_marshmallow import Marshmallow

ma = Marshmallow()
