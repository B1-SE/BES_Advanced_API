"""
Test script for JWT token authentication functionality.
"""


def test_login_and_get_token(client, init_database):
    """Test login with correct and incorrect credentials."""
    # Test 1: Login with correct credentials
    login_data = {"email": "john.doe@test.com", "password": "password123"}
    response = client.post("/customers/login", json=login_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "token" in json_data
    assert json_data["message"] == "Login successful"

    # Test 2: Login with wrong credentials
    wrong_login_data = {"email": "john.doe@test.com", "password": "wrongpassword"}
    response = client.post("/customers/login", json=wrong_login_data)
    assert response.status_code == 401
    assert "Invalid email or password" in response.get_json()["message"]


def test_protected_route_access(client, init_database):
    """Test accessing a protected route with and without a token."""
    # Test 1: Access protected route without token
    response = client.get("/customers/my-tickets")
    assert response.status_code == 401  # Expecting JWT error

    # Test 2: Access protected route with valid token
    login_data = {"email": "john.doe@test.com", "password": "password123"}
    login_response = client.post("/customers/login", json=login_data)
    token = login_response.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/customers/my-tickets", headers=headers)
    assert response.status_code == 200
    assert "tickets" in response.get_json()


def test_authorization_flow(client, init_database):
    """Test that a user cannot modify another user's data."""
    # Get customer IDs from the init_database fixture
    customer1_id = init_database["customer"].id
    customer2_id = init_database["customer2"].id

    # Log in as customer 1
    login_data = {"email": "john.doe@test.com", "password": "password123"}
    login_response = client.post("/customers/login", json=login_data)
    token = login_response.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test 1: Try to update another customer's information (should be forbidden)
    update_data = {"first_name": "UpdatedByJohn"}
    response = client.put(f"/customers/{customer2_id}", json=update_data, headers=headers)
    assert response.status_code == 403
    assert "You can only update your own profile" in response.get_json()["message"]

    # Test 2: Update own information (should be successful)
    update_data = {"first_name": "Johnny"}
    response = client.put(f"/customers/{customer1_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.get_json()["first_name"] == "Johnny"
