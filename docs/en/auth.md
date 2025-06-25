# Authentication API Documentation

This document provides detailed information about the Authentication API endpoints implemented in the Flask Blueprint `auth`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints use session-based authentication via Flask's `session` object.
- The `@session_required` decorator ensures a valid `user_id` (integer) is present in the session.
- The `@admin_required` decorator restricts access to users with admin privileges (`is_admin` set to `True` in the session).
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
  - `email` (string): The email address of the user (must be a valid email format).
  - `password` (string): The password of the user (minimum 6 characters).

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
  - **HTTP 400**: Invalid JSON body or missing required fields.
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
  - **HTTP 400**: Invalid email format.
    ```json
    {
      "error": "Invalid email format"
    }
    ```
  - **HTTP 401**: Invalid credentials.
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

---

## 2. Get Current User
### Endpoint: `/auth/me`
### Method: `GET`
### Description
Retrieves the details of the currently authenticated user based on the session.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs
- None (uses session data).

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
    "created_at": "2025-05-23T22:18:00.000000"
  }
  ```
  - Note: The `created_at` field is a string in ISO 8601 format.
- **Error Responses**:
  - **HTTP 401**: User is not authenticated.
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
  - **HTTP 401**: User is not authenticated.
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

---

## Notes
- All endpoints use the `UserManager` class to interact with the database for user data retrieval and password validation.
- Session data includes `user_id` (integer) and `is_admin` (boolean) to track the authenticated user and their privileges.
- The `created_at` field in the `/auth/me` response is a timestamp in ISO 8601 format (e.g., "2025-05-23T22:18:00.000000") indicating when the user was created.
- Error responses include a descriptive `error` field to help clients understand the issue.
- Logging is configured with `%(asctime)s - %(levelname)s - %(message)s` format for debugging and monitoring, capturing successful logins, failed attempts, and errors.
- Passwords are validated using the `passlib` library's `scrypt` algorithm, ensuring secure authentication.
- The `/auth/login` endpoint enforces a minimum password length of 6 characters, as defined by the `UserManager` class.
- The `is_admin` field is stored as an integer (0 or 1) in the database but returned as a boolean (`true` or `false`) in API responses.