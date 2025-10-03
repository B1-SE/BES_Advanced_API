"""
Unit tests for the Mechanics blueprint.
"""

import unittest
import json
from app import create_app
from app.extensions import db


class MechanicsTestCase(unittest.TestCase):
    """This class represents the mechanics test case."""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.mechanic = {
            "name": "John Wrench",
            "email": "john.wrench@test.com",
            "salary": 60000.00,
        }

        # Binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    def test_1_create_mechanic(self):
        """Test API can create a mechanic (POST request)"""
        res = self.client().post("/mechanics/", data=json.dumps(self.mechanic))
        self.assertEqual(res.status_code, 201)
        self.assertIn("John Wrench", str(res.data))

    def test_2_create_mechanic_duplicate_email(self):
        """Test API cannot create a mechanic with a duplicate email (POST request)"""
        # First, create a mechanic
        self.client().post("/mechanics/", data=json.dumps(self.mechanic))
        # Then, try to create another with the same email
        res = self.client().post("/mechanics/", data=json.dumps(self.mechanic))
        self.assertEqual(res.status_code, 400)
        self.assertIn("Email already associated", str(res.data))

    def test_3_get_all_mechanics(self):
        """Test API can get all mechanics (GET request)"""
        self.client().post("/mechanics/", data=json.dumps(self.mechanic))
        res = self.client().get("/mechanics/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("John Wrench", str(res.data))

    def test_4_get_mechanic_by_id(self):
        """Test API can get a single mechanic by its ID."""
        rv = self.client().post("/mechanics/", data=json.dumps(self.mechanic))
        mechanic_id = json.loads(rv.data).get("id")
        res = self.client().get(f"/mechanics/{mechanic_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("John Wrench", str(res.data))

    def test_5_get_nonexistent_mechanic(self):
        """Test API returns 404 for a nonexistent mechanic."""
        res = self.client().get("/mechanics/999")
        self.assertEqual(res.status_code, 404)
        self.assertIn("Mechanic not found", str(res.data))

    def test_6_update_mechanic(self):
        """Test API can update an existing mechanic. (PUT request)"""
        rv = self.client().post("/mechanics/", data=json.dumps(self.mechanic))
        mechanic_id = json.loads(rv.data).get("id")
        update_data = {"name": "Johnny Wrench", "salary": 65000.00}
        res = self.client().put(
            f"/mechanics/{mechanic_id}", data=json.dumps(update_data)
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("Johnny Wrench", str(res.data))

    def test_7_delete_mechanic(self):
        """Test API can delete a mechanic. (DELETE request)."""
        rv = self.client().post("/mechanics/", data=json.dumps(self.mechanic))
        mechanic_id = json.loads(rv.data).get("id")
        res = self.client().delete(f"/mechanics/{mechanic_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Mechanic deleted successfully", str(res.data))

    def test_8_get_deleted_mechanic(self):
        """Test API returns 404 after a mechanic has been deleted."""
        rv = self.client().post("/mechanics/", data=json.dumps(self.mechanic))
        mechanic_id = json.loads(rv.data).get("id")
        self.client().delete(f"/mechanics/{mechanic_id}")
        res = self.client().get(f"/mechanics/{mechanic_id}")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()