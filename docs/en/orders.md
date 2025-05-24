# Orders API Documentation

This document provides detailed information about the Orders API endpoints defined in `admin_apis/orders.py`. These endpoints manage orders in an e-commerce platform, including adding, retrieving, updating, and deleting orders. Authentication and authorization are enforced using JWT (JSON Web Tokens) with specific roles (`@jwt_required` for user authentication and `@admin_required` for admin-only operations).

## Base URL
All endpoints are prefixed with `/api`. For example, `/orders` is accessed as `/api/orders`.

## Authentication
- **JWT Token**: Required for all endpoints. Include the token in the `Authorization` header as `Bearer <token>`.
- **User Access**: Endpoints marked with `@jwt_required()` allow authenticated users to access their own orders (based on `user_id` matching `get_jwt_identity()`) or admins to access any order.
- **Admin Privileges**: Endpoints marked with `@admin_required` require a JWT token with `is_admin: true`.
- **Public Access**: None of the endpoints are publicly accessible without authentication.

## Endpoints

### 1. Add Order
- **Endpoint**: `POST /api/orders`
- **Description**: Adds a new order for the authenticated user or, if admin, for any user.
- **Authorization**: Requires `@jwt_required()`. Users can only add orders for themselves unless they are admins (`is_admin: true`).
- **Input**:
  ```json
  {
    "user_id": <integer>,           // Required: ID of the user placing the order
    "shipping_address_id": <integer>, // Required: ID of the shipping address
    "total_price": <float>,         // Required: Total price of the order
    "status": <string>              // Optional: Order status (e.g., "pending"), default: "pending"
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {
      "message": "Order added successfully",
      "order_id": <integer>
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "User ID, shipping address ID, and total price are required"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized to add order for another user"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Failed to add order"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 2. Get Order by ID
- **Endpoint**: `GET /api/orders/<order_id>`
- **Description**: Retrieves an order by its ID. Only accessible to the order’s owner or admins.
- **Authorization**: Requires `@jwt_required()`. Users can only access their own orders unless they are admins (`is_admin: true`).
- **Input**: URL parameter `order_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "user_id": <integer>,
      "status": <string>,
      "total_price": <float>,
      "shipping_address_id": <integer>,
      "created_at": <string>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Order not found"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized access to this order"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 3. Get Orders by User
- **Endpoint**: `GET /api/orders/user/<user_id>`
- **Description**: Retrieves all orders for a specific user. Only accessible to the user themselves or admins.
- **Authorization**: Requires `@jwt_required()`. Users can only access their own orders unless they are admins (`is_admin: true`).
- **Input**: URL parameter `user_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "orders": [
        {
          "id": <integer>,
          "user_id": <integer>,
          "status": <string>,
          "total_price": <float>,
          "shipping_address_id": <integer>,
          "created_at": <string>
        },
        ...
      ]
    }
    ```
    or, if no orders:
    ```json
    {
      "orders": [],
      "message": "No orders found for this user"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized to view orders for another user"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 4. Update Order
- **Endpoint**: `PUT /api/orders/<order_id>`
- **Description**: Updates an order’s details (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "status": <string>,             // Optional: Order status (e.g., "shipped")
    "total_price": <float>,         // Optional: Total price of the order
    "shipping_address_id": <integer> // Optional: ID of the shipping address
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Order updated successfully"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Failed to update order"
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 5. Delete Order
- **Endpoint**: `DELETE /api/orders/<order_id>`
- **Description**: Deletes an order by ID (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `order_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Order deleted successfully"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Order not found or failed to delete"
    }
    ```
  - **Error (403, if not admin)**:
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 6. Get All Orders (Paginated)
- **Endpoint**: `GET /api/orders?page=<page>&per_page=<per_page>`
- **Description**: Retrieves a paginated list of all orders (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  - Query parameters:
    - `page` (integer, default: 1)
    - `per_page` (integer, default: 20)
- **Output**:
  - **Success (200)**:
    ```json
    {
      "orders": [
        {
          "id": <integer>,
          "user_id": <integer>,
          "status": <string>,
          "total_price": <float>,
          "shipping_address_id": <integer>,
          "created_at": <string>
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
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

## Example Usage
### Obtaining a JWT Token
First, authenticate via the login endpoint (assumed to be `/api/login`):
```bash
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"password"}'
```
Response:
```json
{
  "access_token": "<your_jwt_token>"
}
```

For admin operations, use an admin account:
```bash
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"adminpassword"}'
```
Response:
```json
{
  "access_token": "<admin_jwt_token>"
}
```

### Adding an Order (User or Admin)
```bash
curl -X POST http://localhost:5000/api/orders -H "Authorization: Bearer <user_token>" -H "Content-Type: application/json" -d '{"user_id":1,"shipping_address_id":1,"total_price":99.99,"status":"pending"}'
```
Response:
```json
{
  "message": "Order added successfully",
  "order_id": 1
}
```
Note: Non-admin users can only add orders for themselves (`user_id` must match `get_jwt_identity()`). Admins can add orders for any user.

### Getting an Order by ID (User or Admin)
```bash
curl -X GET http://localhost:5000/api/orders/1 -H "Authorization: Bearer <user_token>"
```
Response:
```json
{
  "id": 1,
  "user_id": 1,
  "status": "pending",
  "total_price": 99.99,
  "shipping_address_id": 1,
  "created_at": "2025-05-23T12:00:00Z"
}
```
Note: Non-admin users can only access their own orders. Admins can access any order.

### Getting Orders by User (User or Admin)
```bash
curl -X GET http://localhost:5000/api/orders/user/1 -H "Authorization: Bearer <user_token>"
```
Response:
```json
{
  "orders": [
    {
      "id": 1,
      "user_id": 1,
      "status": "pending",
      "total_price": 99.99,
      "shipping_address_id": 1,
      "created_at": "2025-05-23T12:00:00Z"
    }
  ]
}
```
Note: Non-admin users can only access their own orders. Admins can access orders for any user.

### Updating an Order (Admin Only)
```bash
curl -X PUT http://localhost:5000/api/orders/1 -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"status":"shipped","total_price":99.99,"shipping_address_id":1}'
```
Response:
```json
{
  "message": "Order updated successfully"
}
```

### Deleting an Order (Admin Only)
```bash
curl -X DELETE http://localhost:5000/api/orders/1 -H "Authorization: Bearer <admin_token>"
```
Response:
```json
{
  "message": "Order deleted successfully"
}
```

### Getting All Orders (Admin Only)
```bash
curl -X GET http://localhost:5000/api/orders?page=1&per_page=20 -H "Authorization: Bearer <admin_token>"
```
Response:
```json
{
  "orders": [
    {
      "id": 1,
      "user_id": 1,
      "status": "shipped",
      "total_price": 99.99,
      "shipping_address_id": 1,
      "created_at": "2025-05-23T12:00:00Z"
    },
    ...
  ],
  "total": 10,
  "page": 1,
  "per_page": 20
}
```

## Notes
- **Database Manager**: The API relies on `OrderManager` for database operations.
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages. Errors are logged for debugging.
- **Security**: 
  - User-specific endpoints (`POST /api/orders`, `GET /api/orders/<order_id>`, `GET /api/orders/user/<user_id>`) restrict access to the authenticated user’s orders unless the user is an admin.
  - Admin endpoints (`PUT /api/orders/<order_id>`, `DELETE /api/orders/<order_id>`, `GET /api/orders`) require a valid JWT with admin privileges.
- **Data Validation**: Ensures required fields (`user_id`, `shipping_address_id`, `total_price`) are provided when adding an order.
- **Testing**: Unit tests can be created in `test/test_orders.py` to verify functionality.

For further details, refer to the source code in `admin_apis/orders.py`.