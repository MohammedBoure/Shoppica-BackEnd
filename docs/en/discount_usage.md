# Discount Usages API Documentation

This document provides detailed information about the Discount Usages API endpoints implemented in the Flask Blueprint `discount_usages`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding a discount usage (`POST /discount_usages`) and retrieving discount usages by user (`GET /discount_usages/user/<int:user_id>`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- Non-admin users can only add or view discount usages associated with their own `user_id` (`user_id` must match `session['user_id']`).
- Endpoints for retrieving a specific discount usage (`GET /discount_usages/<int:usage_id>`), retrieving discount usages by discount (`GET /discount_usages/discount/<int:discount_id>`), deleting a discount usage (`DELETE /discount_usages/<int:usage_id>`), and retrieving all discount usages (`GET /discount_usages`) require admin privileges, enforced by the `@admin_required` decorator.
- The `DiscountUsageManager` class handles all database interactions for discount usage-related operations.
- The `current_user_id` is extracted from the session as an integer, and the `is_admin` flag determines if the user has admin privileges (defaults to `False` if not set).

## Logging
- Logging is configured with `logging.basicConfig(level=logging.INFO)` and a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and error tracking.

---

## 1. Add a New Discount Usage
### Endpoint: `/discount_usages`
### Method: `POST`
### Description
Records a new usage of a discount by a user. Only the authenticated user can add a discount usage for themselves.

### Authentication
- Requires a valid session (`@session_required`).
- The `user_id` in the request must match the `current_user_id` from the session.

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `discount_id` (integer): The ID of the discount being used (must be a positive integer).
  - `user_id` (integer): The ID of the user applying the discount (must be a positive integer).

**Example Request Body**:
```json
{
  "discount_id": 123,
  "user_id": 456
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Discount usage added successfully",
    "usage_id": 789
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload, missing required fields (`discount_id` or `user_id`), or invalid `discount_id` or `user_id` (not positive integers).
    ```json
    {
      "error": "Invalid JSON payload"
    }
    ```
    ```json
    {
      "error": "Discount ID and user ID are required"
    }
    ```
    ```json
    {
      "error": "Discount ID must be a positive integer"
    }
    ```
    ```json
    {
      "error": "User ID must be a positive integer"
    }
    ```
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 403**: Unauthorized attempt to add a discount usage for another user (`user_id` does not match `current_user_id`).
    ```json
    {
      "error": "Unauthorized: User ID does not match authenticated user"
    }
    ```
  - **HTTP 500**: Server error when failing to add the discount usage to the database.
    ```json
    {
      "error": "Failed to add discount usage"
    }
    ```
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 2. Get Discount Usage by ID
### Endpoint: `/discount_usages/<int:usage_id>`
### Method: `GET`
### Description
Retrieves the details of a specific discount usage by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `usage_id` (integer): The ID of the discount usage to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 789,
    "discount_id": 123,
    "user_id": 456,
    "used_at": "2025-06-26T20:42:00"
  }
  ```
- **Error Responses**:
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Discount usage with the specified ID does not exist.
    ```json
    {
      "error": "Discount usage not found"
    }
    ```
  - **HTTP 500**: Server error when retrieving the discount usage.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 3. Get Discount Usages by Discount
### Endpoint: `/discount_usages/discount/<int:discount_id>`
### Method: `GET`
### Description
Retrieves all discount usages for a specific discount. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `discount_id` (integer): The ID of the discount whose usages are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "discount_usages": [
      {
        "id": 789,
        "discount_id": 123,
        "user_id": 456,
        "used_at": "2025-06-26T20:42:00"
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "discount_usages": []
  }
  ```
- **Error Responses**:
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving discount usages.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 4. Get Discount Usages by User
### Endpoint: `/discount_usages/user/<int:user_id>`
### Method: `GET`
### Description
Retrieves all discount usages for a specific user. Only the authenticated user can view their own discount usages.

### Authentication
- Requires a valid session (`@session_required`).
- The `user_id` in the request must match the `current_user_id` from the session.

### Inputs (URL Parameters)
- `user_id` (integer): The ID of the user whose discount usages are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "discount_usages": [
      {
        "id": 789,
        "discount_id": 123,
        "user_id": 456,
        "used_at": "2025-06-26T20:42:00"
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "discount_usages": []
  }
  ```
- **Error Responses**:
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 403**: Unauthorized attempt to access another user's discount usages (`user_id` does not match `current_user_id`).
    ```json
    {
      "error": "Unauthorized: User ID does not match authenticated user"
    }
    ```
  - **HTTP 500**: Server error when retrieving discount usages.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 5. Delete Discount Usage
### Endpoint: `/discount_usages/<int:usage_id>`
### Method: `DELETE`
### Description
Deletes a discount usage by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `usage_id` (integer): The ID of the discount usage to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Discount usage deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Discount usage with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Discount usage not found or failed to delete"
    }
    ```
  - **HTTP 500**: Server error when deleting the discount usage.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 6. Get All Discount Usages (Admin Only)
### Endpoint: `/discount_usages`
### Method: `GET`
### Description
Retrieves a paginated list of all discount usages in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination (must be positive).
- `per_page` (integer, default: `20`): The number of discount usages per page (must be positive).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "discount_usages": [
      {
        "id": 789,
        "discount_id": 123,
        "user_id": 456,
        "used_at": "2025-06-26T20:42:00",
        "discount_code": "SUMMER25"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid `page` or `per_page` values (negative or zero).
    ```json
    {
      "error": "Page and per_page must be positive integers"
    }
    ```
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving discount usages.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `DiscountUsageManager` class, which encapsulates database operations for discount usages.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` with a dedicated logger (`logger = logging.getLogger(__name__)`) for detailed error tracking.
- The `used_at` field in responses is a timestamp indicating when the discount was used (format: `YYYY-MM-DDTHH:MM:SS`, or `null` if not set), serialized using the `serialize_datetime` helper function.
- The `discount_code` field is included in the response for the `GET /discount_usages` endpoint, providing the discount code associated with each usage, as returned by `DiscountUsageManager.get_discount_usages`.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `POST /discount_usages` and `GET /discount_usages/user/<int:user_id>` endpoints enforce that non-admin users can only interact with their own `user_id`.
- The `GET /discount_usages/<int:usage_id>`, `GET /discount_usages/discount/<int:discount_id>`, `DELETE /discount_usages/<int:usage_id>`, and `GET /discount_usages` endpoints are restricted