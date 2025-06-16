# Reviews API Documentation

This document provides detailed information about the Reviews API endpoints implemented in the Flask Blueprint `reviews`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Most endpoints require session-based authentication using the `@session_required` decorator, which checks for a valid `user_id` in the session.
- The `/reviews` GET endpoint requires admin privileges, enforced by the `@admin_required` decorator.
- The `current_user_id` is extracted from the session as an integer, and the `is_admin` flag determines if the user has admin privileges (defaults to `False` if not set).
- The `/reviews/<int:review_id>` GET and `/reviews/product/<int:product_id>` GET endpoints do not require authentication, allowing public access to review data.

---

## 1. Add a New Review
### Endpoint: `/reviews`
### Method: `POST`
### Description
Creates a new review for a product. Only the authenticated user (matching the `user_id` in the request) or an admin can add a review for the specified user.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only add reviews for themselves (`user_id` must match `session['user_id']`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `user_id` (integer): The ID of the user submitting the review.
  - `product_id` (integer): The ID of the product being reviewed.
  - `rating` (integer): The rating for the product (e.g., 1-5).
- **Optional Fields**:
  - `comment` (string): A comment about the product (defaults to empty string if not provided).

**Example Request Body**:
```json
{
  "user_id": 123,
  "product_id": 456,
  "rating": 5,
  "comment": "Great product, highly recommend!"
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Review added successfully",
    "review_id": 789
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing required fields (`user_id`, `product_id`, or `rating`).
    ```json
    {
      "error": "User ID, product ID, and rating are required"
    }
    ```
  - **HTTP 403**: Unauthorized to add a review for another user (non-admin attempting to use a different `user_id`).
    ```json
    {
      "error": "Unauthorized to add review for another user"
    }
    ```
  - **HTTP 500**: Server error when failing to add the review to the database.
    ```json
    {
      "error": "Failed to add review"
    }
    ```

---

## 2. Get Review by ID
### Endpoint: `/reviews/<int:review_id>`
### Method: `GET`
### Description
Retrieves the details of a specific review by its ID. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `review_id` (integer): The ID of the review to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 789,
    "user_id": 123,
    "product_id": 456,
    "rating": 5,
    "comment": "Great product, highly recommend!",
    "created_at": "2025-06-16T11:05:00"
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Review with the specified ID does not exist.
    ```json
    {
      "error": "Review not found"
    }
    ```

---

## 3. Get Reviews by Product
### Endpoint: `/reviews/product/<int:product_id>`
### Method: `GET`
### Description
Retrieves all reviews for a specific product. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `product_id` (integer): The ID of the product whose reviews are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "reviews": [
      {
        "id": 789,
        "user_id": 123,
        "product_id": 456,
        "rating": 5,
        "comment": "Great product, highly recommend!",
        "created_at": "2025-06-16T11:05:00"
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "reviews": [],
    "message": "No reviews found for this product"
  }
  ```

---

## 4. Update Review
### Endpoint: `/reviews/<int:review_id>`
### Method: `PUT`
### Description
Updates the details of an existing review. Only the user who created the review or an admin can update it.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only update their own reviews (`review['user_id']` must match `session['user_id']`).

### Inputs
- **URL Parameters**:
  - `review_id` (integer): The ID of the review to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `rating` (integer): The updated rating for the product (e.g., 1-5).
    - `comment` (string): The updated comment about the product.

**Example Request Body**:
```json
{
  "rating": 4,
  "comment": "Good product, but could be improved."
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Review updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Failed to update the review (e.g., invalid data or database error).
    ```json
    {
      "error": "Failed to update review"
    }
    ```
  - **HTTP 403**: Unauthorized to update the review (non-admin attempting to update another user's review).
    ```json
    {
      "error": "Unauthorized to update this review"
    }
    ```
  - **HTTP 404**: Review with the specified ID does not exist.
    ```json
    {
      "error": "Review not found"
    }
    ```

---

## 5. Delete Review
### Endpoint: `/reviews/<int:review_id>`
### Method: `DELETE`
### Description
Deletes a review by its ID. Only the user who created the review or an admin can delete it.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only delete their own reviews (`review['user_id']` must match `session['user_id']`).

### Inputs
- **URL Parameters**:
  - `review_id` (integer): The ID of the review to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Review deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized to delete the review (non-admin attempting to delete another user's review).
    ```json
    {
      "error": "Unauthorized to delete this review"
    }
    ```
  - **HTTP 404**: Review with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Review not found or failed to delete"
    }
    ```

---

## 6. Get All Reviews (Admin Only)
### Endpoint: `/reviews`
### Method: `GET`
### Description
Retrieves a paginated list of all reviews in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of reviews per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "reviews": [
      {
        "id": 789,
        "user_id": 123,
        "product_id": 456,
        "rating": 5,
        "comment": "Great product, highly recommend!",
        "created_at": "2025-06-16T11:05:00"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `ReviewManager` class.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` for debugging and monitoring purposes.
- The `created_at` field in responses is a timestamp indicating when the review was created (format: `YYYY-MM-DDTHH:MM:SS`).
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- Public endpoints (`/reviews/<int:review_id>` GET and `/reviews/product/<int:product_id>` GET) provide read-only access to review data without requiring authentication.