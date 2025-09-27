import json
from datetime import date
from tests.base import BaseTestCase
from app.extensions import db
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app.models.service_ticket import ServiceTicket


class ServiceTicketTests(BaseTestCase):
    """Tests for the Service Ticket blueprint."""

    def setUp(self):
        """Set up a customer and mechanic for use in tests."""
        super().setUp()
        self.customer = Customer(
            first_name="Test", last_name="Customer", email="cust@test.com", password="pw"
        )
        self.mechanic = Mechanic(
            name="Test Mechanic", specialty="Everything", hourly_rate=100
        )
        db.session.add(self.customer)
        db.session.add(self.mechanic)
        db.session.commit()

    def test_create_service_ticket(self):
        """Test creating a new service ticket."""
        with self.client:
            response = self.client.post(
                "/service-tickets/",
                data=json.dumps(
                    {
                        "customer_id": self.customer.id,
                        "description": "Annual check-up",
                        "service_date": date.today().isoformat(),
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertEqual(data["description"], "Annual check-up")

    def test_create_service_ticket_no_customer(self):
        """Test creating a ticket for a non-existent customer (negative test)."""
        with self.client:
            response = self.client.post(
                "/service-tickets/",
                data=json.dumps(
                    {
                        "customer_id": 999,
                        "description": "Fake service",
                        "service_date": date.today().isoformat(),
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertEqual(data["error"], "Customer not found")

    def test_get_all_service_tickets(self):
        """Test retrieving all service tickets."""
        ticket = ServiceTicket(
            customer_id=self.customer.id,
            description="Oil change",
            service_date=date.today(),
        )
        db.session.add(ticket)
        db.session.commit()

        with self.client:
            response = self.client.get("/service-tickets/")
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["description"], "Oil change")

    def test_assign_mechanic_to_ticket(self):
        """Test assigning a mechanic to a service ticket."""
        ticket = ServiceTicket(
            customer_id=self.customer.id,
            description="Brake check",
            service_date=date.today(),
        )
        db.session.add(ticket)
        db.session.commit()

        with self.client:
            response = self.client.put(
                f"/service-tickets/{ticket.id}/assign-mechanic/{self.mechanic.id}"
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data["service_ticket"]["mechanics"]), 1)
            self.assertEqual(
                data["service_ticket"]["mechanics"][0]["name"], "Test Mechanic"
            )

    def test_assign_mechanic_already_assigned(self):
        """Test assigning a mechanic who is already on the ticket (negative test)."""
        ticket = ServiceTicket(
            customer_id=self.customer.id,
            description="Tire rotation",
            service_date=date.today(),
        )
        ticket.mechanics.append(self.mechanic)
        db.session.add(ticket)
        db.session.commit()

        with self.client:
            response = self.client.put(
                f"/service-tickets/{ticket.id}/assign-mechanic/{self.mechanic.id}"
            )
            self.assertEqual(response.status_code, 400)

    def test_remove_mechanic_from_ticket(self):
        """Test removing a mechanic from a service ticket."""
        ticket = ServiceTicket(
            customer_id=self.customer.id,
            description="Engine diagnostics",
            service_date=date.today(),
        )
        ticket.mechanics.append(self.mechanic)
        db.session.add(ticket)
        db.session.commit()

        with self.client:
            # First, verify the mechanic is there
            self.assertEqual(len(ticket.mechanics), 1)

            # Then, remove the mechanic
            response = self.client.put(
                f"/service-tickets/{ticket.id}/remove-mechanic/{self.mechanic.id}"
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data["service_ticket"]["mechanics"]), 0)

    def test_get_service_ticket_by_id(self):
        """Test retrieving a single service ticket by ID."""
        ticket = ServiceTicket(
            customer_id=self.customer.id,
            description="Specific Ticket",
            service_date=date.today(),
        )
        db.session.add(ticket)
        db.session.commit()

        with self.client:
            response = self.client.get(f"/service-tickets/{ticket.id}")
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data["description"], "Specific Ticket")

    def test_get_service_ticket_not_found(self):
        """Test retrieving a non-existent service ticket (negative test)."""
        with self.client:
            response = self.client.get("/service-tickets/999")
            self.assertEqual(response.status_code, 404)

    def test_update_service_ticket(self):
        """Test updating a service ticket."""
        ticket = ServiceTicket(
            customer_id=self.customer.id,
            description="Initial Description",
            service_date=date.today(),
        )
        db.session.add(ticket)
        db.session.commit()

        with self.client:
            response = self.client.put(
                f"/service-tickets/{ticket.id}",
                data=json.dumps({"description": "Updated Description"}),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data["description"], "Updated Description")

    def test_update_service_ticket_not_found(self):
        """Test updating a non-existent service ticket (negative test)."""
        with self.client:
            response = self.client.put(
                "/service-tickets/999",
                data=json.dumps({"description": "Ghost Ticket"}),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 404)

    def test_delete_service_ticket(self):
        """Test deleting a service ticket."""
        ticket = ServiceTicket(
            customer_id=self.customer.id,
            description="To Be Deleted",
            service_date=date.today(),
        )
        db.session.add(ticket)
        db.session.commit()

        with self.client:
            response = self.client.delete(f"/service-tickets/{ticket.id}")
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data["message"], "Service ticket deleted successfully")

    def test_delete_service_ticket_not_found(self):
        """Test deleting a non-existent service ticket (negative test)."""
        with self.client:
            response = self.client.delete("/service-tickets/999")
            self.assertEqual(response.status_code, 404)

    def test_edit_ticket_mechanics(self):
        """Test bulk adding and removing mechanics from a ticket."""
        ticket = ServiceTicket(
            customer_id=self.customer.id,
            description="Complex Job",
            service_date=date.today(),
        )
        mechanic2 = Mechanic(name="Mechanic Two", specialty="Transmissions", hourly_rate=110)
        mechanic3 = Mechanic(name="Mechanic Three", specialty="Electrical", hourly_rate=120)
        db.session.add_all([ticket, mechanic2, mechanic3])
        ticket.mechanics.append(self.mechanic) # Start with one mechanic
        db.session.commit()

        with self.client:
            response = self.client.put(
                f"/service-tickets/{ticket.id}/edit",
                data=json.dumps({
                    "add_ids": [mechanic2.id, mechanic3.id],
                    "remove_ids": [self.mechanic.id]
                }),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            mechanic_names = [m['name'] for m in data['service_ticket']['mechanics']]
            self.assertEqual(len(mechanic_names), 2)
            self.assertIn("Mechanic Two", mechanic_names)
            self.assertIn("Mechanic Three", mechanic_names)
            self.assertNotIn("Test Mechanic", mechanic_names)

    def test_edit_ticket_mechanics_partial_fail(self):
        """Test bulk edit where some IDs are invalid (negative test)."""
        ticket = ServiceTicket(
            customer_id=self.customer.id,
            description="Another Job",
            service_date=date.today(),
        )
        db.session.add(ticket)
        db.session.commit()

        with self.client:
            response = self.client.put(
                f"/service-tickets/{ticket.id}/edit",
                data=json.dumps({
                    "add_ids": [self.mechanic.id, 999], # one valid, one invalid
                    "remove_ids": [888] # invalid
                }),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 207) # 207 Multi-Status for partial success
            data = json.loads(response.data)
            self.assertIn("errors", data)
            self.assertEqual(len(data["errors"]), 2)
            self.assertEqual(len(data['service_ticket']['mechanics']), 1)
