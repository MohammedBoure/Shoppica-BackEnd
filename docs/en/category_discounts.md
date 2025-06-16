# Category Discounts API Documentation

This document provides detailed information about the Category Discounts API endpoints implemented in the Flask Blueprint `category_discounts`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /category_discounts`), updating (`PUT /category_discounts/<int:discount_id>`), deleting (`DELETE /category_discounts/<int:discount_id>`), retrieving a specific category discount (`GET /category_discounts/<int:discount_id>`), and retrieving all category discounts (`GET /category_discounts`) require admin privileges, enforced by the `@admin_required` decorator.
- Endpoints for retrieving all discounts for a category (`GET /category_discounts/category/<int:category_id>`) and retrieving valid discounts for a category (`GET /category_discounts/valid/<int:category_id>`) are publicly accessible without authentication.
- The `CategoryDiscountManager` class handles all database interactions for category discount-related operations.

---

## 1. Add a New Category Discount
### Endpoint: `/category_discounts`
### Method: `POST`
### Description
Creates a new discount for a specific category. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `category_id` (integer): The ID of the category to which the discount applies.
  - `discount_percent` (float): The discount percentage (between 0 and 100).
- **Optional Fields**:
  - `starts_at` (string, ISO 8601 format): The start date and time of the discount.
  - `ends_at` (string, ISO 8601 format): The end date and time of the discount.
  - `is_active` (boolean, default: `true`): Whether the discount is active.

**Example Request Body**:
```json
{
  "category_id": 123,
  "discount_percent": 20.0,
  "starts_at": "2025-06-16T00:00:00Z",
  "ends_at": "2025-07-16T23:59:59Z",
  "is_active": true
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "id": 456,
    "category_id": 123,
    "discount_percent": 20.0,
    "starts_at": "2025-06-16T00:00:00Z",
    "ends_at": "2025-07-16T23:59:59Z",
    "is_active": true
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload, missing required fields (`category_id` or `discount_percent`), invalid `category_id` (not a positive integer), invalid `discount_percent` (not between 0 and 100), invalid date format, or `starts_at` is after `ends_at`.
    ```json
    {
      "error": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "Category ID and discount percent are required"
    }
    ```
    ```json
    {
      "error": "Category ID must be a positive integer"
    }
    ```
    ```json
    {
      "error": "Discount percent must be between 0 and 100"
    }
    ```
    ```json
    {
      "error": "Invalid date format: Invalid ISO 8601 string. Use ISO 8601 format."
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
  - **HTTP 500**: Server error when failing to add the category discount to the database.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 2. Update Category Discount
### Endpoint: `/category_discounts/<int:discount_id>`
### Method: `PUT`
### Description
Updates the details of an existing category discount. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `discount_id` (integer): The ID of the category discount to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `category_id` (integer): The updated category ID.
    - `discount_percent` (float): The updated discount percentage (between 0 and 100).
    - `starts_at` (string, ISO 8601 format): The updated start date and time.
    - `ends_at` (string, ISO 8601 format): The updated end date and time.
    - `is_active` (boolean): The updated active status.

**Example Request Body**:
```json
{
  "discount_percent": 25.0,
  "ends_at": "2025-08-16T23:59:59Z",
  "is_active": false
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "category_id": 123,
    "discount_percent": 25.0,
    "starts_at": "2025-06-16T00:00:00Z",
    "ends_at": "2025-08-16T23:59:59Z",
    "is_active": false
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload, invalid `category_id` (not a positive integer), invalid `discount_percent` (not between 0 and 100), invalid date format, `starts_at` is after `ends_at`, or failure to update the discount.
    ```json
    {
      "error": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "Category ID must be a positive integer"
    }
    ```
    ```json
    {
      "error": "Discount percent must be between 0 and 100"
    }
    ```
    ```json
    {
      "error": "Invalid date format: Invalid ISO 8601 string. Use ISO 8601 format."
    }
    ```
    ```json
    {
      "error": "starts_at must be before ends_at"
    }
    ```
    ```json
    {
      "error": "Failed to update category discount"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Category discount with the specified ID does not exist.
    ```json
    {
      "error": "Category discount not found"
    }
    ```
  - **HTTP 500**: Server error when updating the category discount.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 3. Get Category Discount by ID
### Endpoint: `/category_discounts/<int:discount_id>`
### Method: `GET`
### Description
Retrieves the details of a specific category discount by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `discount_id` (integer): The ID of the category discount to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "category_id": 123,
    "discount_percent": 20.0,
    "starts_at": "2025-06-16T00:00:00Z",
    "ends_at": "2025-07-16T23:59:59Z",
    "is_active": true
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Category discount with the specified ID does not exist.
    ```json
    {
      "error": "Category discount not found"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving the category discount.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 4. Get Discounts by Category
### Endpoint: `/category_discounts/category/<int:category_id>`
### Method: `GET`
### Description
Retrieves all discounts associated with a specific category. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `category_id` (integer): The ID of the category whose discounts are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "category_discounts": [
      {
        "id": 456,
        "category_id": 123,
        "discount_percent": 20.0,
        "starts_at": "2025-06-16T00:00:00Z",
        "ends_at": "2025-07-16T23:59:59Z",
        "is_active": true
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "category_discounts": []
  }
  ```
- **Error Responses**:
  - **HTTP 500**: Server error when retrieving the category discounts.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 5. Get Valid Category Discounts
### Endpoint: `/category_discounts/valid/<int:category_id>`
### Method: `GET`
### Description
Retrieves all valid discounts for a specific category (discounts that are active and within their start/end date range). This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `category_id` (integer): The ID of the category whose valid discounts are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "category_discounts": [
      {
        "id": 456,
        "category_id": 123,
        "discount_percent": 20.0,
        "starts_at": "2025-06-16T00:00:00Z",
        "ends_at": "2025-07-16T23:59:59Z",
        "is_active": true
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "category_discounts": []
  }
  ```
- **Error Responses**:
  - **HTTP 500**: Server error when retrieving valid category discounts.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 6. Delete Category Discount
### Endpoint: `/category_discounts/<int:discount_id>`
### Method: `DELETE`
### Description
Deletes a category discount by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `discount_id` (integer): The ID of the category discount to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Category discount deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Category discount with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Category discount not found or failed to delete"
    }
    ```
  - **HTTP 500**: Server error when deleting the category discount.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 7. Get All Category Discounts (Admin Only)
### Endpoint: `/category_discounts`
### Method: `GET`
### Description
Retrieves a paginated list of all category discounts in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of category discounts per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "category_discounts": [
      {
        "id": 456,
        "category_id": 123,
        "discount_percent": 20.0,
        "starts_at": "2025-06-16T00:00:00Z",
        "ends_at": "2025-07-16T23:59:59Z",
        "is_active": true
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
  - **HTTP 500**: Server error when retrieving category discounts.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `CategoryDiscountManager` class.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` with a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and monitoring.
- Date fields (`starts_at` and `ends_at`) in requests and responses are in ISO 8601 format (e.g., `2025-06-16T00:00:00Z`).
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `_validate_discount_data` helper function validates inputs for `POST` and `PUT` endpoints, ensuring consistency in error handling for required fields, data types, and date ranges.
- Public endpoints (`GET /category_discounts/category/<int:category_id>` and `GET /category_discounts/valid/<int:category_id>`) provide read-only access to category discount data without requiring authentication.
- The `GET /category_discounts/valid/<int:category_id>` endpoint returns only discounts that are active (`is_active = true`), have started (`starts_at` is in the past or null), and have not ended (`ends_at` is in the future or null).