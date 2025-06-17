# Authentication API Documentation

This document provides detailed information about the Authentication API endpoints implemented in the Flask Blueprint `auth`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints use session-based authentication via Flask's `session` object.
- The `@session_required` decorator ensures a valid `user_id` is present in the session.
- The `@admin_required` decorator restricts access to users with admin privileges (`is_admin` set to `True` in the session).
- The `/login` endpoint does not require authentication, as it is used to authenticate users and establish a session.

---

## 1. Login
### Endpoint: `/login`
### Method: `POST`
### Description
Authenticates a user with their email and password, creating a session if successful.

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `email` (string): The email address of the user.
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
  - **HTTP 400**: Missing required fields.
    ```json
    {
      "error": "Email and password are required"
    }
    ```
  - **HTTP 401**: Invalid credentials.
    ```json
    {
      "error": "Invalid credentials"
    }
    ```

---

## 2. Get Current User
### Endpoint: `/me`
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
    "created_at": "2025-05-23T22:18:00"
  }
  ```
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

---

## 3. Logout
### Endpoint: `/logout`
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

---

## Notes
- All endpoints use the `UserManager` class to interact with the database for user data retrieval and password validation.
- Session data includes `user_id` and `is_admin` to track the authenticated user and their privileges.
- The `created_at` field in the response is a timestamp indicating when the user was created.
- Error responses include a descriptive `error` field to help clients understand the issue.