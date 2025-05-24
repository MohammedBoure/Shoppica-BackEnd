# Order Items API Documentation

This document provides detailed information about the Order Items API endpoints defined in `admin_apis/order_items.py`. These endpoints manage order items in an e-commerce platform, including adding, retrieving, updating, and deleting order items. Authentication and authorization are enforced using JWT (JSON Web Tokens) with specific roles (`@jwt_required()` for authenticated users and `@admin_required` for admins).

## Base URL
All endpoints are prefixed with `/api`. For example, `/order_items` is accessed as `/api/order_items`.

## Authentication
- **JWT Token**: Required for endpoints marked with `@jwt_required()` or `@admin_required`. Include the token in the `Authorization` header as `Bearer <token>`.
- **Admin Privileges**: Endpoints marked with `@admin_required` require a JWT token with `is_admin: true`.
- **User Authorization**: Non-admin users can only access order items associated with their own orders.

## Endpoints

### 1. Add Order Item
- **Endpoint**: `POST /api/order_items`
- **Description**: Adds a new order item to an order (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "order_id": <integer>,      // Required: ID of the order
    "product_id": <integer>,    // Required: ID of the product
    "quantity": <integer>,      // Required: Quantity of the product
    "price": <float>           // Required: Price per unit
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {
      "message": "Order item added successfully",
      "order_item_id": <integer>
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Order ID, product ID, quantity, and price are required"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Failed to add order item"
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

### 2. Get Order Item by ID
- **Endpoint**: `GET /api/order_items/<order_item_id>`
- **Description**: Retrieves an order item by its ID. Users can only access items from their own orders.
- **Authorization**: Requires `@jwt_required()`. Non-admin users must own the associated order.
- **Input**: URL parameter `order_item_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "order_id": <integer>,
      "product_id": <integer>,
      "quantity": <integer>,
      "price": <float>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Order item not found"
    }
    ```
  - **Error (404, if order not found)**:
    ```json
    {
      "error": "Associated order not found"
    }
    ```
  - **Error (403, if unauthorized)**:
    ```json
    {
      "error": "Unauthorized access to this order item"
    }
    ```

### 3. Get Order Items by Order
- **Endpoint**: `GET /api/order_items/order/<order_id>`
- **Description**: Retrieves all order items for a specific order. Users can only access items from their own orders.
- **Authorization**: Requires `@jwt_required()`. Non-admin users must own the order.
- **Input**: URL parameter `order_id` (integer).
- **Output**:
  - **Success (200, with items)**:
    ```json
    {
      "order_items": [
        {
          "id": <integer>,
          "order_id": <integer>,
          "product_id": <integer>,
          "quantity": <integer>,
          "price": <float>,
          "product_name": <string>
        },
        ...
      ]
    }
    ```
  - **Success (200, no items)**:
    ```json
    {
      "order_items": [],
      "message": "No order items found for this order"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Order not found"
    }
    ```
  - **Error (403, if unauthorized)**:
    ```json
    {
      "error": "Unauthorized to view items for this order"
    }
    ```

### 4. Update Order Item
- **Endpoint**: `PUT /api/order_items/<order_item_id>`
- **Description**: Updates an order item’s quantity or price (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "quantity": <integer>,  // Optional: New quantity
    "price": <float>       // Optional: New price
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Order item updated successfully"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Failed to update order item"
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

### 5. Delete Order Item
- **Endpoint**: `DELETE /api/order_items/<order_item_id>`
- **Description**: Deletes an order item by ID (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `order_item_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Order item deleted successfully"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Order item not found or failed to delete"
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

### 6. Get All Order Items (Paginated)
- **Endpoint**: `GET /api/order_items?page=<page>&per_page=<per_page>`
- **Description**: Retrieves a paginated list of all order items (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  - Query parameters:
    - `page` (integer, default: 1)
    - `per_page` (integer, default: 20)
- **Output**:
  - **Success (200)**:
    ```json
    {
      "order_items": [
        {
          "id": <integer>,
          "order_id": <integer>,
          "product_id": <integer>,
          "quantity": <integer>,
          "price": <float>,
          "product_name": <string>
        },
        ...
      ],
      "total": <integer>,
      "page": <integer>,
      "per_page": <integer>
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

## Example Usage
### Obtaining a JWT Token
First, authenticate via the login endpoint (assumed to be `/api/login`):
```bash
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"adminpassword"}'
```
Response:
```json
{
  "access_token": "<your_jwt_token>"
}
```

### Adding an Order Item (Admin)
```bash
curl -X POST http://localhost:5000/api/order_items -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"order_id":1,"product_id":1,"quantity":2,"price":19.99}'
```
Response:
```json
{
  "message": "Order item added successfully",
  "order_item_id": 1
}
```

### Getting Order Items for an Order (User)
```bash
curl -X GET http://localhost:5000/api/order_items/order/1 -H "Authorization: Bearer <user_token>"
```
Response:
```json
{
  "order_items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 1,
      "quantity": 2,
      "price": 19.99,
      "product_name": "Laptop"
    }
  ]
}
```

## Notes
- **Database Managers**: The API relies on `OrderItemManager` and `OrderManager` for database operations.
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages.
- **Security**: Ensure the JWT secret key is securely configured in `app.py`.
- **Testing**: Unit tests can be created in `test/test_order_items.py` to verify functionality.

For further details, refer to the source code in `admin_apis/order_items.py`.