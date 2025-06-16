# Categories API Documentation

This document provides detailed information about the Categories API endpoints implemented in the Flask Blueprint `categories`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /categories`), updating (`PUT /categories/<int:category_id>`), and deleting (`DELETE /categories/<int:category_id>`) categories require admin privileges, enforced by the `@admin_required` decorator.
- Endpoints for retrieving a specific category (`GET /categories/<int:category_id>`), retrieving categories by parent (`GET /categories/parent`), and retrieving all categories (`GET /categories`) do not require authentication, allowing public access to category data.
- The `CategoryManager` class handles all database interactions for category-related operations.

---

## 1. Add a New Category
### Endpoint: `/categories`
### Method: `POST`
### Description
Creates a new category in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `name` (string): The name of the category.
- **Optional Fields**:
  - `parent_id` (integer): The ID of the parent category (null for top-level categories).

**Example Request Body**:
```json
{
  "name": "Electronics",
  "parent_id": null
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Category added successfully",
    "category_id": 123
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing required field (`name`).
    ```json
    {
      "error": "Category name is required"
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
    "parent_id": null
  }
  ```
- **Error Responses**:
  - **HTTP 404**: Category with the specified ID does not exist.
    ```json
    {
      "error": "Category not found"
    }
    ```

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
        "parent_id": null
      }
    ]
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "categories": [],
    "message": "No categories found for this parent"
  }
  ```

---

## 4. Update Category
### Endpoint: `/categories/<int:category_id>`
### Method: `PUT`
### Description
Updates the details of an existing category. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `category_id` (integer): The ID of the category to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `name` (string): The updated name of the category.
    - `parent_id` (integer): The updated parent category ID (null for top-level categories).

**Example Request Body**:
```json
{
  "name": "Updated Electronics",
  "parent_id": 456
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Category updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Failure to update the category (e.g., invalid data or database error).
    ```json
    {
      "error": "Failed to update category"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

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
        "parent_id": null
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```

---

## Notes
- All endpoints interact with the database through the `CategoryManager` class.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` for debugging and monitoring purposes.
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- Public endpoints (`GET /categories/<int:category_id>`, `GET /categories/parent`, and `GET /categories`) provide read-only access to category data without requiring authentication.
- The `parent_id` field can be null for top-level categories, indicating they have no parent.
- The `GET /categories/parent` endpoint returns an empty list with a message if no categories are found for the specified parent ID.