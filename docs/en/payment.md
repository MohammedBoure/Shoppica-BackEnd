# Products API Documentation

This document provides detailed information about the Products API endpoints defined in `admin_apis/products.py`. These endpoints manage products in an e-commerce platform, including adding, retrieving, updating, and deleting products. Authentication and authorization are enforced using JWT (JSON Web Tokens) with specific roles (`@admin_required` for admin-only operations).

## Base URL
All endpoints are prefixed with `/api`. For example, `/products` is accessed as `/api/products`.

## Authentication
- **JWT Token**: Required for endpoints marked with `@admin_required`. Include the token in the `Authorization` header as `Bearer <token>`.
- **Admin Privileges**: Endpoints marked with `@admin_required` require a JWT token with `is_admin: true`.
- **Public Access**: Endpoints without authentication (`GET /products`, `GET /products/<product_id>`, `GET /products/category/<category_id>`) are accessible to everyone but only return active products (`is_active: 1`).

## Endpoints

### 1. Add Product
- **Endpoint**: `POST /api/products`
- **Description**: Adds a new product to the catalog (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "name": <string>,              // Required: Product name
    "price": <float>,              // Required: Product price
    "stock_quantity": <integer>,   // Required: Available stock
    "category_id": <integer>,      // Optional: Category ID
    "description": <string>,       // Optional: Product description
    "image_url": <string>,         // Optional: URL of product image
    "is_active": <integer>         // Optional: 1 (active) or 0 (inactive), default: 1
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

### 2. Get Product by ID
- **Endpoint**: `GET /api/products/<product_id>`
- **Description**: Retrieves a product by its ID. Only active products are returned.
- **Authorization**: Public access (no JWT required).
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
- **Description**: Retrieves all active products in a specific category.
- **Authorization**: Public access (no JWT required).
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
    "name": <string>,              // Optional: Product name
    "description": <string>,       // Optional: Product description
    "price": <float>,              // Optional: Product price
    "stock_quantity": <integer>,   // Optional: Available stock
    "category_id": <integer>,      // Optional: Category ID
    "image_url": <string>,         // Optional: URL of product image
    "is_active": <integer>         // Optional: 1 (active) or 0 (inactive)
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
      "error": "Failed to update product"
    }
    ```
    or
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

### 6. Get All Products (Paginated)
- **Endpoint**: `GET /api/products?page=<page>&per_page=<per_page>`
- **Description**: Retrieves a paginated list of all active products.
- **Authorization**: Public access (no JWT required).
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

### Adding a Product (Admin)
```bash
curl -X POST http://localhost:5000/api/products -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"name":"Laptop","price":999.99,"stock_quantity":10,"category_id":1,"description":"High-end laptop","image_url":"http://example.com/laptop.jpg"}'
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
  "name": "Laptop",
  "description": "High-end laptop",
  "price": 999.99,
  "stock_quantity": 10,
  "category_id": 1,
  "image_url": "http://example.com/laptop.jpg",
  "is_active": 1,
  "created_at": "2025-05-23T14:18:00Z"
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
      "name": "Laptop",
      "description": "High-end laptop",
      "price": 999.99,
      "stock_quantity": 10,
      "category_id": 1,
      "image_url": "http://example.com/laptop.jpg",
      "is_active": 1,
      "created_at": "2025-05-23T14:18:00Z"
    }
  ]
}
```

## Notes
- **Database Manager**: The API relies on `ProductManager` for database operations.
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages. Errors are logged for debugging.
- **Security**: Only active products (`is_active: 1`) are returned in public endpoints. Admin endpoints require a valid JWT with admin privileges.
- **Testing**: Unit tests are available in `test/test_products.py` to verify functionality.
- **Data Validation**: Price and stock quantity are validated to be non-negative in `POST` and `PUT` endpoints.

For further details, refer to the source code in `admin_apis/products.py`.