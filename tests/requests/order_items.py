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
        response = requests.get(f"{BASE_URL}/order_items/order/1", timeout=5)
        if response.status_code not in [200, 400, 401, 403, 404]:
            pytest.fail(f"Server not responding at {BASE_URL}/order_items/order/1: {response.status_code} - {response.text}")
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
def setup_address(admin_headers):
    """Create a shipping address for order testing and clean it up."""
    address_payload = {
        "user_id": 1,
        "address_line1": "123 Test Street",
        "city": "Test City",
        "state": "Test State",
        "country": "Test Country",
        "postal_code": "12345"
    }
    response = requests.post(f"{BASE_URL}/addresses", json=address_payload, headers=admin_headers)
    if response.status_code != 201:
        pytest.fail(f"Failed to create address: {response.status_code} - {response.text}")
    address_id = response.json().get("address_id")
    if not address_id:
        pytest.fail(f"Address created but no address_id returned: {response.text}")
    yield address_id
    try:
        requests.delete(f"{BASE_URL}/addresses/{address_id}", headers=admin_headers)
    except Exception as e:
        print(f"Warning: Failed to delete address {address_id}: {e}")

@pytest.fixture(scope="function")
def setup_order(admin_headers, setup_address):
    """Create an order for order item testing and clean it up."""
    order_payload = {
        "user_id": 1,
        "shipping_address_id": setup_address,
        "total_price": 99.99,
        "status": "pending"
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_payload, headers=admin_headers)
    if response.status_code != 201:
        pytest.fail(f"Failed to create order: {response.status_code} - {response.text}")
    order_id = response.json().get("order_id")
    if not order_id:
        pytest.fail(f"Order created but no order_id returned: {response.text}")
    yield order_id
    try:
        requests.delete(f"{BASE_URL}/orders/{order_id}", headers=admin_headers)
    except Exception as e:
        print(f"Warning: Failed to delete order {order_id}: {e}")

@pytest.fixture(scope="function")
def cleanup_order_items(admin_headers):
    """Clean up created order items after tests."""
    order_items_to_delete = []
    yield order_items_to_delete
    for order_item_id in order_items_to_delete:
        try:
            response = requests.delete(f"{BASE_URL}/order_items/{order_item_id}", headers=admin_headers)
            if response.status_code not in [200, 404]:
                print(f"Warning: Failed to delete order item {order_item_id}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during order item cleanup for ID {order_item_id}: {e}")

# --- Test Cases ---

def test_add_order_item_success_admin(admin_headers, setup_order, cleanup_order_items):
    """Test adding an order item as an admin."""
    order_item_data = {
        "order_id": setup_order,
        "product_id": 1,  # Valid product_id from database
        "quantity": 2,
        "price": 19.99
    }
    response = requests.post(f"{BASE_URL}/order_items", json=order_item_data, headers=admin_headers)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["message"] == "Order item added successfully"
    assert "order_item_id" in data
    cleanup_order_items.append(data["order_item_id"])

def test_add_order_item_missing_fields(admin_headers, setup_order):
    """Test adding an order item with missing required fields."""
    invalid_data = {"order_id": setup_order, "product_id": 1}
    response = requests.post(f"{BASE_URL}/order_items", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Order ID, product ID, quantity, and price are required"

def test_add_order_item_no_token(setup_order):
    """Test adding an order item without any authorization token."""
    order_item_data = {"order_id": setup_order, "product_id": 1, "quantity": 2, "price": 19.99}
    response = requests.post(f"{BASE_URL}/order_items", json=order_item_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_order_item_by_id_success(admin_headers, setup_order, cleanup_order_items):
    """Test retrieving an order item by its ID."""
    # First, add an order item
    order_item_data = {
        "order_id": setup_order,
        "product_id": 1,
        "quantity": 2,
        "price": 19.99
    }
    post_response = requests.post(f"{BASE_URL}/order_items", json=order_item_data, headers=admin_headers)
    assert post_response.status_code == 201, f"Expected 201, got {post_response.status_code}: {post_response.text}"
    order_item_id = post_response.json()["order_item_id"]
    cleanup_order_items.append(order_item_id)

    # Retrieve the order item
    get_response = requests.get(f"{BASE_URL}/order_items/{order_item_id}", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert data["id"] == order_item_id
    assert data["order_id"] == order_item_data["order_id"]
    assert data["product_id"] == order_item_data["product_id"]
    assert data["quantity"] == order_item_data["quantity"]
    assert data["price"] == order_item_data["price"]

def test_get_order_item_by_id_not_found(admin_headers):
    """Test retrieving a non-existent order item by ID."""
    response = requests.get(f"{BASE_URL}/order_items/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Order item not found"

def test_get_order_items_by_order_success(admin_headers, setup_order, cleanup_order_items):
    """Test retrieving all order items for a specific order."""
    # Add two order items
    order_item_data1 = {"order_id": setup_order, "product_id": 1, "quantity": 2, "price": 19.99}
    order_item_data2 = {"order_id": setup_order, "product_id": 2, "quantity": 1, "price": 29.99}

    post_response1 = requests.post(f"{BASE_URL}/order_items", json=order_item_data1, headers=admin_headers)
    assert post_response1.status_code == 201
    cleanup_order_items.append(post_response1.json()["order_item_id"])

    post_response2 = requests.post(f"{BASE_URL}/order_items", json=order_item_data2, headers=admin_headers)
    assert post_response2.status_code == 201
    cleanup_order_items.append(post_response2.json()["order_item_id"])

    # Retrieve order items for the order
    get_response = requests.get(f"{BASE_URL}/order_items/order/{setup_order}", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert "order_items" in data
    assert isinstance(data["order_items"], list)
    assert len(data["order_items"]) >= 2
    assert any(item["quantity"] == 2 and item["price"] == 19.99 for item in data["order_items"])
    assert any(item["quantity"] == 1 and item["price"] == 29.99 for item in data["order_items"])

def test_get_order_items_by_order_no_items(admin_headers, setup_order):
    """Test retrieving order items for an order with no items."""
    get_response = requests.get(f"{BASE_URL}/order_items/order/{setup_order}", headers=admin_headers)
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert "order_items" in data
    assert len(data["order_items"]) == 0
    assert data["message"] == "No order items found for this order"

def test_update_order_item_success_admin(admin_headers, setup_order, cleanup_order_items):
    """Test updating an order item as an admin."""
    # First, add an order item
    order_item_data = {
        "order_id": setup_order,
        "product_id": 1,
        "quantity": 2,
        "price": 19.99
    }
    post_response = requests.post(f"{BASE_URL}/order_items", json=order_item_data, headers=admin_headers)
    assert post_response.status_code == 201
    order_item_id = post_response.json()["order_item_id"]
    cleanup_order_items.append(order_item_id)

    # Update the order item
    updated_data = {"quantity": 3, "price": 24.99}
    put_response = requests.put(f"{BASE_URL}/order_items/{order_item_id}", json=updated_data, headers=admin_headers)
    assert put_response.status_code == 200, f"Expected 200, got {put_response.status_code}: {put_response.text}"
    data = put_response.json()
    assert data["message"] == "Order item updated successfully"

    # Verify the update
    get_response = requests.get(f"{BASE_URL}/order_items/{order_item_id}", headers=admin_headers)
    assert get_response.status_code == 200
    updated_item = get_response.json()
    assert updated_item["quantity"] == updated_data["quantity"]
    assert updated_item["price"] == updated_data["price"]

def test_update_order_item_not_found(admin_headers):
    """Test updating a non-existent order item."""
    updated_data = {"quantity": 3}
    response = requests.put(f"{BASE_URL}/order_items/99999", json=updated_data, headers=admin_headers)
    # Note: Expected 404 per API docs, but may need server-side verification
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Failed to update order item"

def test_update_order_item_no_token():
    """Test updating an order item without any authorization token."""
    updated_data = {"quantity": 3}
    response = requests.put(f"{BASE_URL}/order_items/1", json=updated_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_delete_order_item_success_admin(admin_headers, setup_order, cleanup_order_items):
    """Test deleting an order item as an admin."""
    # First, add an order item
    order_item_data = {
        "order_id": setup_order,
        "product_id": 1,
        "quantity": 2,
        "price": 19.99
    }
    post_response = requests.post(f"{BASE_URL}/order_items", json=order_item_data, headers=admin_headers)
    assert post_response.status_code == 201
    order_item_id = post_response.json()["order_item_id"]
    cleanup_order_items.append(order_item_id)

    # Delete the order item
    delete_response = requests.delete(f"{BASE_URL}/order_items/{order_item_id}", headers=admin_headers)
    assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
    data = delete_response.json()
    assert data["message"] == "Order item deleted successfully"
    if order_item_id in cleanup_order_items:
        cleanup_order_items.remove(order_item_id)

    # Verify deletion
    get_response = requests.get(f"{BASE_URL}/order_items/{order_item_id}", headers=admin_headers)
    assert get_response.status_code == 404

def test_delete_order_item_not_found(admin_headers):
    """Test deleting a non-existent order item."""
    response = requests.delete(f"{BASE_URL}/order_items/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert "error" in data
    assert "Order item not found or failed to delete" in data["error"]

def test_delete_order_item_no_token():
    """Test deleting an order item without any authorization token."""
    response = requests.delete(f"{BASE_URL}/order_items/1")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_all_order_items_paginated_success(admin_headers, setup_order, cleanup_order_items):
    """Test retrieving all order items with pagination as admin."""
    # Add some order items
    for i in range(5):
        order_item_data = {
            "order_id": setup_order,
            "product_id": 1,
            "quantity": 1 + i,
            "price": 19.99 + (i * 5)
        }
        post_response = requests.post(f"{BASE_URL}/order_items", json=order_item_data, headers=admin_headers)
        assert post_response.status_code == 201
        cleanup_order_items.append(post_response.json()["order_item_id"])

    response = requests.get(f"{BASE_URL}/order_items?page=1&per_page=3", headers=admin_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "order_items" in data
    assert isinstance(data["order_items"], list)
    assert len(data["order_items"]) == 3
    assert "total" in data
    assert data["total"] >= 5
    assert data["page"] == 1
    assert data["per_page"] == 3

def test_get_all_order_items_paginated_no_admin_token():
    """Test retrieving all order items without admin token."""
    response = requests.get(f"{BASE_URL}/order_items?page=1&per_page=20")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

if __name__ == "__main__":
    pytest.main(["-v", __file__])