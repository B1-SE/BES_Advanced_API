import pytest

class TestRelationshipIntegrity:
    def test_delete_customer_with_tickets(self, client, init_database):
        ticket = {
            "customer_id": 1,
            "description": "Relationship test",
            "service_date": "2025-01-01"
        }
        resp = client.post("/service-tickets/", json=ticket)
        assert resp.status_code == 201
        resp2 = client.delete("/customers/1")
        assert resp2.status_code in [400, 403, 409, 204, 200]