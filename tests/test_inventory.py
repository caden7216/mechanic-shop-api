# Tests for every route on the inventory blueprint.
# Run with:  python -m unittest discover tests

import unittest

from application import create_app
from application.models import db, Inventory


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")

        # a part to read, update and delete in the tests below
        self.part = Inventory(name="Brake Pads", price=49.99)

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.part)
            db.session.commit()

        self.client = self.app.test_client()

    def test_create_part(self):
        part_payload = {
            "name": "Oil Filter",
            "price": 12.50,
        }

        response = self.client.post("/inventory/", json=part_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "Oil Filter")

    # NEGATIVE - the payload is missing the price, which is required
    def test_invalid_creation(self):
        part_payload = {
            "name": "Oil Filter",
        }

        response = self.client.post("/inventory/", json=part_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["price"], ["Missing data for required field."])

    def test_get_parts(self):
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["name"], "Brake Pads")

    def test_get_part(self):
        response = self.client.get("/inventory/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["price"], 49.99)

    # NEGATIVE - there is no part 99
    def test_get_invalid_part(self):
        response = self.client.get("/inventory/99")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Invalid part id")

    def test_update_part(self):
        update_payload = {
            "name": "Brake Pads",
            "price": 59.99,
        }

        response = self.client.put("/inventory/1", json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["price"], 59.99)

    # NEGATIVE - there is no part 99 to update
    def test_update_invalid_part(self):
        update_payload = {
            "name": "Brake Pads",
            "price": 59.99,
        }

        response = self.client.put("/inventory/99", json=update_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Invalid part id")

    def test_delete_part(self):
        response = self.client.delete("/inventory/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Successfully deleted part 1")

    # NEGATIVE - there is no part 99 to delete
    def test_delete_invalid_part(self):
        response = self.client.delete("/inventory/99")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Invalid part id")


if __name__ == "__main__":
    unittest.main()
