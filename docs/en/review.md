# Reviews API Documentation

This document provides detailed information about the Reviews API endpoints implemented in the Flask Blueprint `reviews`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses. The API interacts with the `reviews` table in a SQLite database via the `ReviewManager` class.

## Authentication
- Endpoints for adding (`POST /reviews`), updating (`PUT /reviews/<int:review_id>`), and deleting (`DELETE /reviews/<int:review_id>`) reviews require session-based authentication using the `@session_required` decorator, which checks for a valid `user_id` in the session. Non-admin users can only add, update, or delete their own reviews (`user_id` must match `session['user_id']`).
- Endpoints for retrieving all reviews (`GET /reviews`), deleting reviews by product (`DELETE /reviews/by-product/<int:product_id>`), deleting reviews by user (`DELETE /reviews/by-user/<int:user_id>`), and getting overall review statistics (`GET /reviews/stats/overall`) require admin privileges, enforced by the `@admin_required` decorator, which checks for `is_admin=True` in the session.
- Endpoints for retrieving a specific review (`GET /reviews/<int:review_id>`), reviews by product (`GET /reviews/product/<int:product_id>`), searching reviews (`GET /reviews/search`), and product review statistics (`GET /reviews/stats/product/<int:product_id>`) are publicly accessible without authentication.
- The `ReviewManager` class handles all database interactions for review-related operations.

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
  - `rating` (integer): The rating for the product (1-5).
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
  - **HTTP 400**: Missing required fields or invalid rating.
    ```json
    {
      "error": "User ID, product ID, and rating are required"
    }
    ```
    ```json
    {
      "error": "Rating must be an integer between 1 and 5"
    }
    ```
    ```json
    {
      "error": "Request body must be JSON"
    }
    ```
  - **HTTP 401**: Invalid or missing session data.
    ```json
    {
      "error": "Invalid session data"
    }
    ```
  - **HTTP 403**: Non-admin user attempting to add a review for another user.
    ```json
    {
      "error": "Unauthorized to add review for another user"
    }
    ```
  - **HTTP 500**: Server error when adding the review.
    ```json
    {
      "error": "Failed to add review"
    }
    ```

**Notes**:
- Uses `ReviewManager.add_review` to create the review.
- Validates that `rating` is an integer between 1 and 5.
- The `user_id` in the request must match the session's `user_id` unless the user is an admin.

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
    "created_at": "2025-06-26T20:12:00"
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Review not found.
    ```json
    {
      "error": "Review not found"
    }
    ```

**Notes**:
- Uses `ReviewManager.get_review_by_id` to fetch the review.
- The `created_at` field is in ISO 8601 format (e.g., "2025-06-26T20:12:00").

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
        "created_at": "2025-06-26T20:12:00"
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "reviews": []
  }
  ```

**Notes**:
- Uses `ReviewManager.get_reviews_by_product` to fetch reviews.
- Returns an empty list if no reviews exist for the product.

---

## 4. Update Review
### Endpoint: `/reviews/<int:review_id>`
### Method: `PUT`
### Description
Updates the rating or comment of an existing review. Only the user who created the review or an admin can update it.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only update their own reviews (`review['user_id']` must match `session['user_id']`).

### Inputs
- **URL Parameters**:
  - `review_id` (integer): The ID of the review to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `rating` (integer): The updated rating (1-5).
    - `comment` (string): The updated comment.

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
  - **HTTP 400**: Invalid rating or request body.
    ```json
    {
      "error": "Rating must be an integer between 1 and 5"
    }
    ```
    ```json
    {
      "error": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "Failed to update review"
    }
    ```
  - **HTTP 401**: Invalid or missing session data.
    ```json
    {
      "error": "Invalid session data"
    }
    ```
  - **HTTP 403**: Non-admin user attempting to update another user's review.
    ```json
    {
      "error": "Unauthorized to update this review"
    }
    ```
  - **HTTP 404**: Review not found.
    ```json
    {
      "error": "Review not found"
    }
    ```

**Notes**:
- Uses `ReviewManager.update_review` to update the review.
- Validates that `rating` (if provided) is an integer between 1 and 5.

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
  - **HTTP 401**: Invalid or missing session data.
    ```json
    {
      "error": "Invalid session data"
    }
    ```
  - **HTTP 403**: Non-admin user attempting to delete another user's review.
    ```json
    {
      "error": "Unauthorized to delete this review"
    }
    ```
  - **HTTP 404**: Review not found.
    ```json
    {
      "error": "Review not found"
    }
    ```
  - **HTTP 500**: Server error when deleting the review.
    ```json
    {
      "error": "Failed to delete review"
    }
    ```

**Notes**:
- Uses `ReviewManager.delete_review` to delete the review.

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
        "created_at": "2025-06-26T20:12:00"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid pagination parameters.
    ```json
    {
      "error": "Page and per_page must be positive integers"
    }
    ```
  - **HTTP 401**: Invalid or missing session data.
    ```json
    {
      "error": "Invalid session data"
    }
    ```
  - **HTTP 403**: Admin privileges required.
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

**Notes**:
- Uses `ReviewManager.get_reviews` for paginated retrieval.
- Returns pagination metadata (`total`, `page`, `per_page`).

---

## 7. Search Reviews
### Endpoint: `/reviews/search`
### Method: `GET`
### Description
Searches reviews based on product ID, user ID, rating range, or comment keyword with pagination. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (Query Parameters)
- `product_id` (integer, optional): Filter by product ID.
- `user_id` (integer, optional): Filter by user ID.
- `min_rating` (integer, optional): Minimum rating (1-5).
- `max_rating` (integer, optional): Maximum rating (1-5).
- `comment` (string, optional): Keyword to search in review comments.
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
        "created_at": "2025-06-26T20:12:00"
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing search parameters or invalid rating range.
    ```json
    {
      "error": "At least one search parameter (product_id, user_id, min_rating, max_rating, comment) is required"
    }
    ```
    ```json
    {
      "error": "min_rating must be between 1 and 5"
    }
    ```
    ```json
    {
      "error": "max_rating must be between 1 and 5"
    }
    ```
    ```json
    {
      "error": "min_rating cannot be greater than max_rating"
    }
    ```
    ```json
    {
      "error": "Page and per_page must be positive integers"
    }
    ```

**Notes**:
- Uses `ReviewManager.search_reviews` with filters for `product_id`, `user_id`, `min_rating`, `max_rating`, and `comment_keyword`.
- At least one search parameter is required.
- Validates that `min_rating` and `max_rating` are between 1 and 5, and `min_rating` is not greater than `max_rating`.

---

## 8. Delete Reviews by Product (Admin Only)
### Endpoint: `/reviews/by-product/<int:product_id>`
### Method: `DELETE`
### Description
Deletes all reviews for a specific product. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `product_id` (integer): The ID of the product whose reviews are to be deleted.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Successfully deleted 5 reviews for product ID 456."
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "message": "No reviews found for product ID 456."
  }
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session data.
    ```json
    {
      "error": "Invalid session data"
    }
    ```
  - **HTTP 403**: Admin privileges required.
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

**Notes**:
- Uses `ReviewManager.delete_reviews_by_product` to delete reviews.
- Returns the number of deleted reviews in the success message.

---

## 9. Delete Reviews by User (Admin Only)
### Endpoint: `/reviews/by-user/<int:user_id>`
### Method: `DELETE`
### Description
Deletes all reviews by a specific user. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `user_id` (integer): The ID of the user whose reviews are to be deleted.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Successfully deleted 3 reviews by user ID 123."
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "message": "No reviews found for user ID 123."
  }
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session data.
    ```json
    {
      "error": "Invalid session data"
    }
    ```
  - **HTTP 403**: Admin privileges required.
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

**Notes**:
- Uses `ReviewManager.delete_reviews_by_user` to delete reviews.
- Returns the number of deleted reviews in the success message.

---

## 10. Get Product Review Statistics
### Endpoint: `/reviews/stats/product/<int:product_id>`
### Method: `GET`
### Description
Retrieves review statistics for a specific product, such as average rating and review count. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs
- **URL Parameters**:
  - `product_id` (integer): The ID of the product to get statistics for.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "product_id": 456,
    "average_rating": 4.5,
    "review_count": 10
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "product_id": 456,
    "average_rating": 0,
    "review_count": 0
  }
  ```

**Notes**:
- Uses `ReviewManager.get_product_review_stats` to fetch statistics.
- Returns zero values if no reviews exist for the product.

---

## 11. Get Overall Review Statistics (Admin Only)
### Endpoint: `/reviews/stats/overall`
### Method: `GET`
### Description
Retrieves overall review statistics for all products, such as average rating and total review count. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "average_rating": 4.2,
    "total_reviews": 100
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "average_rating": 0,
    "total_reviews": 0
  }
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session data.
    ```json
    {
      "error": "Invalid session data"
    }
    ```
  - **HTTP 403**: Admin privileges required.
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

**Notes**:
- Uses `ReviewManager.get_overall_review_stats` to fetch statistics.
- Returns zero values if no reviews exist.

---

## Notes
- All endpoints interact with the database through the `ReviewManager` class.
- Logging is assumed to be configured at the application level with `logging.basicConfig(level=logging.INFO)` for debugging and monitoring.
- The `created_at` field in responses is in ISO 8601 format (e.g., "2025-06-26T20:12:00").
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- Public endpoints (`GET /reviews/<int:review_id>`, `GET /reviews/product/<int:product_id>`, `GET /reviews/search`, `GET /reviews/stats/product/<int:product_id>`) provide read-only access to review data without authentication.
- SQLite foreign key support is assumed to be enabled (e.g., via `PRAGMA foreign_keys = ON`) to maintain data integrity with related `products` and `users` tables.
- The `comment_keyword` parameter in `GET /reviews/search` allows searching for partial matches in review comments.