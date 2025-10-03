import pytest

class TestErrorHandling:
    def test_malformed_json(self, client, clean_database):
        resp = client.post("/customers/", data="{not: valid json}", content_type="application/json")
        assert resp.status_code == 400

    def test_missing_content_type(self, client, clean_database):
        payload = {"first_name": "Test", "last_name": "User", "email": "x@y.com", "password": "pw"}
        resp = client.post("/customers/", data=str(payload))
        assert resp.status_code in [400, 415]