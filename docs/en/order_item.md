# Order Items API Documentation

This document provides detailed information about the Order Items API endpoints implemented in the Flask Blueprint `order_items`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /order_items`), updating (`PUT /order_items/<int:order_item_id>`), deleting (`DELETE /order_items/<int:order_item_id>`), and retrieving all order items (`GET /order_items`) require admin privileges, enforced by the `@admin_required` decorator.
- Endpoints for retrieving a specific order item (`GET /order_items/<int:order_item_id>`) and retrieving order items by order (`GET /order_items/order/<int:order_id>`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- Non-admin users can only access order items associated with their own orders (`order['user_id']` must match `session['user_id']`).
- The `OrderItemManager` class handles database interactions for order item-related operations, and the `OrderManager` class is used to verify order ownership.

---

## 1. Add a New Order Item
### Endpoint: `/order_items`
### Method: `POST`
### Description
Creates a new order item for a specified order. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `order_id` (integer): The ID of the order to which the item belongs.
  - `product_id` (integer): The ID of the product being ordered.
  - `quantity` (integer): The quantity of the product in the order.
  - `price` (float): The price per unit of the product.

**Example Request Body**:
```json
{
  "order_id": 789,
  "product_id": 123,
  "quantity": 2,
  "price": 49.99
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Order item added successfully",
    "order_item_id": 456
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing required fields (`order_id`, `product_id`, `quantity`, or `price`).
    ```json
    {
      "error": "Order ID, product ID, quantity, and price are required"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when failing to add the order item to the database.
    ```json
    {
      "error": "Failed to add order item"
    }
    ```

---

## 2. Get Order Item by ID
### Endpoint: `/order_items/<int:order_item_id>`
### Method: `GET`
### Description
Retrieves the details of a specific order item by its ID. Only the user who owns the associated order or an admin can access it.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access order items for their own orders (`order['user_id']` must match `session['user_id']`).

### Inputs (URL Parameters)
- `order_item_id` (integer): The ID of the order item to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "order_id": 789,
    "product_id": 123,
    "quantity": 2,
    "price": 49.99
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized to access the order item (non-admin attempting to access an order item from another user's order).
    ```json
    {
      "error": "Unauthorized access to this order item"
    }
    ```
  - **HTTP 404**: Order item or associated order not found.
    ```json
    {
      "error": "Order item not found"
    }
    ```
    ```json
    {
      "error": "Associated order not found"
    }
    ```

---

## 3. Get Order Items by Order
### Endpoint: `/order_items/order/<int:order_id>`
### Method: `GET`
### Description
Retrieves all order items for a specific order. Only the user who owns the order or an admin can access these items.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access order items for their own orders (`order['user_id']` must match `session['user_id']`).

### Inputs (URL Parameters)
- `order_id` (integer): The ID of the order whose items are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "order_items": [
      {
        "id": 456,
        "order_id": 789,
        "product_id": 123,
        "quantity": 2,
        "price": 49.99,
        "product_name": "Wireless Headphones"
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "order_items": [],
    "message": "No order items found for this order"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized to view items for the order (non-admin attempting to access another user's order).
    ```json
    {
      "error": "Unauthorized to view items for this order"
    }
    ```
  - **HTTP 404**: Order not found.
    ```json
    {
      "error": "Order not found"
    }
    ```

---

## 4. Update Order Item
### Endpoint: `/order_items/<int:order_item_id>`
### Method: `PUT`
### Description
Updates the details of an existing order item. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `order_item_id` (integer): The ID of the order item to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `quantity` (integer): The updated quantity of the product.
    - `price` (float): The updated price per unit of the product.

**Example Request Body**:
```json
{
  "quantity": 3,
  "price": 45.99
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Order item updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Failure to update the order item (e.g., invalid data or database error).
    ```json
    {
      "error": "Failed to update order item"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

---

## 5. Delete Order Item
### Endpoint: `/order_items/<int:order_item_id>`
### Method: `DELETE`
### Description
Deletes an order item by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `order_item_id` (integer): The ID of the order item to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Order item deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Order item not found or failed to delete.
    ```json
    {
      "error": "Order item not found or failed to delete"
    }
    ```

---

## 6. Get All Order Items (Admin Only)
### Endpoint: `/order_items`
### Method: `GET`
### Description
Retrieves a paginated list of all order items in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of order items per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "order_items": [
      {
        "id": 456,
        "order_id": 789,
        "product_id": 123,
        "quantity": 2,
        "price": 49.99,
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

---

## Notes
- All endpoints interact with the database through the `OrderItemManager` class, with the `OrderManager` class used to verify order ownership for `GET /order_items/<int:order_item_id>` and `GET /order_items/order/<int:order_id>` endpoints.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` for debugging and monitoring purposes.
- The `product_name` field is included in the response for the `GET /order_items/order/<int:order_id>` and `GET /order_items` endpoints to provide additional context.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `GET /order_items/order/<int:order_id>` endpoint returns an empty list with a message if no order items are found for the specified order.
- The `POST /order_items`, `PUT /order_items/<int:order_item_id>`, `DELETE /order_items/<int:order_item_id>`, and `GET /order_items` endpoints are restricted to admins, while `GET /order_items/<int:order_item_id>` and `GET /order_items/order/<int:order_id>` endpoints allow access to authenticated users who own the associated order.