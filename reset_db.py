# Drops mechanic_shop_db and rebuilds it from scratch.
# Use this when the models change and the old tables no longer match.
#
#   python reset_db.py
#
# WARNING: this deletes everything in mechanic_shop_db.

import os
import getpass

import mysql.connector

password = os.environ.get("MYSQL_PASSWORD")

if not password:
    print("(your typing is hidden - just type it and press Return)")
    password = getpass.getpass("MySQL root password: ")
    os.environ["MYSQL_PASSWORD"] = password

confirm = input("This will DELETE everything in mechanic_shop_db. Type yes to continue: ")

if confirm.strip().lower() != "yes":
    print("Nothing was changed.")
    raise SystemExit

connection = mysql.connector.connect(host="localhost", user="root", password=password)
cursor = connection.cursor()
cursor.execute("DROP DATABASE IF EXISTS mechanic_shop_db")
print("Dropped mechanic_shop_db.")
cursor.execute("CREATE DATABASE mechanic_shop_db")
print("Created mechanic_shop_db.")
cursor.close()
connection.close()

# now let SQLAlchemy build the tables from the models
from application import create_app
from application.models import db

app = create_app("DevelopmentConfig")

with app.app_context():
    db.create_all()

connection = mysql.connector.connect(
    host="localhost", user="root", password=password, database="mechanic_shop_db"
)
cursor = connection.cursor()
cursor.execute("SHOW TABLES")
tables = [t for (t,) in cursor.fetchall()]

print("\nTables in mechanic_shop_db:")
for table in tables:
    print(f"  {table}")

# show the customers columns so you can confirm the password column is there
cursor.execute("SHOW COLUMNS FROM customers")
print("\nColumns in customers:")
for row in cursor.fetchall():
    print(f"  {row[0]:12} {row[1]}")

cursor.close()
connection.close()

print("\nAll set. Now run:  python app.py")
