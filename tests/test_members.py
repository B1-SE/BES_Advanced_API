import json
from tests.base import client, app, init_database, clean_database

class TestMembersAPI:
    def _login_and_get_token(self, client, email="john.doe@test.com", password="password123"):
        login_data = {"email": email, "password": password}
        response = client.post("/members/login", json=login_data)
        if response.status_code == 200:
            return response.get_json()["token"]
        return None

    def test_get_all_members_empty(self, client, clean_database):
        resp = client.get("/members/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "customers" in data
        assert len(data["customers"]) == 0

    def test_get_all_members(self, client, init_database):
        resp = client.get("/members/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "customers" in data
        assert len(data["customers"]) >= 2

    def test_create_member(self, client, clean_database):
        member = {
            "first_name": "Test",
            "last_name": "Member",
            "email": "test.member@test.com",
            "phone_number": "555-1000",
            "password": "testpassword",
        }
        resp = client.post("/members/", json=member)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["email"] == "test.member@test.com"

    def test_create_member_duplicate_email(self, client, init_database):
        member = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@test.com",
            "password": "newpassword",
        }
        resp = client.post("/members/", json=member)
        assert resp.status_code == 400

    def test_get_member_by_id(self, client, init_database):
        resp = client.get("/members/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["id"] == 1
        assert data["email"] == "john.doe@test.com"

    def test_get_member_by_id_not_found(self, client, clean_database):
        resp = client.get("/members/999")
        assert resp.status_code == 404

    def test_member_login_success(self, client, init_database):
        login_data = {"email": "john.doe@test.com", "password": "password123"}
        resp = client.post("/members/login", json=login_data)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "token" in data
        assert "customer" in data
        assert data["customer"]["email"] == "john.doe@test.com"

    def test_member_login_invalid_credentials(self, client, init_database):
        login_data = {"email": "john.doe@test.com", "password": "wrongpassword"}
        resp = client.post("/members/login", json=login_data)
        assert resp.status_code == 401

    def test_update_member_success(self, client, init_database):
        token = self._login_and_get_token(client)
        assert token
        update = {"first_name": "Johnathan"}
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.put("/members/1", json=update, headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["first_name"] == "Johnathan"

    def test_update_other_member_unauthorized(self, client, init_database):
        token = self._login_and_get_token(client, email="john.doe@test.com")
        assert token
        update = {"first_name": "Unauthorized Update"}
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.put("/members/2", json=update, headers=headers)
        assert resp.status_code == 403

    def test_delete_member_success(self, client, init_database):
        token = self._login_and_get_token(client, email="jane.smith@test.com", password="password456")
        assert token
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.delete("/members/2", headers=headers)
        assert resp.status_code == 200
        # Double-check deletion
        resp = client.get("/members/2", headers=headers)
        assert resp.status_code == 404
