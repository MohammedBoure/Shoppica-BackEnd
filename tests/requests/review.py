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
        response = requests.get(f"{BASE_URL}/reviews", timeout=5)
        if response.status_code not in [200, 400, 401, 404]:
            pytest.fail(f"Server not responding at {BASE_URL}/reviews: {response.status_code} - {response.text}")
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
def cleanup_reviews(admin_headers):
    """Clean up created reviews after tests."""
    reviews_to_delete = []
    yield reviews_to_delete
    for review_id in reviews_to_delete:
        try:
            response = requests.delete(f"{BASE_URL}/reviews/{review_id}", headers=admin_headers)
            if response.status_code not in [200, 404]:
                print(f"Warning: Failed to delete review {review_id}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during review cleanup for ID {review_id}: {e}")

# --- Test Cases ---

def test_add_review_success_admin(admin_headers, cleanup_reviews):
    """Test adding a review as an admin."""
    # Replace user_id and product_id with valid values from your database
    review_data = {
        "user_id": 1,  # Replace with a valid user_id
        "product_id": 1,  # Replace with a valid product_id
        "rating": 4,
        "comment": "Good product from admin perspective."
    }
    response = requests.post(f"{BASE_URL}/reviews", json=review_data, headers=admin_headers)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["message"] == "Review added successfully"
    assert "review_id" in data
    cleanup_reviews.append(data["review_id"])

def test_add_review_missing_fields(admin_headers):
    """Test adding a review with missing required fields."""
    invalid_data = {"product_id": 1, "rating": 3}
    response = requests.post(f"{BASE_URL}/reviews", json=invalid_data, headers=admin_headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "User ID, product ID, and rating are required"

def test_add_review_no_token():
    """Test adding a review without any authorization token."""
    review_data = {"user_id": 1, "product_id": 1, "rating": 5}
    response = requests.post(f"{BASE_URL}/reviews", json=review_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_review_by_id_success(admin_headers, cleanup_reviews):
    """Test retrieving a review by its ID."""
    # First, add a review
    review_data = {
        "user_id": 1,  # Replace with a valid user_id
        "product_id": 1,  # Replace with a valid product_id
        "rating": 4,
        "comment": "Nice one."
    }
    post_response = requests.post(f"{BASE_URL}/reviews", json=review_data, headers=admin_headers)
    assert post_response.status_code == 201, f"Expected 201, got {post_response.status_code}: {post_response.text}"
    review_id = post_response.json()["review_id"]
    cleanup_reviews.append(review_id)

    # Retrieve the review
    get_response = requests.get(f"{BASE_URL}/reviews/{review_id}")
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert data["id"] == review_id
    assert data["user_id"] == review_data["user_id"]
    assert data["product_id"] == review_data["product_id"]
    assert data["rating"] == review_data["rating"]
    assert data["comment"] == review_data["comment"]
    assert "created_at" in data

def test_get_review_by_id_not_found():
    """Test retrieving a non-existent review by ID."""
    response = requests.get(f"{BASE_URL}/reviews/99999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Review not found"

def test_get_reviews_by_product_success(admin_headers, cleanup_reviews):
    """Test retrieving reviews for a specific product."""
    product_id = 1  # Replace with a valid product_id
    # Add two reviews
    review_data1 = {"user_id": 1, "product_id": product_id, "rating": 5, "comment": "Review 1"}
    review_data2 = {"user_id": 1, "product_id": product_id, "rating": 4, "comment": "Review 2"}

    post_response1 = requests.post(f"{BASE_URL}/reviews", json=review_data1, headers=admin_headers)
    assert post_response1.status_code == 201
    cleanup_reviews.append(post_response1.json()["review_id"])

    post_response2 = requests.post(f"{BASE_URL}/reviews", json=review_data2, headers=admin_headers)
    assert post_response2.status_code == 201
    cleanup_reviews.append(post_response2.json()["review_id"])

    get_response = requests.get(f"{BASE_URL}/reviews/product/{product_id}")
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"
    data = get_response.json()
    assert "reviews" in data
    assert isinstance(data["reviews"], list)
    assert len(data["reviews"]) >= 2
    assert any(r["comment"] == "Review 1" for r in data["reviews"])
    assert any(r["comment"] == "Review 2" for r in data["reviews"])

def test_get_reviews_by_product_no_reviews():
    """Test retrieving reviews for a product with no reviews."""
    response = requests.get(f"{BASE_URL}/reviews/product/99999")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "reviews" in data
    assert len(data["reviews"]) == 0
    assert data["message"] == "No reviews found for this product"

def test_update_review_success_admin(admin_headers, cleanup_reviews):
    """Test updating a review as an admin."""
    # First, add a review
    initial_review_data = {
        "user_id": 1,  # Replace with a valid user_id
        "product_id": 1,  # Replace with a valid product_id
        "rating": 3,
        "comment": "Admin test original"
    }
    post_response = requests.post(f"{BASE_URL}/reviews", json=initial_review_data, headers=admin_headers)
    assert post_response.status_code == 201
    review_id = post_response.json()["review_id"]
    cleanup_reviews.append(review_id)

    # Update the review
    updated_data = {"rating": 5, "comment": "Admin updated this to perfect!"}
    put_response = requests.put(f"{BASE_URL}/reviews/{review_id}", json=updated_data, headers=admin_headers)
    assert put_response.status_code == 200, f"Expected 200, got {put_response.status_code}: {put_response.text}"
    data = put_response.json()
    assert data["message"] == "Review updated successfully"

    # Verify the update
    get_response = requests.get(f"{BASE_URL}/reviews/{review_id}")
    assert get_response.status_code == 200
    updated_review = get_response.json()
    assert updated_review["rating"] == updated_data["rating"]
    assert updated_review["comment"] == updated_data["comment"]

def test_update_review_not_found(admin_headers):
    """Test updating a non-existent review."""
    updated_data = {"rating": 5}
    response = requests.put(f"{BASE_URL}/reviews/99999", json=updated_data, headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["error"] == "Review not found"

def test_update_review_no_token():
    """Test updating a review without any authorization token."""
    updated_data = {"rating": 5}
    response = requests.put(f"{BASE_URL}/reviews/1", json=updated_data)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_delete_review_success_admin(admin_headers, cleanup_reviews):
    """Test deleting a review as an admin."""
    # First, add a review
    review_data = {
        "user_id": 1,  # Replace with a valid user_id
        "product_id": 1,  # Replace with a valid product_id
        "rating": 5,
        "comment": "Admin will delete this"
    }
    post_response = requests.post(f"{BASE_URL}/reviews", json=review_data, headers=admin_headers)
    assert post_response.status_code == 201
    review_id = post_response.json()["review_id"]
    cleanup_reviews.append(review_id)

    # Delete the review
    delete_response = requests.delete(f"{BASE_URL}/reviews/{review_id}", headers=admin_headers)
    assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
    data = delete_response.json()
    assert data["message"] == "Review deleted successfully"
    if review_id in cleanup_reviews:
        cleanup_reviews.remove(review_id)

    # Verify deletion
    get_response = requests.get(f"{BASE_URL}/reviews/{review_id}")
    assert get_response.status_code == 404

def test_delete_review_not_found(admin_headers):
    """Test deleting a non-existent review."""
    response = requests.delete(f"{BASE_URL}/reviews/99999", headers=admin_headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    data = response.json()
    assert "error" in data
    assert "Review not found" in data["error"] or "failed to delete" in data["error"]

def test_delete_review_no_token():
    """Test deleting a review without any authorization token."""
    response = requests.delete(f"{BASE_URL}/reviews/1")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

def test_get_all_reviews_paginated_success(admin_headers, cleanup_reviews):
    """Test retrieving all reviews with pagination as admin."""
    product_id = 1  # Replace with a valid product_id
    # Add some reviews
    for i in range(5):
        review_data = {
            "user_id": 1,  # Replace with a valid user_id
            "product_id": product_id,
            "rating": 3 + (i % 3),
            "comment": f"Paginated review {i}"
        }
        post_response = requests.post(f"{BASE_URL}/reviews", json=review_data, headers=admin_headers)
        assert post_response.status_code == 201
        cleanup_reviews.append(post_response.json()["review_id"])

    response = requests.get(f"{BASE_URL}/reviews?page=1&per_page=3", headers=admin_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "reviews" in data
    assert isinstance(data["reviews"], list)
    assert len(data["reviews"]) == 3
    assert "total" in data
    assert data["total"] >= 5
    assert data["page"] == 1
    assert data["per_page"] == 3

def test_get_all_reviews_paginated_no_admin_token():
    """Test retrieving all reviews without admin token."""
    response = requests.get(f"{BASE_URL}/reviews?page=1&per_page=20")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["msg"] == "Missing Authorization Header"

if __name__ == "__main__":
    pytest.main(["-v", __file__])