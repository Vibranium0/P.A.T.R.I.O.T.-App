# Sentinel Backend Authentication API

This document describes all authentication-related endpoints for the Sentinel backend. Use these endpoints for registration, login, JWT management, password reset, and user validation.

---

## Endpoints

### 1. Register
- **POST** `/auth/register`
- **Request Body:**
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **Response:**
  - `201 Created` on success
  - `409 Conflict` if user exists
  - `400 Bad Request` if missing fields

---

### 2. Login
- **POST** `/auth/login`
- **Request Body:**
  ```json
  {
    "email": "string", // or username
    "password": "string"
  }
  ```
- **Response:**
  - `200 OK` with access token and user info
  - `401 Unauthorized` if password invalid
  - `404 Not Found` if user not found

---

### 3. Refresh Token
- **POST** `/auth/refresh`
- **Headers:**
  - `Authorization: Bearer <refresh_token>`
- **Response:**
  - `200 OK` with new access token
  - `404 Not Found` if user not found

---

### 4. Validate Token
- **GET** `/auth/validate`
- **Headers:**
  - `Authorization: Bearer <access_token>`
- **Response:**
  - `200 OK` with user info if token valid
  - `404 Not Found` if user not found

---




---

### 7. User Lookup (Sentinel Sync)
- **GET** `/auth/sentinel/user-lookup?identifier=<username_or_email>`
- **Response:**
  - `200 OK` with user info
  - `404 Not Found` if user not found

---

### 8. Health Check
- **GET** `/auth/sentinel/health`
- **Response:**
  - `200 OK` with app status

---

## Notes
- JWT access tokens are required for protected endpoints.
- Use refresh tokens to obtain new access tokens via `/auth/refresh`.
- Passwords must be at least 8 characters for reset.

---

## Example Usage
- Register, login, use access token for protected routes, refresh token as needed, reset password if forgotten.

---

For further details, see the source code in `routes/auth_routes.py`.
