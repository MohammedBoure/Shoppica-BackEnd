import requests
import pytest
import os
import json

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000/api"
TOKEN_FILE = "tests/requests/token.txt"  # Path to token.txt

@pytest.fixture(scope="session")
def check_server():
    """Check if the server is running before tests."""
    try:
        response = requests.get(f"{BASE_URL}/cart_items/user/1", timeout=5)
        if response.status_code not in [200, 400, 401, 403, 404]:
            pytest.fail(f"Server not responding at {BASE_URL}/cart_items/user/1: {response.status_code} - {response.text}")
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
def cleanup_cart_items(admin_headers):
    """Clean up created cart items after tests."""
    cart_items_to_delete = []
    yield cart_items_to_delete
    for cart_item_id in cart_items_to_delete:
        try:
            response = requests.delete(f"{BASE_URL}/cart_items/{cart_item_id}", headers=admin_headers)
            if response.status_code not in [200, 404]:
                print(f"Warning: Failed to delete cart item {cart_item_id}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during cart item cleanup for ID {cart_item_id}: {e}")

# --- Test Cases ---

def test_add_cart_item_success_admin(admin_headers, cleanup_cart_items):
    """Test adding a cart item as an admin."""
    cart_item_data = {
        "user_id": 1,  # Valid user_id from database
        "product_id": 1,  # Valid product_id from database
        "quantity": 2
    }
    response = requests.post(f"{BASE_URL}/cart_items", json=cart_item_data, headers=admin_headers)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["message"] == "Cart item added successfully"
    assert "cart_item_id" in data
    cleanup_cart_items.append(data["cart_item_id"])

def test_add_cart_item_missing_fields(admin_headers):
    """Test adding a cart item with missing required fields."""
    invalid_data = {"product_id": 1, "quantity": 2}
    response = requests.post(f"{BASE_URL}/cart_items", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "User ID, product ID, and quantity are required"

def test_add_cart_item_no_token():
    """Test adding a cart item without any authorization token."""
    cart_item_data = {"user_id": 1, "product_id": 1, "quantity": 2}
    response = requests.post(f"{BASE_URL}/cart_items", json=cart_item_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_cart_item_by_id_success(admin_headers, cleanup_cart_items):
    """Test retrieving a cart item by its ID."""
    # First, add a cart item
    cart_item_data = {
        "user_id": 1,
        "product_id": 1,
        "quantity": 3
    }
    post_response = requests.post(f"{BASE_URL}/cart_items", json=cart_item_data, headers=admin_headers)
    assert post_response.status_code == 201, f"Expected 201, got {post_response.status_code}: {post_response.text}"
    cart_item_id = post_response.json()["cart_item_id"]
    cleanup_cart_items.append(cart_item_id)

    # Retrieve the cart item
    get_response = requests.get(f"{BASE_URL}/cart_items/{cart_item_id}", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert data["id"] == cart_item_id
    assert data["user_id"] == cart_item_data["user_id"]
    assert data["product_id"] == cart_item_data["product_id"]
    assert data["quantity"] == cart_item_data["quantity"]
    assert "added_at" in data

def test_get_cart_item_by_id_not_found(admin_headers):
    """Test retrieving a non-existent cart item by ID."""
    response = requests.get(f"{BASE_URL}/cart_items/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Cart item not found"

def test_get_cart_items_by_user_success(admin_headers, cleanup_cart_items):
    """Test retrieving all cart items for a specific user."""
    user_id = 1
    # Add two cart items
    cart_item_data1 = {"user_id": user_id, "product_id": 1, "quantity": 2}
    cart_item_data2 = {"user_id": user_id, "product_id": 2, "quantity": 1}

    post_response1 = requests.post(f"{BASE_URL}/cart_items", json=cart_item_data1, headers=admin_headers)
    assert post_response1.status_code == 201
    cleanup_cart_items.append(post_response1.json()["cart_item_id"])

    post_response2 = requests.post(f"{BASE_URL}/cart_items", json=cart_item_data2, headers=admin_headers)
    assert post_response2.status_code == 201
    cleanup_cart_items.append(post_response2.json()["cart_item_id"])

    # Retrieve cart items for the user
    get_response = requests.get(f"{BASE_URL}/cart_items/user/{user_id}", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert "cart_items" in data
    assert isinstance(data["cart_items"], list)
    assert len(data["cart_items"]) >= 2
    assert any(item["quantity"] == 2 and item["product_id"] == 1 for item in data["cart_items"])
    assert any(item["quantity"] == 1 and item["product_id"] == 2 for item in data["cart_items"])
    assert all("product_name" in item and "product_price" in item for item in data["cart_items"])

def test_get_cart_items_by_user_no_items(admin_headers):
    """Test retrieving cart items for a user with no cart items."""
    user_id = 1  # Assuming user_id=1 has no cart items after cleanup
    get_response = requests.get(f"{BASE_URL}/cart_items/user/{user_id}", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert "cart_items" in data
    assert len(data["cart_items"]) == 0
    assert data["message"] == "No cart items found for this user"

def test_update_cart_item_success_admin(admin_headers, cleanup_cart_items):
    """Test updating a cart item as an admin."""
    # First, add a cart item
    cart_item_data = {
        "user_id": 1,
        "product_id": 1,
        "quantity": 2
    }
    post_response = requests.post(f"{BASE_URL}/cart_items", json=cart_item_data, headers=admin_headers)
    assert post_response.status_code == 201
    cart_item_id = post_response.json()["cart_item_id"]
    cleanup_cart_items.append(cart_item_id)

    # Update the cart item
    updated_data = {"quantity": 5}
    put_response = requests.put(f"{BASE_URL}/cart_items/{cart_item_id}", json=updated_data, headers=admin_headers)
    assert put_response.status_code == 200, f"Expected 200, got {put_response.status_code}: {put_response.text}"
    data = put_response.json()
    assert data["message"] == "Cart item updated successfully"

    # Verify the update
    get_response = requests.get(f"{BASE_URL}/cart_items/{cart_item_id}", headers=admin_headers)
    assert get_response.status_code == 200
    updated_cart_item = get_response.json()
    assert updated_cart_item["quantity"] == updated_data["quantity"]

def test_update_cart_item_not_found(admin_headers):
    """Test updating a non-existent cart item."""
    updated_data = {"quantity": 5}
    response = requests.put(f"{BASE_URL}/cart_items/99999", json=updated_data, headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Cart item not found"

def test_update_cart_item_no_token():
    """Test updating a cart item without any authorization token."""
    updated_data = {"quantity": 5}
    response = requests.put(f"{BASE_URL}/cart_items/1", json=updated_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_delete_cart_item_success_admin(admin_headers, cleanup_cart_items):
    """Test deleting a cart item as an admin."""
    # First, add a cart item
    cart_item_data = {
        "user_id": 1,
        "product_id": 1,
        "quantity": 3
    }
    post_response = requests.post(f"{BASE_URL}/cart_items", json=cart_item_data, headers=admin_headers)
    assert post_response.status_code == 201
    cart_item_id = post_response.json()["cart_item_id"]
    cleanup_cart_items.append(cart_item_id)

    # Delete the cart item
    delete_response = requests.delete(f"{BASE_URL}/cart_items/{cart_item_id}", headers=admin_headers)
    assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
    data = delete_response.json()
    assert data["message"] == "Cart item deleted successfully"
    if cart_item_id in cleanup_cart_items:
        cleanup_cart_items.remove(cart_item_id)

    # Verify deletion
    get_response = requests.get(f"{BASE_URL}/cart_items/{cart_item_id}", headers=admin_headers)
    assert get_response.status_code == 404

def test_delete_cart_item_not_found(admin_headers):
    """Test deleting a non-existent cart item."""
    response = requests.delete(f"{BASE_URL}/cart_items/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert "error" in data
    assert "Cart item not found" in data["error"] or "Cart item not found or failed to delete" in data["error"]

def test_delete_cart_item_no_token():
    """Test deleting a cart item without any authorization token."""
    response = requests.delete(f"{BASE_URL}/cart_items/1")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_all_cart_items_paginated_success(admin_headers, cleanup_cart_items):
    """Test retrieving all cart items with pagination as admin."""
    user_id = 1
    # Add some cart items
    for i in range(5):
        cart_item_data = {
            "user_id": user_id,
            "product_id": 1,  # Using product_id=1 for simplicity
            "quantity": 1 + (i % 3)
        }
        post_response = requests.post(f"{BASE_URL}/cart_items", json=cart_item_data, headers=admin_headers)
        assert post_response.status_code == 201
        cleanup_cart_items.append(post_response.json()["cart_item_id"])

    response = requests.get(f"{BASE_URL}/cart_items?page=1&per_page=3", headers=admin_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "cart_items" in data
    assert isinstance(data["cart_items"], list)
    assert len(data["cart_items"]) == 3
    assert "total" in data
    assert data["total"] >= 5
    assert data["page"] == 1
    assert data["per_page"] == 3
    assert all("product_name" in item and "product_price" in item for item in data["cart_items"])

def test_get_all_cart_items_paginated_no_admin_token():
    """Test retrieving all cart items without admin token."""
    response = requests.get(f"{BASE_URL}/cart_items?page=1&per_page=20")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

if __name__ == "__main__":
    pytest.main(["-v", __file__])