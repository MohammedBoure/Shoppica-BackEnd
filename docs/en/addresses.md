# Addresses API Documentation

This document provides detailed information about the Addresses API endpoints implemented in the Flask Blueprint `addresses`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses. The API interacts with the `addresses` table in a SQLite database via the `AddressManager` class.

## Authentication
- Endpoints for adding (`POST /addresses`), retrieving a user's own addresses (`GET /addresses/me`), retrieving a user's default address (`GET /addresses/me/default`), retrieving address statistics (`GET /addresses/me/stats`), retrieving a specific address (`GET /addresses/<int:address_id>`), updating an address (`PUT /addresses/<int:address_id>`), and deleting an address (`DELETE /addresses/<int:address_id>`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- The custom `@check_address_ownership` decorator is used for `GET`, `PUT`, and `DELETE` operations on specific addresses, ensuring that the authenticated user owns the address (`user_id` matches `session['user_id']`) or is an admin (`is_admin` is `True` in the session).
- Endpoints for retrieving all addresses for a specific user (`GET /admin/addresses/user/<int:user_id>`), retrieving all addresses with pagination (`GET /admin/addresses`), retrieving overall address statistics (`GET /admin/addresses/stats`), retrieving user-specific address statistics (`GET /admin/addresses/user/<int:user_id>/stats`), and deleting all addresses for a user (`DELETE /admin/addresses/user/<int:user_id>`) require admin privileges, enforced by the `@admin_required` decorator.
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
  - `address_line` (string): The primary address line.
  - `city` (string): The city of the address.
- **Optional Fields**:
  - `state` (string): The state or region of the address.
  - `postal_code` (string): The postal or ZIP code.
  - `is_default` (boolean, default: `false`): Whether this is the user's default address.

**Example Request Body**:
```json
{
  "address_line": "123 Main St",
  "city": "Springfield",
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
    "address_line": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701",
    "is_default": true
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload or missing required fields (`address_line` or `city`).
    ```json
    {
      "error": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "address_line and city are required"
    }
    ```
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 500**: Server error when failing to add the address to the database.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

**Notes**:
- Uses `AddressManager.add_address` to create the address.
- The `user_id` is derived from `session['user_id']`, ensuring security.
- The `is_default` field is converted to an integer (0 or 1) for database storage.

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
      "address_line": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "postal_code": "62701",
      "is_default": true
    }
  ]
  ```
- **Empty Response** (HTTP 200):
  ```json
  []
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 500**: Server error when retrieving addresses.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

**Notes**:
- Uses `AddressManager.get_addresses_by_user` to fetch addresses for `session['user_id']`.
- Addresses are converted to dictionaries using the `address_to_dict` helper function, with `is_default` as a boolean.

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
    "address_line": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701",
    "is_default": true
  }
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
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

**Notes**:
- Uses `AddressManager.get_address_by_id` via the `@check_address_ownership` decorator.
- The address is stored in `g.address` for efficient access.
- The `is_default` field is returned as a boolean.

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
    - `address_line` (string): The updated primary address line.
    - `city` (string): The updated city.
    - `state` (string): The updated state or region.
    - `postal_code` (string): The updated postal or ZIP code.
    - `is_default` (boolean): The updated default status.

**Example Request Body**:
```json
{
  "address_line": "456 Oak St",
  "city": "Springfield",
  "is_default": false
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "user_id": 789,
    "address_line": "456 Oak St",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701",
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
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
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

**Notes**:
- Uses `AddressManager.update_address` to update the address, followed by `AddressManager.get_address_by_id` to return the updated address.
- Only provided fields are updated; others remain unchanged.
- The `is_default` field is converted to an integer (0 or 1) for database storage but returned as a boolean.

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
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
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

**Notes**:
- Uses `AddressManager.delete_address` to delete the address.
- Cascading deletes are handled for related data (e.g., `orders` linked to the address) due to database schema constraints.

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
      "address_line": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "postal_code": "62701",
      "is_default": true
    }
  ]
  ```
- **Empty Response** (HTTP 200):
  ```json
  []
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
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

**Notes**:
- Uses `AddressManager.get_addresses_by_user` to fetch addresses for the specified `user_id`.
- Addresses are converted to dictionaries with `is_default` as a boolean.

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
        "address_line": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "postal_code": "62701",
        "is_default": true
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
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

**Notes**:
- Uses `AddressManager.get_addresses` to fetch paginated addresses.
- The response includes `total`, `page`, and `per_page` for pagination metadata.

---

## 8. Get Default Address
### Endpoint: `/addresses/me/default`
### Method: `GET`
### Description
Retrieves the default address for the currently authenticated user.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "user_id": 789,
    "address_line": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701",
    "is_default": true
  }
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 404**: No default address found for the user.
    ```json
    {
      "error": "No default address found"
    }
    ```
  - **HTTP 500**: Server error when retrieving the default address.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

**Notes**:
- Uses `AddressManager.get_default_address` to fetch the default address for `session['user_id']`.
- Returns HTTP 404 if no address with `is_default=1` exists for the user.

---

## 9. Get User's Address Statistics
### Endpoint: `/addresses/me/stats`
### Method: `GET`
### Description
Retrieves address statistics for the currently authenticated user.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "total_addresses": 5,
    "default_address_count": 1
  }
  ```
  - Note: The exact structure of the response depends on `AddressManager.get_user_address_stats`.
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 500**: Server error when retrieving statistics.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

**Notes**:
- Uses `AddressManager.get_user_address_stats` to fetch statistics for `session['user_id']`.
- The response format is assumed to include fields like `total_addresses` and `default_address_count`, based on typical address statistics.

---

## 10. Search Addresses (Admin Only)
### Endpoint: `/admin/addresses/search`
### Method: `GET`
### Description
Searches addresses by a single query word across multiple fields (e.g., `address_line`, `city`, `state`, `postal_code`). This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `q` (string, required): The search query word for partial matching across address fields.
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
        "address_line": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "postal_code": "62701",
        "is_default": true
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing search query parameter (`q`).
    ```json
    {
      "error": "Search query (q) is required."
    }
    ```
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when searching addresses.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

**Notes**:
- Uses `AddressManager.search_addresses` to perform a case-insensitive search across multiple fields.
- The response includes pagination metadata (`total`, `page`, `per_page`).

---

## 11. Delete Addresses by User (Admin Only)
### Endpoint: `/admin/addresses/user/<int:user_id>`
### Method: `DELETE`
### Description
Deletes all addresses for a specific user. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `user_id` (integer): The ID of the user whose addresses are to be deleted.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Successfully deleted 5 addresses for user ID 789."
  }
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when deleting addresses.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

**Notes**:
- Uses `AddressManager.delete_addresses_by_user` to delete all addresses for the specified `user_id`.
- The response includes the number of deleted addresses.

---

## 12. Get Overall Address Statistics (Admin Only)
### Endpoint: `/admin/addresses/stats`
### Method: `GET`
### Description
Retrieves overall statistics for all addresses in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "total_addresses": 100,
    "default_address_count": 50
  }
  ```
  - Note: The exact structure of the response depends on `AddressManager.get_address_stats`.
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving statistics.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

**Notes**:
- Uses `AddressManager.get_address_stats` to fetch overall statistics.
- The response format is assumed to include fields like `total_addresses` and `default_address_count`.

---

## 13. Get User Address Statistics (Admin Only)
### Endpoint: `/admin/addresses/user/<int:user_id>/stats`
### Method: `GET`
### Description
Retrieves address statistics for a specific user. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `user_id` (integer): The ID of the user whose address statistics are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "total_addresses": 5,
    "default_address_count": 1
  }
  ```
  - Note: The exact structure of the response depends on `AddressManager.get_user_address_stats`.
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving statistics.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

**Notes**:
- Uses `AddressManager.get_user_address_stats` to fetch statistics for the specified `user_id`.
- The response format is assumed to include fields like `total_addresses` and `default_address_count`.

---

## Notes
- All endpoints interact with the database through the `AddressManager` class.
- Logging is configured with `logging.basicConfig(level=logging.INFO)` and a dedicated logger (`logging.getLogger(__name__)`) with the format `%(asctime)s - %(levelname)s - %(message)s` for debugging and monitoring.
- The custom `@check_address_ownership` decorator ensures that users can only access their own addresses unless they are admins, and it optimizes database access by storing the fetched address in Flask's `g` object.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `POST /addresses` endpoint automatically uses the authenticated user's ID (`session['user_id']`) to prevent users from adding addresses for other users.
- The `PUT /addresses/<int:address_id>` endpoint allows partial updates, where only provided fields are modified.
- The `is_default` field is stored as an integer (0 or 1) in the database but returned as a boolean (`true` or `false`) in API responses.
- Admin-only endpoints provide visibility into all addresses or user-specific address data for administrative purposes.
- SQLite foreign key support is assumed to be enabled (e.g., via `PRAGMA foreign_keys = ON`), ensuring data integrity for related tables like `orders`.