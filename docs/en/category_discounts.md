# Category Discounts API Documentation

This document provides detailed information about the Category Discounts API endpoints defined in `admin_apis/category_discounts.py`. These endpoints manage discounts applied to specific product categories in an e-commerce platform, including adding, retrieving, updating, and deleting category discounts. Authentication and authorization are enforced using JWT (JSON Web Tokens) with specific roles (`@admin_required` for admin-only operations).

## Base URL
All endpoints are prefixed with `/api`. For example, `/category_discounts` is accessed as `/api/category_discounts`.

## Authentication
- **JWT Token**: Required for endpoints marked with `@admin_required`. Include the token in the `Authorization` header as `Bearer <token>`.
- **Admin Privileges**: Endpoints marked with `@admin_required` require a JWT token with `is_admin: true`.
- **Public Access**: Endpoints without authentication (`GET /category_discounts/category/<category_id>`, `GET /category_discounts/valid/<category_id>`) are accessible to everyone.

## Endpoints

### 1. Add Category Discount
- **Endpoint**: `POST /api/category_discounts`
- **Description**: Adds a new discount for a specific category (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "category_id": <integer>,      // Required: ID of the category
    "discount_percent": <float>,   // Required: Discount percentage (0-100)
    "starts_at": <string>,        // Optional: Start date (ISO 8601, e.g., "2025-05-23T00:00:00Z")
    "ends_at": <string>,          // Optional: End date (ISO 8601, e.g., "2025-12-31T23:59:59Z")
    "is_active": <integer>        // Optional: 1 (active) or 0 (inactive), default: 1
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {
      "message": "Category discount added successfully",
      "discount_id": <integer>
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Category ID and discount percent are required"
    }
    ```
    or
    ```json
    {
      "error": "Category ID must be a positive integer"
    }
    ```
    or
    ```json
    {
      "error": "Discount percent must be between 0 and 100"
    }
    ```
    or
    ```json
    {
      "error": "starts_at must be in ISO 8601 format"
    }
    ```
    or
    ```json
    {
      "error": "ends_at must be in ISO 8601 format"
    }
    ```
    or
    ```json
    {
      "error": "starts_at must be before ends_at"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

### 2. Get Category Discount by ID
- **Endpoint**: `GET /api/category_discounts/<discount_id>`
- **Description**: Retrieves a category discount by its ID (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `discount_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "category_id": <integer>,
      "discount_percent": <float>,
      "starts_at": <string>,
      "ends_at": <string>,
      "is_active": <integer>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Category discount not found"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

### 3. Get Category Discounts by Category
- **Endpoint**: `GET /api/category_discounts/category/<category_id>`
- **Description**: Retrieves all discounts for a specific category. Publicly accessible.
- **Authorization**: None (public access).
- **Input**: URL parameter `category_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "category_discounts": [
        {
          "id": <integer>,
          "category_id": <integer>,
          "discount_percent": <float>,
          "starts_at": <string>,
          "ends_at": <string>,
          "is_active": <integer>
        },
        ...
      ]
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Category ID must be a positive integer"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```

### 4. Get Valid Category Discounts
- **Endpoint**: `GET /api/category_discounts/valid/<category_id>`
- **Description**: Retrieves valid discounts for a specific category (checks `is_active`, `starts_at`, and `ends_at`). Publicly accessible.
- **Authorization**: None (public access).
- **Input**: URL parameter `category_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "category_discounts": [
        {
          "id": <integer>,
          "category_id": <integer>,
          "discount_percent": <float>,
          "starts_at": <string>,
          "ends_at": <string>,
          "is_active": <integer>
        },
        ...
      ]
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Category ID must be a positive integer"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```

### 5. Update Category Discount
- **Endpoint**: `PUT /api/category_discounts/<discount_id>`
- **Description**: Updates a category discount’s details (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "discount_percent": <float>,   // Optional: Discount percentage (0-100)
    "starts_at": <string>,        // Optional: Start date (ISO 8601)
    "ends_at": <string>,          // Optional: End date (ISO 8601)
    "is_active": <integer>        // Optional: 1 (active) or 0 (inactive)
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Category discount updated successfully"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Failed to update category discount"
    }
    ```
    or
    ```json
    {
      "error": "Discount percent must be between 0 and 100"
    }
    ```
    or
    ```json
    {
      "error": "starts_at must be in ISO 8601 format"
    }
    ```
    or
    ```json
    {
      "error": "ends_at must be in ISO 8601 format"
    }
    ```
    or
    ```json
    {
      "error": "starts_at must be before ends_at"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

### 6. Delete Category Discount
- **Endpoint**: `DELETE /api/category_discounts/<discount_id>`
- **Description**: Deletes a category discount by ID (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `discount_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Category discount deleted successfully"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Category discount not found or failed to delete"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

### 7. Get All Category Discounts (Paginated)
- **Endpoint**: `GET /api/category_discounts?page=<page>&per_page=<per_page>`
- **Description**: Retrieves a paginated list of all category discounts (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  - Query parameters:
    - `page` (integer, default: 1)
    - `per_page` (integer, default: 20)
- **Output**:
  - **Success (200)**:
    ```json
    {
      "category_discounts": [
        {
          "id": <integer>,
          "category_id": <integer>,
          "discount_percent": <float>,
          "starts_at": <string>,
          "ends_at": <string>,
          "is_active": <integer>,
          "category_name": <string>
        },
        ...
      ],
      "total": <integer>,
      "page": <integer>,
      "per_page": <integer>
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

## Example Usage
### Obtaining a JWT Token
First, authenticate via the login endpoint (assumed to be `/api/login`):
```bash
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"adminpassword"}'
```
Response:
```json
{
  "access_token": "<your_jwt_token>"
}
```

### Adding a Category Discount (Admin)
```bash
curl -X POST http://localhost:5000/api/category_discounts -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"category_id":1,"discount_percent":10.0,"starts_at":"2025-05-23T00:00:00Z","ends_at":"2025-12-31T23:59:59Z","is_active":1}'
```
Response:
```json
{
  "message": "Category discount added successfully",
  "discount_id": 1
}
```

### Getting Category Discounts by Category (Public)
```bash
curl -X GET http://localhost:5000/api/category_discounts/category/1
```
Response:
```json
{
  "category_discounts": [
    {
      "id": 1,
      "category_id": 1,
      "discount_percent": 10.0,
      "starts_at": "2025-05-23T00:00:00Z",
      "ends_at": "2025-12-31T23:59:59Z",
      "is_active": 1
    }
  ]
}
```

### Getting Valid Category Discounts (Public)
```bash
curl -X GET http://localhost:5000/api/category_discounts/valid/1
```
Response:
```json
{
  "category_discounts": [
    {
      "id": 1,
      "category_id": 1,
      "discount_percent": 10.0,
      "starts_at": "2025-05-23T00:00:00Z",
      "ends_at": "2025-12-31T23:59:59Z",
      "is_active": 1
    }
  ]
}
```

## Notes
- **Database Manager**: The API relies on `CategoryDiscountManager` for database operations.
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages. Errors are logged for debugging.
- **Security**: Admin endpoints require a valid JWT with admin privileges. Public endpoints are accessible to everyone for viewing category discounts.
- **Data Validation**: Discount percentage is validated to be between 0 and 100, category ID must be a positive integer, and date fields (`starts_at`, `ends_at`) must be in ISO 8601 format.
- **Category Name**: The `category_name` field in `GET /api/category_discounts` assumes the `CategoryDiscountManager` returns a `name` field (e.g., via a database join with the categories table). If not supported, remove this field from the response.
- **Testing**: Unit tests can be created in `test/test_category_discounts.py` to verify functionality (not included in this response per request).

For further details, refer to the source code in `admin_apis/category_discounts.py`.