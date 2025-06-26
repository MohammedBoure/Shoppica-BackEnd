# Payments API Documentation

This document provides detailed information about the Payments API endpoints implemented in the Flask Blueprint `payments`. Each endpoint is described with its purpose, HTTP method, required authentication, inputs, outputs, and possible error responses.

## Authentication
- Endpoints for adding (`POST /payments`), retrieving a specific payment (`GET /payments/<int:payment_id>`), and retrieving payments by order (`GET /payments/order/<int:order_id>`) require session-based authentication, enforced by the `@session_required` decorator, which checks for a valid `user_id` in the session.
- Endpoints for updating (`PUT /payments/<int:payment_id>`), deleting (`DELETE /payments/<int:payment_id>`), and retrieving all payments (`GET /payments`) require admin privileges, enforced by the `@admin_required` decorator.
- The `PaymentManager` class handles all database interactions for payment-related operations.
- Unlike other APIs (e.g., Order Items), there are no ownership checks for payments; any authenticated user can access or add payments, while only admins can update, delete, or retrieve all payments.

## Logging
- Logging is configured with `logging.basicConfig(level=logging.INFO)` for debugging and error tracking.

---

## 1. Add a New Payment
### Endpoint: `/payments`
### Method: `POST`
### Description
Creates a new payment for an order. This endpoint requires a valid user session.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs (Request Body)
- **Content-Type**: `application/json`
- **Required Fields**:
  - `order_id` (integer): The ID of the order associated with the payment.
  - `payment_method` (string): The method used for the payment (e.g., `credit_card`, `paypal`).
- **Optional Fields**:
  - `transaction_id` (string): The transaction ID provided by the payment processor.
  - `payment_status` (string, default: `"unpaid"`): The status of the payment (e.g., `unpaid`, `paid`, `failed`).

**Example Request Body**:
```json
{
  "order_id": 789,
  "payment_method": "credit_card",
  "transaction_id": "txn_123456",
  "payment_status": "paid"
}
```

### Outputs
- **Success Response** (HTTP 201):
  ```json
  {
    "message": "Payment added successfully",
    "payment_id": 456
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Missing required fields (`order_id` or `payment_method`).
    ```json
    {
      "error": "Order ID and payment method are required"
    }
    ```
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 500**: Server error when failing to add the payment to the database.
    ```json
    {
      "error": "Failed to add payment"
    }
    ```

---

## 2. Get Payment by ID
### Endpoint: `/payments/<int:payment_id>`
### Method: `GET`
### Description
Retrieves the details of a specific payment by its ID. This endpoint requires a valid user session.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs (URL Parameters)
- `payment_id` (integer): The ID of the payment to retrieve.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "id": 456,
    "order_id": 789,
    "payment_method": "credit_card",
    "payment_status": "paid",
    "transaction_id": "txn_123456",
    "paid_at": "2025-06-26T20:34:00"
  }
  ```
- **Error Responses**:
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```
  - **HTTP 404**: Payment with the specified ID does not exist.
    ```json
    {
      "error": "Payment not found"
    }
    ```

---

## 3. Get Payments by Order
### Endpoint: `/payments/order/<int:order_id>`
### Method: `GET`
### Description
Retrieves all payments associated with a specific order. This endpoint requires a valid user session.

### Authentication
- Requires a valid session (`@session_required`).

### Inputs (URL Parameters)
- `order_id` (integer): The ID of the order whose payments are to be retrieved.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "payments": [
      {
        "id": 456,
        "order_id": 789,
        "payment_method": "credit_card",
        "payment_status": "paid",
        "transaction_id": "txn_123456",
        "paid_at": "2025-06-26T20:34:00"
      }
    ],
    "message": null
  }
  ```
- **Empty Response** (HTTP 200):
  ```json
  {
    "payments": [],
    "message": "No payments found for this order"
  }
  ```
- **Error Responses**:
  - **HTTP 401**: User not authenticated (missing or invalid session).
    ```json
    {
      "error": "User not authenticated"
    }
    ```

---

## 4. Update Payment
### Endpoint: `/payments/<int:payment_id>`
### Method: `PUT`
### Description
Updates the details of an existing payment. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `payment_id` (integer): The ID of the payment to update.
- **Request Body** (Content-Type: `application/json`):
  - **Optional Fields**:
    - `payment_method` (string): The updated payment method (e.g., `credit_card`, `paypal`).
    - `payment_status` (string): The updated payment status (e.g., `unpaid`, `paid`, `failed`).
    - `transaction_id` (string): The updated transaction ID provided by the payment processor.

**Example Request Body**:
```json
{
  "payment_method": "paypal",
  "payment_status": "failed",
  "transaction_id": "txn_789012"
}
```

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Payment updated successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 400**: Failed to update the payment (e.g., invalid data or database error).
    ```json
    {
      "error": "Failed to update payment"
    }
    ```
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

---

## 5. Delete Payment
### Endpoint: `/payments/<int:payment_id>`
### Method: `DELETE`
### Description
Deletes a payment by its ID. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs
- **URL Parameters**:
  - `payment_id` (integer): The ID of the payment to delete.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "message": "Payment deleted successfully"
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```
  - **HTTP 404**: Payment with the specified ID does not exist or failed to delete.
    ```json
    {
      "error": "Payment not found or failed to delete"
    }
    ```

---

## 6. Get All Payments (Admin Only)
### Endpoint: `/payments`
### Method: `GET`
### Description
Retrieves a paginated list of all payments in the system. This endpoint is restricted to admin users only.

### Authentication
- Requires a valid session with admin privileges (`@admin_required`).

### Inputs (Query Parameters)
- `page` (integer, default: `1`): The page number for pagination.
- `per_page` (integer, default: `20`): The number of payments per page.

### Outputs
- **Success Response** (HTTP 200):
  ```json
  {
    "payments": [
      {
        "id": 456,
        "order_id": 789,
        "payment_method": "credit_card",
        "payment_status": "paid",
        "transaction_id": "txn_123456",
        "paid_at": "2025-06-26T20:34:00"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20
  }
  ```
- **Error Responses**:
  - **HTTP 403**: Admin privileges required (non-admin user attempting to access).
    ```json
    {
      "error": "Admin privileges required"
    }
    ```

---

## Notes
- All endpoints interact with the database through the `PaymentManager` class, which encapsulates database operations for payments.
- Logging is configured using `logging.basicConfig(level=logging.INFO)` for debugging and monitoring purposes.
- The `paid_at` field in responses is a timestamp indicating when the payment was processed (format: `YYYY-MM-DDTHH:MM:SS`, or `null` if not set).
- Error responses include a descriptive `error` field to assist clients in troubleshooting.
- The `POST /payments`, `GET /payments/<int:payment_id>`, and `GET /payments/order/<int:order_id>` endpoints are accessible to any authenticated user, with no additional ownership checks for the associated order.
- The `PUT /payments/<int:payment_id>` and `DELETE /payments/<int:payment_id>` endpoints allow partial updates or deletion of payment details, with `PaymentManager` determining the success of the operation.
- The `GET /payments/order/<int:order_id>` endpoint returns an empty list with a `message` field set to `"No payments found for this order"` if no payments are found.
- Pagination in `GET /payments` is supported with `page` and `per_page` query parameters, but no explicit validation for negative or zero values is present in the code.