# Creates the mechanic_shop_db database and the tables. Run this once first.

import os
import getpass

import mysql.connector

password = os.environ.get("MYSQL_PASSWORD")

if not password:
    print("(your typing is hidden - just type it and press Return)")
    password = getpass.getpass("MySQL root password: ")
    os.environ["MYSQL_PASSWORD"] = password

connection = mysql.connector.connect(host="localhost", user="root", password=password)
cursor = connection.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS mechanic_shop_db")
cursor.close()
connection.close()
print("Database mechanic_shop_db is ready.")

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
print("\nTables in mechanic_shop_db:")
for (table,) in cursor.fetchall():
    print(f"  {table}")
cursor.close()
connection.close()

print("\nAll set. Now run:  python app.py")
