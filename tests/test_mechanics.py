# Tests for every route on the mechanics blueprint.
# Run with:  python -m unittest discover tests

import unittest

from application import create_app
from application.models import db, Mechanic


class TestMechanics(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")

        # the update, delete and get all routes need a mechanic to already be
        # in the database
        self.mechanic = Mechanic(
            name="Mike Wrench",
            email="mike@shop.com",
            phone="123-456-7890",
            salary=55000.0,
        )

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()

        self.client = self.app.test_client()

    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "Sara Socket",
            "email": "sara@shop.com",
            "phone": "222-222-2222",
            "salary": 60000.0,
        }

        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "Sara Socket")

    # NEGATIVE - the payload is missing the email, which is required
    def test_invalid_creation(self):
        mechanic_payload = {
            "name": "Sara Socket",
            "phone": "222-222-2222",
            "salary": 60000.0,
        }

        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["email"], ["Missing data for required field."])

    def test_get_mechanics(self):
        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["name"], "Mike Wrench")

    def test_most_tickets(self):
        response = self.client.get("/mechanics/most-tickets")
        self.assertEqual(response.status_code, 200)
        # our one mechanic has not been put on any tickets yet
        self.assertEqual(response.json[0]["ticket_count"], 0)

    def test_update_mechanic(self):
        update_payload = {
            "name": "Mike Wrench",
            "email": "mike@shop.com",
            "phone": "123-456-7890",
            "salary": 65000.0,
        }

        response = self.client.put("/mechanics/1", json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["salary"], 65000.0)

    # NEGATIVE - there is no mechanic 99 to update
    def test_update_invalid_mechanic(self):
        update_payload = {
            "name": "Mike Wrench",
            "email": "mike@shop.com",
            "phone": "123-456-7890",
            "salary": 65000.0,
        }

        response = self.client.put("/mechanics/99", json=update_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Invalid mechanic id")

    def test_delete_mechanic(self):
        response = self.client.delete("/mechanics/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Successfully deleted mechanic 1")

    # NEGATIVE - there is no mechanic 99 to delete
    def test_delete_invalid_mechanic(self):
        response = self.client.delete("/mechanics/99")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Invalid mechanic id")


if __name__ == "__main__":
    unittest.main()
