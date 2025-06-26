# Orders API Documentation

This document provides detailed information about the Orders API endpoints implemented in the Flask Blueprint `orders`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /orders`), retrieving a specific order (`GET /orders/<int:order_id>`), and retrieving orders by user (`GET /orders/user/<int:user_id>`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- Endpoints for updating (`PUT /orders/<int:order_id>`), deleting (`DELETE /orders/<int:order_id>`), retrieving all orders (`GET /orders`), searching orders (`GET /orders/search`), retrieving order statistics (`GET /orders/statistics`), retrieving top-selling products (`GET /orders/top-products`), and retrieving sales count (`GET /orders/number`) require admin privileges, enforced by the `@admin_required` decorator.
- The `current_user_id` is extracted from the session as an integer, and the `is_admin` flag determines if the user has admin privileges (defaults to `False` if not set).
- The `OrderManager` class handles all database interactions for order-related operations.

## Logging
- Logging is configured with `logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')` for debugging and error tracking.

---

## 1. Add a New Order
### Endpoint: `/orders`
### Method: `POST`
### Description
Creates a new order for a user. Only the authenticated user (matching the `user_id` in the request) or an admin can add an order for the specified user.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only add orders for themselves (`user_id` must match `session['user_id']`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `user_id` (integer): The ID of the user placing the order.
  - `shipping_address_id` (integer): The ID of the shipping address for the order.
  - `total_price` (number): The total price of the order (integer or float, non-negative).
- **Optional Fields**:
  - `status` (string, default: `"pending"`): The status of the order. Must be one of: `pending`, `processing`, `shipped`, `delivered`, `cancelled`.

**Example Request Body**:
```json
{
  "user_id": 123,
  "shipping_address_id": 456,
  "total_price": 99.99,
  "status": "pending"
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Order added successfully",
    "order_id": 789
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing required fields (`user_id`, `shipping_address_id`, or `total_price`), invalid JSON payload, invalid `user_id` or `shipping_address_id` (not integers), invalid `total_price` (not a number or negative), or invalid `status`.
    ```json
    {
      "error": "user_id, shipping_address_id, and total_price are required"
    }
    ```
    ```json
    {
      "error": "Invalid JSON payload"
    }
    ```
    ```json
    {
      "error": "user_id and shipping_address_id must be integers"
    }
    ```
    ```json
    {
      "error": "total_price must be a non-negative number"
    }
    ```
    ```json
    {
      "error": "Invalid status value"
    }
    ```
  - **HTTP 403**: Unauthorized to add an order for another user (non-admin attempting to use a different `user_id`).
    ```json
    {
      "error": "Unauthorized to add order for another user"
    }
    ```
  - **HTTP 500**: Server error when failing to add the order to the database.
    ```json
    {
      "error": "Failed to add order"
    }
    ```

---

## 2. Get Order by ID
### Endpoint: `/orders/<int:order_id>`
### Method: `GET`
### Description
Retrieves the details of a specific order by its ID. Only the user who placed the order or an admin can access it.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access their own orders (`order['user_id']` must match `session['user_id']`).

### Inputs (URL Parameters)
- `order_id` (integer): The ID of the order to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 789,
    "user_id": 123,
    "status": "pending",
    "total_price": 99.99,
    "shipping_address_id": 456,
    "created_at": "2025-06-16T12:58:00"
  }
  ```
  *Note*: The exact structure depends on the implementation of `OrderManager.get_order_by_id`.
- **Error Responses**:
  - **HTTP 403**: Unauthorized to access the order (non-admin attempting to access another user's order).
    ```json
    {
      "error": "Unauthorized access to this order"
    }
    ```
  - **HTTP 404**: Order with the specified ID does not exist.
    ```json
    {
      "error": "Order not found"
    }
    ```

---

## 3. Get Orders by User
### Endpoint: `/orders/user/<int:user_id>`
### Method: `GET`
### Description
Retrieves all orders for a specific user. Only the user themselves or an admin can access these orders.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access their own orders (`user_id` must match `session['user_id']`).

### Inputs (URL Parameters)
- `user_id` (integer): The ID of the user whose orders are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "orders": [
      {
        "id": 789,
        "user_id": 123,
        "status": "pending",
        "total_price": 99.99,
        "shipping_address_id": 456,
        "created_at": "2025-06-16T12:58:00"
      }
    ],
    "message": ""
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "orders": [],
    "message": "No orders found for this user"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized to view orders for another user (non-admin attempting to access another user's orders).
    ```json
    {
      "error": "Unauthorized to view orders for another user"
    }
    ```

---

## 4. Update Order
### Endpoint: `/orders/<int:order_id>`
### Method: `PUT`
### Description
Updates the details of an existing order. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `order_id` (integer): The ID of the order to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields** (at least one must be provided):
    - `status` (string): The updated status of the order. Must be one of: `pending`, `processing`, `shipped`, `delivered`, `cancelled`.
    - `total_price` (number): The updated total price of the order (integer or float, non-negative).
    - `shipping_address_id` (integer): The updated shipping address ID.

**Example Request Body**:
```json
{
  "status": "shipped",
  "total_price": 109.99,
  "shipping_address_id": 457
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Order updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON payload, no fields provided, invalid `status`, invalid `total_price` (not a number or negative), or invalid `shipping_address_id` (not an integer).
    ```json
    {
      "error": "Invalid JSON payload"
    }
    ```
    ```json
    {
      "error": "At least one field (status, total_price, shipping_address_id) must be provided"
    }
    ```
    ```json
    {
      "error": "Invalid status value"
    }
    ```
    ```json
    {
      "error": "total_price must be a non-negative number"
    }
    ```
    ```json
    {
      "error": "shipping_address_id must be an integer"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Order not found or failed to update.
    ```json
    {
      "error": "Order not found or failed to update"
    }
    ```

---

## 5. Delete Order
### Endpoint: `/orders/<int:order_id>`
### Method: `DELETE`
### Description
Deletes an order by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `order_id` (integer): The ID of the order to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Order deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Order with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Order not found or failed to delete"
    }
    ```

---

## 6. Get All Orders (Admin Only)
### Endpoint: `/orders`
### Method: `GET`
### Description
Retrieves a paginated list of all orders in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of orders per page (maximum: `100`).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "orders": [
      {
        "id": 789,
        "user_id": 123,
        "status": "pending",
        "total_price": 99.99,
        "shipping_address_id": 456,
        "created_at": "2025-06-16T12:58:00"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid `page` or `per_page` values (negative, zero, or `per_page` exceeds 100).
    ```json
    {
      "error": "page and per_page must be positive integers"
    }
    ```
    ```json
    {
      "error": "per_page cannot exceed 100"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

---

## 7. Search Orders (Admin Only)
### Endpoint: `/orders/search`
### Method: `GET`
### Description
Searches orders based on specified filters (search term, status, total price range, or date range). This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `search_term` (string, optional): A term to search in order-related fields (e.g., user details, order ID).
- `status` (string, optional): Filter by order status. Must be one of: `pending`, `processing`, `shipped`, `delivered`, `cancelled`.
- `min_total` (float, optional): Minimum total price for filtering.
- `max_total` (float, optional): Maximum total price for filtering.
- `start_date` (string, optional): Start date for filtering orders (ISO format: `YYYY-MM-DDTHH:MM:SS`).
- `end_date` (string, optional): End date for filtering orders (ISO format: `YYYY-MM-DDTHH:MM:SS`).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "orders": [
      {
        "id": 789,
        "user_id": 123,
        "status": "pending",
        "total_price": 99.99,
        "shipping_address_id": 456,
        "created_at": "2025-06-16T12:58:00"
      }
    ],
    "message": ""
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "orders": [],
    "message": "No orders found matching the criteria"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid `status`, `min_total` greater than `max_total`, or invalid date formats for `start_date` or `end_date`.
    ```json
    {
      "error": "Invalid status value"
    }
    ```
    ```json
    {
      "error": "min_total cannot be greater than max_total"
    }
    ```
    ```json
    {
      "error": "start_date and end_date must be in ISO format (YYYY-MM-DDTHH:MM:SS)"
    }
    ```
    ```json
    {
      "error": "start_date cannot be later than end_date"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

---

## 8. Get Order Statistics (Admin Only)
### Endpoint: `/orders/statistics`
### Method: `GET`
### Description
Retrieves statistics for orders, such as total orders or total revenue, within a specified date range. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `start_date` (string, optional): Start date for filtering orders (ISO format: `YYYY-MM-DDTHH:MM:SS`).
- `end_date` (string, optional): End date for filtering orders (ISO format: `YYYY-MM-DDTHH:MM:SS`).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "total_orders": 100,
    "total_revenue": 5000.00
  }
  ```
  *Note*: The exact structure depends on the implementation of `OrderManager.get_order_statistics`.
- **Error Responses**:
  - **HTTP 400**: Invalid date formats for `start_date` or `end_date`, or `start_date` later than `end_date`.
    ```json
    {
      "error": "start_date and end_date must be in ISO format (YYYY-MM-DDTHH:MM:SS)"
    }
    ```
    ```json
    {
      "error": "start_date cannot be later than end_date"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

---

## 9. Get Top-Selling Products (Admin Only)
### Endpoint: `/orders/top-products`
### Method: `GET`
### Description
Retrieves a list of top-selling products based on order data within a specified date range. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `start_date` (string, optional): Start date for filtering orders (ISO format: `YYYY-MM-DDTHH:MM:SS`).
- `end_date` (string, optional): End date for filtering orders (ISO format: `YYYY-MM-DDTHH:MM:SS`).
- `limit` (integer, default: `5`): Number of top products to return (between 1 and 50).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "top_products": [
      {
        "product_id": 123,
        "product_name": "Example Product",
        "total_quantity_sold": 50,
        "total_revenue": 2499.50
      }
    ],
    "message": ""
  }
  ```
  *Note*: The exact structure depends on the implementation of `OrderManager.get_top_selling_products`.
- **Empty Response** (HTTP 200):
  ```json
  {
    "top_products": [],
    "message": "No products found for the given criteria"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid date formats for `start_date` or `end_date`, `start_date` later than `end_date`, or invalid `limit` (not between 1 and 50).
    ```json
    {
      "error": "start_date and end_date must be in ISO format (YYYY-MM-DDTHH:MM:SS)"
    }
    ```
    ```json
    {
      "error": "start_date cannot be later than end_date"
    }
    ```
    ```json
    {
      "error": "limit must be between 1 and 50"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

---

## 10. Get Sales Count (Admin Only)
### Endpoint: `/orders/number`
### Method: `GET`
### Description
Retrieves the total number of orders, optionally filtered by status. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `status` (string, optional): Filter by order status. Can be a single status (e.g., `completed`) or multiple statuses (comma-separated, e.g., `completed,shipped`).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "success": true,
    "sales_count": 100
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving the sales count.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `OrderManager` class, which encapsulates database operations for orders.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` with a custom format for debugging and monitoring.
- The `created_at` field in order responses is a timestamp indicating when the order was created (format: `YYYY-MM-DDTHH:MM:SS`, or implementation-dependent).
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `POST /orders` and `GET /orders/<int:order_id>` endpoints ensure non-admin users can only interact with their own orders, while `PUT`, `DELETE`, `GET /orders`, `GET /orders/search`, `GET /orders/statistics`, `GET /orders/top-products`, and `GET /orders/number` are restricted to admins.
- The `GET /orders/user/<int:user_id>` and `GET /orders/search` endpoints return an empty list with a message if no orders are found.
- Pagination in `GET /orders` is limited to `per_page` values up to 100 to prevent excessive load.
- Date inputs (`start_date`, `end_date`) must be in ISO format (`YYYY-MM-DDTHH:MM:SS`), and validation ensures `start_date` is not later than `end_date`.
- The `GET /orders/number` endpoint supports both single and multiple status filters (comma-separated).