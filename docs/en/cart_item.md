# Cart Items API Documentation

This document provides detailed information about the Cart Items API endpoints implemented in the Flask Blueprint `cart_items`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /cart/items`), retrieving a user's own cart items (`GET /cart/items`), retrieving a specific cart item (`GET /cart/items/<int:cart_item_id>`), updating a cart item (`PUT /cart/items/<int:cart_item_id>`), deleting a cart item (`DELETE /cart/items/<int:cart_item_id>`), clearing a user's cart (`DELETE /cart/clear`), and retrieving user cart statistics (`GET /cart/stats`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- The custom `@check_cart_item_ownership` decorator is used for `GET`, `PUT`, and `DELETE` operations on specific cart items, ensuring that the authenticated user owns the cart item (`user_id` matches `session['user_id']`) or is an admin (`is_admin` is `True`).
- Admin-only endpoints (`GET /admin/cart_items/user/<int:user_id>`, `GET /admin/cart_items`, `GET /admin/cart_items/search`, `DELETE /admin/cart_items/user/<int:user_id>`, `DELETE /admin/cart_items/product/<int:product_id>`, `GET /admin/cart/stats`, `GET /admin/cart_items/user/<int:user_id>/stats`) require admin privileges, enforced by the `@admin_required` decorator.
- The `CartItemManager` class handles all database interactions for cart item-related operations.

## Logging
- Logging is configured with `logging.basicConfig(level=logging.INFO)` and a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and error tracking.

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
  - `quantity` (integer): The quantity of the product to add (must be positive).

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
  - **HTTP 400**: Missing or invalid request body, missing required fields (`product_id` or `quantity`), invalid `product_id` or `quantity` format, quantity not positive, or insufficient stock.
    ```json
    {
      "error": "product_id and quantity are required"
    }
    ```
    ```json
    {
      "error": "Invalid product_id or quantity format"
    }
    ```
    ```json
    {
      "error": "Quantity must be a positive integer"
    }
    ```
    ```json
    {
      "error": "Failed to add cart item, possibly due to insufficient stock"
    }
    ```
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 500**: Server error when adding the cart item or retrieving the newly added item.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```
    ```json
    {
      "error": "Failed to retrieve newly added cart item"
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
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
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
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
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
    - `quantity` (integer): The updated quantity of the product (must be positive).

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
  - **HTTP 400**: Missing or invalid `quantity`, invalid quantity format, quantity not positive, or insufficient stock.
    ```json
    {
      "error": "Quantity is required"
    }
    ```
    ```json
    {
      "error": "Invalid quantity format"
    }
    ```
    ```json
    {
      "error": "Quantity must be a positive integer"
    }
    ```
    ```json
    {
      "error": "Failed to update cart item, possibly due to insufficient stock"
    }
    ```
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
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
  - **HTTP 500**: Server error when updating or retrieving the updated cart item.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```
    ```json
    {
      "error": "Failed to retrieve updated cart item"
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
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
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
  - **HTTP 500**: Server error when deleting the cart item.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 6. Clear User's Cart
### Endpoint: `/cart/clear`
### Method: `DELETE`
### Description
Clears all items from the authenticated user's cart.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Cart cleared successfully. 2 items removed."
  }
  ```
- **Error Responses**:
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 500**: Server error when clearing the cart.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 7. Get User's Cart Statistics
### Endpoint: `/cart/stats`
### Method: `GET`
### Description
Retrieves statistics for the authenticated user's cart, such as total items or total cost (as defined by `CartItemManager.get_user_cart_stats`).

### Authentication
- Requires a valid session (`@session_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "total_items": 5,
    "total_cost": 150.00
  }
  ```
  *Note*: The exact structure depends on the implementation of `CartItemManager.get_user_cart_stats`.
- **Error Responses**:
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 500**: Server error when retrieving cart statistics.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 8. Get Cart Items by User (Admin Only)
### Endpoint: `/admin/cart_items/user/<int:user_id>`
### Method: `GET`
### Description
Retrieves all cart items for a specific user. Restricted to admin users only.

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

## 9. Get All Cart Items Paginated (Admin Only)
### Endpoint: `/admin/cart_items`
### Method: `GET`
### Description
Retrieves a paginated list of all cart items in the system. Restricted to admin users only.

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
  - **HTTP 400**: Invalid `page` or `per_page` values (negative or zero).
    ```json
    {
      "error": "Invalid page or per_page value"
    }
    ```
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

## 10. Search Cart Items (Admin Only)
### Endpoint: `/admin/cart_items/search`
### Method: `GET`
### Description
Searches for cart items based on `user_id` or `product_id` with pagination. Restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `user_id` (integer, optional): The ID of the user to filter cart items.
- `product_id` (integer, optional): The ID of the product to filter cart items.
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of cart items per page.

*Note*: At least one of `user_id` or `product_id` must be provided.

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
    "total": 10,
    "page": 1,
    "per_page": doctrine: 20
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing both `user_id` and `product_id`, or invalid `page` or `per_page` values.
    ```json
    {
      "error": "At least one search parameter (user_id or product_id) is required"
    }
    ```
    ```json
    {
      "error": "Invalid page or per_page value"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when searching cart items.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 11. Clear User's Cart (Admin Only)
### Endpoint: `/admin/cart_items/user/<int:user_id>`
### Method: `DELETE`
### Description
Clears all cart items for a specific user. Restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `user_id` (integer): The ID of the user whose cart is to be cleared.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Cart for user 789 cleared successfully. 2 items removed."
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when clearing the cart.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 12. Delete Cart Items by Product (Admin Only)
### Endpoint: `/admin/cart_items/product/<int:product_id>`
### Method: `DELETE`
### Description
Deletes all cart items associated with a specific product. Restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `product_id` (integer): The ID of the product whose cart items are to be deleted.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "All cart items for product 123 deleted successfully. 5 items removed."
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when deleting cart items.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 13. Get Overall Cart Statistics (Admin Only)
### Endpoint: `/admin/cart/stats`
### Method: `GET`
### Description
Retrieves overall statistics for all cart items in the system, such as total items or total value (as defined by `CartItemManager.get_cart_stats`). Restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "total_items": 100,
    "total_value": 2500.00
  }
  ```
  *Note*: The exact structure depends on the implementation of `CartItemManager.get_cart_stats`.
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving statistics.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## 14. Get User's Cart Statistics (Admin Only)
### Endpoint: `/admin/cart_items/user/<int:user_id>/stats`
### Method: `GET`
### Description
Retrieves statistics for a specific user's cart, such as total items or total cost (as defined by `CartItemManager.get_user_cart_stats`). Restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (URL Parameters)
- `user_id` (integer): The ID of the user whose cart statistics are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "total_items": 5,
    "total_cost": 150.00
  }
  ```
  *Note*: The exact structure depends on the implementation of `CartItemManager.get_user_cart_stats`.
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when retrieving cart statistics.
    ```json
    {
      "error": "An internal server error occurred"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `CartItemManager` class, which encapsulates database operations for cart items.
- The `@check_cart_item_ownership` decorator optimizes database access by fetching the cart item once and passing it to the route handler via Flask's `g` object, avoiding redundant database calls.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `POST /cart/items` and `PUT /cart/items/<int:cart_item_id>` endpoints validate that `quantity` is a positive integer and check for sufficient stock.
- Admin-only endpoints provide visibility and control over all cart items for administrative purposes.
- The `@admin_required` decorator ensures that only users with `is_admin=True` in their session can access admin endpoints.
- Pagination is supported for admin endpoints (`GET /admin/cart_items` and `GET /admin/cart_items/search`) with `page` and `per_page` query parameters.
- The exact structure of responses for `/cart/stats`, `/admin/cart/stats`, and `/admin/cart_items/user/<int:user_id>/stats` depends on the implementation of `CartItemManager` methods (`get_user_cart_stats` and `get_cart_stats`).