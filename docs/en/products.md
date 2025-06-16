# Products API Documentation

This document provides detailed information about the Products API endpoints implemented in the Flask Blueprint `products`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /products`), updating (`PUT /products/<int:product_id>`), and deleting (`DELETE /products/<int:product_id>`) products require admin privileges, enforced by the `@admin_required` decorator.
- The `/products/<int:product_id>` GET, `/products/category/<int:category_id>` GET, and `/products` GET endpoints do not require authentication, allowing public access to product data.
- The `ProductManager` class handles all database interactions for product-related operations.

---

## 1. Add a New Product
### Endpoint: `/products`
### Method: `POST`
### Description
Creates a new product in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `name` (string): The name of the product.
  - `price` (float): The price of the product.
  - `stock_quantity` (integer): The available stock quantity.
- **Optional Fields**:
  - `category_id` (integer): The ID of the category the product belongs to.
  - `description` (string): A description of the product.
  - `image_url` (string): URL of the product image.
  - `is_active` (integer, default: `1`): Indicates if the product is active (1 for active, 0 for inactive).

**Example Request Body**:
```json
{
  "name": "Wireless Headphones",
  "price": 99.99,
  "stock_quantity": 50,
  "category_id": 1,
  "description": "High-quality wireless headphones with noise cancellation.",
  "image_url": "https://example.com/images/headphones.jpg",
  "is_active": 1
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Product added successfully",
    "product_id": 123
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing required fields (`name`, `price`, or `stock_quantity`) or invalid input (negative `price` or `stock_quantity`).
    ```json
    {
      "error": "Name, price, and stock quantity are required"
    }
    ```
    ```json
    {
      "error": "Price and stock quantity must be non-negative"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when failing to add the product to the database.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 2. Get Product by ID
### Endpoint: `/products/<int:product_id>`
### Method: `GET`
### Description
Retrieves the details of a specific product by its ID. Only active products (`is_active = 1`) are returned. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `product_id` (integer): The ID of the product to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 123,
    "name": "Wireless Headphones",
    "description": "High-quality wireless headphones with noise cancellation.",
    "price": 99.99,
    "stock_quantity": 50,
    "category_id": 1,
    "image_url": "https://example.com/images/headphones.jpg",
    "is_active": 1,
    "created_at": "2025-06-16T12:05:00"
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Product with the specified ID does not exist or is inactive.
    ```json
    {
      "error": "Product not found or inactive"
    }
    ```
  - **HTTP 500**: Server error when retrieving the product.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 3. Get Products by Category
### Endpoint: `/products/category/<int:category_id>`
### Method: `GET`
### Description
Retrieves all active products (`is_active = 1`) for a specific category. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `category_id` (integer): The ID of the category whose products are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "products": [
      {
        "id": 123,
        "name": "Wireless Headphones",
        "description": "High-quality wireless headphones with noise cancellation.",
        "price": 99.99,
        "stock_quantity": 50,
        "category_id": 1,
        "image_url": "https://example.com/images/headphones.jpg",
        "is_active": 1,
        "created_at": "2025-06-16T12:05:00"
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "products": []
  }
  ```
- **Error Responses**:
  - **HTTP 500**: Server error when retrieving products.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 4. Update Product
### Endpoint: `/products/<int:product_id>`
### Method: `PUT`
### Description
Updates the details of an existing product. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `product_id` (integer): The ID of the product to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `name` (string): The updated name of the product.
    - `description` (string): The updated description of the product.
    - `price` (float): The updated price of the product.
    - `stock_quantity` (integer): The updated stock quantity.
    - `category_id` (integer): The updated category ID.
    - `image_url` (string): The updated URL of the product image.
    - `is_active` (integer): The updated active status (1 for active, 0 for inactive).

**Example Request Body**:
```json
{
  "name": "Wireless Headphones Pro",
  "price": 129.99,
  "stock_quantity": 30,
  "description": "Upgraded wireless headphones with enhanced noise cancellation."
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Product updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid input (negative `price` or `stock_quantity`) or failure to update the product.
    ```json
    {
      "error": "Price must be non-negative"
    }
    ```
    ```json
    {
      "error": "Stock quantity must be non-negative"
    }
    ```
    ```json
    {
      "error": "Failed to update product"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when updating the product.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 5. Delete Product
### Endpoint: `/products/<int:product_id>`
### Method: `DELETE`
### Description
Deletes a product by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `product_id` (integer): The ID of the product to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Product deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Product with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Product not found or failed to delete"
    }
    ```
  - **HTTP 500**: Server error when deleting the product.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 6. Get All Products
### Endpoint: `/products`
### Method: `GET`
### Description
Retrieves a paginated list of all active products (`is_active = 1`) in the system. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of products per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "products": [
      {
        "id": 123,
        "name": "Wireless Headphones",
        "description": "High-quality wireless headphones with noise cancellation.",
        "price": 99.99,
        "stock_quantity": 50,
        "category_id": 1,
        "image_url": "https://example.com/images/headphones.jpg",
        "is_active": 1,
        "created_at": "2025-06-16T12:05:00"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 500**: Server error when retrieving products.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `ProductManager` class.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` with a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and monitoring.
- The `created_at` field in responses is a timestamp indicating when the product was created (format: `YYYY-MM-DDTHH:MM:SS`).
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- Public endpoints (`/products/<int:product_id>` GET, `/products/category/<int:category_id>` GET, and `/products` GET) provide read-only access to active product data without requiring authentication.
- Only active products (`is_active = 1`) are returned in GET requests to ensure inactive products are not exposed.