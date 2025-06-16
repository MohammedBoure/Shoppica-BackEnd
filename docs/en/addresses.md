# Addresses API Documentation

This document provides detailed information about the Addresses API endpoints implemented in the Flask Blueprint `addresses`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /addresses`), retrieving a user's own addresses (`GET /addresses/me`), retrieving a specific address (`GET /addresses/<int:address_id>`), updating an address (`PUT /addresses/<int:address_id>`), and deleting an address (`DELETE /addresses/<int:address_id>`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- The custom `@check_address_ownership` decorator is used for `GET`, `PUT`, and `DELETE` operations on specific addresses, ensuring that the authenticated user owns the address (`user_id` matches `session['user_id']`) or is an admin (`is_admin` is `True`).
- Endpoints for retrieving all addresses for a specific user (`GET /admin/addresses/user/<int:user_id>`) and retrieving all addresses with pagination (`GET /admin/addresses`) require admin privileges, enforced by the `@admin_required` decorator.
- The `AddressManager` class handles all database interactions for address-related operations.

---

## 1. Add a New Address
### Endpoint: `/addresses`
### Method: `POST`
### Description
Adds a new address for the authenticated user. The `user_id` is automatically taken from the session, ensuring users can only add addresses for themselves.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `address_line1` (string): The primary address line.
  - `city` (string): The city of the address.
  - `country` (string): The country of the address.
- **Optional Fields**:
  - `address_line2` (string): The secondary address line.
  - `state` (string): The state or region of the address.
  - `postal_code` (string): The postal or ZIP code.
  - `is_default` (boolean, default: `false`): Whether this is the user's default address.

**Example Request Body**:
```json
{
  "address_line1": "123 Main St",
  "city": "Springfield",
  "country": "USA",
  "address_line2": "Apt 4B",
  "state": "IL",
  "postal_code": "62701",
  "is_default": true
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "id": 456,
    "user_id": 789,
    "address_line1": "123 Main St",
    "address_line2": "Apt 4B",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701",
    "country": "USA",
    "is_default": true
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload or missing required fields (`address_line1`, `city`, or `country`).
    ```json
    {
      "error": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "address_line1, city, and country are required"
    }
    ```
  - **HTTP 403**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Authentication required"
    }
    ```
  - **HTTP 500**: Server error when failing to add the address to the database.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 2. Get User's Addresses
### Endpoint: `/addresses/me`
### Method: `GET`
### Description
Retrieves all addresses for the currently authenticated user.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  [
    {
      "id": 456,
      "user_id": 789,
      "address_line1": "123 Main St",
      "address_line2": "Apt 4B",
      "city": "Springfield",
      "state": "IL",
      "postal_code": "62701",
      "country": "USA",
      "is_default": true
    }
  ]
  ```
- **Empty Response** (HTTP 200):
  ```json
  []
  ```
- **Error Responses**:
  - **HTTP 403**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Authentication required"
    }
    ```
  - **HTTP 500**: Server error when retrieving addresses.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 3. Get Address by ID
### Endpoint: `/addresses/<int:address_id>`
### Method: `GET`
### Description
Retrieves a specific address by its ID. Only the user who owns the address or an admin can access it.

### Authentication
- Requires a valid session (`@session_required`) and ownership verification (`@check_address_ownership`).

### Inputs (URL Parameters)
- `address_id` (integer): The ID of the address to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "user_id": 789,
    "address_line1": "123 Main St",
    "address_line2": "Apt 4B",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701",
    "country": "USA",
    "is_default": true
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized access to the address (non-owner and non-admin user).
    ```json
    {
      "error": "Unauthorized access to this address"
    }
    ```
  - **HTTP 404**: Address with the specified ID does not exist.
    ```json
    {
      "error": "Address not found"
    }
    ```
  - **HTTP 500**: Server error when retrieving the address (handled by `@check_address_ownership`).

---

## 4. Update Address
### Endpoint: `/addresses/<int:address_id>`
### Method: `PUT`
### Description
Updates the details of a specific address. Only the user who owns the address or an admin can update it.

### Authentication
- Requires a valid session (`@session_required`) and ownership verification (`@check_address_ownership`).

### Inputs
- **URL Parameters**:
  - `address_id` (integer): The ID of the address to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `address_line1` (string): The updated primary address line.
    - `address_line2` (string): The updated secondary address line.
    - `city` (string): The updated city.
    - `state` (string): The updated state or region.
    - `postal_code` (string): The updated postal or ZIP code.
    - `country` (string): The updated country.
    - `is_default` (boolean): The updated default status.

**Example Request Body**:
```json
{
  "address_line1": "456 Oak St",
  "city": "Springfield",
  "country": "USA",
  "is_default": false
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "user_id": 789,
    "address_line1": "456 Oak St",
    "address_line2": "Apt 4B",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701",
    "country": "USA",
    "is_default": false
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload or failure to update the address.
    ```json
    {
      "error": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "Failed to update address"
    }
    ```
  - **HTTP 403**: Unauthorized access to the address (non-owner and non-admin user).
    ```json
    {
      "error": "Unauthorized access to this address"
    }
    ```
  - **HTTP 404**: Address with the specified ID does not exist.
    ```json
    {
      "error": "Address not found"
    }
    ```
  - **HTTP 500**: Server error when updating the address.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 5. Delete Address
### Endpoint: `/addresses/<int:address_id>`
### Method: `DELETE`
### Description
Deletes a specific address by its ID. Only the user who owns the address or an admin can delete it.

### Authentication
- Requires a valid session (`@session_required`) and ownership verification (`@check_address_ownership`).

### Inputs
- **URL Parameters**:
  - `address_id` (integer): The ID of the address to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Address deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized access to the address (non-owner and non-admin user).
    ```json
    {
      "error": "Unauthorized access to this address"
    }
    ```
  - **HTTP 404**: Address with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Address not found or failed to delete"
    }
    ```
  - **HTTP 500**: Server error when deleting the address.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 6. Get Addresses by User (Admin Only)
### Endpoint: `/admin/addresses/user/<int:user_id>`
### Method: `GET`
### Description
Retrieves all addresses for a specific user. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `user_id` (integer): The ID of the user whose addresses are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  [
    {
      "id": 456,
      "user_id": 789,
      "address_line1": "123 Main St",
      "address_line2": "Apt 4B",
      "city": "Springfield",
      "state": "IL",
      "postal_code": "62701",
      "country": "USA",
      "is_default": true
    }
  ]
  ```
- **Empty Response** (HTTP 200):
  ```json
  []
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving addresses.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 7. Get All Addresses (Admin Only)
### Endpoint: `/admin/addresses`
### Method: `GET`
### Description
Retrieves a paginated list of all addresses in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of addresses per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "addresses": [
      {
        "id": 456,
        "user_id": 789,
        "address_line1": "123 Main St",
        "address_line2": "Apt 4B",
        "city": "Springfield",
        "state": "IL",
        "postal_code": "62701",
        "country": "USA",
        "is_default": true
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
  - **HTTP 500**: Server error when retrieving addresses.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `AddressManager` class.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` with a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and monitoring.
- The custom `@check_address_ownership` decorator ensures that users can only access their own addresses unless they are admins, and it optimizes database access by passing the fetched address to the route handler via Flask's `g` object.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `POST /addresses` endpoint automatically uses the authenticated user's ID (`session['user_id']`) to prevent users from adding addresses for other users.
- The `PUT /addresses/<int:address_id>` endpoint allows partial updates, where only provided fields are modified.
- Admin-only endpoints (`GET /admin/addresses/user/<int:user_id>` and `GET /admin/addresses`) provide visibility into all addresses for administrative purposes.