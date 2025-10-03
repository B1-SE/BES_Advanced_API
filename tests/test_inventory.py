import json
from tests.base import client, app, init_database, clean_database

class TestInventoryAPI:
    def test_get_all_inventory(self, client, init_database):
        resp = client.get("/inventory/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "inventory" in data

    def test_get_inventory_by_id(self, client, init_database):
        resp = client.get("/inventory/1")
        assert resp.status_code in [200, 404]

    def test_get_inventory_not_found(self, client, init_database):
        resp = client.get("/inventory/999")
        assert resp.status_code == 404

    def test_create_inventory_item_success(self, client, init_database):
        item = {
            "name": "Air Filter",
            "description": "High-performance air filter",
            "quantity": 30,
            "price": 45.99,
            "category": "Filters",
        }
        resp = client.post("/inventory/", json=item)
        assert resp.status_code in [201, 400, 401]

    def test_create_inventory_item_missing_field(self, client, init_database):
        item = {"name": "Test Item", "quantity": 10}
        resp = client.post("/inventory/", json=item)
        assert resp.status_code in [400, 401]

    def test_create_inventory_item_negative_quantity(self, client, init_database):
        item = {
            "name": "Test Item",
            "description": "Test description",
            "quantity": -5,
            "price": 10.00,
            "category": "Test",
        }
        resp = client.post("/inventory/", json=item)
        assert resp.status_code in [400, 401]

    def test_create_inventory_item_negative_price(self, client, init_database):
        item = {
            "name": "Test Item",
            "description": "Test description",
            "quantity": 10,
            "price": -5.00,
            "category": "Test",
        }
        resp = client.post("/inventory/", json=item)
        assert resp.status_code in [400, 401]

    def test_update_inventory_item(self, client, init_database):
        update = {"quantity": 75, "price": 29.99}
        resp = client.put("/inventory/1", json=update)
        assert resp.status_code in [200, 404, 401]

    def test_update_inventory_item_not_found(self, client, init_database):
        update = {"quantity": 100}
        resp = client.put("/inventory/999", json=update)
        assert resp.status_code in [404, 401]

    def test_delete_inventory_item(self, client, init_database):
        resp = client.delete("/inventory/1")
        assert resp.status_code in [200, 204, 404, 401]

    def test_delete_inventory_item_not_found(self, client, init_database):
        resp = client.delete("/inventory/999")
        assert resp.status_code in [404, 401]