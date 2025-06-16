# Orders API Documentation

This document provides detailed information about the Orders API endpoints implemented in the Flask Blueprint `orders`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /orders`), retrieving a specific order (`GET /orders/<int:order_id>`), and retrieving orders by user (`GET /orders/user/<int:user_id>`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- Endpoints for updating (`PUT /orders/<int:order_id>`), deleting (`DELETE /orders/<int:order_id>`), and retrieving all orders (`GET /orders`) require admin privileges, enforced by the `@admin_required` decorator.
- The `current_user_id` is extracted from the session as an integer, and the `is_admin` flag determines if the user has admin privileges (defaults to `False` if not set).
- The `OrderManager` class handles all database interactions for order-related operations.

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
  - `total_price` (float): The total price of the order.
- **Optional Fields**:
  - `status` (string, default: `"pending"`): The status of the order (e.g., pending, shipped, delivered).

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
  - **HTTP 400**: Missing required fields (`user_id`, `shipping_address_id`, or `total_price`) or invalid JSON payload.
    ```json
    {
      "error": "User ID, shipping address ID, and total price are required"
    }
    ```
    ```json
    {
      "error": "Invalid JSON payload"
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
  - **Optional Fields**:
    - `status` (string): The updated status of the order (e.g., pending, shipped, delivered).
    - `total_price` (float): The updated total price of the order.
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
  - **HTTP 400**: Invalid JSON payload or failure to update the order (e.g., invalid data or database error).
    ```json
    {
      "error": "Invalid JSON payload"
    }
    ```
    ```json
    {
      "error": "Failed to update order"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
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
- `per_page` (integer, default: `20`): The number of orders per page.

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
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `OrderManager` class.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` for debugging and monitoring purposes.
- The `created_at` field in responses is a timestamp indicating when the order was created (format: `YYYY-MM-DDTHH:MM:SS`, or empty string if not available).
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `GET /orders/user/<int:user_id>` endpoint returns an empty list with a message if no orders are found for the specified user.
- The `POST /orders` and `GET /orders/<int:order_id>` endpoints check that non-admin users can only interact with their own orders, while `PUT`, `DELETE`, and `GET /orders` endpoints are restricted to admins.