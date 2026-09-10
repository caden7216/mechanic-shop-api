# Tests for every route on the customers blueprint.
# Run with:  python -m unittest discover tests

import unittest

from application import create_app
from application.models import db, Customer


class TestCustomers(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")

        # a customer has to already be in the database before we can log in
        # as them, so we make one here
        self.customer = Customer(
            name="test_user",
            email="test@email.com",
            phone="123-456-7890",
            password="test",
        )

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()

        self.client = self.app.test_client()

    # logs the test customer in and hands the token back, so the token
    # authenticated tests below can just call this
    def test_login_customer(self):
        credentials = {
            "email": "test@email.com",
            "password": "test",
        }

        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")
        return response.json["auth_token"]

    # NEGATIVE - wrong email and password should not get a token
    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_password",
        }

        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["messages"], "Invalid email or password")

    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "555-555-5555",
            "password": "123",
        }

        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "John Doe")

    # NEGATIVE - the payload is missing the email, which is required
    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "555-555-5555",
            "password": "123",
        }

        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["email"], ["Missing data for required field."])

    def test_get_customers(self):
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)
        # the customer we made in setUp should be on page 1
        self.assertEqual(response.json["total_customers"], 1)
        self.assertEqual(response.json["customers"][0]["name"], "test_user")

    def test_get_customer(self):
        response = self.client.get("/customers/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["email"], "test@email.com")

    # NEGATIVE - there is no customer 99
    def test_get_invalid_customer(self):
        response = self.client.get("/customers/99")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Invalid customer id")

    def test_my_tickets(self):
        headers = {"Authorization": "Bearer " + self.test_login_customer()}

        response = self.client.get("/customers/my-tickets", headers=headers)
        self.assertEqual(response.status_code, 200)
        # the test customer has not got any tickets yet
        self.assertEqual(response.json, [])

    # NEGATIVE - a token authenticated route with no token should be blocked
    def test_my_tickets_no_token(self):
        response = self.client.get("/customers/my-tickets")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Token is missing!")

    def test_update_customer(self):
        update_payload = {
            "name": "Updated Name",
            "email": "test@email.com",
            "phone": "999-999-9999",
            "password": "test",
        }

        headers = {"Authorization": "Bearer " + self.test_login_customer()}

        response = self.client.put("/customers/", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Updated Name")
        self.assertEqual(response.json["phone"], "999-999-9999")

    def test_delete_customer(self):
        headers = {"Authorization": "Bearer " + self.test_login_customer()}

        response = self.client.delete("/customers/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Successfully deleted customer 1")


if __name__ == "__main__":
    unittest.main()
