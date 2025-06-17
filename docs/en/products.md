# Products API Documentation

This document provides detailed information about the Products API endpoints implemented in the Flask Blueprint `products`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /products`, `POST /products/<int:product_id>/images`), updating (`PUT /products/<int:product_id>`, `PUT /products/images/<int:image_id>`), and deleting (`DELETE /products/<int:product_id>`, `DELETE /products/images/<int:image_id>`) products or product images require admin privileges, enforced by the `@admin_required` decorator.
- The `/products/<int:product_id>` GET, `/products/category/<int:category_id>` GET, `/products` GET, `/products/images/<int:image_id>` GET, `/products/<int:product_id>/images` GET, and `/product_images` GET endpoints do not require authentication, allowing public access to product and image data.
- The `ProductManager` and `ProductImageManager` classes handle all database interactions for product and product image-related operations, respectively.

---

## 1. Add a New Product
### Endpoint: `/products`
### Method: `POST`
### Description
Creates a new product in the system with an optional image upload. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Request Body)
- **Content-Type**: `multipart/form-data`
- **Required Fields**:
  - `name` (string): The name of the product.
  - `price` (float): The price of the product.
  - `stock_quantity` (integer): The available stock quantity.
- **Optional Fields**:
  - `category_id` (integer): The ID of the category the product belongs to.
  - `description` (string): A description of the product.
  - `image` (file): A primary product image (jpg, jpeg, png, or gif).
  - `is_active` (integer, default: `1`): Indicates if the product is active (1 for active, 0 for inactive).

**Example Request** (cURL):
```bash
curl -X POST http://localhost:5000/products \
  -H "Authorization: Bearer <admin_token>" \
  -F "name=Wireless Headphones" \
  -F "price=99.99" \
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
  - **HTTP 400**: Missing required fields (`name`, `price`, or `stock_quantity`) or invalid inputs (negative `price` or `stock_quantity`, invalid number formats, or invalid image file).
    ```json
    {
      "error": "Name, price, and stock quantity are required"
    }
    ```
    ```json
    {
      "error": "Price and stock quantity must be valid numbers"
    }
    ```
    ```json
    {
      "error": "Price and stock quantity must be non-negative"
    }
    ```
    ```json
    {
      "error": "Invalid or missing image file. Allowed extensions: jpg, jpeg, png, gif"
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
Retrieves the details of a specific product by its ID, including associated images. Only active products (`is_active = 1`) are returned. This endpoint is publicly accessible without authentication.

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
    "image_url": "uploads/products/product_123_20250617_180500_abcdef12.jpg",
    "is_active": 1,
    "created_at": "2025-06-17T18:05:00",
    "images": [
      {
        "id": 1,
        "image_url": "uploads/products/image_1_20250617_180600_abcdef12.jpg",
        "created_at": "2025-06-17T18:06:00"
      },
      {
        "id": 2,
        "image_url": "uploads/products/image_2_20250617_180700_abcdef34.jpg",
        "created_at": "2025-06-17T18:07:00"
      }
    ]
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
Retrieves all active products (`is_active = 1`) for a specific category, including their associated images. This endpoint is publicly accessible without authentication.

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
        "image_url": "uploads/products/product_123_20250617_180500_abcdef12.jpg",
        "is_active": 1,
        "created_at": "2025-06-17T18:05:00",
        "images": [
          {
            "id": 1,
            "image_url": "uploads/products/image_1_20250617_180600_abcdef12.jpg",
            "created_at": "2025-06-17T18:06:00"
          }
        ]
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
Updates the details of an existing product with an optional image upload. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `product_id` (integer): The ID of the product to update.
- **Request Body** (Content-Type: `multipart/form-data`):
  - **Optional Fields**:
    - `name` (string): The updated name of the product.
    - `description` (string): The updated description of the product.
    - `price` (float): The updated price of the product.
    - `stock_quantity` (integer): The updated stock quantity.
    - `category_id` (integer): The updated category ID.
    - `image` (file): The updated primary product image (jpg, jpeg, png, or gif).
    - `is_active` (integer): The updated active status (1 for active, 0 for inactive).

**Example Request** (cURL):
```bash
curl -X PUT http://localhost:5000/products/123 \
  -H "Authorization: Bearer <admin_token>" \
  -F "name=Wireless Headphones Pro" \
  -F "price=129.99" \
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
  - **HTTP 400**: Invalid input (negative `price` or `stock_quantity`, invalid number formats, or invalid image file) or failure to update the product.
    ```json
    {
      "error": "Price must be a valid number"
    }
    ```
    ```json
    {
      "error": "Stock quantity must be a valid integer"
    }
    ```
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
      "error": "Invalid or missing image file. Allowed extensions: jpg, jpeg, png, gif"
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
Deletes a product by its ID. Associated images in the `product_images` table are automatically deleted due to the `ON DELETE CASCADE` foreign key constraint. This endpoint is restricted to admin users only.

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
Retrieves a paginated list of all active products (`is_active = 1`) in the system, including their associated images. This endpoint is publicly accessible without authentication.

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
        "image_url": "uploads/products/product_123_20250617_180500_abcdef12.jpg",
        "is_active": 1,
        "created_at": "2025-06-17T18:05:00",
        "images": [
          {
            "id": 1,
            "image_url": "uploads/products/image_1_20250617_180600_abcdef12.jpg",
            "created_at": "2025-06-17T18:06:00"
          }
        ]
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

## 7. Add a Product Image
### Endpoint: `/products/<int:product_id>/images`
### Method: `POST`
### Description
Adds a new image for a specific product via file upload. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `product_id` (integer): The ID of the product to associate the image with.
- **Request Body** (Content-Type: `multipart/form-data`):
  - **Required Fields**:
    - `image` (file): The product image (jpg, jpeg, png, or gif).

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
  - **HTTP 400**: Missing required field (`image`) or invalid image file.
    ```json
    {
      "error": "Image file is required"
    }
    ```
    ```json
    {
      "error": "Invalid image file. Allowed extensions: jpg, jpeg, png, gif"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when failing to add the product image.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 8. Get Product Image by ID
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
    "image_url": "uploads/products/image_1_20250617_180600_abcdef12.jpg",
    "created_at": "2025-06-17T18:06:00"
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Product image with the specified ID does not exist.
    ```json
    {
      "error": "Product image not found"
    }
    ```
  - **HTTP 500**: Server error when retrieving the product image.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 9. Get Images by Product
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
        "image_url": "uploads/products/image_1_20250617_180600_abcdef12.jpg",
        "created_at": "2025-06-17T18:06:00"
      },
      {
        "id": 2,
        "product_id": 123,
        "image_url": "uploads/products/image_2_20250617_180700_abcdef34.jpg",
        "created_at": "2025-06-17T18:07:00"
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "images": []
  }
  ```
- **Error Responses**:
  - **HTTP 500**: Server error when retrieving product images.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 10. Update Product Image
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
    - `image` (file): The updated product image (jpg, jpeg, png, or gif).

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
  - **HTTP 400**: Missing required field (`image`) or invalid image file.
    ```json
    {
      "error": "Image file is required"
    }
    ```
    ```json
    {
      "error": "Invalid image file. Allowed extensions: jpg, jpeg, png, gif"
    }
    ```
    ```json
    {
      "error": "Failed to update product image"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when updating the product image.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 11. Delete Product Image
### Endpoint: `/products/images/<int:image_id>`
### Method: `DELETE`
### Description
Deletes a product image by its ID. This endpoint is restricted to admin users only.

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
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Product image with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Product image not found or failed to delete"
    }
    ```
  - **HTTP 500**: Server error when deleting the product image.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## 12. Get All Product Images
### Endpoint: `/product_images`
### Method: `GET`
### Description
Retrieves a paginated list of all product images in the system. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of product images per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "images": [
      {
        "id": 1,
        "product_id": 123,
        "image_url": "uploads/products/image_1_20250617_180600_abcdef12.jpg",
        "created_at": "2025-06-17T18:06:00"
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 500**: Server error when retrieving product images.
    ```json
    {
      "error": "Internal server error"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `ProductManager` and `ProductImageManager` classes.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` with a dedicated logger (`logger = logging.getLogger(__name__)`) for debugging and monitoring.
- The `created_at` field in responses is a timestamp indicating when the product or image was created (format: `YYYY-MM-DDTHH:MM:SS`).
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- Public endpoints (`/products/<int:product_id>` GET, `/products/category/<int:category_id>` GET, `/products` GET, `/products/images/<int:image_id>` GET, `/products/<int:product_id>/images` GET, and `/product_images` GET) provide read-only access to active product and image data without requiring authentication.
- Only active products (`is_active = 1`) are returned in product-related GET requests to ensure inactive products are not exposed.
- The `product_images` table has a foreign key constraint (`ON DELETE CASCADE`) with the `products` table, ensuring that deleting a product automatically removes its associated images.
- Image uploads are saved to the `static/uploads/products` directory (`UPLOAD_FOLDER`) with unique filenames generated using a prefix, identifier, timestamp, and random string.
- Supported image extensions are jpg, jpeg, png, and gif (`ALLOWED_EXTENSIONS`).
- Uploaded images are renamed post-insertion to include the actual `product_id` or `image_id` for consistency.