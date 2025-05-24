# Discounts API Documentation

This document provides detailed information about the Discounts API endpoints defined in `admin_apis/discounts.py`. These endpoints manage discount codes in an e-commerce platform, including adding, retrieving, updating, and deleting discounts. Authentication and authorization are enforced using JWT (JSON Web Tokens) with specific roles (`@jwt_required()` for authenticated users and `@admin_required` for admins).

## Base URL
All endpoints are prefixed with `/api`. For example, `/discounts` is accessed as `/api/discounts`.

## Authentication
- **JWT Token**: Required for endpoints marked with `@jwt_required()` or `@admin_required`. Include the token in the `Authorization` header as `Bearer <token>`.
- **Admin Privileges**: Endpoints marked with `@admin_required` require a JWT token with `is_admin: true`.
- **User Access**: Endpoints with `@jwt_required()` allow authenticated users to access discount information (e.g., checking discount codes during checkout).

## Endpoints

### 1. Add Discount
- **Endpoint**: `POST /api/discounts`
- **Description**: Adds a new discount code (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "code": <string>,              // Required: Unique discount code
    "discount_percent": <float>,   // Required: Discount percentage (0-100)
    "max_uses": <integer>,         // Optional: Maximum number of uses
    "expires_at": <string>,        // Optional: Expiration date (ISO 8601, e.g., "2025-12-31T23:59:59Z")
    "description": <string>        // Optional: Discount description
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {
      "message": "Discount added successfully",
      "discount_id": <integer>
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Code and discount percent are required"
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
      "error": "Max uses must be non-negative"
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

### 2. Get Discount by ID
- **Endpoint**: `GET /api/discounts/<discount_id>`
- **Description**: Retrieves a discount by its ID (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `discount_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "code": <string>,
      "description": <string>,
      "discount_percent": <float>,
      "max_uses": <integer>,
      "expires_at": <string>,
      "is_active": <integer>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Discount not found"
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

### 3. Get Discount by Code
- **Endpoint**: `GET /api/discounts/code/<code>`
- **Description**: Retrieves a discount by its code. Useful for users checking discount details.
- **Authorization**: Requires `@jwt_required()` (authenticated users).
- **Input**: URL parameter `code` (string).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "code": <string>,
      "description": <string>,
      "discount_percent": <float>,
      "max_uses": <integer>,
      "expires_at": <string>,
      "is_active": <integer>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Discount not found"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```
  - **Error (401, if no JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 4. Get Valid Discount by Code
- **Endpoint**: `GET /api/discounts/valid/<code>`
- **Description**: Retrieves a valid discount by its code (checks `is_active`, `expires_at`, and `max_uses`). Used during checkout.
- **Authorization**: Requires `@jwt_required()` (authenticated users).
- **Input**: URL parameter `code` (string).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "code": <string>,
      "description": <string>,
      "discount_percent": <float>,
      "max_uses": <integer>,
      "expires_at": <string>,
      "is_active": <integer>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Valid discount not found"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```
  - **Error (401, if no JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 5. Update Discount
- **Endpoint**: `PUT /api/discounts/<discount_id>`
- **Description**: Updates a discount’s details (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "code": <string>,              // Optional: Unique discount code
    "description": <string>,       // Optional: Discount description
    "discount_percent": <float>,   // Optional: Discount percentage (0-100)
    "max_uses": <integer>,         // Optional: Maximum number of uses
    "expires_at": <string>,        // Optional: Expiration date (ISO 8601)
    "is_active": <integer>         // Optional: 1 (active) or 0 (inactive)
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Discount updated successfully"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Failed to update discount"
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
      "error": "Max uses must be non-negative"
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

### 6. Delete Discount
- **Endpoint**: `DELETE /api/discounts/<discount_id>`
- **Description**: Deletes a discount by ID (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `discount_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Discount deleted successfully"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Discount not found or failed to delete"
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

### 7. Get All Discounts (Paginated)
- **Endpoint**: `GET /api/discounts?page=<page>&per_page=<per_page>`
- **Description**: Retrieves a paginated list of all discounts (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  - Query parameters:
    - `page` (integer, default: 1)
    - `per_page` (integer, default: 20)
- **Output**:
  - **Success (200)**:
    ```json
    {
      "discounts": [
        {
          "id": <integer>,
          "code": <string>,
          "description": <string>,
          "discount_percent": <float>,
          "max_uses": <integer>,
          "expires_at": <string>,
          "is_active": <integer>
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

### Adding a Discount (Admin)
```bash
curl -X POST http://localhost:5000/api/discounts -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"code":"SAVE10","discount_percent":10.0,"max_uses":100,"expires_at":"2025-12-31T23:59:59Z","description":"10% off your order"}'
```
Response:
```json
{
  "message": "Discount added successfully",
  "discount_id": 1
}
```

### Getting a Discount by Code (User)
```bash
curl -X GET http://localhost:5000/api/discounts/code/SAVE10 -H "Authorization: Bearer <user_token>"
```
Response:
```json
{
  "id": 1,
  "code": "SAVE10",
  "description": "10% off your order",
  "discount_percent": 10.0,
  "max_uses": 100,
  "expires_at": "2025-12-31T23:59:59Z",
  "is_active": 1
}
```

### Getting a Valid Discount (User)
```bash
curl -X GET http://localhost:5000/api/discounts/valid/SAVE10 -H "Authorization: Bearer <user_token>"
```
Response:
```json
{
  "id": 1,
  "code": "SAVE10",
  "description": "10% off your order",
  "discount_percent": 10.0,
  "max_uses": 100,
  "expires_at": "2025-12-31T23:59:59Z",
  "is_active": 1
}
```

## Notes
- **Database Manager**: The API relies on `DiscountManager` for database operations.
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages. Errors are logged for debugging.
- **Security**: Admin endpoints require a valid JWT with admin privileges. User endpoints require authentication to prevent unauthorized access to discount details.
- **Data Validation**: Discount percentage is validated to be between 0 and 100, and max uses must be non-negative.
- **Testing**: Unit tests can be created in `test/test_discounts.py` to verify functionality.

For further details, refer to the source code in `admin_apis/discounts.py`.