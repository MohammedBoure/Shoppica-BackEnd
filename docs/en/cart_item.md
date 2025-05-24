# Cart Items API Documentation

This document provides detailed information about the Cart Items API endpoints defined in `admin_apis/cart_items.py`. These endpoints manage items in a user's shopping cart within an e-commerce platform, including adding, retrieving, updating, and deleting cart items. Authentication and authorization are enforced using JWT (JSON Web Tokens) with specific roles (`@jwt_required` for user authentication and `@admin_required` for admin-only operations).

## Base URL
All endpoints are prefixed with `/api`. For example, `/cart_items` is accessed as `/api/cart_items`.

## Authentication
- **JWT Token**: Required for all endpoints. Include the token in the `Authorization` header as `Bearer <token>`.
- **User Access**: Endpoints marked with `@jwt_required()` allow authenticated users to manage their own cart items (based on `user_id` matching `get_jwt_identity()`) or admins to manage any cart items.
- **Admin Privileges**: The endpoint marked with `@admin_required` (`GET /api/cart_items`) requires a JWT token with `is_admin: true`.
- **Public Access**: None of the endpoints are publicly accessible without authentication.

## Endpoints

### 1. Add Cart Item
- **Endpoint**: `POST /api/cart_items`
- **Description**: Adds a new item to a user's shopping cart. Only accessible to the user themselves or admins.
- **Authorization**: Requires `@jwt_required()`. Users can only add items to their own cart unless they are admins (`is_admin: true`).
- **Input**:
  ```json
  {
    "user_id": <integer>,     // Required: ID of the user
    "product_id": <integer>,  // Required: ID of the product
    "quantity": <integer>     // Required: Quantity of the product
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {
      "message": "Cart item added successfully",
      "cart_item_id": <integer>
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "User ID, product ID, and quantity are required"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized to add cart item for another user"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Failed to add cart item"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 2. Get Cart Item by ID
- **Endpoint**: `GET /api/cart_items/<cart_item_id>`
- **Description**: Retrieves a cart item by its ID. Only accessible to the cart item’s owner or admins.
- **Authorization**: Requires `@jwt_required()`. Users can only access their own cart items unless they are admins (`is_admin: true`).
- **Input**: URL parameter `cart_item_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "user_id": <integer>,
      "product_id": <integer>,
      "quantity": <integer>,
      "added_at": <string>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Cart item not found"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized access to this cart item"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 3. Get Cart Items by User
- **Endpoint**: `GET /api/cart_items/user/<user_id>`
- **Description**: Retrieves all cart items for a specific user. Only accessible to the user themselves or admins.
- **Authorization**: Requires `@jwt_required()`. Users can only access their own cart items unless they are admins (`is_admin: true`).
- **Input**: URL parameter `user_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "cart_items": [
        {
          "id": <integer>,
          "user_id": <integer>,
          "product_id": <integer>,
          "quantity": <integer>,
          "added_at": <string>,
          "product_name": <string>,
          "product_price": <float>
        },
        ...
      ]
    }
    ```
    or, if no cart items:
    ```json
    {
      "cart_items": [],
      "message": "No cart items found for this user"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized to view cart items for another user"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 4. Update Cart Item
- **Endpoint**: `PUT /api/cart_items/<cart_item_id>`
- **Description**: Updates a cart item’s details (e.g., quantity). Only accessible to the cart item’s owner or admins.
- **Authorization**: Requires `@jwt_required()`. Users can only update their own cart items unless they are admins (`is_admin: true`).
- **Input**:
  ```json
  {
    "quantity": <integer>     // Required: New quantity of the product
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Cart item updated successfully"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Failed to update cart item"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Cart item not found"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized to update this cart item"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 5. Delete Cart Item
- **Endpoint**: `DELETE /api/cart_items/<cart_item_id>`
- **Description**: Deletes a cart item by ID. Only accessible to the cart item’s owner or admins.
- **Authorization**: Requires `@jwt_required()`. Users can only delete their own cart items unless they are admins (`is_admin: true`).
- **Input**: URL parameter `cart_item_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Cart item deleted successfully"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Cart item not found"
    }
    ```
    or
    ```json
    {
      "error": "Cart item not found or failed to delete"
    }
    ```
  - **Error (403)**:
    ```json
    {
      "error": "Unauthorized to delete this cart item"
    }
    ```
  - **Error (401, if no valid JWT)**:
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

### 6. Get All Cart Items (Paginated)
- **Endpoint**: `GET /api/cart_items?page=<page>&per_page=<per_page>`
- **Description**: Retrieves a paginated list of all cart items across all users (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  - Query parameters:
    - `page` (integer, default: 1)
    - `per_page` (integer, default: 20)
- **Output**:
  - **Success (200)**:
    ```json
    {
      "cart_items": [
        {
          "id": <integer>,
          "user_id": <integer>,
          "product_id": <integer>,
          "quantity": <integer>,
          "added_at": <string>,
          "product_name": <string>,
          "product_price": <float>
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

### Adding a Cart Item (User or Admin)
```bash
curl -X POST http://localhost:5000/api/cart_items -H "Authorization: Bearer <user_token>" -H "Content-Type: application/json" -d '{"user_id":1,"product_id":1,"quantity":2}'
```
Response:
```json
{
  "message": "Cart item added successfully",
  "cart_item_id": 1
}
```
Note: Non-admin users can only add items to their own cart (`user_id` must match `get_jwt_identity()`). Admins can add items to any user’s cart.

### Getting a Cart Item by ID (User or Admin)
```bash
curl -X GET http://localhost:5000/api/cart_items/1 -H "Authorization: Bearer <user_token>"
```
Response:
```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 1,
  "quantity": 2,
  "added_at": "2025-05-23T22:00:00Z"
}
```
Note: Non-admin users can only access their own cart items. Admins can access any cart item.

### Getting Cart Items by User (User or Admin)
```bash
curl -X GET http://localhost:5000/api/cart_items/user/1 -H "Authorization: Bearer <user_token>"
```
Response:
```json
{
  "cart_items": [
    {
      "id": 1,
      "user_id": 1,
      "product_id": 1,
      "quantity": 2,
      "added_at": "2025-05-23T22:00:00Z",
      "product_name": "Sample Product",
      "product_price": 19.99
    }
  ]
}
```
Note: Non-admin users can only access their own cart items. Admins can access cart items for any user.

### Updating a Cart Item (User or Admin)
```bash
curl -X PUT http://localhost:5000/api/cart_items/1 -H "Authorization: Bearer <user_token>" -H "Content-Type: application/json" -d '{"quantity":3}'
```
Response:
```json
{
  "message": "Cart item updated successfully"
}
```
Note: Non-admin users can only update their own cart items. Admins can update any cart item.

### Deleting a Cart Item (User or Admin)
```bash
curl -X DELETE http://localhost:5000/api/cart_items/1 -H "Authorization: Bearer <user_token>"
```
Response:
```json
{
  "message": "Cart item deleted successfully"
}
```
Note: Non-admin users can only delete their own cart items. Admins can delete any cart item.

### Getting All Cart Items (Admin Only)
```bash
curl -X GET http://localhost:5000/api/cart_items?page=1&per_page=20 -H "Authorization: Bearer <admin_token>"
```
Response:
```json
{
  "cart_items": [
    {
      "id": 1,
      "user_id": 1,
      "product_id": 1,
      "quantity": 3,
      "added_at": "2025-05-23T22:00:00Z",
      "product_name": "Sample Product",
      "product_price": 19.99
    },
    ...
  ],
  "total": 10,
  "page": 1,
  "per_page": 20
}
```

## Notes
- **Database Manager**: The API relies on `CartItemManager` for database operations.
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages. Errors are logged for debugging.
- **Security**:
  - User-specific endpoints (`POST /api/cart_items`, `GET /api/cart_items/<cart_item_id>`, `GET /api/cart_items/user/<user_id>`, `PUT /api/cart_items/<cart_item_id>`, `DELETE /api/cart_items/<cart_item_id>`) restrict access to the authenticated user’s cart items unless the user is an admin.
  - The admin endpoint (`GET /api/cart_items`) requires a valid JWT with admin privileges.
- **Data Validation**: Ensures required fields (`user_id`, `product_id`, `quantity`) are provided when adding a cart item. The `update_cart_item` endpoint requires a valid `quantity`.
- **Product Information**: The `product_name` and `product_price` fields in `GET /api/cart_items/user/<user_id>` and `GET /api/cart_items` assume the `CartItemManager` returns `name` and `price` fields (e.g., via a database join with the products table). If not supported, remove these fields from the response.
- **Testing**: Unit tests can be created in `test/test_cart_items.py` to verify functionality.

For further details, refer to the source code in `admin_apis/cart_items.py`.