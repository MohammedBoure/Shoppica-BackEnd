# Authentication API Documentation

This document provides detailed information about the Authentication API endpoints implemented in the Flask Blueprint `auth`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses. The API interacts with the `users` table in a SQLite database via the `UserManager` class.

## Authentication
- Endpoints use session-based authentication via Flask's `session` object.
- The `@session_required` decorator ensures a valid `user_id` (integer) is present in the session.
- The `@admin_required` decorator restricts access to users with `is_admin=True` in the session (converted from the database's integer `0` or `1`).
- The `/auth/login` endpoint does not require authentication, as it is used to authenticate users and establish a session.
- Session data includes `user_id` (integer) and `is_admin` (boolean) to track the authenticated user and their privileges.

---

## 1. Login
### Endpoint: `/auth/login`
### Method: `POST`
### Description
Authenticates a user with their email and password, creating a session if successful.

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `email` (string): The email address of the user (must match a valid email format).
  - `password` (string): The password of the user.

**Example Request Body**:
```json
{
  "email": "john.doe@example.com",
  "password": "securepassword123"
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "user": {
      "id": 123,
      "username": "johndoe",
      "email": "john.doe@example.com",
      "is_admin": false
    }
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Invalid JSON body, missing required fields, or invalid email format.
    ```json
    {
      "error": "Request body must be JSON"
    }
    ```
    ```json
    {
      "error": "Email and password are required"
    }
    ```
    ```json
    {
      "error": "Invalid email format"
    }
    ```
  - **HTTP 401**: Invalid credentials (email not found or password incorrect).
    ```json
    {
      "error": "Invalid credentials"
    }
    ```
  - **HTTP 500**: Database error.
    ```json
    {
      "error": "Failed to login due to database error"
    }
    ```

**Notes**:
- Uses `UserManager.get_user_by_email` to retrieve the user and `UserManager.validate_password` to verify the password.
- The `validate_email` function checks the email format using a regex pattern.
- On successful login, the session stores `user_id` (integer) and `is_admin` (boolean, converted from the database's integer `0` or `1`).
- The response includes only `id`, `username`, `email`, and `is_admin` (boolean) for security, excluding sensitive fields like `password_hash`.

---

## 2. Get Current User
### Endpoint: `/auth/me`
### Method: `GET`
### Description
Retrieves the details of the currently authenticated user based on the session.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs
- None (uses `user_id` from session data).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 123,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "is_admin": false,
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "created_at": "2025-06-26T20:01:00.000000"
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
  - The `is_admin` field is returned as a boolean.
- **Error Responses**:
  - **HTTP 401**: User is not authenticated (no `user_id` in session).
    ```json
    {
      "error": "Unauthorized"
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
- Uses `UserManager.get_user_by_id` to fetch user data based on `session['user_id']`.
- The `created_at` field is serialized to ISO 8601 format using `isoformat()`.
- The `is_admin` field is converted to a boolean in the response.
- The `password_hash` field is excluded from the response for security.

---

## 3. Logout
### Endpoint: `/auth/logout`
### Method: `POST`
### Description
Logs out the current user by clearing their session.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs
- None (uses session data).

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Logged out successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 401**: User is not authenticated (no `user_id` in session).
    ```json
    {
      "error": "Unauthorized"
    }
    ```
  - **HTTP 500**: Server error during session clearing.
    ```json
    {
      "error": "Failed to logout due to server error"
    }
    ```

**Notes**:
- Clears all session data using `session.clear()`.
- Logs the `user_id` before clearing the session for auditing purposes.

---

## Notes
- All endpoints use the `UserManager` class to interact with the `users` table for user data retrieval and password validation.
- Session data includes `user_id` (integer) and `is_admin` (boolean, converted from the database's integer `0` or `1`).
- The `created_at` field in the `/auth/me` response is a timestamp in ISO 8601 format (e.g., "2025-06-26T20:01:00.000000").
- Error responses include a descriptive `error` field to help clients understand the issue.
- Logging is configured with the format `%(asctime)s - %(levelname)s - %(message)s` for debugging and monitoring, capturing successful logins, failed attempts, and errors.
- Passwords are validated using the `passlib` library's `scrypt` algorithm via `UserManager.validate_password`.
- The `/auth/login` endpoint validates email format using a regex pattern in the `validate_email` function.
- The `is_admin` field is stored as an integer (0 or 1) in the database but converted to a boolean (`true` or `false`) in API responses for consistency.
- Sensitive data like `password_hash` is never exposed in API responses.
- The `@admin_required` decorator is not used in these endpoints but is available for routes requiring admin privileges.