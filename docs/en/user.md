# User API Documentation

This document provides detailed information about the User API endpoints implemented using the `UserManager` class. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses. The API interacts with the `users` table in a SQLite database via SQLAlchemy.

## Authentication
- Most endpoints require session-based authentication, typically enforced by a `@session_required` decorator, which checks for a valid `user_id` in the session.
- Endpoints requiring admin privileges (e.g., `/users`, `/users/<int:user_id>` DELETE, `/users/search`, `/users/clear-all`, `/users/count`) are restricted to users with `is_admin=1`, enforced by an `@admin_required` decorator.
- The `current_user_id` is extracted from the session as an integer, and the `is_admin` flag (stored as an integer `0` or `1`) determines admin privileges.
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
  - `email` (string): The email address of the new user (must be unique).
  - `password` (string): The password for the new user.
- **Optional Fields**:
  - `full_name` (string): The full name of the user.
  - `phone_number` (string): The phone number of the user.
  - `is_admin` (integer, default: `0`): Indicates if the user has admin privileges (0 or 1).

**Example Request Body**:
```json
{
  "username": "johndoe",
  "email": "john.doe@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "is_admin": 0
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

**Notes**:
- The `UserManager.add_user` method checks for duplicate `username` or `email` before creating the user.
- Passwords are hashed using the `scrypt` algorithm from `passlib`.
- The `is_admin` field is stored as an integer (0 or 1) in the database.

---

## 2. Get User by ID
### Endpoint: `/users/<int:user_id>`
### Method: `GET`
### Description
Retrieves the details of a specific user by their ID. Only the user themselves or an admin can access the user data.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access their own user data (i.e., `current_user_id == user_id`).

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
    "is_admin": 0,
    "created_at": "2025-06-26T19:58:00.000000"
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
  - The `is_admin` field is returned as an integer (0 or 1).
- **Error Responses**:
  - **HTTP 403**: Unauthorized to access the user data (non-admin accessing another user's data).
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

**Notes**:
- Uses `UserManager.get_user_by_id` to fetch user data.
- The `password_hash` field is included in the response for consistency with the code, but it should be excluded in a production API for security.

---

## 3. Get User by Email
### Endpoint: `/users/email/<string:email>`
### Method: `GET`
### Description
Retrieves the details of a specific user by their email address. Only the user themselves or an admin can access the user data.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access their own user data (i.e., `current_user.email == email`).

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
    "is_admin": 0,
    "created_at": "2025-06-26T19:58:00.000000"
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
  - The `is_admin` field is returned as an integer (0 or 1).
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

**Notes**:
- Uses `UserManager.get_user_by_email` to fetch user data.
- The `password_hash` field is included in the response for consistency with the code, but it should be excluded in a production API for security.

---

## 4. Get User by Username
### Endpoint: `/users/username/<string:username>`
### Method: `GET`
### Description
Retrieves the details of a specific user by their username. Only the user themselves or an admin can access the user data.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only access their own user data (i.e., `current_user.username == username`).

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
    "is_admin": 0,
    "created_at": "2025-06-26T19:58:00.000000"
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
  - The `is_admin` field is returned as an integer (0 or 1).
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

**Notes**:
- Uses `UserManager.get_user_by_username` to fetch user data.
- The `password_hash` field is included in the response for consistency with the code, but it should be excluded in a production API for security.

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
    - `is_admin` (integer): Indicates if the user has admin privileges (0 or 1, admin-only).
    - `password` (string): The new password for the user.

**Example Request Body**:
```json
{
  "full_name": "John A. Doe",
  "phone_number": "+0987654321",
  "is_admin": 0,
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
  - **HTTP 404**: User not found.
    ```json
    {
      "error": "User not found"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to update user due to database error"
    }
    ```

**Notes**:
- Uses `UserManager.update_user` to update user data.
- Only provided fields are updated; others remain unchanged.
- The `is_admin` field is stored and processed as an integer (0 or 1).
- The restriction on `is_admin` updates is enforced in the API layer, not in `UserManager.update_user`.

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
  - **HTTP 404**: User not found.
    ```json
    {
      "error": "User not found"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to delete user due to database error"
    }
    ```

**Notes**:
- Uses `UserManager.delete_user` to delete the user.
- Cascading deletes are handled for related data (e.g., `addresses`, `reviews`) due to `cascade="all, delete-orphan"` in the database schema.

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
        "is_admin": 0,
        "created_at": "2025-06-26T19:58:00.000000"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
  - The `is_admin` field is returned as an integer (0 or 1).
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

**Notes**:
- Uses `UserManager.get_users` to fetch paginated user data.
- The `password_hash` field is included in the response for consistency with the code, but it should be excluded in a production API for security.

---

## 8. Validate User Password
### Endpoint: `/users/<int:user_id>/validate-password`
### Method: `POST`
### Description
Validates a user's password. Only the user themselves or an admin can validate the password.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only validate their own password (i.e., `current_user_id == user_id`).

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
      "error": "Password is required"
    }
    ```
  - **HTTP 401**: Invalid password or user not found.
    ```json
    {
      "error": "Invalid password or user not found"
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

**Notes**:
- Uses `UserManager.validate_password` to check the password against the stored hash.
- The `scrypt.verify` method from `passlib` is used for password validation.
- The code returns `False` for both invalid passwords and non-existent users, so the API should map this to HTTP 401.

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
        "is_admin": 0,
        "created_at": "2025-06-26T19:58:00.000000"
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
  - The `is_admin` field is returned as an integer (0 or 1).
- **Error Responses**:
  - **HTTP 400**: Missing search query parameter.
    ```json
    {
      "error": "Search query parameter 'q' is required"
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

**Notes**:
- Uses `UserManager.search_users` to perform case-insensitive partial matches on `username` or `email` using `ilike`.
- The `password_hash` field is included in the response for consistency with the code, but it should be excluded in a production API for security.

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

**Notes**:
- Uses `UserManager.clear_all_users` to delete all users.
- Cascading deletes are handled for related data due to `cascade="all, delete-orphan"` in the database schema.

---

## 11. Get Total User Count (Admin Only)
### Endpoint: `/users/count`
### Method: `GET`
### Description
Returns the total number of users in the database. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- None.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "total_users": 50
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
      "error": "Failed to retrieve total user count due to database error"
    }
    ```

**Notes**:
- Uses `UserManager.get_total_user_count` to fetch the total number of users.