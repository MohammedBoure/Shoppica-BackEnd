import requests
import pytest
import os
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000/api"
TOKEN_FILE = "tests/requests/token.txt"  # Path to token.txt

@pytest.fixture(scope="session")
def check_server():
    """Check if the server is running before tests."""
    try:
        response = requests.get(f"{BASE_URL}/discounts/code/TESTCODE", timeout=5)
        if response.status_code not in [200, 400, 401, 404, 500]:
            pytest.fail(f"Server not responding at {BASE_URL}/discounts/code/TESTCODE: {response.status_code} - {response.text}")
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
def cleanup_discounts(admin_headers):
    """Clean up created discounts after tests."""
    discounts_to_delete = []
    yield discounts_to_delete
    for discount_id in discounts_to_delete:
        try:
            response = requests.delete(f"{BASE_URL}/discounts/{discount_id}", headers=admin_headers)
            if response.status_code not in [200, 404]:
                print(f"Warning: Failed to delete discount {discount_id}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during discount cleanup for ID {discount_id}: {e}")

# --- Test Cases ---

def test_add_discount_success_admin(admin_headers, cleanup_discounts):
    """Test adding a discount as an admin."""
    discount_data = {
        "code": "SAVE10",
        "discount_percent": 10.0,
        "max_uses": 100,
        "expires_at": "2025-12-31T23:59:59Z",
        "description": "10% off your order"
    }
    response = requests.post(f"{BASE_URL}/discounts", json=discount_data, headers=admin_headers)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["message"] == "Discount added successfully"
    assert "discount_id" in data
    cleanup_discounts.append(data["discount_id"])

def test_add_discount_missing_fields(admin_headers):
    """Test adding a discount with missing required fields."""
    invalid_data = {"code": "SAVE10"}
    response = requests.post(f"{BASE_URL}/discounts", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Code and discount percent are required"

def test_add_discount_invalid_percent(admin_headers):
    """Test adding a discount with invalid discount percent."""
    invalid_data = {
        "code": "SAVE10",
        "discount_percent": 150.0
    }
    response = requests.post(f"{BASE_URL}/discounts", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Discount percent must be between 0 and 100"

def test_add_discount_negative_max_uses(admin_headers):
    """Test adding a discount with negative max uses."""
    invalid_data = {
        "code": "SAVE10",
        "discount_percent": 10.0,
        "max_uses": -1
    }
    response = requests.post(f"{BASE_URL}/discounts", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Max uses must be non-negative"

def test_add_discount_no_token():
    """Test adding a discount without any authorization token."""
    discount_data = {
        "code": "SAVE10",
        "discount_percent": 10.0
    }
    response = requests.post(f"{BASE_URL}/discounts", json=discount_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_discount_by_id_success_admin(admin_headers, cleanup_discounts):
    """Test retrieving a discount by its ID (admin)."""
    # First, add a discount
    discount_data = {
        "code": "SAVE10",
        "discount_percent": 10.0,
        "max_uses": 100,
        "expires_at": "2025-12-31T23:59:59Z"
    }
    post_response = requests.post(f"{BASE_URL}/discounts", json=discount_data, headers=admin_headers)
    assert post_response.status_code == 201
    discount_id = post_response.json()["discount_id"]
    cleanup_discounts.append(discount_id)

    # Retrieve the discount
    get_response = requests.get(f"{BASE_URL}/discounts/{discount_id}", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert data["id"] == discount_id
    assert data["code"] == discount_data["code"]
    assert data["discount_percent"] == discount_data["discount_percent"]
    assert data["max_uses"] == discount_data["max_uses"]
    assert data["expires_at"] == discount_data["expires_at"]
    assert data["is_active"] == 1

def test_get_discount_by_id_not_found_admin(admin_headers):
    """Test retrieving a non-existent discount by ID (admin)."""
    response = requests.get(f"{BASE_URL}/discounts/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {get_response.text}"
    data = response.json()
    assert data["error"] == "Discount not found"

def test_get_discount_by_code_success(admin_headers, cleanup_discounts):
    """Test retrieving a discount by its code (user)."""
    # First, add a discount
    discount_data = {
        "code": "SAVE20",
        "discount_percent": 20.0,
        "max_uses": 50,
        "expires_at": "2025-12-31T23:59:59Z"
    }
    post_response = requests.post(f"{BASE_URL}/discounts", json=discount_data, headers=admin_headers)
    assert post_response.status_code == 201
    discount_id = post_response.json()["discount_id"]
    cleanup_discounts.append(discount_id)

    # Retrieve the discount by code
    get_response = requests.get(f"{BASE_URL}/discounts/code/SAVE20", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert data["id"] == discount_id
    assert data["code"] == discount_data["code"]
    assert data["discount_percent"] == discount_data["discount_percent"]
    assert data["max_uses"] == discount_data["max_uses"]
    assert data["expires_at"] == discount_data["expires_at"]

def test_get_discount_by_code_not_found(admin_headers):
    """Test retrieving a non-existent discount by code."""
    response = requests.get(f"{BASE_URL}/discounts/code/NONEXISTENT", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Discount not found"

def test_get_discount_by_code_no_token():
    """Test retrieving a discount by code without any authorization token."""
    response = requests.get(f"{BASE_URL}/discounts/code/SAVE20")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_valid_discount_success(admin_headers, cleanup_discounts):
    """Test retrieving a valid discount by its code."""
    # First, add a valid discount
    discount_data = {
        "code": "SAVE15",
        "discount_percent": 15.0,
        "max_uses": 100,
        "expires_at": "2025-12-31T23:59:59Z",
        "is_active": 1
    }
    post_response = requests.post(f"{BASE_URL}/discounts", json=discount_data, headers=admin_headers)
    assert post_response.status_code == 201
    discount_id = post_response.json()["discount_id"]
    cleanup_discounts.append(discount_id)

    # Retrieve the valid discount
    get_response = requests.get(f"{BASE_URL}/discounts/valid/SAVE15", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert data["id"] == discount_id
    assert data["code"] == discount_data["code"]
    assert data["discount_percent"] == discount_data["discount_percent"]

def test_get_valid_discount_expired(admin_headers, cleanup_discounts):
    """Test retrieving an expired discount by its code."""
    # Add an expired discount
    expired_date = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    discount_data = {
        "code": "EXPIRED",
        "discount_percent": 10.0,
        "expires_at": expired_date
    }
    post_response = requests.post(f"{BASE_URL}/discounts", json=discount_data, headers=admin_headers)
    assert post_response.status_code == 201
    discount_id = post_response.json()["discount_id"]
    cleanup_discounts.append(discount_id)

    # Try to retrieve the valid discount
    get_response = requests.get(f"{BASE_URL}/discounts/valid/EXPIRED", headers=admin_headers)
    assert get_response.status_code == 404, f"Expected 404, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert data["error"] == "Valid discount not found"

def test_get_valid_discount_no_token():
    """Test retrieving a valid discount without any authorization token."""
    response = requests.get(f"{BASE_URL}/discounts/valid/SAVE15")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_update_discount_success_admin(admin_headers, cleanup_discounts):
    """Test updating a discount as an admin."""
    # First, add a discount
    discount_data = {
        "code": "SAVE10",
        "discount_percent": 10.0,
        "max_uses": 100
    }
    post_response = requests.post(f"{BASE_URL}/discounts", json=discount_data, headers=admin_headers)
    assert post_response.status_code == 201
    discount_id = post_response.json()["discount_id"]
    cleanup_discounts.append(discount_id)

    # Update the discount
    updated_data = {
        "code": "SAVE10NEW",
        "discount_percent": 15.0,
        "max_uses": 50,
        "description": "Updated 15% off",
        "is_active": 0
    }
    put_response = requests.put(f"{BASE_URL}/discounts/{discount_id}", json=updated_data, headers=admin_headers)
    assert put_response.status_code == 200, f"Expected 200, got {put_response.status_code}: {put_response.text}"
    data = put_response.json()
    assert data["message"] == "Discount updated successfully"

    # Verify the update
    get_response = requests.get(f"{BASE_URL}/discounts/{discount_id}", headers=admin_headers)
    assert get_response.status_code == 200
    updated_discount = get_response.json()
    assert updated_discount["code"] == updated_data["code"]
    assert updated_discount["discount_percent"] == updated_data["discount_percent"]
    assert updated_discount["max_uses"] == updated_data["max_uses"]
    assert updated_discount["description"] == updated_data["description"]
    assert updated_discount["is_active"] == updated_data["is_active"]

def test_update_discount_not_found(admin_headers):
    """Test updating a non-existent discount."""
    updated_data = {"code": "SAVE10NEW"}
    response = requests.put(f"{BASE_URL}/discounts/99999", json=updated_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Failed to update discount"

def test_update_discount_invalid_percent(admin_headers, cleanup_discounts):
    """Test updating a discount with invalid discount percent."""
    # First, add a discount
    discount_data = {
        "code": "SAVE10",
        "discount_percent": 10.0
    }
    post_response = requests.post(f"{BASE_URL}/discounts", json=discount_data, headers=admin_headers)
    assert post_response.status_code == 201
    discount_id = post_response.json()["discount_id"]
    cleanup_discounts.append(discount_id)

    # Update with invalid percent
    updated_data = {"discount_percent": 150.0}
    response = requests.put(f"{BASE_URL}/discounts/{discount_id}", json=updated_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Discount percent must be between 0 and 100"

def test_update_discount_no_token():
    """Test updating a discount without any authorization token."""
    updated_data = {"code": "SAVE10NEW"}
    response = requests.put(f"{BASE_URL}/discounts/1", json=updated_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_delete_discount_success_admin(admin_headers, cleanup_discounts):
    """Test deleting a discount as an admin."""
    # First, add a discount
    discount_data = {
        "code": "SAVE10",
        "discount_percent": 10.0
    }
    post_response = requests.post(f"{BASE_URL}/discounts", json=discount_data, headers=admin_headers)
    assert post_response.status_code == 201
    discount_id = post_response.json()["discount_id"]
    cleanup_discounts.append(discount_id)

    # Delete the discount
    delete_response = requests.delete(f"{BASE_URL}/discounts/{discount_id}", headers=admin_headers)
    assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
    data = delete_response.json()
    assert data["message"] == "Discount deleted successfully"
    if discount_id in cleanup_discounts:
        cleanup_discounts.remove(discount_id)

    # Verify deletion
    get_response = requests.get(f"{BASE_URL}/discounts/{discount_id}", headers=admin_headers)
    assert get_response.status_code == 404

def test_delete_discount_not_found(admin_headers):
    """Test deleting a non-existent discount."""
    response = requests.delete(f"{BASE_URL}/discounts/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert "error" in data
    assert "Discount not found or failed to delete" in data["error"]

def test_delete_discount_no_token():
    """Test deleting a discount without any authorization token."""
    response = requests.delete(f"{BASE_URL}/discounts/1")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_all_discounts_paginated_success_admin(admin_headers, cleanup_discounts):
    """Test retrieving all discounts with pagination (admin)."""
    # Add some discounts
    for i in range(5):
        discount_data = {
            "code": f"SAVE{i}",
            "discount_percent": 10.0 + i,
            "max_uses": 100 + i
        }
        post_response = requests.post(f"{BASE_URL}/discounts", json=discount_data, headers=admin_headers)
        assert post_response.status_code == 201
        cleanup_discounts.append(post_response.json()["discount_id"])

    response = requests.get(f"{BASE_URL}/discounts?page=1&per_page=3", headers=admin_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "discounts" in data
    assert isinstance(data["discounts"], list)
    assert len(data["discounts"]) == 3
    assert "total" in data
    assert data["total"] >= 5
    assert data["page"] == 1
    assert data["per_page"] == 3

def test_get_all_discounts_paginated_no_token():
    """Test retrieving all discounts without any authorization token."""
    response = requests.get(f"{BASE_URL}/discounts?page=1&per_page=20")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

if __name__ == "__main__":
    pytest.main(["-v", __file__])