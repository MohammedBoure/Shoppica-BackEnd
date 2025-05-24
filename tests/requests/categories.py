import pytest
import requests
import json
import os

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000/api"
TOKEN_FILE = "tests/requests/token.txt"

@pytest.fixture(scope="module")
def admin_headers():
    """
    Fixture to read the admin token and provide headers for authorized requests.
    """
    token = None
    try:
        with open(TOKEN_FILE, "r") as file:
            token = file.read().strip()
    except FileNotFoundError:
        pytest.fail(f"Token file {TOKEN_FILE} not found. Please create it with your admin token.")

    if not token:
        pytest.fail(f"Token file {TOKEN_FILE} is empty. Please provide a valid admin token.")

    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

@pytest.fixture(scope="function")
def created_category_ids(request, admin_headers):
    """
    Fixture to manage created category IDs and automatically delete them after the test.
    """
    created_ids = []

    def cleanup():
        for category_id in created_ids:
            response = requests.delete(
                f"{BASE_URL}/categories/{category_id}", headers=admin_headers
            )
            if response.status_code not in [200, 404]:
                print(f"Warning: Failed to delete category {category_id}")

    request.addfinalizer(cleanup)
    return created_ids


def test_add_category_success(admin_headers, created_category_ids):
    """Test adding a valid category."""
    payload = {"name": "Electronics", "parent_id": None}
    response = requests.post(
        f"{BASE_URL}/categories", headers=admin_headers, json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Category added successfully"
    assert "category_id" in data
    created_category_ids.append(data["category_id"])

def test_add_category_missing_name(admin_headers):
    """Test adding a category without name (should fail)."""
    payload = {"parent_id": None}
    response = requests.post(
        f"{BASE_URL}/categories", headers=admin_headers, json=payload
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Category name is required"

def test_add_category_unauthorized():
    """Test adding a category without token."""
    payload = {"name": "Electronics", "parent_id": None}
    response = requests.post(
        f"{BASE_URL}/categories",
        headers={"Content-Type": "application/json"},
        json=payload,
    )
    assert response.status_code == 401
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_category_by_id(admin_headers, created_category_ids):
    """Test getting a category by ID."""
    # First, create a category
    payload = {"name": "Books", "parent_id": None}
    response = requests.post(
        f"{BASE_URL}/categories", headers=admin_headers, json=payload
    )
    assert response.status_code == 201
    category_id = response.json()["category_id"]
    created_category_ids.append(category_id)

    # Test getting the category by ID
    response = requests.get(f"{BASE_URL}/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Books"
    assert data["parent_id"] is None

def test_get_category_not_found():
    """Test getting a non-existent category."""
    response = requests.get(f"{BASE_URL}/categories/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Category not found"

def test_get_categories_by_parent(admin_headers, created_category_ids):
    """Test getting categories by parent_id."""
    # Create a parent category
    payload = {"name": "Electronics", "parent_id": None}
    response = requests.post(
        f"{BASE_URL}/categories", headers=admin_headers, json=payload
    )
    assert response.status_code == 201
    parent_id = response.json()["category_id"]
    created_category_ids.append(parent_id)

    # Create a child category
    payload = {"name": "Smartphones", "parent_id": parent_id}
    response = requests.post(
        f"{BASE_URL}/categories", headers=admin_headers, json=payload
    )
    assert response.status_code == 201
    created_category_ids.append(response.json()["category_id"])

    # Test getting categories by parent_id
    response = requests.get(f"{BASE_URL}/categories/parent?parent_id={parent_id}")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) == 1
    assert data["categories"][0]["name"] == "Smartphones"
    assert data["categories"][0]["parent_id"] == parent_id

def test_get_top_level_categories(admin_headers, created_category_ids):
    """Test getting top-level categories."""
    # Create a top-level category
    payload = {"name": "Clothing", "parent_id": None}
    response = requests.post(
        f"{BASE_URL}/categories", headers=admin_headers, json=payload
    )
    assert response.status_code == 201
    created_category_ids.append(response.json()["category_id"])

    # Test getting top-level categories
    response = requests.get(f"{BASE_URL}/categories/parent")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert any(cat["name"] == "Clothing" for cat in data["categories"])

def test_update_category_success(admin_headers, created_category_ids):
    """Test updating a category successfully."""
    # Create a category to update
    payload = {"name": "Books", "parent_id": None}
    response = requests.post(
        f"{BASE_URL}/categories", headers=admin_headers, json=payload
    )
    assert response.status_code == 201
    category_id = response.json()["category_id"]
    created_category_ids.append(category_id)

    # Update the category
    update_payload = {"name": "Updated Books", "parent_id": None}
    response = requests.put(
        f"{BASE_URL}/categories/{category_id}",
        headers=admin_headers,
        json=update_payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Category updated successfully"

    # Verify the update
    response = requests.get(f"{BASE_URL}/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Books"

def test_update_category_unauthorized(admin_headers, created_category_ids):
    """Test updating a category without authorization."""
    # Create a category
    payload = {"name": "Books", "parent_id": None}
    response = requests.post(
        f"{BASE_URL}/categories", headers=admin_headers, json=payload
    )
    assert response.status_code == 201
    category_id = response.json()["category_id"]
    created_category_ids.append(category_id)

    # Try updating without token
    update_payload = {"name": "Updated Books", "parent_id": None}
    response = requests.put(
        f"{BASE_URL}/categories/{category_id}",
        headers={"Content-Type": "application/json"},
        json=update_payload,
    )
    assert response.status_code == 401
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_delete_category_success(admin_headers, created_category_ids):
    """Test deleting a category successfully."""
    # Create a category to delete
    payload = {"name": "Books", "parent_id": None}
    response = requests.post(
        f"{BASE_URL}/categories", headers=admin_headers, json=payload
    )
    assert response.status_code == 201
    category_id = response.json()["category_id"]
    created_category_ids.append(category_id) # Add to list to ensure cleanup if delete fails later

    # Delete the category
    response = requests.delete(
        f"{BASE_URL}/categories/{category_id}", headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Category deleted successfully"

    # Remove from cleanup list as it's already deleted
    if category_id in created_category_ids:
        created_category_ids.remove(category_id)

    # Verify deletion
    response = requests.get(f"{BASE_URL}/categories/{category_id}")
    assert response.status_code == 404

def test_delete_category_unauthorized(admin_headers, created_category_ids):
    """Test deleting a category without authorization."""
    # Create a category
    payload = {"name": "Books", "parent_id": None}
    response = requests.post(
        f"{BASE_URL}/categories", headers=admin_headers, json=payload
    )
    assert response.status_code == 201
    category_id = response.json()["category_id"]
    created_category_ids.append(category_id)

    # Try deleting without token
    response = requests.delete(
        f"{BASE_URL}/categories/{category_id}",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_all_categories_paginated(admin_headers, created_category_ids):
    """Test getting all categories with pagination."""
    # Create multiple categories
    for i in range(3):
        payload = {"name": f"Category {i}", "parent_id": None}
        response = requests.post(
            f"{BASE_URL}/categories", headers=admin_headers, json=payload
        )
        assert response.status_code == 201
        created_category_ids.append(response.json()["category_id"])

    # Test pagination
    response = requests.get(f"{BASE_URL}/categories?page=1&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert len(data["categories"]) <= 2
    assert data["total"] >= 3