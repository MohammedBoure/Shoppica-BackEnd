# Products API Documentation

This document provides detailed information about the Products API endpoints defined in `admin_apis/products.py`. These endpoints manage products in an e-commerce platform, including adding, retrieving, updating, and deleting products. Authentication and authorization are enforced using JWT (JSON Web Tokens) with specific roles (`@admin_required` for admin-only operations).

## Base URL
All endpoints are prefixed with `/api`. For example, `/products` is accessed as `/api/products`.

## Authentication
- **JWT Token**: Required for endpoints marked with `@admin_required`. Include the token in the `Authorization` header as `Bearer <token>`.
- **Admin Privileges**: Endpoints marked with `@admin_required` (`POST /api/products`, `PUT /api/products/<product_id>`, `DELETE /api/products/<product_id>`) require a JWT token with `is_admin: true`.
- **Public Access**: Endpoints `GET /api/products`, `GET /api/products/<product_id>`, and `GET /api/products/category/<category_id>` are publicly accessible without authentication, but only return active products (`is_active: 1`).

## Endpoints

### 1. Add Product
- **Endpoint**: `POST /api/products`
- **Description**: Adds a new product to the platform (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "name": <string>,            // Required: Name of the product
    "price": <float>,            // Required: Price of the product
    "stock_quantity": <integer>, // Required: Available stock quantity
    "category_id": <integer>,    // Optional: ID of the product category
    "description": <string>,     // Optional: Product description
    "image_url": <string>,       // Optional: URL of the product image
    "is_active": <integer>       // Optional: 1 (active) or 0 (inactive), default: 1
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {
      "message": "Product added successfully",
      "product_id": <integer>
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Name, price, and stock quantity are required"
    }
    ```
    or
    ```json
    {
      "error": "Price and stock quantity must be non-negative"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
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

### 2. Get Product by ID
- **Endpoint**: `GET /api/products/<product_id>`
- **Description**: Retrieves a product by its ID. Only active products are returned. Publicly accessible.
- **Authorization**: None (public access).
- **Input**: URL parameter `product_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "name": <string>,
      "description": <string>,
      "price": <float>,
      "stock_quantity": <integer>,
      "category_id": <integer>,
      "image_url": <string>,
      "is_active": <integer>,
      "created_at": <string>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Product not found or inactive"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```

### 3. Get Products by Category
- **Endpoint**: `GET /api/products/category/<category_id>`
- **Description**: Retrieves all active products in a specific category. Publicly accessible.
- **Authorization**: None (public access).
- **Input**: URL parameter `category_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "products": [
        {
          "id": <integer>,
          "name": <string>,
          "description": <string>,
          "price": <float>,
          "stock_quantity": <integer>,
          "category_id": <integer>,
          "image_url": <string>,
          "is_active": <integer>,
          "created_at": <string>
        },
        ...
      ]
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```

### 4. Update Product
- **Endpoint**: `PUT /api/products/<product_id>`
- **Description**: Updates a product’s details (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "name": <string>,            // Optional: Name of the product
    "description": <string>,     // Optional: Product description
    "price": <float>,            // Optional: Price of the product
    "stock_quantity": <integer>, // Optional: Available stock quantity
    "category_id": <integer>,    // Optional: ID of the product category
    "image_url": <string>,       // Optional: URL of the product image
    "is_active": <integer>       // Optional: 1 (active) or 0 (inactive)
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Product updated successfully"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Price must be non-negative"
    }
    ```
    or
    ```json
    {
      "error": "Stock quantity must be non-negative"
    }
    ```
    or
    ```json
    {
      "error": "Failed to update product"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
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

### 5. Delete Product
- **Endpoint**: `DELETE /api/products/<product_id>`
- **Description**: Deletes a product by ID (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `product_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Product deleted successfully"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Product not found or failed to delete"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
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

### 6. Get All Products (Paginated)
- **Endpoint**: `GET /api/products?page=<page>&per_page=<per_page>`
- **Description**: Retrieves a paginated list of all active products. Publicly accessible.
- **Authorization**: None (public access).
- **Input**:
  - Query parameters:
    - `page` (integer, default: 1)
    - `per_page` (integer, default: 20)
- **Output**:
  - **Success (200)**:
    ```json
    {
      "products": [
        {
          "id": <integer>,
          "name": <string>,
          "description": <string>,
          "price": <float>,
          "stock_quantity": <integer>,
          "category_id": <integer>,
          "image_url": <string>,
          "is_active": <integer>,
          "created_at": <string>
        },
        ...
      ],
      "total": <integer>,
      "page": <integer>,
      "per_page": <integer>
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Internal server error"
    }
    ```

## Example Usage
### Obtaining a JWT Token (for Admin Operations)
Authenticate via the login endpoint (assumed to be `/api/login`) using an admin account:
```bash
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"adminpassword"}'
```
Response:
```json
{
  "access_token": "<admin_jwt_token>"
}
```

### Adding a Product (Admin Only)
```bash
curl -X POST http://localhost:5000/api/products -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"name":"Sample Product","price":19.99,"stock_quantity":100,"category_id":1,"description":"A sample product description","image_url":"https://example.com/image.jpg","is_active":1}'
```
Response:
```json
{
  "message": "Product added successfully",
  "product_id": 1
}
```

### Getting a Product by ID (Public)
```bash
curl -X GET http://localhost:5000/api/products/1
```
Response:
```json
{
  "id": 1,
  "name": "Sample Product",
  "description": "A sample product description",
  "price": 19.99,
  "stock_quantity": 100,
  "category_id": 1,
  "image_url": "https://example.com/image.jpg",
  "is_active": 1,
  "created_at": "2025-05-23T22:00:00Z"
}
```

### Getting Products by Category (Public)
```bash
curl -X GET http://localhost:5000/api/products/category/1
```
Response:
```json
{
  "products": [
    {
      "id": 1,
      "name": "Sample Product",
      "description": "A sample product description",
      "price": 19.99,
      "stock_quantity": 100,
      "category_id": 1,
      "image_url": "https://example.com/image.jpg",
      "is_active": 1,
      "created_at": "2025-05-23T22:00:00Z"
    }
  ]
}
```

### Updating a Product (Admin Only)
```bash
curl -X PUT http://localhost:5000/api/products/1 -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"name":"Updated Product","price":29.99,"stock_quantity":90,"description":"Updated description","image_url":"https://example.com/updated_image.jpg","is_active":1}'
```
Response:
```json
{
  "message": "Product updated successfully"
}
```

### Deleting a Product (Admin Only)
```bash
curl -X DELETE http://localhost:5000/api/products/1 -H "Authorization: Bearer <admin_token>"
```
Response:
```json
{
  "message": "Product deleted successfully"
}
```

### Getting All Products (Public)
```bash
curl -X GET http://localhost:5000/api/products?page=1&per_page=20
```
Response:
```json
{
  "products": [
    {
      "id": 1,
      "name": "Updated Product",
      "description": "Updated description",
      "price": 29.99,
      "stock_quantity": 90,
      "category_id": 1,
      "image_url": "https://example.com/updated_image.jpg",
      "is_active": 1,
      "created_at": "2025-05-23T22:00:00Z"
    },
    ...
  ],
  "total": 10,
  "page": 1,
  "per_page": 20
}
```

## Notes
- **Database Manager**: The API relies on `ProductManager` for database operations.
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages. Errors are logged for debugging using a custom logger.
- **Security**:
  - Admin endpoints (`POST /api/products`, `PUT /api/products/<product_id>`, `DELETE /api/products/<product_id>`) require a valid JWT with admin privileges.
  - Public endpoints (`GET /api/products`, `GET /api/products/<product_id>`, `GET /api/products/category/<category_id>`) only return active products (`is_active: 1`) to ensure customers only see available products.
- **Data Validation**:
  - Ensures required fields (`name`, `price`, `stock_quantity`) are provided when adding a product.
  - Validates that `price` and `stock_quantity` are non-negative for both adding and updating products.
- **Product Fields**: The `created_at` field is assumed to be returned in ISO 8601 format (e.g., "2025-05-23T22:00:00Z").
- **Testing**: Unit tests can be created in `test/test_products.py` to verify functionality.

For further details, refer to the source code in `admin_apis/products.py`.