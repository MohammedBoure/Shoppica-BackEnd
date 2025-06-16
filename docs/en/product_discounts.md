# Product Discounts API Documentation

This document provides detailed information about the Product Discounts API endpoints implemented in the Flask Blueprint `product_discounts`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /product_discounts`), updating (`PUT /product_discounts/<int:discount_id>`), deleting (`DELETE /product_discounts/<int:discount_id>`), retrieving a specific discount (`GET /product_discounts/<int:discount_id>`), and retrieving all discounts (`GET /product_discounts`) require admin privileges, enforced by the `@admin_required` decorator.
- The `/product_discounts/product/<int:product_id>` GET and `/product_discounts/valid/<int:product_id>` GET endpoints do not require authentication, allowing public access to product discount data.
- The `ProductDiscountManager` class handles all database interactions for product discount-related operations.

---

## 1. Add a New Product Discount
### Endpoint: `/product_discounts`
### Method: `POST`
### Description
Creates a new discount for a product. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `product_id` (integer): The ID of the product to which the discount applies.
  - `discount_percent` (float): The discount percentage (between 0 and 100).
- **Optional Fields**:
  - `starts_at` (string, ISO 8601 format): The start date and time of the discount.
  - `ends_at` (string, ISO 8601 format): The end date and time of the discount.
  - `is_active` (integer, default: `1`): Indicates if the discount is active (1 for active, 0 for inactive).

**Example Request Body**:
```json
{
  "product_id": 123,
  "discount_percent": 20.0,
  "starts_at": "2025-06-16T12:00:00Z",
  "ends_at": "2025-06-30T23:59:59Z",
  "is_active": 1
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Product discount added successfully",
    "discount_id": 456
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing required fields (`product_id` or `discount_percent`), invalid `product_id` (not a positive integer), invalid `discount_percent` (not between 0 and 100), invalid ISO 8601 format for `starts_at` or `ends_at`, or `starts_at` is after `ends_at`.
    ```json
    {
      "error": "Product ID and discount percent are required"
    }
    ```
    ```json
    {
      "error": "Product ID must be a positive integer"
    }
    ```
    ```json
    {
      "error": "Discount percent must be between 0 and 100"
    }
    ```
    ```json
    {
      "error": "starts_at must be in ISO 8601 format"
    }
    ```
    ```json
    {
      "error": "ends_at must be in ISO 8601 format"
    }
    ```
    ```json
    {
      "error": "starts_at must be before ends_at"
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
      "error": "Internal server error"
    }
    ```

---

## 2. Get Product Discount by ID
### Endpoint: `/product_discounts/<int:discount_id>`
### Method: `GET`
### Description
Retrieves the details of a specific product discount by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `discount_id` (integer): The ID of the discount to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "product_id": 123,
    "discount_percent": 20.0,
    "starts_at": "2025-06-16T12:00:00Z",
    "ends_at": "2025-06-30T23:59:59Z",
    "is_active": 1
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Discount with the specified ID does not exist.
    ```json
    {
      "error": "Product discount not found"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving the discount.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 3. Get Product Discounts by Product
### Endpoint: `/product_discounts/product/<int:product_id>`
### Method: `GET`
### Description
Retrieves all discounts for a specific product. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `product_id` (integer): The ID of the product whose discounts are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "product_discounts": [
      {
        "id": 456,
        "product_id": 123,
        "discount_percent": 20.0,
        "starts_at": "2025-06-16T12:00:00Z",
        "ends_at": "2025-06-30T23:59:59Z",
        "is_active": 1
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "product_discounts": []
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid `product_id` (not a positive integer).
    ```json
    {
      "error": "Product ID must be a positive integer"
    }
    ```
  - **HTTP 500**: Server error when retrieving discounts.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 4. Get Valid Product Discounts
### Endpoint: `/product_discounts/valid/<int:product_id>`
### Method: `GET`
### Description
Retrieves all valid (active and within date range) discounts for a specific product. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `product_id` (integer): The ID of the product whose valid discounts are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "product_discounts": [
      {
        "id": 456,
        "product_id": 123,
        "discount_percent": 20.0,
        "starts_at": "2025-06-16T12:00:00Z",
        "ends_at": "2025-06-30T23:59:59Z",
        "is_active": 1
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "product_discounts": []
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid `product_id` (not a positive integer).
    ```json
    {
      "error": "Product ID must be a positive integer"
    }
    ```
  - **HTTP 500**: Server error when retrieving valid discounts.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 5. Update Product Discount
### Endpoint: `/product_discounts/<int:discount_id>`
### Method: `PUT`
### Description
Updates the details of an existing product discount. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `discount_id` (integer): The ID of the discount to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `discount_percent` (float): The updated discount percentage (between 0 and 100).
    - `starts_at` (string, ISO 8601 format): The updated start date and time of the discount.
    - `ends_at` (string, ISO 8601 format): The updated end date and time of the discount.
    - `is_active` (integer): The updated active status (1 for active, 0 for inactive).

**Example Request Body**:
```json
{
  "discount_percent": 25.0,
  "starts_at": "2025-07-01T00:00:00Z",
  "ends_at": "2025-07-15T23:59:59Z",
  "is_active": 1
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Product discount updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid `discount_percent` (not between 0 and 100), invalid ISO 8601 format for `starts_at` or `ends_at`, `starts_at` is after `ends_at`, or failure to update the discount.
    ```json
    {
      "error": "Discount percent must be between 0 and 100"
    }
    ```
    ```json
    {
      "error": "starts_at must be in ISO 8601 format"
    }
    ```
    ```json
    {
      "error": "ends_at must be in ISO 8601 format"
    }
    ```
    ```json
    {
      "error": "starts_at must be before ends_at"
    }
    ```
    ```json
    {
      "error": "Failed to update product discount"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when updating the discount.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 6. Delete Product Discount
### Endpoint: `/product_discounts/<int:discount_id>`
### Method: `DELETE`
### Description
Deletes a product discount by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `discount_id` (integer): The ID of the discount to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Product discount deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Discount with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Product discount not found or failed to delete"
    }
    ```
  - **HTTP 500**: Server error when deleting the discount.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 7. Get All Product Discounts (Admin Only)
### Endpoint: `/product_discounts`
### Method: `GET`
### Description
Retrieves a paginated list of all product discounts in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of discounts per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "product_discounts": [
      {
        "id": 456,
        "product_id": 123,
        "discount_percent": 20.0,
        "starts_at": "2025-06-16T12:00:00Z",
        "ends_at": "2025-06-30T23:59:59Z",
        "is_active": 1,
        "product_name": "Wireless Headphones"
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
  - **HTTP 500**: Server error when retrieving discounts.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `ProductDiscountManager` class.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` with a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and monitoring.
- The `starts_at` and `ends_at` fields in requests and responses are in ISO 8601 format (e.g., `2025-06-16T12:00:00Z`).
- The `product_name` field is included in the response for the `GET /product_discounts` endpoint to provide additional context.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- Public endpoints (`/product_discounts/product/<int:product_id>` GET and `/product_discounts/valid/<int:product_id>` GET) provide read-only access to product discount data without requiring authentication.
- The `/product_discounts/valid/<int:product_id>` GET endpoint returns only discounts that are active (`is_active = 1`) and within their valid date range (current time is between `starts_at` and `ends_at`).