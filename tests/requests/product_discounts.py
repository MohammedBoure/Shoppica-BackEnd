import requests
import pytest
import os
import json
from datetime import datetime, UTC

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000/api"
TOKEN_FILE = "tests/requests/token.txt"  # Path to token.txt

@pytest.fixture(scope="session")
def check_server():
    """Check if the server is running before tests."""
    try:
        response = requests.get(f"{BASE_URL}/product_discounts/product/1", timeout=5)
        if response.status_code not in [200, 400, 500]:
            pytest.fail(f"Server not responding at {BASE_URL}/product_discounts/product/1: {response.status_code} - {response.text}")
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
def setup_product_discount(admin_headers):
    """Create a product discount for testing and clean it up."""
    discount_data = {
        "product_id": 1,  # Matches existing product from get_tables.py
        "discount_percent": 15.0,
        "starts_at": "2025-05-23T00:00:00Z",
        "ends_at": "2025-12-31T23:59:59Z",
        "is_active": 1
    }
    response = requests.post(f"{BASE_URL}/product_discounts", json=discount_data, headers=admin_headers)
    if response.status_code != 201:
        pytest.fail(f"Failed to create product discount: {response.status_code} - {response.text}")
    discount_id = response.json().get("discount_id")
    if not discount_id:
        pytest.fail(f"Product discount created but no discount_id returned: {response.text}")
    yield discount_id
    try:
        requests.delete(f"{BASE_URL}/product_discounts/{discount_id}", headers=admin_headers)
    except Exception as e:
        print(f"Warning: Failed to delete product discount {discount_id}: {e}")

# --- Test Cases ---

def test_add_product_discount_success(admin_headers):
    """Test adding a product discount as an admin."""
    discount_data = {
        "product_id": 1,
        "discount_percent": 15.0,
        "starts_at": "2025-05-23T00:00:00Z",
        "ends_at": "2025-12-31T23:59:59Z",
        "is_active": 1
    }
    response = requests.post(f"{BASE_URL}/product_discounts", json=discount_data, headers=admin_headers)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["message"] == "Product discount added successfully"
    assert "discount_id" in data
    # Clean up
    requests.delete(f"{BASE_URL}/product_discounts/{data['discount_id']}", headers=admin_headers)

def test_add_product_discount_missing_fields(admin_headers):
    """Test adding a product discount with missing required fields."""
    invalid_data = {"product_id": 1}
    response = requests.post(f"{BASE_URL}/product_discounts", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Product ID and discount percent are required"

def test_add_product_discount_invalid_product_id(admin_headers):
    """Test adding a product discount with invalid product ID."""
    invalid_data = {
        "product_id": 0,
        "discount_percent": 15.0
    }
    response = requests.post(f"{BASE_URL}/product_discounts", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Product ID and discount percent are required"

def test_add_product_discount_invalid_discount_percent(admin_headers):
    """Test adding a product discount with invalid discount percent."""
    invalid_data = {
        "product_id": 1,
        "discount_percent": 150.0
    }
    response = requests.post(f"{BASE_URL}/product_discounts", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Discount percent must be between 0 and 100"

def test_add_product_discount_invalid_dates(admin_headers):
    """Test adding a product discount with invalid date range."""
    invalid_data = {
        "product_id": 1,
        "discount_percent": 15.0,
        "starts_at": "2025-12-31T23:59:59Z",
        "ends_at": "2025-05-23T00:00:00Z"
    }
    response = requests.post(f"{BASE_URL}/product_discounts", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "starts_at must be before ends_at"

def test_add_product_discount_no_token():
    """Test adding a product discount without authorization token."""
    discount_data = {
        "product_id": 1,
        "discount_percent": 15.0
    }
    response = requests.post(f"{BASE_URL}/product_discounts", json=discount_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_product_discount_by_id_success_admin(admin_headers, setup_product_discount):
    """Test retrieving a product discount by its ID (admin)."""
    discount_id = setup_product_discount
    response = requests.get(f"{BASE_URL}/product_discounts/{discount_id}", headers=admin_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["id"] == discount_id
    assert data["product_id"] == 1
    assert data["discount_percent"] == 15.0
    assert "starts_at" in data
    assert "ends_at" in data
    assert data["is_active"] == 1

def test_get_product_discount_by_id_not_found_admin(admin_headers):
    """Test retrieving a non-existent product discount by ID (admin)."""
    response = requests.get(f"{BASE_URL}/product_discounts/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Product discount not found"

def test_get_product_discounts_by_product_success(admin_headers):
    """Test retrieving all discounts for a specific product (public)."""
    # First, add a product discount
    discount_data = {
        "product_id": 1,
        "discount_percent": 15.0,
        "starts_at": "2025-05-23T00:00:00Z",
        "ends_at": "2025-12-31T23:59:59Z",
        "is_active": 1
    }
    post_response = requests.post(f"{BASE_URL}/product_discounts", json=discount_data, headers=admin_headers)
    assert post_response.status_code == 201
    discount_id = post_response.json()["discount_id"]

    # Retrieve discounts
    response = requests.get(f"{BASE_URL}/product_discounts/product/1")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "product_discounts" in data
    assert isinstance(data["product_discounts"], list)
    assert any(discount["id"] == discount_id for discount in data["product_discounts"])

    # Clean up
    requests.delete(f"{BASE_URL}/product_discounts/{discount_id}", headers=admin_headers)

def test_get_product_discounts_by_product_invalid_id():
    """Test retrieving discounts for an invalid product ID (public)."""
    response = requests.get(f"{BASE_URL}/product_discounts/product/0")
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Product ID must be a positive integer"

def test_get_valid_product_discounts_success(admin_headers):
    """Test retrieving valid discounts for a specific product (public)."""
    # Add a valid product discount
    discount_data = {
        "product_id": 1,
        "discount_percent": 15.0,
        "starts_at": "2025-05-23T00:00:00Z",
        "ends_at": "2025-12-31T23:59:59Z",
        "is_active": 1
    }
    post_response = requests.post(f"{BASE_URL}/product_discounts", json=discount_data, headers=admin_headers)
    assert post_response.status_code == 201
    discount_id = post_response.json()["discount_id"]

    # Retrieve valid discounts
    response = requests.get(f"{BASE_URL}/product_discounts/valid/1")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "product_discounts" in data
    assert isinstance(data["product_discounts"], list)
    assert any(discount["id"] == discount_id for discount in data["product_discounts"])

    # Clean up
    requests.delete(f"{BASE_URL}/product_discounts/{discount_id}", headers=admin_headers)

def test_get_valid_product_discounts_invalid_id():
    """Test retrieving valid discounts for an invalid product ID (public)."""
    response = requests.get(f"{BASE_URL}/product_discounts/valid/0")
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Product ID must be a positive integer"

def test_update_product_discount_success(admin_headers, setup_product_discount):
    """Test updating a product discount as an admin."""
    discount_id = setup_product_discount
    update_data = {
        "discount_percent": 20.0,
        "starts_at": "2025-06-01T00:00:00Z",
        "ends_at": "2025-12-31T23:59:59Z",
        "is_active": 0
    }
    response = requests.put(f"{BASE_URL}/product_discounts/{discount_id}", json=update_data, headers=admin_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["message"] == "Product discount updated successfully"

def test_update_product_discount_invalid_percent(admin_headers, setup_product_discount):
    """Test updating a product discount with invalid discount percent."""
    discount_id = setup_product_discount
    invalid_data = {
        "discount_percent": 150.0
    }
    response = requests.put(f"{BASE_URL}/product_discounts/{discount_id}", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Discount percent must be between 0 and 100"

def test_update_product_discount_no_token(setup_product_discount):
    """Test updating a product discount without authorization token."""
    discount_id = setup_product_discount
    update_data = {"discount_percent": 20.0}
    response = requests.put(f"{BASE_URL}/product_discounts/{discount_id}", json=update_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_delete_product_discount_success_admin(admin_headers, setup_product_discount):
    """Test deleting a product discount as an admin."""
    discount_id = setup_product_discount
    response = requests.delete(f"{BASE_URL}/product_discounts/{discount_id}", headers=admin_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["message"] == "Product discount deleted successfully"
    # Verify deletion
    get_response = requests.get(f"{BASE_URL}/product_discounts/{discount_id}", headers=admin_headers)
    assert get_response.status_code == 404

def test_delete_product_discount_not_found_admin(admin_headers):
    """Test deleting a non-existent product discount."""
    response = requests.delete(f"{BASE_URL}/product_discounts/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Product discount not found or failed to delete"

def test_get_all_product_discounts_paginated_success_admin(admin_headers, setup_product_discount):
    """Test retrieving all product discounts with pagination (admin)."""
    # Add multiple discounts
    for i in range(3):
        discount_data = {
            "product_id": 1,
            "discount_percent": 15.0 + i,
            "starts_at": "2025-05-23T00:00:00Z",
            "ends_at": "2025-12-31T23:59:59Z",
            "is_active": 1
        }
        post_response = requests.post(f"{BASE_URL}/product_discounts", json=discount_data, headers=admin_headers)
        assert post_response.status_code == 201

    response = requests.get(f"{BASE_URL}/product_discounts?page=1&per_page=2", headers=admin_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "product_discounts" in data
    assert isinstance(data["product_discounts"], list)
    assert len(data["product_discounts"]) == 2
    assert "total" in data
    assert data["total"] >= 3
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert all("product_name" in discount for discount in data["product_discounts"])

def test_get_all_product_discounts_paginated_no_token():
    """Test retrieving all product discounts without authorization token."""
    response = requests.get(f"{BASE_URL}/product_discounts?page=1&per_page=20")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

if __name__ == "__main__":
    pytest.main(["-v", __file__])