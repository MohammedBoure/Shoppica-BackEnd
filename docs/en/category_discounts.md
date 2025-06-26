# Category Discounts API Documentation

This document provides detailed information about the Category Discounts API endpoints implemented in the Flask Blueprint `category_discounts`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /category_discounts`), updating (`PUT /category_discounts/<int:discount_id>`), deleting (`DELETE /category_discounts/<int:discount_id>`), and retrieving all category discounts (`GET /category_discounts`) require admin privileges, enforced by the `require_admin` function, which checks for `session.get('is_admin')` being `True`.
- The `GET /category_discounts/<int:discount_id>` endpoint does not explicitly require admin privileges in the provided code, making it publicly accessible, though this may be an oversight.
- Endpoints for retrieving all discounts for a category (`GET /category_discounts/category/<int:category_id>`) and valid discounts for a category (`GET /category_discounts/valid/<int:category_id>`) are publicly accessible without authentication.
- The `CategoryDiscountManager` class handles all database interactions for category discount-related operations.

## Logging
- Logging is configured with `logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')` and a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and error tracking. Each endpoint logs warnings for invalid inputs or missing resources and errors for exceptions, with success logs for completed operations.

## Date Handling
- The `parse_date` helper function parses ISO 8601 date strings (e.g., `2025-06-26T20:42:00Z`) by replacing `Z` with `+00:00` and converting to  `datetime` object with UTC timezone information removed.

---

## 1. Add a New Category Discount
### Endpoint: `/category_discounts`
### Method: `POST`
### Description
Creates a new discount for a specific category. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`require_admin` checks `session.get('is_admin')`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `category_id` (integer): The ID of the category to which the discount applies.
  - `discount_percent` (number): The discount percentage (must be a positive number).
- **Optional Fields**:
  - `starts_at` (string, ISO 8601 format): The start date and time of the discount (e.g., `2025-06-26T20:42:00Z`).
  - `ends_at` (string, ISO 8601 format): The end date and time of the discount (e.g., `2025-07-10T23:59:59Z`).
  - `is_active` (integer, default: `1`): Indicates if the discount is active (`1` for active, `0` for inactive).

**Example Request Body**:
```json
{
  "category_id": 123,
  "discount_percent": 20.0,
  "starts_at": "2025-06-26T20:42:00Z",
  "ends_at": "2025-07-10T23:59:59Z",
  "is_active": 1
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Category discount added successfully",
    "discount": {
      "id": 456,
      "category_id": 123,
      "discount_percent": 20.0,
      "starts_at": "2025-06-26T20:42:00+00:00",
      "ends_at": "2025-07-10T23:59:59+00:00",
      "is_active": 1
    }
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload, missing required fields (`category_id` or `discount_percent`), invalid `discount_percent` (not a positive number), or invalid date format for `starts_at` or `ends_at`.
    ```json
    {
      "error": "Bad Request",
      "message": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "Bad Request",
      "message": "category_id and discount_percent are required"
    }
    ```
    ```json
    {
      "error": "Bad Request",
      "message": "discount_percent must be a positive number"
    }
    ```
    ```json
    {
      "error": "Bad Request",
      "message": "Invalid date format. Use ISO 8601 format (e.g., '2025-06-25T12:00:00Z')"
    }
    ```
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "Unauthorized",
      "message": "User not authenticated"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Unauthorized",
      "message": "Admin access required"
    }
    ```
  - **HTTP 500**: Server error when failing to add the category discount to the database or database error.
    ```json
    {
      "error": "Internal Server Error",
      "message": "Failed to add category discount"
    }
    ```
    ```json
    {
      "error": "Internal Server Error",
      "message": "Database error"
    }
    ```

---

## 2. Get Category Discount by ID
### Endpoint: `/category_discounts/<int:discount_id>`
### Method: `GET`
### Description
Retrieves the details of a specific category discount by its ID. This endpoint is publicly accessible (no authentication required in the code, though this may be an oversight).

### Authentication
- No authentication required (based on the provided code).

### Inputs (URL Parameters)
- `discount_id` (integer): The ID of the category discount to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "discount": {
      "id": 456,
      "category_id": 123,
      "discount_percent": 20.0,
      "starts_at": "2025-06-26T20:42:00+00:00",
      "ends_at": "2025-07-10T23:59:59+00:00",
      "is_active": 1
    }
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Category discount with the specified ID does not exist.
    ```json
    {
      "error": "Not Found",
      "message": "Category discount not found"
    }
    ```
  - **HTTP 500**: Database error when retrieving the category discount.
    ```json
    {
      "error": "Internal Server Error",
      "message": "Database error"
    }
    ```

---

## 3. Get All Category Discounts (Admin Only)
### Endpoint: `/category_discounts`
### Method: `GET`
### Description
Retrieves a paginated list of all category discounts in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`require_admin` checks `session.get('is_admin')`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination (must be a positive integer).
- `per_page` (integer, default: `20`): The number of category discounts per page (must be a positive integer).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "category_discounts": [
      {
        "id": 456,
        "category_id": 123,
        "discount_percent": 20.0,
        "starts_at": "2025-06-26T20:42:00+00:00",
        "ends_at": "2025-07-10T23:59:59+00:00",
        "is_active": 1
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid `page` or `per_page` values (not positive integers).
    ```json
    {
      "error": "Bad Request",
      "message": "Page and per_page must be positive"
    }
    ```
    ```json
    {
      "error": "Bad Request",
      "message": "Invalid page or per_page value"
    }
    ```
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "Unauthorized",
      "message": "User not authenticated"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Unauthorized",
      "message": "Admin access required"
    }
    ```
  - **HTTP 500**: Database error when retrieving category discounts.
    ```json
    {
      "error": "Internal Server Error",
      "message": "Database error"
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
        "starts_at": "2025-06-26T20:42:00+00:00",
        "ends_at": "2025-07-10T23:59:59+00:00",
        "is_active": 1
      }
    ],
    "category_id": 123
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "category_discounts": [],
    "category_id": 123
  }
  ```
- **Error Responses**:
  - **HTTP 500**: Database error when retrieving the category discounts.
    ```json
    {
      "error": "Internal Server Error",
      "message": "Database error"
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
        "starts_at": "2025-06-26T20:42:00+00:00",
        "ends_at": "2025-07-10T23:59:59+00:00",
        "is_active": 1
      }
    ],
    "category_id": 123
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "category_discounts": [],
    "category_id": 123
  }
  ```
- **Error Responses**:
  - **HTTP 500**: Database error when retrieving valid category discounts.
    ```json
    {
      "error": "Internal Server Error",
      "message": "Database error"
    }
    ```

---

## 6. Update Category Discount
### Endpoint: `/category_discounts/<int:discount_id>`
### Method: `PUT`
### Description
Updates the details of an existing category discount. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`require_admin` checks `session.get('is_admin')`).

### Inputs
- **URL Parameters**:
  - `discount_id` (integer): The ID of the category discount to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `discount_percent` (number): The updated discount percentage (must be a positive number).
    - `starts_at` (string, ISO 8601 format): The updated start date and time (e.g., `2025-06-26T20:42:00Z`).
    - `ends_at` (string, ISO 8601 format): The updated end date and time (e.g., `2025-07-10T23:59:59Z`).
    - `is_active` (integer): The updated active status (`1` for active, `0` for inactive).

**Example Request Body**:
```json
{
  "discount_percent": 25.0,
  "starts_at": "2025-06-26T20:42:00Z",
  "ends_at": "2025-08-10T23:59:59Z",
  "is_active": 0
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Category discount updated successfully",
    "discount": {
      "id": 456,
      "category_id": 123,
      "discount_percent": 25.0,
      "starts_at": "2025-06-26T20:42:00+00:00",
      "ends_at": "2025-08-10T23:59:59+00:00",
      "is_active": 0
    }
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload, invalid `discount_percent` (not a positive number), or invalid date format for `starts_at` or `ends_at`.
    ```json
    {
      "error": "Bad Request",
      "message": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "Bad Request",
      "message": "discount_percent must be a positive number"
    }
    ```
    ```json
    {
      "error": "Bad Request",
      "message": "Invalid date format. Use ISO 8601 format (e.g., '2025-06-25T12:00:00Z')"
    }
    ```
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "Unauthorized",
      "message": "User not authenticated"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Unauthorized",
      "message": "Admin access required"
    }
    ```
  - **HTTP 404**: Category discount with the specified ID does not exist.
    ```json
    {
      "error": "Not Found",
      "message": "Category discount not found"
    }
    ```
  - **HTTP 500**: Database error when updating the category discount.
    ```json
    {
      "error": "Internal Server Error",
      "message": "Database error"
    }
    ```

---

## 7. Delete Category Discount
### Endpoint: `/category_discounts/<int:discount_id>`
### Method: `DELETE`
### Description
Deletes a category discount by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`require_admin` checks `session.get('is_admin')`).

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
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "Unauthorized",
      "message": "User not authenticated"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Unauthorized",
      "message": "Admin access required"
    }
    ```
  - **HTTP 404**: Category discount with the specified ID does not exist.
    ```json
    {
      "error": "Not Found",
      "message": "Category discount not found"
    }
    ```
  - **HTTP 500**: Database error when deleting the category discount.
    ```json
    {
      "error": "Internal Server Error",
      "message": "Database error"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `CategoryDiscountManager` class, which encapsulates database operations for category discounts.
- Logging is configured using `logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')` with a dedicated logger (`logger = logging.getLogger(__name__)`) for detailed error and success tracking.
- Date fields (`starts_at` and `ends_at`) in requests are parsed using the `parse_date` function, which expects ISO 8601 format and replaces `Z` with `+00:00` for UTC compatibility. Responses include timezone information (`+00:00`).
- The `discount_percent` field accepts both integers and floats but must be positive (no upper bound of 100 is enforced in the code).
- The `is_active` field is an integer (`0` or `1`) in both requests and responses, with `1` as the default for new discounts.
- No validation ensures `starts_at` is before `ends_at` or that `category_id` is positive in the provided code.
- Error responses include both an `error` field (e.g., "Bad Request", "Not Found") and a descriptive `message` field to assist clients in troubleshooting.
- The `GET /category_discounts/<int:discount_id>` endpoint lacks authentication in the code, which may be unintentional and could require admin privileges in practice.
- Public endpoints (`GET /category_discounts/category/<int:category_id>` and `GET /category_discounts/valid/<int:category_id>`) provide read-only access to category discount data without requiring authentication.
- The `GET /category_discounts/valid/<int:category_id>` endpoint returns only discounts that are active (`is_active = 1`) and within their valid date range (current time is between `starts_at` and `ends_at`, if set), as determined by `CategoryDiscountManager.get_valid_category_discounts`.
- The discount object structure in responses (e.g., `id`, `category_id`, `discount_percent`, `starts_at`, `ends_at`, `is_active`) is determined by the `CategoryDiscountManager` methods, though the exact format (e.g., datetime serialization) depends on the database implementation.