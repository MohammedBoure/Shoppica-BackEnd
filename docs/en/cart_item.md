# Cart Items API Documentation

This document provides detailed information about the Cart Items API endpoints implemented in the Flask Blueprint `cart_items`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /cart/items`), retrieving a user's own cart items (`GET /cart/items`), retrieving a specific cart item (`GET /cart/items/<int:cart_item_id>`), updating a cart item (`PUT /cart/items/<int:cart_item_id>`), and deleting a cart item (`DELETE /cart/items/<int:cart_item_id>`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- The custom `@check_cart_item_ownership` decorator is used for `GET`, `PUT`, and `DELETE` operations on specific cart items, ensuring that the authenticated user owns the cart item (`user_id` matches `session['user_id']`) or is an admin (`is_admin` is `True`).
- Endpoints for retrieving all cart items for a specific user (`GET /admin/cart_items/user/<int:user_id>`) and retrieving all cart items with pagination (`GET /admin/cart_items`) require admin privileges, enforced by the `@admin_required` decorator.
- The `CartItemManager` class handles all database interactions for cart item-related operations.

---

## 1. Add a New Cart Item
### Endpoint: `/cart/items`
### Method: `POST`
### Description
Adds a new item to the authenticated user's cart. The `user_id` is automatically taken from the session, ensuring users can only add items to their own cart.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `product_id` (integer): The ID of the product to add to the cart.
  - `quantity` (integer): The quantity of the product to add.
  
**Example Request Body**:
```json
{
  "product_id": 123,
  "quantity": 2
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "id": 456,
    "user_id": 789,
    "product_id": 123,
    "quantity": 2
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing or invalid request body, or missing required fields (`product_id` or `quantity`).
    ```json
    {
      "error": "product_id and quantity are required"
    }
    ```
  - **HTTP 403**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Authentication required"
    }
    ```
  - **HTTP 500**: Server error when failing to add the cart item to the database.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 2. Get User's Cart Items
### Endpoint: `/cart/items`
### Method: `GET`
### Description
Retrieves all cart items for the currently authenticated user.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  [
    {
      "id": 456,
      "user_id": 789,
      "product_id": 123,
      "quantity": 2
    }
  ]
  ```
- **Empty Response** (HTTP 200):
  ```json
  []
  ```
- **Error Responses**:
  - **HTTP 403**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Authentication required"
    }
    ```
  - **HTTP 500**: Server error when retrieving cart items.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 3. Get Cart Item by ID
### Endpoint: `/cart/items/<int:cart_item_id>`
### Method: `GET`
### Description
Retrieves a specific cart item by its ID. Only the user who owns the cart item or an admin can access it.

### Authentication
- Requires a valid session (`@session_required`) and ownership verification (`@check_cart_item_ownership`).

### Inputs (URL Parameters)
- `cart_item_id` (integer): The ID of the cart item to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "user_id": 789,
    "product_id": 123,
    "quantity": 2
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized access to the cart item (non-owner and non-admin user).
    ```json
    {
      "error": "Unauthorized access to this cart item"
    }
    ```
  - **HTTP 404**: Cart item with the specified ID does not exist.
    ```json
    {
      "error": "Cart item not found"
    }
    ```
  - **HTTP 500**: Server error when retrieving the cart item (handled by `@check_cart_item_ownership`).

---

## 4. Update Cart Item
### Endpoint: `/cart/items/<int:cart_item_id>`
### Method: `PUT`
### Description
Updates the quantity of a specific cart item. Only the user who owns the cart item or an admin can update it.

### Authentication
- Requires a valid session (`@session_required`) and ownership verification (`@check_cart_item_ownership`).

### Inputs
- **URL Parameters**:
  - `cart_item_id` (integer): The ID of the cart item to update.
- **Request Body** (Content-Type: `application/json`):
  - **Required Fields**:
    - `quantity` (integer): The updated quantity of the product (must be non-negative).

**Example Request Body**:
```json
{
  "quantity": 3
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "user_id": 789,
    "product_id": 123,
    "quantity": 3
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing or invalid `quantity` (not an integer or negative).
    ```json
    {
      "error": "A valid quantity is required"
    }
    ```
  - **HTTP 403**: Unauthorized access to the cart item (non-owner and non-admin user).
    ```json
    {
      "error": "Unauthorized access to this cart item"
    }
    ```
  - **HTTP 404**: Cart item with the specified ID does not exist.
    ```json
    {
      "error": "Cart item not found"
    }
    ```
  - **HTTP 500**: Server error when updating the cart item.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 5. Delete Cart Item
### Endpoint: `/cart/items/<int:cart_item_id>`
### Method: `DELETE`
### Description
Deletes a specific cart item by its ID. Only the user who owns the cart item or an admin can delete it.

### Authentication
- Requires a valid session (`@session_required`) and ownership verification (`@check_cart_item_ownership`).

### Inputs
- **URL Parameters**:
  - `cart_item_id` (integer): The ID of the cart item to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Cart item deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized access to the cart item (non-owner and non-admin user).
    ```json
    {
      "error": "Unauthorized access to this cart item"
    }
    ```
  - **HTTP 404**: Cart item with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Cart item not found or failed to delete"
    }
    ```
  - **HTTP 500**: Server error when deleting the cart item.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 6. Get Cart Items by User (Admin Only)
### Endpoint: `/admin/cart_items/user/<int:user_id>`
### Method: `GET`
### Description
Retrieves all cart items for a specific user. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `user_id` (integer): The ID of the user whose cart items are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  [
    {
      "id": 456,
      "user_id": 789,
      "product_id": 123,
      "quantity": 2
    }
  ]
  ```
- **Empty Response** (HTTP 200):
  ```json
  []
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving cart items.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 7. Get All Cart Items (Admin Only)
### Endpoint: `/admin/cart_items`
### Method: `GET`
### Description
Retrieves a paginated list of all cart items in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of cart items per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "cart_items": [
      {
        "id": 456,
        "user_id": 789,
        "product_id": 123,
        "quantity": 2
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
  - **HTTP 500**: Server error when retrieving cart items.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `CartItemManager` class.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` with a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and monitoring.
- The custom `@check_cart_item_ownership` decorator ensures that users can only access their own cart items unless they are admins, and it optimizes database access by passing the fetched cart item to the route handler via Flask's `g` object.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `POST /cart/items` endpoint automatically uses the authenticated user's ID (`session['user_id']`) to prevent users from adding items to another user's cart.
- The `PUT /cart/items/<int:cart_item_id>` endpoint validates that the `quantity` is a non-negative integer.
- Admin-only endpoints (`GET /admin/cart_items/user/<int:user_id>` and `GET /admin/cart_items`) provide visibility into all cart items for administrative purposes.