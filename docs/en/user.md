# User API Documentation

This document provides detailed information about the User API endpoints implemented in the Flask Blueprint `users`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Most endpoints require session-based authentication using the `@session_required` decorator, which checks for a valid `user_id` in the session.
- Some endpoints (e.g., `/users` GET, `/users/<int:user_id>` DELETE, `/users/search`, `/users/clear-all`) require admin privileges, enforced by the `@admin_required` decorator.
- The `current_user_id` is extracted from the session as an integer, and the `is_admin` flag (boolean) determines if the user has admin privileges.
- The `/users` POST endpoint does not require authentication, allowing anyone to register a new user.

---

## 1. Add a New User
### Endpoint: `/users`
### Method: `POST`
### Description
Creates a new user in the system. This endpoint does not require authentication, allowing anyone to register a new user.

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `username` (string): The username for the new user (must be unique).
  - `email` (string): The email address of the new user (must be unique and valid format).
  - `password` (string): The password for the new user (minimum 6 characters).
- **Optional Fields**:
  - `full_name` (string): The full name of the user.
  - `phone_number` (string): The phone number of the user.

**Example Request Body**:
```json
{
  "username": "johndoe",
  "email": "john.doe@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "phone_number": "+1234567890"
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "User added successfully",
    "user_id": 123
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing required fields or invalid email/password.
    ```json
    {
      "error": "Username, email, and password are required"
    }
    ```
    ```json
    {
      "error": "Invalid email format"
    }
    ```
    ```json
    {
      "error": "Password must be at least 6 characters long"
    }
    ```
  - **HTTP 409**: Username or email already exists.
    ```json
    {
      "error": "Username or email already exists"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to add user due to database error"
    }
    ```

---

## 2. Get User by ID
### Endpoint: `/users/<int:user_id>`
### Method: `GET`
### Description
Retrieves the details of a specific user by their ID. Only the user themselves or an admin can access the user data.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access their own user data.

### Inputs (URL Parameters)
- `user_id` (integer): The ID of the user to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 123,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "is_admin": false,
    "created_at": "2025-05-23T22:18:00.000000"
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
- **Error Responses**:
  - **HTTP 403**: Unauthorized to access the user data.
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
  - **HTTP 404**: User not found.
    ```json
    {
      "error": "User not found"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to retrieve user due to database error"
    }
    ```

---

## 3. Get User by Email
### Endpoint: `/users/email/<string:email>`
### Method: `GET`
### Description
Retrieves the details of a specific user by their email address. Only the user themselves or an admin can access the user data.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access their own user data.

### Inputs (URL Parameters)
- `email` (string): The email address of the user to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 123,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "is_admin": false,
    "created_at": "2025-05-23T22:18:00.000000"
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
- **Error Responses**:
  - **HTTP 403**: Unauthorized to access the user data.
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
  - **HTTP 404**: User not found.
    ```json
    {
      "error": "User not found"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to retrieve user due to database error"
    }
    ```

---

## 4. Get User by Username
### Endpoint: `/users/username/<string:username>`
### Method: `GET`
### Description
Retrieves the details of a specific user by their username. Only the user themselves or an admin can access the user data.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access their own user data.

### Inputs (URL Parameters)
- `username` (string): The username of the user to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 123,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "is_admin": false,
    "created_at": "2025-05-23T22:18:00.000000"
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
- **Error Responses**:
  - **HTTP 403**: Unauthorized to access the user data.
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
  - **HTTP 404**: User not found.
    ```json
    {
      "error": "User not found"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to retrieve user due to database error"
    }
    ```

---

## 5. Update User
### Endpoint: `/users/<int:user_id>`
### Method: `PUT`
### Description
Updates the details of an existing user. Only the user themselves or an admin can update the user data. Only admins can update the `is_admin` field.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only update their own user data and cannot modify `is_admin`.

### Inputs
- **URL Parameters**:
  - `user_id` (integer): The ID of the user to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `full_name` (string): The full name of the user.
    - `phone_number` (string): The phone number of the user.
    - `is_admin` (boolean): Indicates if the user has admin privileges (admin-only).
    - `password` (string): The new password for the user (minimum 6 characters).

**Example Request Body**:
```json
{
  "full_name": "John A. Doe",
  "phone_number": "+0987654321",
  "is_admin": false,
  "password": "newpassword123"
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "User updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid request body, no updates provided, or invalid password length.
    ```json
    {
      "error": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "Password must be at least 6 characters long"
    }
    ```
  - **HTTP 403**: Unauthorized to update the user data or non-admin attempting to update `is_admin`.
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
    ```json
    {
      "error": "Only admins can update is_admin status"
    }
    ```
  - **HTTP 404**: User not found or no updates provided.
    ```json
    {
      "error": "User not found or no updates provided"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to update user due to database error"
    }
    ```

---

## 6. Delete User
### Endpoint: `/users/<int:user_id>`
### Method: `DELETE`
### Description
Deletes a user by their ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `user_id` (integer): The ID of the user to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "User deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized access (admin privileges required).
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
  - **HTTP 404**: User not found or failed to delete.
    ```json
    {
      "error": "User not found or failed to delete"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to delete user due to database error"
    }
    ```

---

## 7. Get All Users (Admin Only)
### Endpoint: `/users`
### Method: `GET`
### Description
Retrieves a paginated list of all users in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of users per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "users": [
      {
        "id": 123,
        "username": "johndoe",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "phone_number": "+1234567890",
        "is_admin": false,
        "created_at": "2025-05-23T22:18:00.000000"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
- **Error Responses**:
  - **HTTP 403**: Unauthorized access (admin privileges required).
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to retrieve users due to database error"
    }
    ```

---

## 8. Validate User Password
### Endpoint: `/users/<int:user_id>/validate-password`
### Method: `POST`
### Description
Validates a user's password. Only the user themselves or an admin can validate the password.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only validate their own password.

### Inputs
- **URL Parameters**:
  - `user_id` (integer): The ID of the user whose password is to be validated.
- **Request Body** (Content-Type: `application/json`):
  - **Required Fields**:
    - `password` (string): The password to validate.

**Example Request Body**:
```json
{
  "password": "securepassword123"
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Password is valid"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing or invalid request body.
    ```json
    {
      "error": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "Password is required"
    }
    ```
  - **HTTP 401**: Invalid password.
    ```json
    {
      "error": "Invalid password"
    }
    ```
  - **HTTP 403**: Unauthorized to validate the password.
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to validate password due to database error"
    }
    ```

---

## 9. Search Users (Admin Only)
### Endpoint: `/users/search`
### Method: `GET`
### Description
Searches for users by username or email (partial match) with pagination. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `q` (string, required): The search query for username or email (partial match).
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of users per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "users": [
      {
        "id": 123,
        "username": "johndoe",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "phone_number": "+1234567890",
        "is_admin": false,
        "created_at": "2025-05-23T22:18:00.000000"
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
- **Error Responses**:
  - **HTTP 400**: Missing search query parameter.
    ```json
    {
      "error": "Search query parameter \"q\" is required"
    }
    ```
  - **HTTP 403**: Unauthorized access (admin privileges required).
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to search users due to database error"
    }
    ```

---

## 10. Clear All Users (Admin Only)
### Endpoint: `/users/clear-all`
### Method: `DELETE`
### Description
Deletes all users from the database. This is a destructive operation and is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "All users have been successfully deleted"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Unauthorized access (admin privileges required).
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to clear users due to database error"
    }
    ```

---

## Notes
- All endpoints (except `/users` POST) use the `UserManager` class to interact with the database, leveraging SQLAlchemy for data operations.
- Logging is configured with `%(asctime)s - %(levelname)s - %(message)s` format for debugging and monitoring.
- The `is_admin` field is stored as an integer (0 or 1) in the database but is returned as a boolean (`true` or `false`) in API responses.
- The `created_at` field in responses is a string in ISO 8601 format (e.g., "2025-05-23T22:18:00.000000").
- The `UserManager` class handles database operations, including unique constraints for `username` and `email`, and foreign key support for SQLite.
- Passwords are hashed using `passlib`'s `scrypt` algorithm, ensuring security.
- The `update_user` endpoint restricts `is_admin` updates to admins only, enhancing security.
- Error responses include descriptive `error` fields to help clients diagnose issues.
- Sensitive data (e.g., `password_hash`) is never exposed in API responses.
- Indexes (`idx_users_username`, `idx_users_email`) defined in the database schema improve query performance for lookups and searches.