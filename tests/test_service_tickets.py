"""
Service ticket tests for the mechanic shop application.
"""
import json
from tests.base import client, app, init_database

class TestServiceTicketAPI:
    def test_create_service_ticket_success(self, client, init_database):
        ticket = {
            "customer_id": 1,
            "description": "Oil change and tire rotation",
            "service_date": "2024-08-15",
            "mechanic_ids": [1],
        }
        resp = client.post("/service-tickets/", json=ticket)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["customer_id"] == 1
        assert data["description"] == "Oil change and tire rotation"
        assert len(data["mechanics"]) == 1
        assert data["mechanics"][0]["id"] == 1

    def test_get_all_service_tickets_success(self, client, init_database):
        resp = client.get("/service-tickets/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_get_service_ticket_by_id_success(self, client, init_database):
        ticket = {
            "customer_id": 1,
            "description": "Test service",
            "service_date": "2024-08-16",
        }
        create_response = client.post("/service-tickets/", json=ticket)
        assert create_response.status_code == 201
        created_ticket = create_response.get_json()
        ticket_id = created_ticket["id"]
        resp = client.get(f"/service-tickets/{ticket_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["id"] == ticket_id

    def test_get_service_ticket_by_id_not_found(self, client, init_database):
        resp = client.get("/service-tickets/999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data