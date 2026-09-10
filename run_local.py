# Entry point for running the API locally on MySQL. Run with:  python run_local.py

import os
import getpass

# Ask for the MySQL password if it is not already set, and put it in the
# environment so config.py can read it (and so Flask's reloader does not ask
# a second time).
if not os.environ.get("MYSQL_PASSWORD") and not os.environ.get("DATABASE_URL"):
    print("(your typing is hidden - just type it and press Return)")
    os.environ["MYSQL_PASSWORD"] = getpass.getpass("MySQL root password: ")

from application import create_app
from application.models import db

app = create_app("DevelopmentConfig")

# create the tables if they are not there yet
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # port 5001 because macOS AirPlay Receiver already sits on port 5000
    app.run(debug=True, port=5001)
