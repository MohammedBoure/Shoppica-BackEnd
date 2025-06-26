# Products API Documentation

This document provides detailed information about the Products API endpoints implemented in the Flask Blueprint `products`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses. The API interacts with the `products` and `product_images` tables in a SQLite database via the `ProductManager` and `ProductImageManager` classes.

## Authentication
- Endpoints for adding (`POST /products`, `POST /products/<int:product_id>/images`), updating (`PUT /products/<int:product_id>`, `PUT /products/images/<int:image_id>`), deleting (`DELETE /products/<int:product_id>`, `DELETE /products/images/<int:image_id>`), and retrieving low stock products (`GET /products/low_stock`) require admin privileges, enforced by the `@admin_required` decorator, which checks for a valid `user_id` and `is_admin=True` in the session.
- Endpoints for retrieving a specific product (`GET /products/<int:product_id>`), products by category (`GET /products/category/<int:category_id>`), all products (`GET /products`), searching products (`GET /products/search`), a specific product image (`GET /products/images/<int:image_id>`), images by product (`GET /products/<int:product_id>/images`), all product images (`GET /product_images`), and total product count (`GET /products/number`) are publicly accessible without authentication.
- The `ProductManager` and `ProductImageManager` classes handle all database interactions for product and product image-related operations, respectively.

---

## 1. Add a New Product
### Endpoint: `/products`
### Method: `POST`
### Description
Creates a new product with an optional image upload. This endpoint is restricted to admin users only and uses `multipart/form-data` for file uploads.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Request Body)
- **Content-Type**: `multipart/form-data`
- **Required Fields**:
  - `name` (string): The name of the product.
  - `price` (float): The price of the product.
  - `purchase_price` (float): The purchase price of the product.
  - `stock_quantity` (integer): The available stock quantity.
- **Optional Fields**:
  - `category_id` (integer): The ID of the category the product belongs to.
  - `description` (string): A description of the product.
  - `image` (file): A primary product image (jpg, jpeg, png).
  - `is_active` (integer, default: `1`): Indicates if the product is active (1 for active, 0 for inactive).

**Example Request** (cURL):
```bash
curl -X POST http://localhost:5000/products \
  -H "Authorization: Bearer <admin_token>" \
  -F "name=Wireless Headphones" \
  -F "price=99.99" \
  -F "purchase_price=49.99" \
  -F "stock_quantity=50" \
  -F "category_id=1" \
  -F "description=High-quality wireless headphones with noise cancellation." \
  -F "image=@/path/to/headphones.jpg" \
  -F "is_active=1"
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
  - **HTTP 400**: Missing required fields, invalid input formats, negative values, invalid `is_active`, or invalid `category_id`.
    ```json
    {
      "error": "Name, price, purchase price and stock quantity are required",
      "error_code": "INVALID_INPUT"
    }
    ```
    ```json
    {
      "error": "Invalid price, purchase price or stock quantity",
      "error_code": "INVALID_TYPE"
    }
    ```
    ```json
    {
      "error": "Values must be non-negative",
      "error_code": "INVALID_VALUE"
    }
    ```
    ```json
    {
      "error": "is_active must be 0 or 1",
      "error_code": "INVALID_VALUE"
    }
    ```
    ```json
    {
      "error": "Invalid category ID",
      "error_code": "INVALID_CATEGORY"
    }
    ```
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized",
      "error_code": "UNAUTHORIZED"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required",
      "error_code": "FORBIDDEN"
    }
    ```
  - **HTTP 500**: Server error when adding the product.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductManager.add_product` to create the product.
- Validates `category_id` by checking the `categories` table.
- Image files are saved to `static/uploads/products/` with unique filenames.
- Only jpg, jpeg, and png formats are supported, validated by `ProductImageManager._allowed_file`.
- The `is_active` field is converted to a boolean for database storage.

---

## 2. Get Product by ID
### Endpoint: `/products/<int:product_id>`
### Method: `GET`
### Description
Retrieves the details of a specific active product (`is_active = True`) by its ID, including associated images. This endpoint is publicly accessible without authentication.

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
    "image_url": "/static/uploads/products/product_123_20250626_200900_abcdef12.jpg",
    "is_active": true,
    "created_at": "2025-06-26T20:09:00",
    "images": [
      {
        "id": 1,
        "image_url": "/static/uploads/products/image_1_20250626_201000_abcdef12.jpg",
        "created_at": "2025-06-26T20:10:00"
      }
    ]
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Product with the specified ID does not exist or is inactive.
    ```json
    {
      "error": "Product not found or inactive",
      "error_code": "NOT_FOUND"
    }
    ```
  - **HTTP 500**: Server error when retrieving the product.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductManager.get_product_by_id` with `joinedload(Product.images)` for efficient image retrieval.
- The `is_active` field is returned as a boolean.
- Timestamps are formatted in ISO 8601 (e.g., "2025-06-26T20:09:00").

---

## 3. Get Products by Category
### Endpoint: `/products/category/<int:category_id>`
### Method: `GET`
### Description
Retrieves all active products (`is_active = True`) for a specific category, including their associated images. This endpoint is publicly accessible without authentication.

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
        "image_url": "/static/uploads/products/product_123_20250626_200900_abcdef12.jpg",
        "is_active": true,
        "created_at": "2025-06-26T20:09:00",
        "images": [
          {
            "id": 1,
            "image_url": "/static/uploads/products/image_1_20250626_201000_abcdef12.jpg",
            "created_at": "2025-06-26T20:10:00"
          }
        ]
      }
    ],
    "message": "Products retrieved successfully"
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "products": [],
    "message": "No products found for this category"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid `category_id`.
    ```json
    {
      "error": "Invalid category ID",
      "error_code": "INVALID_CATEGORY"
    }
    ```
  - **HTTP 500**: Server error when retrieving products.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Validates `category_id` by checking the `categories` table.
- Uses `ProductManager` with `joinedload(Product.images)` for efficient image retrieval.
- Only active products are returned.

---

## 4. Update Product
### Endpoint: `/products/<int:product_id>`
### Method: `PUT`
### Description
Updates the details of an existing product with an optional image upload. This endpoint is restricted to admin users only and uses `multipart/form-data`.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `product_id` (integer): The ID of the product to update.
- **Request Body** (Content-Type: `multipart/form-data`):
  - **Optional Fields**:
    - `name` (string): The updated name of the product.
    - `description` (string): The updated description.
    - `price` (float): The updated price.
    - `purchase_price` (float): The updated purchase price.
    - `stock_quantity` (integer): The updated stock quantity.
    - `category_id` (integer): The updated category ID.
    - `image` (file): The updated primary product image (jpg, jpeg, png).
    - `is_active` (integer): The updated active status (1 for active, 0 for inactive).

**Example Request** (cURL):
```bash
curl -X PUT http://localhost:5000/products/123 \
  -H "Authorization: Bearer <admin_token>" \
  -F "name=Wireless Headphones Pro" \
  -F "price=129.99" \
  -F "purchase_price=69.99" \
  -F "stock_quantity=30" \
  -F "description=Upgraded wireless headphones with enhanced noise cancellation." \
  -F "image=@/path/to/headphones_updated.jpg"
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Product updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: No fields provided, invalid input formats, negative values, invalid `is_active`, or invalid `category_id`.
    ```json
    {
      "error": "At least one field must be provided",
      "error_code": "INVALID_INPUT"
    }
    ```
    ```json
    {
      "error": "Price must be non-negative",
      "error_code": "INVALID_VALUE"
    }
    ```
    ```json
    {
      "error": "Purchase price must be non-negative",
      "error_code": "INVALID_VALUE"
    }
    ```
    ```json
    {
      "error": "Stock quantity must be non-negative",
      "error_code": "INVALID_VALUE"
    }
    ```
    ```json
    {
      "error": "is_active must be 0 or 1",
      "error_code": "INVALID_VALUE"
    }
    ```
    ```json
    {
      "error": "Invalid category ID",
      "error_code": "INVALID_CATEGORY"
    }
    ```
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized",
      "error_code": "UNAUTHORIZED"
    }
    ```
  - **HTTP 403**: Admin privileges required.
    ```json
    {
      "error": "Admin privileges required",
      "error_code": "FORBIDDEN"
    }
    ```
  - **HTTP 404**: Product not found or failed to update.
    ```json
    {
      "error": "Product not found or failed to update",
      "error_code": "NOT_FOUND"
    }
    ```
  - **HTTP 500**: Server error when updating the product.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductManager.update_product` to update the product.
- At least one field must be provided for the update.
- If an image is uploaded, the existing image file (if any) is deleted.
- Validates `category_id` and ensures non-negative values.

---

## 5. Delete Product
### Endpoint: `/products/<int:product_id>`
### Method: `DELETE`
### Description
Deletes a product by its ID, including associated images in the `product_images` table and their files. This endpoint is restricted to admin users only.

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
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized",
      "error_code": "UNAUTHORIZED"
    }
    ```
  - **HTTP 403**: Admin privileges required.
    ```json
    {
      "error": "Admin privileges required",
      "error_code": "FORBIDDEN"
    }
    ```
  - **HTTP 404**: Product not found.
    ```json
    {
      "error": "Product not found",
      "error_code": "NOT_FOUND"
    }
    ```
  - **HTTP 500**: Server error when deleting the product.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductManager.delete_product` to delete the product.
- Deletes associated image files from `static/uploads/products/`.
- The `ON DELETE CASCADE` foreign key constraint ensures associated `product_images` entries are removed.

---

## 6. Get All Products
### Endpoint: `/products`
### Method: `GET`
### Description
Retrieves a paginated list of all active products (`is_active = True`), including their associated images. This endpoint is publicly accessible without authentication.

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
        "image_url": "/static/uploads/products/product_123_20250626_200900_abcdef12.jpg",
        "is_active": true,
        "created_at": "2025-06-26T20:09:00",
        "images": [
          {
            "id": 1,
            "image_url": "/static/uploads/products/image_1_20250626_201000_abcdef12.jpg",
            "created_at": "2025-06-26T20:10:00"
          }
        ]
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20,
    "message": "Products retrieved successfully"
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "products": [],
    "total": 0,
    "page": 1,
    "per_page": 20,
    "message": "No products found"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid pagination parameters.
    ```json
    {
      "error": "Page and per_page must be positive integers",
      "error_code": "INVALID_INPUT"
    }
    ```
  - **HTTP 500**: Server error when retrieving products.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductManager.get_products` with `joinedload(Product.images)` for efficient retrieval.
- Only active products are returned, ordered by `created_at` descending.

---

## 7. Search Products
### Endpoint: `/products/search`
### Method: `GET`
### Description
Searches active products (`is_active = True`) by name with pagination, including their associated images. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (Query Parameters)
- `search_term` (string, required): The term to search for in product names (case-insensitive partial match).
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
        "image_url": "/static/uploads/products/product_123_20250626_200900_abcdef12.jpg",
        "is_active": true,
        "created_at": "2025-06-26T20:09:00",
        "images": [
          {
            "id": 1,
            "image_url": "/static/uploads/products/image_1_20250626_201000_abcdef12.jpg",
            "created_at": "2025-06-26T20:10:00"
          }
        ]
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20,
    "message": "Products retrieved successfully"
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "products": [],
    "total": 0,
    "page": 1,
    "per_page": 20,
    "message": "No products found for this search term"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing search term or invalid pagination parameters.
    ```json
    {
      "error": "Search term is required",
      "error_code": "INVALID_INPUT"
    }
    ```
    ```json
    {
      "error": "Page and per_page must be positive integers",
      "error_code": "INVALID_INPUT"
    }
    ```
  - **HTTP 500**: Server error when searching products.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductManager.search_products` with `joinedload(Product.images)` for efficient retrieval.
- Searches are case-insensitive using `ilike` on the `name` field.

---

## 8. Get Total Products
### Endpoint: `/products/number`
### Method: `GET`
### Description
Retrieves the total number of products in the database. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "total_products": 50,
    "message": "Total products count retrieved successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 500**: Server error when retrieving the total count.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductManager.get_total_products` to fetch the total count.

---

## 9. Get Low Stock Products
### Endpoint: `/products/low_stock`
### Method: `GET`
### Description
Retrieves a list of products with stock quantities below their low stock threshold. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "status": "success",
    "message": "3 low stock products found.",
    "data": [
      {
        "id": 123,
        "name": "Wireless Headphones",
        "stock_quantity": 5,
        "low_stock_threshold": 10,
        "category_id": 1,
        "price": 99.99,
        "image_url": "/static/uploads/products/product_123_20250626_200900_abcdef12.jpg"
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "status": "success",
    "message": "0 low stock products found.",
    "data": []
  }
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized",
      "error_code": "UNAUTHORIZED"
    }
    ```
  - **HTTP 403**: Admin privileges required.
    ```json
    {
      "error": "Admin privileges required",
      "error_code": "FORBIDDEN"
    }
    ```
  - **HTTP 500**: Server error when retrieving low stock products.
    ```json
    {
      "status": "error",
      "message": "Failed to retrieve low stock products."
    }
    ```

**Notes**:
- Uses `ProductManager.get_low_stock_products` to fetch products where `stock_quantity` is below `low_stock_threshold`.

---

## 10. Add a Product Image
### Endpoint: `/products/<int:product_id>/images`
### Method: `POST`
### Description
Adds a new image for a specific active product via file upload. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `product_id` (integer): The ID of the product to associate the image with.
- **Request Body** (Content-Type: `multipart/form-data`):
  - **Required Fields**:
    - `image` (file): The product image (jpg, jpeg, png).

**Example Request** (cURL):
```bash
curl -X POST http://localhost:5000/products/123/images \
  -H "Authorization: Bearer <admin_token>" \
  -F "image=@/path/to/headphones_side.jpg"
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Product image added successfully",
    "image_id": 1
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing or invalid image file.
    ```json
    {
      "error": "Image file is required",
      "error_code": "INVALID_INPUT"
    }
    ```
    ```json
    {
      "error": "Invalid image file. Allowed extensions: jpg, jpeg, png",
      "error_code": "INVALID_FILE"
    }
    ```
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized",
      "error_code": "UNAUTHORIZED"
    }
    ```
  - **HTTP 403**: Admin privileges required.
    ```json
    {
      "error": "Admin privileges required",
      "error_code": "FORBIDDEN"
    }
    ```
  - **HTTP 404**: Product not found or inactive.
    ```json
    {
      "error": "Product not found or inactive",
      "error_code": "NOT_FOUND"
    }
    ```
  - **HTTP 500**: Server error when adding the image.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductImageManager.add_product_image` to add the image.
- Validates that the product exists and is active.

---

## 11. Get Product Image by ID
### Endpoint: `/products/images/<int:image_id>`
### Method: `GET`
### Description
Retrieves the details of a specific product image by its ID. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `image_id` (integer): The ID of the product image to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 1,
    "product_id": 123,
    "image_url": "/static/uploads/products/image_1_20250626_201000_abcdef12.jpg",
    "created_at": "2025-06-26T20:10:00"
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Product image not found.
    ```json
    {
      "error": "Product image not found",
      "error_code": "NOT_FOUND"
    }
    ```
  - **HTTP 500**: Server error when retrieving the image.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductImageManager.get_product_image_by_id` to fetch the image.

---

## 12. Get Images by Product
### Endpoint: `/products/<int:product_id>/images`
### Method: `GET`
### Description
Retrieves all images associated with a specific product. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `product_id` (integer): The ID of the product whose images are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "images": [
      {
        "id": 1,
        "product_id": 123,
        "image_url": "/static/uploads/products/image_1_20250626_201000_abcdef12.jpg",
        "created_at": "2025-06-26T20:10:00"
      }
    ],
    "message": "Images retrieved successfully"
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "images": [],
    "message": "No images found for this product"
  }
  ```
- **Error Responses**:
  - **HTTP 500**: Server error when retrieving images.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductImageManager.get_images_by_product` to fetch images.

---

## 13. Update Product Image
### Endpoint: `/products/images/<int:image_id>`
### Method: `PUT`
### Description
Updates an existing product image via file upload. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `image_id` (integer): The ID of the product image to update.
- **Request Body** (Content-Type: `multipart/form-data`):
  - **Required Fields**:
    - `image` (file): The updated product image (jpg, jpeg, png).

**Example Request** (cURL):
```bash
curl -X PUT http://localhost:5000/products/images/1 \
  -H "Authorization: Bearer <admin_token>" \
  -F "image=@/path/to/headphones_side_updated.jpg"
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Product image updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing or invalid image file.
    ```json
    {
      "error": "Image file is required",
      "error_code": "INVALID_INPUT"
    }
    ```
    ```json
    {
      "error": "Invalid image file. Allowed extensions: jpg, jpeg, png",
      "error_code": "INVALID_FILE"
    }
    ```
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized",
      "error_code": "UNAUTHORIZED"
    }
    ```
  - **HTTP 403**: Admin privileges required.
    ```json
    {
      "error": "Admin privileges required",
      "error_code": "FORBIDDEN"
    }
    ```
  - **HTTP 404**: Product image not found.
    ```json
    {
      "error": "Product image not found",
      "error_code": "NOT_FOUND"
    }
    ```
  - **HTTP 500**: Server error when updating the image.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductImageManager.update_product_image` to update the image.
- The existing image file is deleted before saving the new one.

---

## 14. Delete Product Image
### Endpoint: `/products/images/<int:image_id>`
### Method: `DELETE`
### Description
Deletes a product image by its ID, including the associated file. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `image_id` (integer): The ID of the product image to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Product image deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized",
      "error_code": "UNAUTHORIZED"
    }
    ```
  - **HTTP 403**: Admin privileges required.
    ```json
    {
      "error": "Admin privileges required",
      "error_code": "FORBIDDEN"
    }
    ```
  - **HTTP 404**: Product image not found.
    ```json
    {
      "error": "Product image not found",
      "error_code": "NOT_FOUND"
    }
    ```
  - **HTTP 500**: Server error when deleting the image.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductImageManager.delete_product_image` to delete the image.
- The associated image file is deleted from `static/uploads/products/`.

---

## 15. Get All Product Images
### Endpoint: `/product_images`
### Method: `GET`
### Description
Retrieves a paginated list of all product images. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of images per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "images": [
      {
        "id": 1,
        "product_id": 123,
        "image_url": "/static/uploads/products/image_1_20250626_201000_abcdef12.jpg",
        "created_at": "2025-06-26T20:10:00"
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20,
    "message": "Images retrieved successfully"
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "images": [],
    "total": 0,
    "page": 1,
    "per_page": 20,
    "message": "No images found"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid pagination parameters.
    ```json
    {
      "error": "Page and per_page must be positive integers",
      "error_code": "INVALID_INPUT"
    }
    ```
  - **HTTP 500**: Server error when retrieving images.
    ```json
    {
      "error": "Database error",
      "error_code": "DATABASE_ERROR"
    }
    ```
    ```json
    {
      "error": "Internal server error",
      "error_code": "INTERNAL_ERROR"
    }
    ```

**Notes**:
- Uses `ProductImageManager.get_product_images` for paginated retrieval.

---

## Notes
- All endpoints use `ProductManager` or `ProductImageManager` for database interactions.
- Logging is configured with a dedicated logger (`logging.getLogger(__name__)`) for debugging and monitoring.
- The `created_at` field is returned in ISO 8601 format (e.g., "2025-06-26T20:09:00").
- Error responses include an `error_code` for programmatic handling (e.g., `INVALID_INPUT`, `NOT_FOUND`).
- Public endpoints only return active products (`is_active = True`).
- The `product_images` table has an `ON DELETE CASCADE` foreign key constraint with `products`.
- Image files are stored in `static/uploads/products/` with unique filenames.
- Supported image extensions are jpg, jpeg, and png, validated by `ProductImageManager._allowed_file`.
- SQLite foreign key support is assumed to be enabled (e.g., via `PRAGMA foreign_keys = ON`).
- The `/products/low_stock` endpoint uses a `low_stock_threshold` field in the `products` table to identify low stock products.