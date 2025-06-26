# Analytics API Documentation

This document provides detailed information about the Analytics API endpoints implemented in the Flask Blueprint `analytics`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- All endpoints (`GET /analytics/products`, `GET /analytics/sales`, `GET /analytics/users`, `GET /analytics/customer-retention`, `GET /analytics/product-performance`, `GET /analytics/discount-effectiveness`) require admin privileges, enforced by the `@admin_required` decorator, which checks for a valid session and admin status.
- The `AnalyticsManager` class handles all database interactions for analytics-related operations.

## Logging
- Logging is configured with `logging.basicConfig(level=logging.INFO)` and a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and error tracking. Each endpoint logs errors for database exceptions (`SQLAlchemyError`) and unexpected errors, with specific error messages for invalid inputs.

## Date Handling
- Date parameters (`start_date` and `end_date`) are optional and, when provided, must be in `YYYY-MM-DD` format (e.g., `2025-06-26`). They are converted to `datetime` objects using `datetime.strptime`. If not provided, they are `None`.
- Date range validation ensures `start_date` is not later than `end_date`.

---

## 1. Get Top-Selling Products
### Endpoint: `/analytics/products`
### Method: `GET`
### Description
Retrieves a list of top-selling products based on total quantity sold. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `limit` (integer, default: `5`): The number of products to return (must be between 1 and 100, inclusive).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "status": "success",
    "data": [
      {
        "product_id": 123,
        "product_name": "Wireless Headphones",
        "total_quantity_sold": 150
      }
    ],
    "count": 1
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid `limit` (not between 1 and 100).
    ```json
    {
      "error": "Limit must be between 1 and 100"
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
  - **HTTP 500**: Database error or unexpected error.
    ```json
    {
      "error": "Database error occurred"
    }
    ```
    ```json
    {
      "error": "An unexpected error occurred"
    }
    ```

---

## 2. Get Sales Statistics
### Endpoint: `/analytics/sales`
### Method: `GET`
### Description
Retrieves sales statistics for a specified date range. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `start_date` (string, optional): Start date in `YYYY-MM-DD` format (e.g., `2025-06-26`).
- `end_date` (string, optional): End date in `YYYY-MM-DD` format (e.g., `2025-07-10`).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "status": "success",
    "data": {
      "total_sales": 1000,
      "total_revenue": 50000.0,
      "average_order_value": 50.0
    }
  }
  ```
  *Note*: The exact structure of `data` depends on the implementation of `AnalyticsManager.get_sales_statistics`.
- **Error Responses**:
  - **HTTP 400**: Invalid date format or `start_date` is later than `end_date`.
    ```json
    {
      "error": "Invalid date format. Use YYYY-MM-DD"
    }
    ```
    ```json
    {
      "error": "start_date cannot be later than end_date"
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
  - **HTTP 500**: Database error or unexpected error.
    ```json
    {
      "error": "Database error occurred"
    }
    ```
    ```json
    {
      "error": "An unexpected error occurred"
    }
    ```

---

## 3. Get User Statistics
### Endpoint: `/analytics/users`
### Method: `GET`
### Description
Retrieves user statistics for a specified date range. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `start_date` (string, optional): Start date in `YYYY-MM-DD` format (e.g., `2025-06-26`).
- `end_date` (string, optional): End date in `YYYY-MM-DD` format (e.g., `2025-07-10`).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "status": "success",
    "data": {
      "total_users": 500,
      "new_users": 50,
      "active_users": 300
    }
  }
  ```
  *Note*: The exact structure of `data` depends on the implementation of `AnalyticsManager.get_user_statistics`.
- **Error Responses**:
  - **HTTP 400**: Invalid date format or `start_date` is later than `end_date`.
    ```json
    {
      "error": "Invalid date format. Use YYYY-MM-DD"
    }
    ```
    ```json
    {
      "error": "start_date cannot be later than end_date"
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
  - **HTTP 500**: Database error or unexpected error.
    ```json
    {
      "error": "Database error occurred"
    }
    ```
    ```json
    {
      "error": "An unexpected error occurred"
    }
    ```

---

## 4. Get Customer Retention Rate
### Endpoint: `/analytics/customer-retention`
### Method: `GET`
### Description
Retrieves customer retention rate for a specified date range. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `start_date` (string, optional): Start date in `YYYY-MM-DD` format (e.g., `2025-06-26`).
- `end_date` (string, optional): End date in `YYYY-MM-DD` format (e.g., `2025-07-10`).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "status": "success",
    "data": {
      "retention_rate": 0.75,
      "returning_customers": 300,
      "total_customers": 400
    }
  }
  ```
  *Note*: The exact structure of `data` depends on the implementation of `AnalyticsManager.get_customer_retention_rate`.
- **Error Responses**:
  - **HTTP 400**: Invalid date format or `start_date` is later than `end_date`.
    ```json
    {
      "error": "Invalid date format. Use YYYY-MM-DD"
    }
    ```
    ```json
    {
      "error": "start_date cannot be later than end_date"
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
  - **HTTP 500**: Database error or unexpected error.
    ```json
    {
      "error": "Database error occurred"
    }
    ```
    ```json
    {
      "error": "An unexpected error occurred"
    }
    ```

---

## 5. Get Product Performance Trend
### Endpoint: `/analytics/product-performance`
### Method: `GET`
### Description
Retrieves performance trend data for a specific product over a specified date range. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `product_id` (integer, required): The ID of the product to analyze.
- `start_date` (string, optional): Start date in `YYYY-MM-DD` format (e.g., `2025-06-26`).
- `end_date` (string, optional): End date in `YYYY-MM-DD` format (e.g., `2025-07-10`).
- `interval` (string, default: `daily`): Time interval for aggregation (`daily` or `monthly`).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "status": "success",
    "data": [
      {
        "date": "2025-06-26",
        "quantity_sold": 50,
        "revenue": 2500.0
      }
    ]
  }
  ```
  *Note*: The exact structure of `data` depends on the implementation of `AnalyticsManager.get_product_performance_trend`.
- **Error Responses**:
  - **HTTP 400**: Missing `product_id`, invalid `interval` (not `daily` or `monthly`), invalid date format, or `start_date` is later than `end_date`.
    ```json
    {
      "error": "product_id is required"
    }
    ```
    ```json
    {
      "error": "Interval must be either \"daily\" or \"monthly\""
    }
    ```
    ```json
    {
      "error": "Invalid input. Ensure product_id is valid and dates are in YYYY-MM-DD format"
    }
    ```
    ```json
    {
      "error": "start_date cannot be later than end_date"
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
  - **HTTP 500**: Database error or unexpected error.
    ```json
    {
      "error": "Database error occurred"
    }
    ```
    ```json
    {
      "error": "An unexpected error occurred"
    }
    ```

---

## 6. Get Discount Effectiveness
### Endpoint: `/analytics/discount-effectiveness`
### Method: `GET`
### Description
Retrieves metrics on discount effectiveness for a specified date range. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `start_date` (string, optional): Start date in `YYYY-MM-DD` format (e.g., `2025-06-26`).
- `end_date` (string, optional): End date in `YYYY-MM-DD` format (e.g., `2025-07-10`).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "status": "success",
    "data": {
      "total_discounts_applied": 100,
      "revenue_impact": 5000.0,
      "average_discount_amount": 50.0
    }
  }
  ```
  *Note*: The exact structure of `data` depends on the implementation of `AnalyticsManager.get_discount_effectiveness`.
- **Error Responses**:
  - **HTTP 400**: Invalid date format or `start_date` is later than `end_date`.
    ```json
    {
      "error": "Invalid date format. Use YYYY-MM-DD"
    }
    ```
    ```json
    {
      "error": "start_date cannot be later than end_date"
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
  - **HTTP 500**: Database error or unexpected error.
    ```json
    {
      "error": "Database error occurred"
    }
    ```
    ```json
    {
      "error": "An unexpected error occurred"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `AnalyticsManager` class, which encapsulates database operations for analytics data.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` with a dedicated logger (`logger = logging.getLogger(__name__)`) for detailed error tracking.
- Date parameters (`start_date` and `end_date`) are optional and, if provided, must be in `YYYY-MM-DD` format. They are converted to `datetime` objects for processing.
- The `limit` parameter in `GET /analytics/products` is validated to be between 1 and 100, inclusive.
- The `interval` parameter in `GET /analytics/product-performance` is validated to be either `daily` or `monthly`.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- All endpoints require admin privileges, ensuring that only authorized users can access analytics data.
- The response structure includes a `status` field (`success`) and a `data` field containing the analytics results. For `GET /analytics/products`, a `count` field is also included.
- The exact structure of the `data` field in responses depends on the implementation of the `AnalyticsManager` methods, but examples are provided based on typical analytics output formats.