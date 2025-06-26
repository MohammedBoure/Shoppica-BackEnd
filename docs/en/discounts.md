# Discounts API Documentation

This document provides detailed information about the Discounts API endpoints implemented in the Flask Blueprint `discounts`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /discounts`), retrieving a specific discount (`GET /discounts/<int:discount_id>`), updating (`PUT /discounts/<int:discount_id>`), deleting (`DELETE /discounts/<int:discount_id>`), and retrieving all discounts (`GET /discounts`) require admin privileges, enforced by the `@admin_required` decorator, which checks for a valid session and admin status.
- Endpoints for retrieving a discount by code (`GET /discounts/code/<string:code>`) and retrieving a valid discount by code (`GET /discounts/valid/<string:code>`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- The `DiscountManager` class handles all database interactions for discount-related operations.

## Logging
- Logging is configured with `logging.basicConfig(level=logging.INFO)` and a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and error tracking. Each endpoint logs warnings for invalid inputs and errors for exceptions, with success logs for completed operations.

---

## 1. Add a New Discount
### Endpoint: `/discounts`
### Method: `POST`
### Description
Creates a new discount in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `code` (string): The unique code for the discount.
  - `discount_percent` (number): The discount percentage (must be a number between 0 and 100, inclusive).
- **Optional Fields**:
  - `max_uses` (integer): The maximum number of times the discount can be used (null for unlimited, must be non-negative).
  - `expires_at` (string, ISO 8601 format): The expiration date and time of the discount (e.g., `2025-08-31T23:59:59`).
  - `description` (string): A description of the discount.

**Example Request Body**:
```json
{
  "code": "SUMMER25",
  "discount_percent": 25.0,
  "max_uses": 100,
  "expires_at": "2025-08-31T23:59:59",
  "description": "Summer sale discount"
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Discount added successfully",
    "discount_id": 123
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload, missing required fields (`code` or `discount_percent`), invalid `discount_percent` (not a number between 0 and 100), invalid `max_uses` (not a non-negative integer), or invalid `expires_at` (not a valid ISO datetime).
    ```json
    {
      "error": "Request must contain JSON data"
    }
    ```
    ```json
    {
      "error": "Code and discount percent are required"
    }
    ```
    ```json
    {
      "error": "Discount percent must be a number between 0 and 100"
    }
    ```
    ```json
    {
      "error": "Max uses must be a non-negative integer"
    }
    ```
    ```json
    {
      "error": "Expires at must be a valid ISO datetime"
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
  - **HTTP 500**: Server error when failing to add the discount to the database.
    ```json
    {
      "error": "Failed to add discount"
    }
    ```
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 2. Get Discount by ID
### Endpoint: `/discounts/<int:discount_id>`
### Method: `GET`
### Description
Retrieves the details of a specific discount by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `discount_id` (integer): The ID of the discount to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 123,
    "code": "SUMMER25",
    "description": "Summer sale discount",
    "discount_percent": 25.0,
    "max_uses": 100,
    "expires_at": "2025-08-31T23:59:59",
    "is_active": true
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
  - **HTTP 404**: Discount with the specified ID does not exist.
    ```json
    {
      "error": "Discount not found"
    }
    ```
  - **HTTP 500**: Server error when retrieving the discount.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 3. Get Discount by Code
### Endpoint: `/discounts/code/<string:code>`
### Method: `GET`
### Description
Retrieves the details of a discount by its code. This endpoint is accessible to authenticated users.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs (URL Parameters)
- `code` (string): The code of the discount to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 123,
    "code": "SUMMER25",
    "description": "Summer sale discount",
    "discount_percent": 25.0,
    "max_uses": 100,
    "expires_at": "2025-08-31T23:59:59",
    "is_active": true
  }
  ```
- **Error Responses**:
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 404**: Discount with the specified code does not exist.
    ```json
    {
      "error": "Discount not found"
    }
    ```
  - **HTTP 500**: Server error when retrieving the discount.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 4. Get Valid Discount by Code
### Endpoint: `/discounts/valid/<string:code>`
### Method: `GET`
### Description
Retrieves a valid discount by its code (must be active, not expired, and not exceeded max uses). This endpoint is accessible to authenticated users.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs (URL Parameters)
- `code` (string): The code of the discount to validate and retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 123,
    "code": "SUMMER25",
    "description": "Summer sale discount",
    "discount_percent": 25.0,
    "max_uses": 100,
    "expires_at": "2025-08-31T23:59:59",
    "is_active": true
  }
  ```
- **Error Responses**:
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 404**: No valid discount found for the specified code (e.g., inactive, expired, or max uses exceeded).
    ```json
    {
      "error": "Valid discount not found"
    }
    ```
  - **HTTP 500**: Server error when retrieving the valid discount.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 5. Update Discount
### Endpoint: `/discounts/<int:discount_id>`
### Method: `PUT`
### Description
Updates the details of an existing discount. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `discount_id` (integer): The ID of the discount to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `code` (string): The updated discount code.
    - `description` (string): The updated description of the discount.
    - `discount_percent` (number): The updated discount percentage (must be a number between 0 and 100, inclusive).
    - `max_uses` (integer): The updated maximum number of uses (null for unlimited, must be non-negative).
    - `expires_at` (string, ISO 8601 format): The updated expiration date and time (e.g., `2025-09-15T23:59:59`).
    - `is_active` (boolean): The updated active status (`true` for active, `false` for inactive).

**Example Request Body**:
```json
{
  "code": "SUMMER30",
  "description": "Updated summer sale discount",
  "discount_percent": 30.0,
  "max_uses": 50,
  "expires_at": "2025-09-15T23:59:59",
  "is_active": true
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Discount updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload, invalid `discount_percent` (not a number between 0 and 100), invalid `max_uses` (not a non-negative integer), invalid `expires_at` (not a valid ISO datetime), or invalid `is_active` (not a boolean).
    ```json
    {
      "error": "Request must contain JSON data"
    }
    ```
    ```json
    {
      "error": "Discount percent must be a number between 0 and 100"
    }
    ```
    ```json
    {
      "error": "Max uses must be a non-negative integer"
    }
    ```
    ```json
    {
      "error": "Expires at must be a valid ISO datetime"
    }
    ```
    ```json
    {
      "error": "Is active must be a boolean"
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
  - **HTTP 404**: Discount with the specified ID does not exist or failed to update.
    ```json
    {
      "error": "Discount not found or failed to update"
    }
    ```
  - **HTTP 500**: Server error when updating the discount.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 6. Delete Discount
### Endpoint: `/discounts/<int:discount_id>`
### Method: `DELETE`
### Description
Deletes a discount by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `discount_id` (integer): The ID of the discount to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Discount deleted successfully"
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
  - **HTTP 404**: Discount with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Discount not found or failed to delete"
    }
    ```
  - **HTTP 500**: Server error when deleting the discount.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 7. Get All Discounts (Admin Only)
### Endpoint: `/discounts`
### Method: `GET`
### Description
Retrieves a paginated list of all discounts in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination (must be positive).
- `per_page` (integer, default: `20`): The number of discounts per page (must be positive).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "discounts": [
      {
        "id": 123,
        "code": "SUMMER25",
        "description": "Summer sale discount",
        "discount_percent": 25.0,
        "max_uses": 100,
        "expires_at": "2025-08-31T23:59:59",
        "is_active": true
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
      "error": "Page number must be positive"
    }
    ```
    ```json
    {
      "error": "Per page must be positive"
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
  - **HTTP 500**: Server error when retrieving discounts.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `DiscountManager` class, which encapsulates database operations for discounts.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` with a dedicated logger (`logger = logging.getLogger(__name__)`) for detailed error and success tracking.
- The `expires_at` field in requests and responses is in ISO 8601 format (e.g., `2025-08-31T23:59:59`), with `null` returned if not set.
- The `discount_percent` field accepts both integers and floats but must be between 0 and 100, inclusive.
- The `is_active` field is stored as an integer (`0` or `1`) in the database but returned as a boolean (`true` or `false`) in responses. For the `PUT /discounts/<int:discount_id>` endpoint, it must be provided as a boolean and is converted to an integer internally.
- The `max_uses` field can be `null` for unlimited uses or a non-negative integer.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `GET /discounts/code/<string:code>` and `GET /discounts/valid/<string:code>` endpoints are accessible to any authenticated user, with no additional ownership checks.
- The `GET /discounts/valid/<string:code>` endpoint returns only discounts that are active (`is_active = 1`), not expired (current time is before `expires_at`, if set), and have not exceeded their `max_uses` limit (if applicable), as determined by `DiscountManager.get_valid_discount`.