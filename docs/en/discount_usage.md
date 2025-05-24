# Discount Usages API Documentation

This document provides detailed information about the Discount Usages API endpoints defined in `admin_apis/discount_usages.py`. These endpoints manage discount usage records in an e-commerce platform, tracking when users apply discount codes. Authentication and authorization are enforced using JWT (JSON Web Tokens) with specific roles (`@jwt_required()` for authenticated users and `@admin_required` for admins).

## Base URL
All endpoints are prefixed with `/api`. For example, `/discount_usages` is accessed as `/api/discount_usages`.

## Authentication
- **JWT Token**: Required for endpoints marked with `@jwt_required()` or `@admin_required`. Include the token in the `Authorization` header as `Bearer <token>`.
- **Admin Privileges**: Endpoints marked with `@admin_required` require a JWT token with `is_admin: true`.
- **User Access**: Endpoints with `@jwt_required()` allow authenticated users to access their own discount usage records, with validation to ensure the `user_id` matches the authenticated user’s identity.

## Endpoints

### 1. Add Discount Usage
- **Endpoint**: `POST /api/discount_usages`
- **Description**: Adds a new discount usage record, linking a discount to a user (e.g., during checkout).
- **Authorization**: Requires `@jwt_required()`. The `user_id` in the request must match the authenticated user’s ID.
- **Input**:
  ```json
  {
    "discount_id": <integer>, // Required: ID of the discount
    "user_id": <integer>     // Required: ID of the user (must match JWT identity)
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {
      "message": "Discount usage added successfully",
      "usage_id": <integer>
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Discount ID and user ID are required"
    }
    ```
    or
    ```json
    {
      "error": "Discount ID must be a positive integer"
    }
    ```
    or
    ```json
    {
      "error": "User ID must be a positive integer"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized: User ID does not match authenticated user"
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

### 2. Get Discount Usage by ID
- **Endpoint**: `GET /api/discount_usages/<usage_id>`
- **Description**: Retrieves a discount usage record by its ID (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `usage_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "discount_id": <integer>,
      "user_id": <integer>,
      "used_at": <string>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Discount usage not found"
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

### 3. Get Discount Usages by Discount
- **Endpoint**: `GET /api/discount_usages/discount/<discount_id>`
- **Description**: Retrieves all discount usage records for a specific discount (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `discount_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "discount_usages": [
        {
          "id": <integer>,
          "discount_id": <integer>,
          "user_id": <integer>,
          "used_at": <string>
        },
        ...
      ]
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

### 4. Get Discount Usages by User
- **Endpoint**: `GET /api/discount_usages/user/<user_id>`
- **Description**: Retrieves all Investigator: all discount usage records for a specific user. The `user_id` must match the authenticated user’s ID.
- **Authorization**: Requires `@jwt_required()`. The `user_id` in the request must match the authenticated user’s ID.
- **Input**: URL parameter `user_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "discount_usages": [
        {
          "id": <integer>,
          "discount_id": <integer>,
          "user_id": <integer>,
          "used_at": <string>
        },
        ...
      ]
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized: User ID does not match authenticated user"
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

### 5. Delete Discount Usage
- **Endpoint**: `DELETE /api/discount_usages/<usage_id>`
- **Description**: Deletes a discount usage record by ID (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `usage_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Discount usage deleted successfully"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Discount usage not found or failed to delete"
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

### 6. Get All Discount Usages (Paginated)
- **Endpoint**: `GET /api/discount_usages?page=<page>&per_page=<per_page>`
- **Description**: Retrieves a paginated list of all discount usage records (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  - Query parameters:
    - `page` (integer, default: 1)
    - `per_page` (integer, default: 20)
- **Output**:
  - **Success (200)**:
    ```json
    {
      "discount_usages": [
        {
          "id": <integer>,
          "discount_id": <integer>,
          "user_id": <integer>,
          "used_at": <string>,
          "discount_code": <string>
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

### Adding a Discount Usage (User)
```bash
curl -X POST http://localhost:5000/api/discount_usages -H "Authorization: Bearer <user_token>" -H "Content-Type: application/json" -d '{"discount_id":1,"user_id":1}'
```
Response:
```json
{
  "message": "Discount usage added successfully",
  "usage_id": 1
}
```

### Getting Discount Usages by User (User)
```bash
curl -X GET http://localhost:5000/api/discount_usages/user/1 -H "Authorization: Bearer <user_token>"
```
Response:
```json
{
  "discount_usages": [
    {
      "id": 1,
      "discount_id": 1,
      "user_id": 1,
      "used_at": "2025-05-23T14:18:00Z"
    }
  ]
}
```

### Getting All Discount Usages (Admin)
```bash
curl -X GET http://localhost:5000/api/discount_usages?page=1&per_page=10 -H "Authorization: Bearer <admin_token>"
```
Response:
```json
{
  "discount_usages": [
    {
      "id": 1,
      "discount_id": 1,
      "user_id": 1,
      "used_at": "2025-05-23T14:18:00Z",
      "discount_code": "SAVE10"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

## Notes
- **Database Manager**: The API relies on `DiscountUsageManager` for database operations.
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages. Errors are logged for debugging.
- **Security**: User endpoints validate that the `user_id` matches the authenticated user’s ID. Admin endpoints require a valid JWT with admin privileges.
- **Data Validation**: Discount ID and user ID are validated to be positive integers.
- **Testing**: Unit tests can be created in `test/test_discount_usages.py` to verify functionality.
- **Discount Code**: The `discount_code` field in `GET /api/discount_usages` assumes the `DiscountUsageManager` returns a `code` field (e.g., via a database join with the discounts table). If not supported, remove this field from the response.

For further details, refer to the source code in `admin_apis/discount_usages.py`.