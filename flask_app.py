# Entry point for the deployed app. Render runs this with gunicorn:
#
#   gunicorn flask_app:app
#
# There is no app.run() here, because gunicorn is the web server in
# production. Flask's built in server is only for development.

from application import create_app
from application.models import db

app = create_app("ProductionConfig")

# create the tables on the live database if they are not there yet
with app.app_context():
    db.create_all()
