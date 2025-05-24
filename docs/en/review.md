# Reviews API Documentation

This document provides detailed information about the Reviews API endpoints defined in `admin_apis/reviews.py`. These endpoints manage product reviews in an e-commerce platform, including adding, retrieving, updating, and deleting reviews. Authentication and authorization are enforced using JWT (JSON Web Tokens) with specific roles (`@jwt_required` for user authentication and `@admin_required` for admin-only operations).

## Base URL
All endpoints are prefixed with `/api`. For example, `/reviews` is accessed as `/api/reviews`.

## Authentication
- **JWT Token**: Required for endpoints marked with `@jwt_required()`. Include the token in the `Authorization` header as `Bearer <token>`.
- **User Access**: Endpoints marked with `@jwt_required()` allow authenticated users to manage their own reviews (based on `user_id` matching `get_jwt_identity()`) or admins to manage any reviews.
- **Admin Privileges**: The endpoint marked with `@admin_required` (`GET /api/reviews`) requires a JWT token with `is_admin: true`.
- **Public Access**: Endpoints `GET /api/reviews/<review_id>` and `GET /api/reviews/product/<product_id>` are publicly accessible without authentication.

## Endpoints

### 1. Add Review
- **Endpoint**: `POST /api/reviews`
- **Description**: Adds a new review for a product. Only accessible to the user themselves or admins.
- **Authorization**: Requires `@jwt_required()`. Users can only add reviews under their own `user_id` unless they are admins (`is_admin: true`).
- **Input**:
  ```json
  {
    "user_id": <integer>,     // Required: ID of the user
    "product_id": <integer>,  // Required: ID of the product
    "rating": <integer>,      // Required: Rating (e.g., 1-5)
    "comment": <string>       // Optional: Review comment
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {
      "message": "Review added successfully",
      "review_id": <integer>
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "User ID, product ID, and rating are required"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized to add review for another user"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Failed to add review"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 2. Get Review by ID
- **Endpoint**: `GET /api/reviews/<review_id>`
- **Description**: Retrieves a review by its ID. Publicly accessible.
- **Authorization**: None (public access).
- **Input**: URL parameter `review_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "user_id": <integer>,
      "product_id": <integer>,
      "rating": <integer>,
      "comment": <string>,
      "created_at": <string>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Review not found"
    }
    ```

### 3. Get Reviews by Product
- **Endpoint**: `GET /api/reviews/product/<product_id>`
- **Description**: Retrieves all reviews for a specific product. Publicly accessible.
- **Authorization**: None (public access).
- **Input**: URL parameter `product_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "reviews": [
        {
          "id": <integer>,
          "user_id": <integer>,
          "product_id": <integer>,
          "rating": <integer>,
          "comment": <string>,
          "created_at": <string>
        },
        ...
      ]
    }
    ```
    or, if no reviews:
    ```json
    {
      "reviews": [],
      "message": "No reviews found for this product"
    }
    ```

### 4. Update Review
- **Endpoint**: `PUT /api/reviews/<review_id>`
- **Description**: Updates a review’s details (e.g., rating or comment). Only accessible to the review’s owner or admins.
- **Authorization**: Requires `@jwt_required()`. Users can only update their own reviews unless they are admins (`is_admin: true`).
- **Input**:
  ```json
  {
    "rating": <integer>,      // Optional: New rating (e.g., 1-5)
    "comment": <string>       // Optional: New comment
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Review updated successfully"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Failed to update review"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Review not found"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized to update this review"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 5. Delete Review
- **Endpoint**: `DELETE /api/reviews/<review_id>`
- **Description**: Deletes a review by ID. Only accessible to the review’s owner or admins.
- **Authorization**: Requires `@jwt_required()`. Users can only delete their own reviews unless they are admins (`is_admin: true`).
- **Input**: URL parameter `review_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Review deleted successfully"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Review not found"
    }
    ```
    or
    ```json
    {
      "error": "Review not found or failed to delete"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized to delete this review"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 6. Get All Reviews (Paginated)
- **Endpoint**: `GET /api/reviews?page=<page>&per_page=<per_page>`
- **Description**: Retrieves a paginated list of all reviews across all products (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  - Query parameters:
    - `page` (integer, default: 1)
    - `per_page` (integer, default: 20)
- **Output**:
  - **Success (200)**:
    ```json
    {
      "reviews": [
        {
          "id": <integer>,
          "user_id": <integer>,
          "product_id": <integer>,
          "rating": <integer>,
          "comment": <string>,
          "created_at": <string>
        },
        ...
      ],
      "total": <integer>,
      "page": <integer>,
      "per_page": <integer>
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

## Example Usage
### Obtaining a JWT Token
First, authenticate via the login endpoint (assumed to be `/api/login`):
```bash
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"password"}'
```
Response:
```json
{
  "access_token": "<your_jwt_token>"
}
```

For admin operations, use an admin account:
```bash
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"adminpassword"}'
```
Response:
```json
{
  "access_token": "<admin_jwt_token>"
}
```

### Adding a Review (User or Admin)
```bash
curl -X POST http://localhost:5000/api/reviews -H "Authorization: Bearer <user_token>" -H "Content-Type: application/json" -d '{"user_id":1,"product_id":1,"rating":5,"comment":"Great product!"}'
```
Response:
```json
{
  "message": "Review added successfully",
  "review_id": 1
}
```
Note: Non-admin users can only add reviews under their own `user_id`. Admins can add reviews for any user.

### Getting a Review by ID (Public)
```bash
curl -X GET http://localhost:5000/api/reviews/1
```
Response:
```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 1,
  "rating": 5,
  "comment": "Great product!",
  "created_at": "2025-05-23T22:00:00Z"
}
```

### Getting Reviews by Product (Public)
```bash
curl -X GET http://localhost:5000/api/reviews/product/1
```
Response:
```json
{
  "reviews": [
    {
      "id": 1,
      "user_id": 1,
      "product_id": 1,
      "rating": 5,
      "comment": "Great product!",
      "created_at": "2025-05-23T22:00:00Z"
    }
  ]
}
```

### Updating a Review (User or Admin)
```bash
curl -X PUT http://localhost:5000/api/reviews/1 -H "Authorization: Bearer <user_token>" -H "Content-Type: application/json" -d '{"rating":4,"comment":"Updated: Very good product!"}'
```
Response:
```json
{
  "message": "Review updated successfully"
}
```
Note: Non-admin users can only update their own reviews. Admins can update any review.

### Deleting a Review (User or Admin)
```bash
curl -X DELETE http://localhost:5000/api/reviews/1 -H "Authorization: Bearer <user_token>"
```
Response:
```json
{
  "message": "Review deleted successfully"
}
```
Note: Non-admin users can only delete their own reviews. Admins can delete any review.

### Getting All Reviews (Admin Only)
```bash
curl -X GET http://localhost:5000/api/reviews?page=1&per_page=20 -H "Authorization: Bearer <admin_token>"
```
Response:
```json
{
  "reviews": [
    {
      "id": 1,
      "user_id": 1,
      "product_id": 1,
      "rating": 4,
      "comment": "Updated: Very good product!",
      "created_at": "2025-05-23T22:00:00Z"
    },
    ...
  ],
  "total": 10,
  "page": 1,
  "per_page": 20
}
```

## Notes
- **Database Manager**: The API relies on `ReviewManager` for database operations.
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages. Errors are logged for debugging.
- **Security**:
  - User-specific endpoints (`POST /api/reviews`, `PUT /api/reviews/<review_id>`, `DELETE /api/reviews/<review_id>`) restrict access to the authenticated user’s reviews unless the user is an admin.
  - The admin endpoint (`GET /api/reviews`) requires a valid JWT with admin privileges.
  - Public endpoints (`GET /api/reviews/<review_id>`, `GET /api/reviews/product/<product_id>`) allow anyone to view review details.
- **Data Validation**: Ensures required fields (`user_id`, `product_id`, `rating`) are provided when adding a review. The `update_review` endpoint allows optional updates to `rating` and `comment`.
- **Review Fields**: The `created_at` field is assumed to be returned in ISO 8601 format (e.g., "2025-05-23T22:00:00Z").
- **Testing**: Unit tests can be created in `test/test_reviews.py` to verify functionality.

For further details, refer to the source code in `admin_apis/reviews.py`.