"""
Unit tests for the Mechanics blueprint.
"""
import json


class TestMechanicsAPI:
    """This class represents the mechanics test case."""

    def test_1_create_mechanic(self, client, init_database):
        """Test API can create a mechanic (POST request)"""
        mechanic_data = {
            "name": "John Wrench",
            "email": "john.wrench@test.com",
            "salary": 60000.00,
        }
        res = client.post("/mechanics/", data=json.dumps(mechanic_data))
        assert res.status_code == 201
        assert "John Wrench" in str(res.data)

    def test_2_create_mechanic_duplicate_email(self, client, init_database):
        """Test API cannot create a mechanic with a duplicate email (POST request)"""
        mechanic_data = {
            "name": "Another Mike",
            "email": "mike.johnson@shop.com",  # This email exists in init_database
            "salary": 70000.00,
        }
        res = client.post("/mechanics/", data=json.dumps(mechanic_data))
        assert res.status_code == 400
        assert "Email already associated" in str(res.data)

    def test_3_get_all_mechanics(self, client, init_database):
        """Test API can get all mechanics (GET request)"""
        res = client.get("/mechanics/")
        assert res.status_code == 200
        assert "Mike Johnson" in str(res.data)

    def test_4_get_mechanic_by_id(self, client, init_database):
        """Test API can get a single mechanic by its ID."""
        mechanic_id = init_database["mechanic"].id
        res = client.get(f"/mechanics/{mechanic_id}")
        assert res.status_code == 200
        assert "Mike Johnson" in str(res.data)

    def test_5_get_nonexistent_mechanic(self, client, init_database):
        """Test API returns 404 for a nonexistent mechanic."""
        res = client.get("/mechanics/999")
        assert res.status_code == 404
        assert "Mechanic not found" in str(res.data)

    def test_6_update_mechanic(self, client, init_database):
        """Test API can update an existing mechanic. (PUT request)"""
        mechanic_id = init_database["mechanic"].id
        update_data = {"name": "Michael Johnson", "salary": 80000.00}
        res = client.put(f"/mechanics/{mechanic_id}", data=json.dumps(update_data))
        assert res.status_code == 200
        assert "Michael Johnson" in str(res.data)

    def test_7_delete_mechanic(self, client, init_database):
        """Test API can delete a mechanic. (DELETE request)."""
        mechanic_id = init_database["mechanic"].id
        res = client.delete(f"/mechanics/{mechanic_id}")
        assert res.status_code == 200
        assert "Mechanic deleted successfully" in str(res.data)

    def test_8_get_deleted_mechanic(self, client, init_database):
        """Test API returns 404 after a mechanic has been deleted."""
        mechanic_id = init_database["mechanic"].id
        client.delete(f"/mechanics/{mechanic_id}")
        res = client.get(f"/mechanics/{mechanic_id}")
        assert res.status_code == 404