# Categories API Documentation

This document provides detailed information about the Categories API endpoints implemented in the Flask Blueprint `categories`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses. The API interacts with the `categories` table in a SQLite database via the `CategoryManager` class.

## Authentication
- Endpoints for adding (`POST /categories`), updating (`PUT /categories/<int:category_id>`), and deleting (`DELETE /categories/<int:category_id>`) categories require admin privileges, enforced by the `@admin_required` decorator, which checks for a valid `user_id` and `is_admin=True` in the session.
- Endpoints for retrieving a specific category (`GET /categories/<int:category_id>`), retrieving categories by parent (`GET /categories/parent`), retrieving all categories (`GET /categories`), and searching categories (`GET /categories/search`) are publicly accessible without authentication.
- The `CategoryManager` class handles all database interactions for category-related operations.

---

## 1. Add a New Category
### Endpoint: `/categories`
### Method: `POST`
### Description
Creates a new category with an optional image upload or image URL. This endpoint is restricted to admin users only and uses `multipart/form-data` for file uploads.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Request Body)
- **Content-Type**: `multipart/form-data`
- **Required Fields**:
  - `name` (string): The name of the category.
- **Optional Fields**:
  - `parent_id` (integer): The ID of the parent category (null for top-level categories).
  - `image_url` (string): A URL to an image for the category (used if no image file is provided).
  - `image` (file): An image file (PNG, JPG, or JPEG) to upload for the category.

**Example Request** (using `multipart/form-data`):
- Form fields:
  - `name`: "Electronics"
  - `parent_id`: null
  - `image_url`: "" (optional, fallback if no image file)
  - `image`: (file upload, e.g., `electronics.jpg`)

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Category added successfully",
    "category_id": 123
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing required field (`name`) or invalid image file.
    ```json
    {
      "error": "Category name is required"
    }
    ```
    ```json
    {
      "error": "Invalid image file"
    }
    ```
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 500**: Server error when failing to add the category to the database.
    ```json
    {
      "error": "Failed to add category"
    }
    ```

**Notes**:
- Uses `CategoryManager.add_category` to create the category.
- Image files are saved to `static/uploads/categories/` with a unique filename generated using UUID.
- Only PNG, JPG, and JPEG image formats are allowed, validated by the `allowed_file` function.
- If an image file is provided, it takes precedence over `image_url`.

---

## 2. Get Category by ID
### Endpoint: `/categories/<int:category_id>`
### Method: `GET`
### Description
Retrieves the details of a specific category by its ID. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (URL Parameters)
- `category_id` (integer): The ID of the category to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 123,
    "name": "Electronics",
    "parent_id": null,
    "image_url": "/static/uploads/categories/abc123.jpg"
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Category with the specified ID does not exist.
    ```json
    {
      "error": "Category not found"
    }
    ```

**Notes**:
- Uses `CategoryManager.get_category_by_id` to fetch the category.
- The `image_url` field may be empty or null if no image is associated with the category.

---

## 3. Get Categories by Parent
### Endpoint: `/categories/parent`
### Method: `GET`
### Description
Retrieves all categories with a specified parent ID (or top-level categories if no `parent_id` is provided). This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (Query Parameters)
- `parent_id` (integer, optional): The ID of the parent category (omit or set to null for top-level categories).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "categories": [
      {
        "id": 123,
        "name": "Electronics",
        "parent_id": null,
        "image_url": "/static/uploads/categories/abc123.jpg"
      }
    ],
    "message": "Categories retrieved successfully"
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "categories": [],
    "message": "No categories found for this parent"
  }
  ```

**Notes**:
- Uses `CategoryManager.get_categories_by_parent` to fetch categories.
- The `message` field provides context for empty results.

---

## 4. Update Category
### Endpoint: `/categories/<int:category_id>`
### Method: `PUT`
### Description
Updates the details of an existing category with optional image upload or image URL. This endpoint is restricted to admin users only and uses `multipart/form-data` for file uploads.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `category_id` (integer): The ID of the category to update.
- **Request Body** (Content-Type: `multipart/form-data`):
  - **Optional Fields**:
    - `name` (string): The updated name of the category.
    - `parent_id` (integer): The updated parent category ID (null for top-level categories).
    - `image_url` (string): The updated image URL (used if no image file is provided).
    - `image` (file): An updated image file (PNG, JPG, or JPEG) to upload for the category.

**Example Request** (using `multipart/form-data`):
- Form fields:
  - `name`: "Updated Electronics"
  - `parent_id`: 456
  - `image_url`: "" (optional, fallback if no image file)
  - `image`: (file upload, e.g., `updated_electronics.jpg`)

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Category updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: No valid fields provided or invalid image file.
    ```json
    {
      "error": "At least one field (name, parent_id, image_url, or image) must be provided"
    }
    ```
    ```json
    {
      "error": "Invalid image file"
    }
    ```
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Category with the specified ID does not exist or failed to update.
    ```json
    {
      "error": "Category not found or failed to update"
    }
    ```

**Notes**:
- Uses `CategoryManager.update_category` to update the category.
- At least one field (`name`, `parent_id`, `image_url`, or `image`) must be provided.
- Image files are saved to `static/uploads/categories/` with a unique filename, and `image_url` is updated if an image is uploaded.

---

## 5. Delete Category
### Endpoint: `/categories/<int:category_id>`
### Method: `DELETE`
### Description
Deletes a category by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `category_id` (integer): The ID of the category to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Category deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 401**: Invalid or missing session (user not authenticated).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Category with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Category not found or failed to delete"
    }
    ```

**Notes**:
- Uses `CategoryManager.delete_category` to delete the category.
- Cascading deletes are assumed to handle related data (e.g., child categories or products) due to database schema constraints.

---

## 6. Get All Categories
### Endpoint: `/categories`
### Method: `GET`
### Description
Retrieves a paginated list of all categories in the system. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of categories per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "categories": [
      {
        "id": 123,
        "name": "Electronics",
        "parent_id": null,
        "image_url": "/static/uploads/categories/abc123.jpg"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```

**Notes**:
- Uses `CategoryManager.get_categories` to fetch paginated categories.
- The response includes pagination metadata (`total`, `page`, `per_page`).

---

## 7. Search Categories
### Endpoint: `/categories/search`
### Method: `GET`
### Description
Searches categories by name with pagination. This endpoint is publicly accessible without authentication.

### Authentication
- No authentication required.

### Inputs (Query Parameters)
- `search_term` (string, required): The term to search for in category names (case-insensitive partial match).
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of categories per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "categories": [
      {
        "id": 123,
        "name": "Electronics",
        "parent_id": null,
        "image_url": "/static/uploads/categories/abc123.jpg"
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20,
    "message": "Categories retrieved successfully"
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "categories": [],
    "total": 0,
    "page": 1,
    "per_page": 20,
    "message": "No categories found for this search term"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing search term.
    ```json
    {
      "error": "Search term is required"
    }
    ```

**Notes**:
- Uses `CategoryManager.search_categories` to perform a case-insensitive search on category names.
- The response includes pagination metadata and a `message` field for context.

---

## Notes
- All endpoints interact with the database through the `CategoryManager` class.
- Logging is configured with `logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')` for debugging and monitoring, with checks to avoid duplicate handler configuration.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- Public endpoints (`GET /categories/<int:category_id>`, `GET /categories/parent`, `GET /categories`, `GET /categories/search`) provide read-only access to category data without requiring authentication.
- The `parent_id` field can be null for top-level categories, indicating they have no parent.
- Image uploads are stored in `static/uploads/categories/` with unique filenames generated using UUID, and only PNG, JPG, and JPEG formats are supported.
- The `POST /categories` and `PUT /categories/<int:category_id>` endpoints use `multipart/form-data` to support file uploads.
- SQLite foreign key support is assumed to be enabled (e.g., via `PRAGMA foreign_keys = ON`), ensuring data integrity for related tables like `products` or child categories.