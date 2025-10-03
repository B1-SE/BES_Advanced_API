import json
from tests.base import client, app, init_database, clean_database

class TestCustomersAPI:
    def test_create_customer_success(self, client, clean_database):
        """Test creating a customer (POST /customers/)"""
        payload = {
            "first_name": "Alice",
            "last_name": "Wonderland",
            "email": "alice@example.com",
            "password": "pw12345",
            "phone_number": "555-1111",
            "address": "1 Magic Lane"
        }
        resp = client.post("/customers/", json=payload)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["email"] == "alice@example.com"

    def test_create_customer_missing_field(self, client, clean_database):
        """Test missing last_name returns 400"""
        payload = {
            "first_name": "Bob",
            "email": "bob@example.com",
            "password": "pw12345"
        }
        resp = client.post("/customers/", json=payload)
        assert resp.status_code == 400

    def test_get_all_customers(self, client, init_database):
        """Test GET /customers/ returns a list"""
        resp = client.get("/customers/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_customer_by_id(self, client, init_database):
        """Test GET /customers/{id} returns the customer"""
        resp = client.get("/customers/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["id"] == 1

    def test_get_customer_not_found(self, client, clean_database):
        """Test GET /customers/999 returns 404"""
        resp = client.get("/customers/999")
        assert resp.status_code == 404

    def test_update_customer(self, client, init_database):
        """Test updating a customer (PUT /customers/{id})"""
        payload = {"first_name": "Johnny"}
        resp = client.put("/customers/1", json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["first_name"] == "Johnny"

    def test_delete_customer(self, client, init_database):
        """Test deleting a customer (DELETE /customers/{id})"""
        resp = client.delete("/customers/1")
        assert resp.status_code in [200, 204, 404]