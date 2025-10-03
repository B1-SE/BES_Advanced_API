import pytest

class TestEdgeCaseValidation:
    def test_quantity_and_price_boundaries(self, client, clean_database):
        # Zero quantity & price
        item = {"name": "Zero Q", "quantity": 0, "price": 0.0, "category": "Test"}
        resp = client.post("/inventory/", json=item)
        assert resp.status_code in [201, 400]

        # Negative quantity & price
        item = {"name": "Negative Q", "quantity": -1, "price": -1.0, "category": "Test"}
        resp = client.post("/inventory/", json=item)
        assert resp.status_code == 400

        # Large quantity & price
        item = {"name": "Big Q", "quantity": 10**9, "price": 1e8, "category": "Test"}
        resp = client.post("/inventory/", json=item)
        assert resp.status_code in [201, 400]

    def test_large_payloads(self, client, clean_database):
        big_desc = "A" * 100_000
        item = {"name": "BigDesc", "quantity": 10, "price": 9.99, "description": big_desc, "category": "Test"}
        resp = client.post("/inventory/", json=item)
        assert resp.status_code in [201, 400, 413]

    def test_special_unicode_characters(self, client, clean_database):
        item = {
            "name": "Üñîçødë",
            "quantity": 1,
            "price": 2.50,
            "description": "测试 🚗 🔧 ñáç",
            "category": "特殊"
        }
        resp = client.post("/inventory/", json=item)
        assert resp.status_code in [201, 400]
        if resp.status_code == 201:
            assert "Üñîçødë" in resp.get_data(as_text=True)