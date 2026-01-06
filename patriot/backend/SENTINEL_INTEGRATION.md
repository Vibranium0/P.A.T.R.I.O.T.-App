# P.A.T.R.I.O.T. Backend - Sentinel Integration Guide

## Overview

P.A.T.R.I.O.T. backend is now fully integrated with Sentinel Login for authentication. This means:

1. **Token Validation**: P.A.T.R.I.O.T. can validate JWT tokens issued by Sentinel
2. **Cross-Backend Communication**: Both backends can communicate about authentication status
3. **Health Checks**: P.A.T.R.I.O.T. can verify Sentinel is online
4. **Token Info Endpoints**: Sentinel can query token validity from P.A.T.R.I.O.T.

## Architecture

```
┌──────────────────────────────┐
│  P.A.T.R.I.O.T. Frontend     │
│  (React, Port 5174)          │
└──────────┬───────────────────┘
           │ GET /auth/validate
           │ + Bearer <token>
           ▼
┌──────────────────────────────┐
│  P.A.T.R.I.O.T. Backend      │
│  (Flask, Port 5000)          │
│  ┌─────────────────────────┐ │
│  │ /auth/validate          │ │ ◄── Validates token
│  │ /sentinel/health        │ │ ◄── Health check
│  │ /sentinel/token-info    │ │ ◄── Token info
│  │ /debug/sentinel-status  │ │ ◄── Debug info
│  └─────────────────────────┘ │
└──────────┬───────────────────┘
           │ Uses JWT_SECRET_KEY
           │ Communicates via HTTP
           ▼
┌──────────────────────────────┐
│  Sentinel Login Backend       │
│  (Flask, Port 5001)          │
│  ┌─────────────────────────┐ │
│  │ /auth/login             │ │ ◄── Issues tokens
│  │ /auth/sentinel/health   │ │ ◄── Health check
│  │ /auth/sentinel/user-... │ │ ◄── User lookup
│  └─────────────────────────┘ │
└──────────────────────────────┘
```

## Environment Setup

Both backends must share the **same JWT_SECRET_KEY**:

```bash
# Create .env file in project root
JWT_SECRET_KEY=your-shared-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=1

# Optional: Specify Sentinel location (defaults to http://localhost:5001)
SENTINEL_LOGIN_URL=http://localhost:5001

# Optional: Enable/disable Sentinel integration
SENTINEL_ENABLED=true
```

## API Endpoints

### 1. **Token Validation** (Frontend → P.A.T.R.I.O.T. Backend)

```
GET /auth/validate
Authorization: Bearer <jwt_token>

Response (200):
{
  "user_id": "123",
  "username": "john_doe",
  "household_id": "456"
}

Response (401):
{
  "error": "Token validation failed",
  "details": "Signature verification failed"
}
```

**Used by**: ProtectedRoute component in frontend

### 2. **Health Check** (Sentinel → P.A.T.R.I.O.T. Backend)

```
GET /auth/sentinel/health

Response (200):
{
  "status": "online",
  "app_name": "P.A.T.R.I.O.T.",
  "version": "1.0.0",
  "sentinel_system": true,
  "jwt_secret_configured": true
}
```

**Used by**: Sentinel to verify P.A.T.R.I.O.T. is online

### 3. **Token Info** (Sentinel → P.A.T.R.I.O.T. Backend)

```
POST /auth/sentinel/token-info
Content-Type: application/json

Request:
{
  "token": "<jwt_token_string>"
}

Response (200):
{
  "valid": true,
  "user_id": "123",
  "username": "john_doe",
  "household_id": "456"
}

Response (401):
{
  "valid": false,
  "error": "Token validation failed",
  "details": "Signature verification failed"
}
```

**Used by**: Sentinel backend to validate tokens

### 4. **Debug Status** (Development Only)

```
GET /auth/debug/sentinel-status

Response (200):
{
  "sentinel_online": true,
  "sentinel_url": "http://localhost:5001",
  "jwt_configured": true,
  "p_a_t_r_i_o_t_url": "http://localhost:5174",
  "patriot_url": "http://localhost:5000",
  "connection_status": "ready"
}
```

**Used by**: Developers to troubleshoot connection issues

## How It Works

### Token Validation Flow

1. **Frontend sends request to protected page**
   ```javascript
   // ProtectedRoute.jsx
   fetch("/auth/validate", {
     headers: {
       "Authorization": "Bearer <token>"
     }
   })
   ```

2. **P.A.T.R.I.O.T. backend validates token**
   ```python
   # auth_routes.py - /auth/validate endpoint
   @jwt_required()  # Validates JWT signature
   def validate():
       # Extract user claims from token
       # Return user data
   ```

3. **Frontend stores user data**
   ```javascript
   localStorage.setItem("user_id", data.user_id)
   localStorage.setItem("username", data.username)
   localStorage.setItem("household_id", data.household_id)
   ```

### Sentinel Communication Flow

1. **Sentinel checks if P.A.T.R.I.O.T. is online**
   ```
   GET /auth/sentinel/health
   → Returns 200 "online"
   ```

2. **Sentinel validates token from P.A.T.R.I.O.T.**
   ```
   POST /auth/sentinel/token-info
   → Returns token claims
   ```

## Key Components

### Backend Auth Routes (`patriot/backend/routes/auth_routes.py`)

- `/auth/validate` - Main token validation endpoint
- `/auth/sentinel/health` - Health check for Sentinel systems
- `/auth/sentinel/token-info` - Token validation for Sentinel
- `/auth/debug/sentinel-status` - Debug connection status

### Sentinel Client Utility (`patriot/backend/utils/sentinel_client.py`)

Helper class for communicating with Sentinel:

```python
from patriot.backend.utils.sentinel_client import get_sentinel_client

# Get client instance
client = get_sentinel_client()

# Check if Sentinel is online
is_online = client.health_check()

# Validate a token
result = client.validate_token(token_string)
if result['valid']:
    user_id = result['user_id']

# Verify full connection
status = client.verify_sentinel_connection()
print(status['connection_status'])  # "ready", "incomplete", or "error"
```

### Configuration (`patriot/backend/config.py`)

```python
# Sentinel Integration settings
SENTINEL_LOGIN_URL = "http://localhost:5001"  # Sentinel backend URL
SENTINEL_ENABLED = True  # Enable/disable integration
APP_BACKEND_URL = "http://localhost:5000"  # This app's backend URL
```

## JWT Token Format

Tokens issued by Sentinel include the following claims:

```json
{
  "sub": "user_id",           // User ID (required)
  "username": "john_doe",     // Username (required)
  "household_id": "456",      // Household association (required)
  "iat": 1234567890,          // Issued at
  "exp": 1234571490           // Expiration
}
```

The P.A.T.R.I.O.T. backend extracts and returns these claims via the `/auth/validate` endpoint.

## Security Considerations

1. **Shared JWT Secret**
   - Both backends MUST use the same `JWT_SECRET_KEY`
   - This is how token signatures are verified
   - Never share this key publicly or with untrusted systems

2. **CORS Configuration**
   - Both backends have CORS enabled
   - Only allow communication between trusted apps
   - In production, restrict CORS to specific origins

3. **Token Validation**
   - Tokens are validated using JWT signature verification
   - Token expiration is checked
   - Invalid tokens return 401 Unauthorized

4. **Debug Endpoints**
   - `/auth/debug/sentinel-status` should only be used in development
   - Disable in production to prevent information leakage
   - Consider adding authentication to this endpoint

## Testing

### 1. Test Connection from Command Line

```bash
# Check if Sentinel is online
curl http://localhost:5001/auth/sentinel/health

# Check if P.A.T.R.I.O.T. is online
curl http://localhost:5000/auth/sentinel/health

# Get debug status
curl http://localhost:5000/auth/debug/sentinel-status
```

### 2. Test Token Validation

```bash
# Get a token from Sentinel (after login)
TOKEN="<jwt_token_from_login>"

# Validate with P.A.T.R.I.O.T. backend
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/auth/validate

# Send to Sentinel for verification
curl -X POST http://localhost:5001/auth/sentinel/token-info \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$TOKEN\"}"
```

### 3. Test Full Flow

1. Start Sentinel backend: `python -m flask --app sentinel_login.backend.app run --port 5001`
2. Start P.A.T.R.I.O.T. backend: `python -m flask --app patriot.backend.app run --port 5000`
3. Start frontend: `npm run dev` (in patriot/frontend)
4. Navigate to `http://localhost:5174`
5. Should redirect to Sentinel login
6. Log in with test credentials
7. Should return to P.A.T.R.I.O.T. with token
8. Check browser console: should see successful validation

## Troubleshooting

### "Connection refused" to Sentinel

**Problem**: P.A.T.R.I.O.T. backend can't reach Sentinel

**Solutions**:
- Verify Sentinel backend is running on port 5001
- Check `SENTINEL_LOGIN_URL` in `.env` matches actual Sentinel location
- Check firewall allows communication between 5000 and 5001
- Run `curl http://localhost:5001/auth/sentinel/health` to test

### "JWT_SECRET_KEY mismatch"

**Problem**: Token validation fails even though token looks valid

**Solutions**:
- Verify both backends have the **exact same** `JWT_SECRET_KEY` in `.env`
- Restart both servers after changing the key
- Check that you haven't accidentally set different keys

### "Token validation failed"

**Problem**: Valid token gets 401 from `/auth/validate`

**Solutions**:
- Check token isn't expired (default 30 minutes)
- Verify Authorization header format: `Bearer <token>` (with space)
- Check JWT_SECRET_KEY matches between backends
- Look at backend logs for specific error message

### "Connection incomplete"

**Problem**: Debug status shows `connection_status: "incomplete"`

**Solutions**:
- JWT_SECRET_KEY not configured: add to `.env`
- Sentinel not online: start Sentinel backend
- Check SENTINEL_LOGIN_URL points to correct address

## Next Steps

1. ✅ Verify both backends are running and can communicate
2. ✅ Test token validation flow end-to-end
3. ✅ Add user logout endpoint
4. ✅ Implement token refresh logic
5. ✅ Add role-based access control (RBAC)
6. ✅ Move tokens to HttpOnly cookies (production)

## Files Modified

- `patriot/backend/routes/auth_routes.py` - Added Sentinel endpoints
- `patriot/backend/config.py` - Added Sentinel configuration
- `patriot/backend/utils/sentinel_client.py` - New Sentinel communication client

## Files Referenced

- `sentinel_login/backend/routes/auth_routes.py` - Sentinel endpoints
- `patriot/frontend/src/components/ProtectedRoute.jsx` - Token validation on frontend
- `shared/api/client.js` - Automatic token inclusion in API requests
