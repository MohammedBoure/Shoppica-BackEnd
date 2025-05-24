# Address API Documentation

This document provides detailed information about the Address API endpoints implemented in the Flask Blueprint `addresses`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- All endpoints require JWT authentication using the `@jwt_required()` decorator.
- Some endpoints (e.g., `/api/addresses`) require admin privileges, enforced by the `@admin_required` decorator.
- The `current_user_id` is extracted from the JWT token, and the `is_admin` claim determines if the user has admin privileges.

---

## 1. Add a New Address
### Endpoint: `/api/addresses`
### Method: `POST`
### Description
Adds a new address for a user. The address can only be added for the authenticated user unless the requester is an admin.

### Authentication
- Requires a valid JWT token.
- Non-admin users can only add addresses for themselves.

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `user_id` (integer): The ID of the user to associate with the address.
  - `address_line1` (string): The primary address line.
  - `city` (string): The city of the address.
  - `country` (string): The country of the address.
- **Optional Fields**:
  - `address_line2` (string): The secondary address line (optional).
  - `state` (string): The state or region (optional).
  - `postal_code` (string): The postal code (optional).
  - `is_default` (boolean, default: `0`): Indicates if the address is the default for the user.

**Example Request Body**:
```json
{
  "user_id": 1,
  "address_line1": "123 Main St",
  "city": "New York",
  "country": "USA",
  "address_line2": "Apt 4B",
  "state": "NY",
  "postal_code": "10001",
  "is_default": true
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Address added successfully",
    "address_id": 123
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing required fields.
    ```json
    {
      "error": "User ID, address line 1, city, and country are required"
    }
    ```
  - **HTTP 403**: Unauthorized to add an address for another user.
    ```json
    {
      "error": "Unauthorized to add address for another user"
    }
    ```
  - **HTTP 500**: Failed to add the address.
    ```json
    {
      "error": "Failed to add address"
    }
    ```

---

## 2. Get Address by ID
### Endpoint: `/api/addresses/<int:address_id>`
### Method: `GET`
### Description
Retrieves the details of a specific address by its ID. Only the address owner or an admin can access the address.

### Authentication
- Requires a valid JWT token.
- Non-admin users can only access their own addresses.

### Inputs (URL Parameters)
- `address_id` (integer): The ID of the address to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 123,
    "user_id": 1,
    "address_line1": "123 Main St",
    "address_line2": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA",
    "is_default": true
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Address not found.
    ```json
    {
      "error": "Address not found"
    }
    ```
  - **HTTP 403**: Unauthorized to access the address.
    ```json
    {
      "error": "Unauthorized access to this address"
    }
    ```

---

## 3. Get Addresses by User
### Endpoint: `/api/addresses/user/<int:user_id>`
### Method: `GET`
### Description
Retrieves all addresses associated with a specific user. Only the user or an admin can access the addresses.

### Authentication
- Requires a valid JWT token.
- Non-admin users can only view their own addresses.

### Inputs (URL Parameters)
- `user_id` (integer): The ID of the user whose addresses are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  - If addresses are found:
    ```json
    {
      "addresses": [
        {
          "id": 123,
          "user_id": 1,
          "address_line1": "123 Main St",
          "address_line2": "Apt 4B",
          "city": "New York",
          "state": "NY",
          "postal_code": "10001",
          "country": "USA",
          "is_default": true
        },
        ...
      ]
    }
    ```
  - If no addresses are found:
    ```json
    {
      "addresses": [],
      "message": "No addresses found for this user"
    }
    ```
- **Error Response**:
  - **HTTP 403**: Unauthorized to view addresses for another user.
    ```json
    {
      "error": "Unauthorized to view addresses for another user"
    }
    ```

---

## 4. Update Address
### Endpoint: `/api/addresses/<int:address_id>`
### Method: `PUT`
### Description
Updates the details of an existing address. Only the address owner or an admin can update the address.

### Authentication
- Requires a valid JWT token.
- Non-admin users can only update their own addresses.

### Inputs
- **URL Parameters**:
  - `address_id` (integer): The ID of the address to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields** (only include fields to update):
    - `address_line1` (string): The primary address line.
    - `address_line2` (string): The secondary address line.
    - `city` (string): The city of the address.
    - `state` (string): The state or region.
    - `postal_code` (string): The postal code.
    - `country` (string): The country of the address.
    - `is_default` (boolean): Indicates if the address is the default.

**Example Request Body**:
```json
{
  "address_line1": "456 New St",
  "city": "Boston",
  "is_default": false
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Address updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Address not found.
    ```json
    {
      "error": "Address not found"
    }
    ```
  - **HTTP 403**: Unauthorized to update the address.
    ```json
    {
      "error": "Unauthorized to update this address"
    }
    ```
  - **HTTP 400**: Failed to update the address (e.g., invalid data).
    ```json
    {
      "error": "Failed to update address"
    }
    ```

---

## 5. Delete Address
### Endpoint: `/api/addresses/<int:address_id>`
### Method: `DELETE`
### Description
Deletes an address by its ID. Only the address owner or an admin can delete the address.

### Authentication
- Requires a valid JWT token.
- Non-admin users can only delete their own addresses.

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
  - **HTTP 404**: Address not found or failed to delete.
    ```json
    {
      "error": "Address not found or failed to delete"
    }
    ```
  - **HTTP 403**: Unauthorized to delete the address.
    ```json
    {
      "error": "Unauthorized to delete this address"
    }
    ```

---

## 6. Get All Addresses (Admin Only)
### Endpoint: `/api/addresses`
### Method: `GET`
### Description
Retrieves a paginated list of all addresses in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid JWT token with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of addresses per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "addresses": [
      {
        "id": 123,
        "user_id": 1,
        "address_line1": "123 Main St",
        "address_line2": "Apt 4B",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "is_default": true
      },
      ...
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```

---

## Notes
- All endpoints use the `AddressManager` class to interact with the database.
- Logging is configured with `logging.basicConfig(level=logging.INFO)` for debugging and monitoring.
- The `is_default` field is stored as a boolean (`0` or `1`) in the database but can be provided as a boolean (`true` or `false`) in the request body.
- Error responses include a descriptive `error` field to help clients understand the issue.