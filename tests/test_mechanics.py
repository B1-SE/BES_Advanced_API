import json
from tests.base import client, app, init_database

class TestMechanicsAPI:
    def test_create_mechanic_success(self, client, init_database):
        payload = {
            "name": "John Wrench",
            "email": "john.wrench@test.com",
            "salary": 60000.00,
        }
        resp = client.post("/mechanics/", json=payload)
        assert resp.status_code == 201
        assert "John Wrench" in str(resp.data)

    def test_create_mechanic_duplicate_email(self, client, init_database):
        payload = {
            "name": "Another Mike",
            "email": "mike.johnson@shop.com",
            "salary": 70000.00,
        }
        resp = client.post("/mechanics/", json=payload)
        assert resp.status_code == 400

    def test_get_all_mechanics(self, client, init_database):
        resp = client.get("/mechanics/")
        assert resp.status_code == 200
        assert "Mike Johnson" in str(resp.data)

    def test_get_mechanic_by_id(self, client, init_database):
        mid = init_database["mechanic"].id
        resp = client.get(f"/mechanics/{mid}")
        assert resp.status_code == 200
        assert "Mike Johnson" in str(resp.data)

    def test_get_mechanic_not_found(self, client, init_database):
        resp = client.get("/mechanics/999")
        assert resp.status_code == 404

    def test_update_mechanic(self, client, init_database):
        mid = init_database["mechanic"].id
        update = {"name": "Michael Johnson", "salary": 80000.00}
        resp = client.put(f"/mechanics/{mid}", json=update)
        assert resp.status_code == 200
        assert "Michael Johnson" in str(resp.data)

    def test_delete_mechanic(self, client, init_database):
        mid = init_database["mechanic"].id
        resp = client.delete(f"/mechanics/{mid}")
        assert resp.status_code in [200, 204, 404]

    def test_get_deleted_mechanic(self, client, init_database):
        mid = init_database["mechanic"].id
        client.delete(f"/mechanics/{mid}")
        resp = client.get(f"/mechanics/{mid}")
        assert resp.status_code == 404