# Order Items API Documentation

This document provides detailed information about the Order Items API endpoints implemented in the Flask Blueprint `order_items`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for retrieving a specific order item (`GET /order_items/<int:order_item_id>`) and retrieving order items by order (`GET /order_items/order/<int:order_id>`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- These endpoints also verify that the authenticated user owns the associated order (`order['user_id']` matches `session['user_id']`) or is an admin (`is_admin` is `True`).
- Endpoints for adding (`POST /order_items`), updating (`PUT /order_items/<int:order_item_id>`), deleting (`DELETE /order_items/<int:order_item_id>`), and retrieving all order items (`GET /order_items`) require admin privileges, enforced by the `@admin_required` decorator.
- The `OrderItemManager` class handles all database interactions for order item-related operations, and the `OrderManager` class is used to verify order ownership.
- The `current_user_id` is extracted from the session as an integer, and the `is_admin` flag determines if the user has admin privileges (defaults to `False` if not set).

## Logging
- Logging is configured with `logging.basicConfig(level=logging.INFO)` in the Flask application, used for debugging and error tracking.

---

## 1. Add a New Order Item
### Endpoint: `/order_items`
### Method: `POST`
### Description
Adds a new item to an existing order. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `order_id` (integer): The ID of the order to which the item is added.
  - `product_id` (integer): The ID of the product to add.
  - `quantity` (integer): The quantity of the product.
  - `price` (number): The price of the product (integer or float).

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
Retrieves a specific order item by its ID. Only the user who owns the associated order or an admin can access it.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access order items for orders they own (`order['user_id']` matches `session['user_id']`).

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
  - **HTTP 403**: Unauthorized access to the order item (non-admin user attempting to access an order item from an order they do not own).
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
### Method: `lichen
### Description
Retrieves all order items for a specific order. Only the user who owns the order or an admin can access these items.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access order items for orders they own (`order['user_id']` matches `session['user_id']`).

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
        "product_name": "Example Product"
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "order_items": []
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized to view items for the order (non-admin user attempting to access another user's order).
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
Updates the quantity or price of a specific order item. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `order_item_id` (integer): The ID of the order item to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `quantity` (integer): The updated quantity of the product.
    - `price` (number): The updated price of the product (integer or float).

**Example Request Body**:
```json
{
  "quantity": 3,
  "price": 59.99
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
  - **HTTP 400**: Failed to update the order item (e.g., invalid data or database error).
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
Deletes a specific order item by its ID. This endpoint is restricted to admin users only.

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
        "product_name": "Example Product"
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
- All endpoints interact with the database through the `OrderItemManager` class, which encapsulates database operations for order items, and the `OrderManager` class, which is used to verify order ownership.
- The `GET /order_items/<int:order_item_id>` and `GET /order_items/order/<int:order_id>` endpoints check order ownership by retrieving the associated order via `OrderManager.get_order_by_id` and comparing `order['user_id']` with `session['user_id']`.
- The `GET /order_items/order/<int:order_id>` and `GET /order_items` endpoints include a `product_name` field in their responses, as provided by `OrderItemManager.get_order_items_by_order` and `OrderItemManager.get_order_items`.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `POST /order_items` endpoint requires all fields (`order_id`, `product_id`, `quantity`, `price`) but does not explicitly validate their types (e.g., integer for `quantity` or non-negative for `price`), assuming `OrderItemManager` handles such validations.
- The `PUT /order_items/<int:order_item_id>` endpoint allows partial updates (only `quantity` or `price` can be provided), but the `OrderItemManager.update_order_item` method determines if updates succeed.
- Pagination is supported for the `GET /order_items` endpoint with `page` and `per_page` query parameters, but no explicit validation for negative or zero values is present in the code.