# Quick Reference - Token Check Integration

## What Was Done

Integrated token authentication checks into P.A.T.R.I.O.T. frontend to ensure users are authenticated before accessing protected routes.

## Key Changes

### 1. Backend Auth Endpoint (NEW)
- **File**: `patriot/backend/routes/auth_routes.py`
- **Endpoint**: `GET /auth/validate`
- **Response**: `{ user_id, username, household_id }`

### 2. Enhanced ProtectedRoute
- **File**: `patriot/frontend/src/components/ProtectedRoute.jsx`
- **Now stores**: user_id, username, household_id in localStorage
- **Validates**: Token on every route change

### 3. New useAuth Hook
- **File**: `patriot/frontend/src/hooks/useAuth.js`
- **Usage**: `const { userId, username, householdId } = useAuth();`

## How It Works

```
User visits page
    ↓
ProtectedRoute checks token
    ↓
Token missing? → Redirect to Sentinel Login
    ↓
Token exists? → Call /auth/validate
    ↓
Valid? → Store user data, show page
Invalid? → Clear token, redirect to login
```

## Usage in Components

```javascript
// Get current user
import useAuth from '../hooks/useAuth';

function MyComponent() {
  const { userId, username, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) return <div>Loading...</div>;
  
  return <div>Hello {username}!</div>;
}
```

## Required Setup

Both backends need the same JWT secret in `.env`:
```
JWT_SECRET_KEY=shared-secret-key
```

## Testing

1. Start both backends:
   - Sentinel: `python -m flask --app sentinel_login.backend.app run --port 5001`
   - P.A.T.R.I.O.T.: `python -m flask --app patriot.backend.app run --port 5000`

2. Start frontend:
   - `npm run dev`

3. Navigate to localhost:5174
   - Should redirect to Sentinel login
   - After login, should return to P.A.T.R.I.O.T.
   - Check localStorage for user_id, username, household_id

## Files Summary

| File | Status | Purpose |
|------|--------|---------|
| `patriot/backend/routes/auth_routes.py` | NEW | Validates JWT tokens |
| `patriot/frontend/src/hooks/useAuth.js` | NEW | React hook for auth data |
| `patriot/backend/app.py` | MODIFIED | Register auth blueprint |
| `patriot/frontend/src/components/ProtectedRoute.jsx` | MODIFIED | Store user data |
| `patriot/frontend/AUTHENTICATION_INTEGRATION.md` | NEW | Full documentation |
| `TOKEN_CHECK_IMPLEMENTATION.md` | NEW | Implementation summary |

## Troubleshooting

**"Token validation failed"**
- Check both apps use same `JWT_SECRET_KEY`
- Verify `/auth/validate` endpoint exists
- Check Authorization header format

**Redirect loop**
- Verify `VITE_SENTINEL_LOGIN_URL` is correct
- Check token validation is succeeding
- Clear localStorage and try again

**User data not storing**
- Check network tab for `/auth/validate` response
- Verify localStorage is enabled
- Check for browser console errors

## Next Steps

Protected routes can now:
- Access user_id via `useAuth()` hook
- Make API calls with user context
- Render user-specific content
- Implement role-based access control

See `AUTHENTICATION_INTEGRATION.md` for full details.
