# Tests for every route on the service tickets blueprint.
# Run with:  python -m unittest discover tests

import unittest
from datetime import date

from application import create_app
from application.models import db, Customer, Mechanic, Inventory, ServiceTicket


class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")

        # a ticket needs a customer, and the assign / add part routes need a
        # mechanic and a part, so everything gets made here
        self.customer = Customer(
            name="test_user",
            email="test@email.com",
            phone="123-456-7890",
            password="test",
        )
        self.mechanic = Mechanic(
            name="Mike Wrench",
            email="mike@shop.com",
            phone="222-222-2222",
            salary=55000.0,
        )
        self.part = Inventory(name="Brake Pads", price=49.99)
        self.ticket = ServiceTicket(
            VIN="1HGCM82633A004352",
            # made by hand instead of by the schema, so it has to be a real
            # date object and not a string
            service_date=date(2025, 9, 10),
            service_desc="Oil change",
            customer_id=1,
        )

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.add(self.mechanic)
            db.session.add(self.part)
            db.session.commit()
            db.session.add(self.ticket)
            db.session.commit()

        self.client = self.app.test_client()

    def test_create_service_ticket(self):
        ticket_payload = {
            "VIN": "2HGCM82633A004352",
            "service_date": "2025-09-11",
            "service_desc": "New brakes",
            "customer_id": 1,
        }

        response = self.client.post("/service-tickets/", json=ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["service_desc"], "New brakes")

    # NEGATIVE - the payload is missing the VIN, which is required
    def test_invalid_creation(self):
        ticket_payload = {
            "service_date": "2025-09-11",
            "service_desc": "New brakes",
            "customer_id": 1,
        }

        response = self.client.post("/service-tickets/", json=ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["VIN"], ["Missing data for required field."])

    # NEGATIVE - customer 99 does not exist, so there is nobody to bill
    def test_create_ticket_invalid_customer(self):
        ticket_payload = {
            "VIN": "2HGCM82633A004352",
            "service_date": "2025-09-11",
            "service_desc": "New brakes",
            "customer_id": 99,
        }

        response = self.client.post("/service-tickets/", json=ticket_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Invalid customer id")

    def test_get_service_tickets(self):
        response = self.client.get("/service-tickets/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["VIN"], "1HGCM82633A004352")

    def test_edit_service_ticket(self):
        # add mechanic 1 to the ticket and remove nobody
        edit_payload = {
            "add_ids": [1],
            "remove_ids": [],
        }

        response = self.client.put("/service-tickets/1/edit", json=edit_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["mechanics"]), 1)
        self.assertEqual(response.json["mechanics"][0]["name"], "Mike Wrench")

    # NEGATIVE - there is no ticket 99 to edit
    def test_edit_invalid_ticket(self):
        edit_payload = {
            "add_ids": [1],
            "remove_ids": [],
        }

        response = self.client.put("/service-tickets/99/edit", json=edit_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Invalid ticket id")

    def test_add_part(self):
        response = self.client.put("/service-tickets/1/add-part/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["parts"]), 1)
        self.assertEqual(response.json["parts"][0]["name"], "Brake Pads")

    # NEGATIVE - the same part cannot go on the ticket twice
    def test_add_part_twice(self):
        self.client.put("/service-tickets/1/add-part/1")

        response = self.client.put("/service-tickets/1/add-part/1")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "That part is already on this ticket")

    def test_assign_mechanic(self):
        response = self.client.put("/service-tickets/1/assign-mechanic/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["mechanics"]), 1)

    # NEGATIVE - the same mechanic cannot be assigned twice
    def test_assign_mechanic_twice(self):
        self.client.put("/service-tickets/1/assign-mechanic/1")

        response = self.client.put("/service-tickets/1/assign-mechanic/1")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["message"], "That mechanic is already on this ticket"
        )

    def test_remove_mechanic(self):
        # put the mechanic on first, otherwise there is nothing to remove
        self.client.put("/service-tickets/1/assign-mechanic/1")

        response = self.client.put("/service-tickets/1/remove-mechanic/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["mechanics"]), 0)

    # NEGATIVE - cannot remove a mechanic who was never on the ticket
    def test_remove_mechanic_not_on_ticket(self):
        response = self.client.put("/service-tickets/1/remove-mechanic/1")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "That mechanic is not on this ticket")


if __name__ == "__main__":
    unittest.main()
