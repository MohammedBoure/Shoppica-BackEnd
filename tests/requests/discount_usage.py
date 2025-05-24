import requests
import pytest
import os
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000/api"
TOKEN_FILE = "tests/requests/token.txt"  # Path to token.txt

@pytest.fixture(scope="session")
def check_server():
    """Check if the server is running before tests."""
    try:
        response = requests.get(f"{BASE_URL}/discount_usages/user/1", timeout=5)
        if response.status_code not in [200, 401, 403, 500]:
            pytest.fail(f"Server not responding at {BASE_URL}/discount_usages/user/1: {response.status_code} - {response.text}")
    except requests.ConnectionError:
        pytest.fail(f"Cannot connect to server at {BASE_URL}. Ensure the server is running.")

@pytest.fixture(scope="session")
def admin_token(check_server):
    """Read admin token from token.txt."""
    try:
        with open(TOKEN_FILE, 'r') as file:
            token = file.read().strip()
            if not token:
                pytest.fail("Token file is empty or invalid.")
            return token
    except FileNotFoundError:
        pytest.fail(f"Token file not found at {TOKEN_FILE}.")
    except Exception as e:
        pytest.fail(f"Error reading token file: {e}")

@pytest.fixture(scope="session")
def admin_headers(admin_token):
    """Provide admin authentication headers."""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}

@pytest.fixture(scope="function")
def setup_discount(admin_headers):
    """Create a discount for discount usage testing and clean it up."""
    discount_data = {
        "code": f"SAVE10_{datetime.utcnow().timestamp()}",
        "discount_percent": 10.0,
        "max_uses": 100,
        "expires_at": "2025-12-31T23:59:59Z"
    }
    response = requests.post(f"{BASE_URL}/discounts", json=discount_data, headers=admin_headers)
    if response.status_code != 201:
        pytest.fail(f"Failed to create discount: {response.status_code} - {response.text}")
    discount_id = response.json().get("discount_id")
    if not discount_id:
        pytest.fail(f"Discount created but no discount_id returned: {response.text}")
    yield discount_id
    try:
        requests.delete(f"{BASE_URL}/discounts/{discount_id}", headers=admin_headers)
    except Exception as e:
        print(f"Warning: Failed to delete discount {discount_id}: {e}")

@pytest.fixture(scope="function")
def cleanup_discount_usages(admin_headers):
    """Clean up created discount usages after tests."""
    usages_to_delete = []
    yield usages_to_delete
    for usage_id in usages_to_delete:
        try:
            response = requests.delete(f"{BASE_URL}/discount_usages/{usage_id}", headers=admin_headers)
            if response.status_code not in [200, 404]:
                print(f"Warning: Failed to delete discount usage {usage_id}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during discount usage cleanup for ID {usage_id}: {e}")

# --- Test Cases ---

def test_add_discount_usage_success(admin_headers, setup_discount, cleanup_discount_usages):
    """Test adding a discount usage as an authenticated user."""
    usage_data = {
        "discount_id": setup_discount,
        "user_id": 1  # Matches admin user in token
    }
    response = requests.post(f"{BASE_URL}/discount_usages", json=usage_data, headers=admin_headers)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["message"] == "Discount usage added successfully"
    assert "usage_id" in data
    cleanup_discount_usages.append(data["usage_id"])

def test_add_discount_usage_missing_fields(admin_headers, setup_discount):
    """Test adding a discount usage with missing required fields."""
    invalid_data = {"discount_id": setup_discount}
    response = requests.post(f"{BASE_URL}/discount_usages", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Discount ID and user ID are required"

def test_add_discount_usage_invalid_discount_id(admin_headers):
    """Test adding a discount usage with invalid discount ID."""
    invalid_data = {
        "discount_id": 0,
        "user_id": 1
    }
    response = requests.post(f"{BASE_URL}/discount_usages", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Discount ID and user ID are required"
    
def test_add_discount_usage_unauthorized_user_id(admin_headers, setup_discount):
    """Test adding a discount usage with user_id not matching token identity."""
    invalid_data = {
        "discount_id": setup_discount,
        "user_id": 999  # Does not match admin user_id=1
    }
    response = requests.post(f"{BASE_URL}/discount_usages", json=invalid_data, headers=admin_headers)
    assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Unauthorized: User ID does not match authenticated user"

def test_add_discount_usage_no_token(setup_discount):
    """Test adding a discount usage without any authorization token."""
    usage_data = {
        "discount_id": setup_discount,
        "user_id": 1
    }
    response = requests.post(f"{BASE_URL}/discount_usages", json=usage_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_discount_usage_by_id_success_admin(admin_headers, setup_discount, cleanup_discount_usages):
    """Test retrieving a discount usage by its ID (admin)."""
    # First, add a discount usage
    usage_data = {
        "discount_id": setup_discount,
        "user_id": 1
    }
    post_response = requests.post(f"{BASE_URL}/discount_usages", json=usage_data, headers=admin_headers)
    assert post_response.status_code == 201
    usage_id = post_response.json()["usage_id"]
    cleanup_discount_usages.append(usage_id)

    # Retrieve the discount usage
    get_response = requests.get(f"{BASE_URL}/discount_usages/{usage_id}", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert data["id"] == usage_id
    assert data["discount_id"] == usage_data["discount_id"]
    assert data["user_id"] == usage_data["user_id"]
    assert "used_at" in data

def test_get_discount_usage_by_id_not_found_admin(admin_headers):
    """Test retrieving a non-existent discount usage by ID (admin)."""
    response = requests.get(f"{BASE_URL}/discount_usages/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Discount usage not found"

def test_get_discount_usages_by_discount_success_admin(admin_headers, setup_discount, cleanup_discount_usages):
    """Test retrieving all discount usages for a specific discount (admin)."""
    # Add two discount usages
    usage_data1 = {"discount_id": setup_discount, "user_id": 1}
    usage_data2 = {"discount_id": setup_discount, "user_id": 1}

    post_response1 = requests.post(f"{BASE_URL}/discount_usages", json=usage_data1, headers=admin_headers)
    assert post_response1.status_code == 201
    cleanup_discount_usages.append(post_response1.json()["usage_id"])

    post_response2 = requests.post(f"{BASE_URL}/discount_usages", json=usage_data2, headers=admin_headers)
    assert post_response2.status_code == 201
    cleanup_discount_usages.append(post_response2.json()["usage_id"])

    # Retrieve discount usages for the discount
    get_response = requests.get(f"{BASE_URL}/discount_usages/discount/{setup_discount}", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert "discount_usages" in data
    assert isinstance(data["discount_usages"], list)
    assert len(data["discount_usages"]) >= 2
    assert all(usage["discount_id"] == setup_discount for usage in data["discount_usages"])

def test_get_discount_usages_by_discount_no_usages_admin(admin_headers, setup_discount):
    """Test retrieving discount usages for a discount with no usages."""
    get_response = requests.get(f"{BASE_URL}/discount_usages/discount/{setup_discount}", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert "discount_usages" in data
    assert len(data["discount_usages"]) == 0

def test_get_discount_usages_by_user_success(admin_headers, setup_discount, cleanup_discount_usages):
    """Test retrieving all discount usages for a specific user."""
    # Add a discount usage
    usage_data = {"discount_id": setup_discount, "user_id": 1}
    post_response = requests.post(f"{BASE_URL}/discount_usages", json=usage_data, headers=admin_headers)
    assert post_response.status_code == 201
    usage_id = post_response.json()["usage_id"]
    cleanup_discount_usages.append(usage_id)

    # Retrieve discount usages for the user
    get_response = requests.get(f"{BASE_URL}/discount_usages/user/1", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert "discount_usages" in data
    assert isinstance(data["discount_usages"], list)
    assert len(data["discount_usages"]) >= 1
    assert any(usage["id"] == usage_id for usage in data["discount_usages"])

def test_get_discount_usages_by_user_unauthorized(admin_headers, setup_discount):
    """Test retrieving discount usages for a user_id not matching token identity."""
    response = requests.get(f"{BASE_URL}/discount_usages/user/999", headers=admin_headers)
    assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Unauthorized: User ID does not match authenticated user"

def test_get_discount_usages_by_user_no_token():
    """Test retrieving discount usages by user without any authorization token."""
    response = requests.get(f"{BASE_URL}/discount_usages/user/1")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_delete_discount_usage_success_admin(admin_headers, setup_discount, cleanup_discount_usages):
    """Test deleting a discount usage as an admin."""
    # First, add a discount usage
    usage_data = {"discount_id": setup_discount, "user_id": 1}
    post_response = requests.post(f"{BASE_URL}/discount_usages", json=usage_data, headers=admin_headers)
    assert post_response.status_code == 201
    usage_id = post_response.json()["usage_id"]
    cleanup_discount_usages.append(usage_id)

    # Delete the discount usage
    delete_response = requests.delete(f"{BASE_URL}/discount_usages/{usage_id}", headers=admin_headers)
    assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
    data = delete_response.json()
    assert data["message"] == "Discount usage deleted successfully"
    if usage_id in cleanup_discount_usages:
        cleanup_discount_usages.remove(usage_id)

    # Verify deletion
    get_response = requests.get(f"{BASE_URL}/discount_usages/{usage_id}", headers=admin_headers)
    assert get_response.status_code == 404

def test_delete_discount_usage_not_found_admin(admin_headers):
    """Test deleting a non-existent discount usage."""
    response = requests.delete(f"{BASE_URL}/discount_usages/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert "error" in data
    assert "Discount usage not found or failed to delete" in data["error"]

def test_delete_discount_usage_no_token():
    """Test deleting a discount usage without any authorization token."""
    response = requests.delete(f"{BASE_URL}/discount_usages/1")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_all_discount_usages_paginated_success_admin(admin_headers, setup_discount, cleanup_discount_usages):
    """Test retrieving all discount usages with pagination (admin)."""
    # Add some discount usages
    for i in range(5):
        usage_data = {"discount_id": setup_discount, "user_id": 1}
        post_response = requests.post(f"{BASE_URL}/discount_usages", json=usage_data, headers=admin_headers)
        assert post_response.status_code == 201
        cleanup_discount_usages.append(post_response.json()["usage_id"])

    response = requests.get(f"{BASE_URL}/discount_usages?page=1&per_page=3", headers=admin_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "discount_usages" in data
    assert isinstance(data["discount_usages"], list)
    assert len(data["discount_usages"]) == 3
    assert "total" in data
    assert data["total"] >= 5
    assert data["page"] == 1
    assert data["per_page"] == 3
    # Check if discount_code is included (assuming supported by DiscountUsageManager)
    assert all("discount_code" in usage for usage in data["discount_usages"])

def test_get_all_discount_usages_paginated_no_token():
    """Test retrieving all discount usages without any authorization token."""
    response = requests.get(f"{BASE_URL}/discount_usages?page=1&per_page=20")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

if __name__ == "__main__":
    pytest.main(["-v", __file__])