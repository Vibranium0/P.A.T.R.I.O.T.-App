# P.A.T.R.I.O.T. Frontend Token Check Integration

## Overview
This document describes how token authentication is integrated into the P.A.T.R.I.O.T. frontend.

## Architecture

### Components

#### 1. **TokenHandler** (`src/components/TokenHandler.jsx`)
- Runs at application startup (wraps the entire app)
- Extracts JWT token from URL query parameters (after Sentinel login redirect)
- Stores token in localStorage
- Removes token from URL for security
- Redirects to dashboard if landing on root or login page

#### 2. **ProtectedRoute** (`src/components/ProtectedRoute.jsx`)
- Wraps all protected pages
- Checks for token presence in localStorage
- If token missing: redirects to Sentinel Login
- If token present: validates with `/auth/validate` endpoint
- On validation success: stores user information (user_id, username, household_id)
- On validation failure: clears token and redirects to Sentinel Login
- Shows "AUTHENTICATING..." loading state while checking

#### 3. **useAuth Hook** (`src/hooks/useAuth.js`)
- Custom React hook for accessing user data
- Provides: userId, username, householdId, token, isAuthenticated
- Logout method to clear all auth data
- Can be used in any component: `const { userId, username } = useAuth()`

### Backend Auth Endpoint

#### `/auth/validate` (GET)
- **Location**: `patriot/backend/routes/auth_routes.py`
- **Authorization**: Requires `Authorization: Bearer <token>` header
- **Response**: 
  ```json
  {
    "user_id": "123",
    "username": "john_doe",
    "household_id": "456"
  }
  ```
- **Uses**: Flask-JWT-Extended to validate token signature and claims

## Authentication Flow

### Initial Page Load
```
1. User accesses P.A.T.R.I.O.T. at http://localhost:5174
2. TokenHandler checks URL for ?token=... parameter
3. If token exists: stored in localStorage
4. ProtectedRoute checks for token
5. If missing: redirects to Sentinel Login
6. If present: calls /auth/validate
7. On success: stores user data, renders page
8. On failure: clears token, redirects to login
```

### After Sentinel Login
```
1. User logs in at Sentinel (localhost:5173)
2. Sentinel creates JWT token
3. Redirects to: http://localhost:5174?token=<jwt>
4. TokenHandler extracts and stores token
5. ProtectedRoute validates token with /auth/validate
6. User data stored, user redirected to dashboard
```

### Token Validation
```
1. ProtectedRoute sends: GET /auth/validate with Authorization header
2. Backend validates JWT signature using JWT_SECRET_KEY
3. Extracts user_id from JWT claims
4. Returns user metadata
5. Frontend stores: user_id, username, household_id in localStorage
```

## Environment Setup

### Required Environment Variables
Both Sentinel and P.A.T.R.I.O.T. must share the same `JWT_SECRET_KEY`:

```bash
# .env file (create if missing)
JWT_SECRET_KEY=your-shared-secret-key-here
JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7
FLASK_ENV=development
```

### Frontend Configuration
File: `patriot/frontend/.env.development`
```
VITE_SENTINEL_LOGIN_URL=http://localhost:5173
VITE_API_URL=http://localhost:5000
```

## Usage in Components

### Access Current User
```javascript
import useAuth from '../hooks/useAuth';

function MyComponent() {
  const { userId, username, householdId, isAuthenticated } = useAuth();
  
  return (
    <div>
      <p>Welcome, {username}</p>
      <p>User ID: {userId}</p>
    </div>
  );
}
```

### Logout
```javascript
import useAuth from '../hooks/useAuth';

function LogoutButton() {
  const { logout } = useAuth();
  
  const handleLogout = () => {
    logout();
    window.location.href = 'http://localhost:5173/logout';
  };
  
  return <button onClick={handleLogout}>Logout</button>;
}
```

## Token Storage
Tokens are stored in localStorage with the following keys:
- `token`: JWT access token (used for API requests)
- `user_id`: User ID from token validation
- `username`: Username from token validation
- `household_id`: Household ID from token validation

⚠️ **Note**: localStorage is accessible to JavaScript and XSS attacks. For production, consider using HttpOnly cookies via the refresh token endpoint.

## Security Considerations

1. **Token in URL**: Tokens are extracted from the URL and immediately removed from browser history
2. **Authorization Header**: Token sent via `Authorization: Bearer <token>` header for all API requests
3. **Token Validation**: Every protected route validates the token on mount
4. **Shared Secret**: Both apps use the same `JWT_SECRET_KEY` for token validation
5. **CORS**: Both apps must be configured to allow cross-origin requests if on different origins

## Troubleshooting

### "Token validation failed" error
- Check that both apps use the same `JWT_SECRET_KEY`
- Verify `/auth/validate` endpoint is registered in P.A.T.R.I.O.T. backend
- Check browser console for network errors
- Verify token format: `Bearer <token>`

### Token not persisting after refresh
- Check if localStorage is enabled in browser
- Verify token is being stored by TokenHandler (check console logs)
- Check if token is expired (default 30 minutes)

### Redirect loop between apps
- Verify `VITE_SENTINEL_LOGIN_URL` points to correct Sentinel instance
- Check that token validation succeeds (not returning 401)
- Verify redirect URL parameters are correct

## API Integration

All API requests to P.A.T.R.I.O.T. backend automatically include the token:

```javascript
// From shared/api/client.js
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    }
);
```

## Testing

### Test Authentication Flow
1. Start both applications
2. Navigate to `http://localhost:5174`
3. Should be redirected to Sentinel login
4. Log in with test credentials
5. Should return to P.A.T.R.I.O.T. with token
6. User data should be visible in localStorage

### Test Protected Routes
1. Try accessing protected pages directly
2. Without token: should redirect to Sentinel
3. With valid token: should load page
4. With invalid token: should clear token and redirect

### Test Token Validation
Open browser DevTools and run:
```javascript
const token = localStorage.getItem('token');
fetch('/auth/validate', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(console.log);
```

Should return user data or 401 error.
