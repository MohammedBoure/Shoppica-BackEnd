# Categories API Documentation

This document provides detailed information about the Categories API endpoints defined in `admin_apis/categories.py`. These endpoints manage product categories in an e-commerce platform, including adding, retrieving, updating, and deleting categories. Authentication and authorization are enforced using JWT (JSON Web Tokens) with specific roles (`@admin_required` for admin-only operations).

## Base URL
All endpoints are prefixed with `/api`. For example, `/categories` is accessed as `/api/categories`.

## Authentication
- **JWT Token**: Required for endpoints marked with `@admin_required`. Include the token in the `Authorization` header as `Bearer <token>`.
- **Admin Privileges**: Endpoints marked with `@admin_required` (`POST /api/categories`, `PUT /api/categories/<category_id>`, `DELETE /api/categories/<category_id>`) require a JWT token with `is_admin: true`.
- **Public Access**: Endpoints `GET /api/categories`, `GET /api/categories/<category_id>`, and `GET /api/categories/parent` are publicly accessible without authentication.

## Endpoints

### 1. Add Category
- **Endpoint**: `POST /api/categories`
- **Description**: Adds a new category to the platform (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "name": <string>,         // Required: Name of the category
    "parent_id": <integer>    // Optional: ID of the parent category (null for top-level)
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {
      "message": "Category added successfully",
      "category_id": <integer>
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Category name is required"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Failed to add category"
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

### 2. Get Category by ID
- **Endpoint**: `GET /api/categories/<category_id>`
- **Description**: Retrieves a category by its ID. Publicly accessible.
- **Authorization**: None (public access).
- **Input**: URL parameter `category_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": <integer>,
      "name": <string>,
      "parent_id": <integer>
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Category not found"
    }
    ```

### 3. Get Categories by Parent
- **Endpoint**: `GET /api/categories/parent?parent_id=<parent_id>`
- **Description**: Retrieves all categories under a specific parent ID (or top-level categories if `parent_id` is not provided). Publicly accessible.
- **Authorization**: None (public access).
- **Input**:
  - Query parameter: `parent_id` (integer, optional; null for top-level categories).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "categories": [
        {
          "id": <integer>,
          "name": <string>,
          "parent_id": <integer>
        },
        ...
      ]
    }
    ```
    or, if no categories:
    ```json
    {
      "categories": [],
      "message": "No categories found for this parent"
    }
    ```

### 4. Update Category
- **Endpoint**: `PUT /api/categories/<category_id>`
- **Description**: Updates a category’s details (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**:
  ```json
  {
    "name": <string>,         // Optional: Name of the category
    "parent_id": <integer>    // Optional: ID of the parent category (null for top-level)
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Category updated successfully"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Failed to update category"
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

### 5. Delete Category
- **Endpoint**: `DELETE /api/categories/<category_id>`
- **Description**: Deletes a category by ID (admin-only).
- **Authorization**: Requires `@admin_required` (JWT token with `is_admin: true`).
- **Input**: URL parameter `category_id` (integer).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "message": "Category deleted successfully"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Category not found or failed to delete"
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

### 6. Get All Categories (Paginated)
- **Endpoint**: `GET /api/categories?page=<page>&per_page=<per_page>`
- **Description**: Retrieves a paginated list of all categories. Publicly accessible.
- **Authorization**: None (public access).
- **Input**:
  - Query parameters:
    - `page` (integer, default: 1)
    - `per_page` (integer, default: 20)
- **Output**:
  - **Success (200)**:
    ```json
    {
      "categories": [
        {
          "id": <integer>,
          "name": <string>,
          "parent_id": <integer>
        },
        ...
      ],
      "total": <integer>,
      "page": <integer>,
      "per_page": <integer>
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

### Adding a Category (Admin Only)
```bash
curl -X POST http://localhost:5000/api/categories -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"name":"Electronics","parent_id":null}'
```
Response:
```json
{
  "message": "Category added successfully",
  "category_id": 1
}
```

### Getting a Category by ID (Public)
```bash
curl -X GET http://localhost:5000/api/categories/1
```
Response:
```json
{
  "id": 1,
  "name": "Electronics",
  "parent_id": null
}
```

### Getting Categories by Parent (Public)
```bash
curl -X GET http://localhost:5000/api/categories/parent?parent_id=1
```
Response:
```json
{
  "categories": [
    {
      "id": 2,
      "name": "Smartphones",
      "parent_id": 1
    }
  ]
}
```
For top-level categories:
```bash
curl -X GET http://localhost:5000/api/categories/parent
```
Response:
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "parent_id": null
    }
  ]
}
```

### Updating a Category (Admin Only)
```bash
curl -X PUT http://localhost:5000/api/categories/1 -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"name":"Updated Electronics","parent_id":null}'
```
Response:
```json
{
  "message": "Category updated successfully"
}
```

### Deleting a Category (Admin Only)
```bash
curl -X DELETE http://localhost:5000/api/categories/1 -H "Authorization: Bearer <admin_token>"
```
Response:
```json
{
  "message": "Category deleted successfully"
}
```

### Getting All Categories (Public)
```bash
curl -X GET http://localhost:5000/api/categories?page=1&per_page=20
```
Response:
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Updated Electronics",
      "parent_id": null
    },
    {
      "id": 2,
      "name": "Smartphones",
      "parent_id": 1
    },
    ...
  ],
  "total": 10,
  "page": 1,
  "per_page": 20
}
```

## Notes
- **Database Manager**: The API relies on `CategoryManager` for database operations.
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages. Errors are logged for debugging.
- **Security**:
  - Admin endpoints (`POST /api/categories`, `PUT /api/categories/<category_id>`, `DELETE /api/categories/<category_id>`) require a valid JWT with admin privileges.
  - Public endpoints (`GET /api/categories`, `GET /api/categories/<category_id>`, `GET /api/categories/parent`) allow anyone to view category details, as categories are typically public in e-commerce platforms.
- **Data Validation**: Ensures the required field (`name`) is provided when adding a category. Updates allow optional changes to `name` and `parent_id`.
- **Category Hierarchy**: The `parent_id` field supports a hierarchical structure (e.g., top-level categories with `parent_id: null` and subcategories with a valid `parent_id`).
- **Testing**: Unit tests can be created in `test/test_categories.py` to verify functionality.

For further details, refer to the source code in `admin_apis/categories.py`.