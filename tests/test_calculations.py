import pytest

class TestCalculationsAPI:
    def test_addition_basic_success(self, client):
        resp = client.post("/calculations/add", json={"numbers": [2, 3, 5]})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["operation"] == "addition"
        assert data["result"] == 10
        assert data["operands"] == [2, 3, 5]

    def test_addition_with_decimals(self, client):
        resp = client.post("/calculations/add", json={"numbers": [2.5, 3.7, 1.3]})
        assert resp.status_code == 200
        data = resp.get_json()
        assert abs(data["result"] - 7.5) < 0.0001

    def test_addition_insufficient_numbers(self, client):
        resp = client.post("/calculations/add", json={"numbers": [5]})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_addition_invalid_data_type(self, client):
        resp = client.post("/calculations/add", json={"numbers": [5, "invalid", 3]})
        assert resp.status_code == 400

    def test_addition_missing_numbers_field(self, client):
        resp = client.post("/calculations/add", json={"invalid_field": [5, 3]})
        assert resp.status_code == 400

    def test_subtraction_basic_success(self, client):
        resp = client.post("/calculations/subtract", json={"numbers": [20, 5, 3]})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["operation"] == "subtraction"
        assert data["result"] == 12

    def test_subtraction_negative_result(self, client):
        resp = client.post("/calculations/subtract", json={"numbers": [5, 10]})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["result"] == -5

    def test_multiplication_basic_success(self, client):
        resp = client.post("/calculations/multiply", json={"numbers": [4, 5, 2]})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["operation"] == "multiplication"
        assert data["result"] == 40

    def test_multiplication_with_zero(self, client):
        resp = client.post("/calculations/multiply", json={"numbers": [5, 0, 3]})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["result"] == 0

    def test_division_basic_success(self, client):
        resp = client.post("/calculations/divide", json={"numbers": [100, 5, 2]})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["operation"] == "division"
        assert data["result"] == 10.0

    def test_division_by_zero_error(self, client):
        resp = client.post("/calculations/divide", json={"numbers": [10, 0]})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "Division by zero" in data["error"]

    def test_division_with_zero_in_middle(self, client):
        resp = client.post("/calculations/divide", json={"numbers": [100, 5, 0, 2]})
        assert resp.status_code == 400

    def test_calculations_health_check(self, client):
        resp = client.get("/calculations/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["service"] == "calculations"
        assert data["status"] == "healthy"
        assert len(data["endpoints"]) == 4