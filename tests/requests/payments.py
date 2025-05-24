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
        response = requests.get(f"{BASE_URL}/products", timeout=5)
        if response.status_code not in [200, 400, 500]:
            pytest.fail(f"Server not responding at {BASE_URL}/products: {response.status_code} - {response.text}")
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
def cleanup_products(admin_headers):
    """Clean up created products after tests."""
    products_to_delete = []
    yield products_to_delete
    for product_id in products_to_delete:
        try:
            response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=admin_headers)
            if response.status_code not in [200, 404]:
                print(f"Warning: Failed to delete product {product_id}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during product cleanup for ID {product_id}: {e}")

# --- Test Cases ---

def test_add_product_success_admin(admin_headers, cleanup_products):
    """Test adding a product as an admin."""
    product_data = {
        "name": "New Laptop",
        "price": 999.99,
        "stock_quantity": 10,
        "category_id": 1,  # Valid category_id from database
        "description": "High-end laptop",
        "image_url": "http://example.com/laptop.jpg",
        "is_active": 1
    }
    response = requests.post(f"{BASE_URL}/products", json=product_data, headers=admin_headers)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["message"] == "Product added successfully"
    assert "product_id" in data
    cleanup_products.append(data["product_id"])

def test_add_product_missing_fields(admin_headers):
    """Test adding a product with missing required fields."""
    invalid_data = {"name": "Laptop", "price": 999.99}
    response = requests.post(f"{BASE_URL}/products", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Name, price, and stock quantity are required"

def test_add_product_negative_price(admin_headers):
    """Test adding a product with negative price."""
    invalid_data = {
        "name": "Laptop",
        "price": -999.99,
        "stock_quantity": 10
    }
    response = requests.post(f"{BASE_URL}/products", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Price and stock quantity must be non-negative"

def test_add_product_no_token():
    """Test adding a product without any authorization token."""
    product_data = {
        "name": "Laptop",
        "price": 999.99,
        "stock_quantity": 10
    }
    response = requests.post(f"{BASE_URL}/products", json=product_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_product_by_id_success():
    """Test retrieving a product by its ID (public)."""
    product_id = 1  # Valid product_id from database
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Test Product"
    assert data["price"] == 19.99
    assert data["stock_quantity"] == 100
    assert data["category_id"] == 1
    assert data["is_active"] == 1

def test_get_product_by_id_not_found():
    """Test retrieving a non-existent or inactive product by ID."""
    response = requests.get(f"{BASE_URL}/products/99999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Product not found or inactive"

def test_get_products_by_category_success():
    """Test retrieving all products in a specific category (public)."""
    category_id = 1  # Valid category_id from database
    response = requests.get(f"{BASE_URL}/products/category/{category_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "products" in data
    assert isinstance(data["products"], list)
    assert len(data["products"]) >= 5  # At least 5 products in category_id=1
    assert all(product["category_id"] == category_id for product in data["products"])
    assert all(product["is_active"] == 1 for product in data["products"])

def test_get_products_by_category_no_products():
    """Test retrieving products for a category with no products."""
    category_id = 5  # Clothing category, assumed to have no products
    response = requests.get(f"{BASE_URL}/products/category/{category_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "products" in data
    assert len(data["products"]) == 0

def test_update_product_success_admin(admin_headers, cleanup_products):
    """Test updating a product as an admin."""
    # First, add a product
    product_data = {
        "name": "Laptop",
        "price": 999.99,
        "stock_quantity": 10,
        "category_id": 1
    }
    post_response = requests.post(f"{BASE_URL}/products", json=product_data, headers=admin_headers)
    assert post_response.status_code == 201
    product_id = post_response.json()["product_id"]
    cleanup_products.append(product_id)

    # Update the product
    updated_data = {
        "name": "Updated Laptop",
        "price": 1099.99,
        "stock_quantity": 8,
        "description": "Updated high-end laptop",
        "is_active": 1
    }
    put_response = requests.put(f"{BASE_URL}/products/{product_id}", json=updated_data, headers=admin_headers)
    assert put_response.status_code == 200, f"Expected 200, got {put_response.status_code}: {put_response.text}"
    data = put_response.json()
    assert data["message"] == "Product updated successfully"

    # Verify the update
    get_response = requests.get(f"{BASE_URL}/products/{product_id}")
    assert get_response.status_code == 200
    updated_product = get_response.json()
    assert updated_product["name"] == updated_data["name"]
    assert updated_product["price"] == updated_data["price"]
    assert updated_product["stock_quantity"] == updated_data["stock_quantity"]
    assert updated_product["description"] == updated_data["description"]
    assert updated_product["is_active"] == updated_data["is_active"]

def test_update_product_not_found(admin_headers):
    """Test updating a non-existent product."""
    updated_data = {"name": "Updated Laptop"}
    response = requests.put(f"{BASE_URL}/products/99999", json=updated_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Failed to update product"

def test_update_product_negative_price(admin_headers, cleanup_products):
    """Test updating a product with negative price."""
    # First, add a product
    product_data = {
        "name": "Laptop",
        "price": 999.99,
        "stock_quantity": 10
    }
    post_response = requests.post(f"{BASE_URL}/products", json=product_data, headers=admin_headers)
    assert post_response.status_code == 201
    product_id = post_response.json()["product_id"]
    cleanup_products.append(product_id)

    # Update with negative price
    updated_data = {"price": -999.99}
    response = requests.put(f"{BASE_URL}/products/{product_id}", json=updated_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Price must be non-negative"

def test_update_product_no_token():
    """Test updating a product without any authorization token."""
    updated_data = {"name": "Updated Laptop"}
    response = requests.put(f"{BASE_URL}/products/1", json=updated_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_delete_product_success_admin(admin_headers, cleanup_products):
    """Test deleting a product as an admin."""
    # First, add a product
    product_data = {
        "name": "Laptop",
        "price": 999.99,
        "stock_quantity": 10
    }
    post_response = requests.post(f"{BASE_URL}/products", json=product_data, headers=admin_headers)
    assert post_response.status_code == 201
    product_id = post_response.json()["product_id"]
    cleanup_products.append(product_id)

    # Delete the product
    delete_response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=admin_headers)
    assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
    data = delete_response.json()
    assert data["message"] == "Product deleted successfully"
    if product_id in cleanup_products:
        cleanup_products.remove(product_id)

    # Verify deletion
    get_response = requests.get(f"{BASE_URL}/products/{product_id}")
    assert get_response.status_code == 404

def test_delete_product_not_found(admin_headers):
    """Test deleting a non-existent product."""
    response = requests.delete(f"{BASE_URL}/products/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert "error" in data
    assert "Product not found or failed to delete" in data["error"]

def test_delete_product_no_token():
    """Test deleting a product without any authorization token."""
    response = requests.delete(f"{BASE_URL}/products/1")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_all_products_paginated_success():
    """Test retrieving all products with pagination (public)."""
    response = requests.get(f"{BASE_URL}/products?page=1&per_page=3")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "products" in data
    assert isinstance(data["products"], list)
    assert len(data["products"]) <= 3  # Up to 3 products per page
    assert "total" in data
    assert data["total"] >= 5  # At least 5 products in database
    assert data["page"] == 1
    assert data["per_page"] == 3
    assert all(product["is_active"] == 1 for product in data["products"])

if __name__ == "__main__":
    pytest.main(["-v", __file__])