 # User API Documentation

This document provides detailed information about the User API endpoints implemented in the Flask Blueprint `users`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Most endpoints require session-based authentication using the `@session_required` decorator, which checks for a valid `user_id` in the session.
- Some endpoints (e.g., `/users` GET, `/users/<int:user_id>` DELETE) require admin privileges, enforced by the `@admin_required` decorator.
- The `current_user_id` is extracted from the session, and the `is_admin` flag determines if the user has admin privileges.
- The `/users` POST endpoint does not require authentication, as it is used to create a new user.

---

## 1. Add a New User
### Endpoint: `/users`
### Method: `POST`
### Description
Creates a new user in the system. This endpoint does not require authentication, allowing anyone to register a new user.

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `username` (string): The username for the new user.
  - `email` (string): The email address of the new user.
  - `password` (string): The password for the new user.
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
  - **HTTP 400**: Missing required fields.
    ```json
    {
      "error": "Username, email, and password are required"
    }
    ```
  - **HTTP 500**: Failed to add the user.
    ```json
    {
      "error": "Failed to add user"
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
    "created_at": "2025-05-23T22:18:00"
  }
  ```
  - Note: The `created_at` field is a string representing a timestamp.
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
    "created_at": "2025-05-23T22:18:00"
  }
  ```
  - Note: The `created_at` field is a string representing a timestamp.
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
    "created_at": "2025-05-23T22:18:00"
  }
  ```
  - Note: The `created_at` field is a string representing a timestamp.
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

---

## 5. Update User
### Endpoint: `/users/<int:user_id>`
### Method: `PUT`
### Description
Updates the details of an existing user. Only the user themselves or an admin can update the user data.

### Authentication
- Requires a valid session (`@session_required`).
- Non-admin users can only update their own user data.

### Inputs
- **URL Parameters**:
  - `user_id` (integer): The ID of the user to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `full_name` (string): The full name of the user.
    - `phone_number` (string): The phone number of the user.
    - `is_admin` (boolean): Indicates if the user has admin privileges.
    - `password` (string): The new password for the user.

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
  - **HTTP 403**: Unauthorized to update the user data.
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
  - **HTTP 400**: Failed to update the user (e.g., invalid data).
    ```json
    {
      "error": "Failed to update user"
    }
    ```

**Note**: The `is_admin` field can be updated by any authorized user (self or admin), but in a production environment, this should likely be restricted to admins only via additional checks in `user_manager.update_user`.

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
  - **HTTP 404**: User not found or failed to delete.
    ```json
    {
      "error": "User not found or failed to delete"
    }
    ```
  - **HTTP 403**: Unauthorized access (admin privileges required).
    ```json
    {
      "error": "Unauthorized access"
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
        "created_at": "2025-05-23T22:18:00"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
  - Note: The `created_at` field is a string representing a timestamp.
- **Error Responses**:
  - **HTTP 403**: Unauthorized access (admin privileges required).
    ```json
    {
      "error": "Unauthorized access"
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
  - **HTTP 400**: Password is missing.
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

---

## Notes
- All endpoints (except `/users` POST) use the `UserManager` class to interact with the database.
- Logging is configured with `logging.basicConfig(level=logging.INFO)` for debugging and monitoring.
- The `is_admin` field is stored as a boolean in the session and can be provided as a boolean (`true` or `false`) in the request body. Note that updating `is_admin` in the `/users/<int:user_id>` PUT endpoint is allowed for any authorized user, which may be a security concern and should be restricted to admins in production.
- Error responses include a descriptive `error` field to help clients understand the issue.
- The `created_at` field in responses is a string representing a timestamp (e.g., "2025-05-23T22:18:00").
- The `UserManager` class is assumed to handle database operations correctly, but its implementation is not provided in the code.