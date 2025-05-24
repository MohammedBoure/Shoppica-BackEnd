import requests
import pytest
import json
import os

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000/api"

@pytest.fixture
def admin_token():
    """Read JWT token from token.txt file."""
    token_file = "tests/requests/token.txt"
    assert os.path.exists(token_file), f"Token file {token_file} not found in the current directory"
    with open(token_file, "r") as f:
        token = f.read().strip()
    assert token, "Token file is empty"
    return token

@pytest.fixture
def product_data():
    """Sample product data for testing."""
    return {
        "name": "Test Product",
        "price": 19.99,
        "stock_quantity": 100,
        "category_id": 1,
        "description": "A test product description",
        "image_url": "https://example.com/test_image.jpg",
        "is_active": 1
    }

@pytest.fixture
def updated_product_data():
    """Sample data for updating a product."""
    return {
        "name": "Updated Test Product",
        "price": 29.99,
        "stock_quantity": 90,
        "description": "Updated test product description",
        "image_url": "https://example.com/updated_image.jpg",
        "is_active": 1
    }

def test_add_product_success(admin_token, product_data):
    """Test adding a product with valid data (admin only)."""
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/products", json=product_data, headers=headers)
    
    assert response.status_code == 201, f"Expected status 201, got {response.status_code}: {response.text}"
    response_data = response.json()
    assert "message" in response_data, "Response missing 'message' key"
    assert response_data["message"] == "Product added successfully", "Unexpected success message"
    assert "product_id" in response_data, "Response missing 'product_id' key"
    return response_data["product_id"]  # Return product_id for use in other tests

def test_add_product_missing_fields(admin_token):
    """Test adding a product with missing required fields (admin only)."""
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    invalid_data = {"price": 19.99, "stock_quantity": 100}  # Missing 'name'
    response = requests.post(f"{BASE_URL}/products", json=invalid_data, headers=headers)
    
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}: {response.text}"
    response_data = response.json()
    assert "error" in response_data
    assert response_data["error"] == "Name, price, and stock quantity are required"

def test_add_product_negative_price(admin_token):
    """Test adding a product with negative price (admin only)."""
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    invalid_data = {
        "name": "Invalid Product",
        "price": -10.0,
        "stock_quantity": 100
    }
    response = requests.post(f"{BASE_URL}/products", json=invalid_data, headers=headers)
    
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}: {response.text}"
    response_data = response.json()
    assert "error" in response_data
    assert response_data["error"] == "Price and stock quantity must be non-negative"

def test_get_product_by_id_success(admin_token, product_data):
    """Test retrieving a product by ID (public access)."""
    # First, add a product
    product_id = test_add_product_success(admin_token, product_data)
    
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.text}"
    response_data = response.json()
    
    assert "id" in response_data
    assert response_data["id"] == product_id
    assert response_data["name"] == product_data["name"]
    assert response_data["price"] == product_data["price"]
    assert response_data["stock_quantity"] == product_data["stock_quantity"]
    assert response_data["is_active"] == 1

def test_get_product_by_id_not_found():
    """Test retrieving a non-existent or inactive product by ID."""
    response = requests.get(f"{BASE_URL}/products/9999")
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}: {response.text}"
    response_data = response.json()
    assert "error" in response_data
    assert response_data["error"] == "Product not found or inactive"

def test_get_products_by_category_success(admin_token, product_data):
    """Test retrieving products by category ID (public access)."""
    # Add a product to category 1
    test_add_product_success(admin_token, product_data)
    
    response = requests.get(f"{BASE_URL}/products/category/1")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.text}"
    response_data = response.json()
    
    assert "products" in response_data
    assert isinstance(response_data["products"], list)
    assert len(response_data["products"]) > 0
    assert response_data["products"][0]["category_id"] == 1
    assert response_data["products"][0]["is_active"] == 1

def test_update_product_success(admin_token, product_data, updated_product_data):
    """Test updating a product with valid data (admin only)."""
    # Add a product
    product_id = test_add_product_success(admin_token, product_data)
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    response = requests.put(f"{BASE_URL}/products/{product_id}", json=updated_product_data, headers=headers)
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.text}"
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"] == "Product updated successfully"
    
    # Verify the update
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == updated_product_data["name"]
    assert response_data["price"] == updated_product_data["price"]
    assert response_data["stock_quantity"] == updated_product_data["stock_quantity"]

def test_update_product_negative_price(admin_token, product_data):
    """Test updating a product with negative price (admin only)."""
    product_id = test_add_product_success(admin_token, product_data)
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    invalid_data = {"price": -10.0}
    response = requests.put(f"{BASE_URL}/products/{product_id}", json=invalid_data, headers=headers)
    
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}: {response.text}"
    response_data = response.json()
    assert "error" in response_data
    assert response_data["error"] == "Price must be non-negative"

def test_delete_product_success(admin_token, product_data):
    """Test deleting a product (admin only)."""
    product_id = test_add_product_success(admin_token, product_data)
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.text}"
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"] == "Product deleted successfully"
    
    # Verify the product is deleted or inactive
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}: {response.text}"

def test_delete_product_not_found(admin_token):
    """Test deleting a non-existent product (admin only)."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.delete(f"{BASE_URL}/products/9999", headers=headers)
    
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}: {response.text}"
    response_data = response.json()
    assert "error" in response_data
    assert response_data["error"] == "Product not found or failed to delete"

def test_get_all_products_paginated_success():
    """Test retrieving all active products with pagination (public access)."""
    response = requests.get(f"{BASE_URL}/products?page=1&per_page=20")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.text}"
    response_data = response.json()
    
    assert "products" in response_data
    assert isinstance(response_data["products"], list)
    assert "total" in response_data
    assert "page" in response_data and response_data["page"] == 1
    assert "per_page" in response_data and response_data["per_page"] == 20
    for product in response_data["products"]:
        assert product["is_active"] == 1

def test_admin_required_no_token(product_data):
    """Test admin-only endpoint (POST /products) without token."""
    response = requests.post(f"{BASE_URL}/products", json=product_data)
    assert response.status_code == 401, f"Expected status 401, got {response.status_code}: {response.text}"
    response_data = response.json()
    assert "msg" in response_data
    assert response_data["msg"] == "Missing Authorization Header"

if __name__ == "__main__":
    pytest.main(["-v", __file__])