# Cross-App Authentication & Redirect Flow

## Overview

The Sentinel Login app serves as a centralized authentication service for the P.A.T.R.I.O.T. application. This document explains how users are redirected between apps during the authentication process.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Authentication Flow                          │
└─────────────────────────────────────────────────────────────────┘

User → P.A.T.R.I.O.T. App (Port 5174)
         │
         │ No Token / Invalid Token
         ↓
    ProtectedRoute detects unauthenticated user
         │
         ↓
    Redirect to Sentinel Login (Port 5173)
    URL: http://localhost:5173/patriot-login?redirect=http://localhost:5174/dashboard
         │
         │ User enters credentials
         ↓
    Login successful → Access token generated
         │
         ↓
    Redirect back to P.A.T.R.I.O.T. with token
    URL: http://localhost:5174/dashboard?token=eyJ...
         │
         ↓
    TokenHandler extracts token from URL
         │
         ├─ Stores token in localStorage
         ├─ Removes token from URL (security)
         └─ Redirects to clean URL
         │
         ↓
    User is authenticated in P.A.T.R.I.O.T. app
```

## Port Configuration

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| P.A.T.R.I.O.T. Backend | 5000 | http://localhost:5000 | API server |
| Sentinel Backend | 5001 | http://localhost:5001 | Auth API server |
| Sentinel Frontend | 5173 | http://localhost:5173 | Login UI |
| P.A.T.R.I.O.T. Frontend | 5174 | http://localhost:5174 | Main app UI |

## Redirect Flow Details

### 1. User Visits Protected Page

**Location:** P.A.T.R.I.O.T. App (`http://localhost:5174/dashboard`)

**What Happens:**
- `ProtectedRoute` component checks for valid token
- If no token or invalid token:
  - Constructs redirect URL with current location
  - Redirects to: `http://localhost:5173/patriot-login?redirect=http://localhost:5174/dashboard`

**Code:** `patriot/frontend/src/components/ProtectedRoute.jsx`
```javascript
const sentinelLoginUrl = import.meta.env.VITE_SENTINEL_LOGIN_URL || 'http://localhost:5173';
const currentUrl = window.location.origin + location.pathname;
const redirectUrl = `${sentinelLoginUrl}/patriot-login?redirect=${encodeURIComponent(currentUrl)}`;
window.location.href = redirectUrl;
```

### 2. User Logs In

**Location:** Sentinel Login (`http://localhost:5173/patriot-login`)

**What Happens:**
- User enters credentials
- Login component extracts `redirect` parameter from URL
- After successful authentication:
  - Gets access token from backend
  - Appends token to redirect URL
  - Redirects to: `http://localhost:5174/dashboard?token=eyJ...`

**Code:** `sentinel_login/frontend/src/pages/Patriot-Login/Patriot-Login.jsx`
```javascript
const getRedirectUrl = () => {
  const searchParams = new URLSearchParams(location.search);
  const redirectParam = searchParams.get('redirect');
  
  if (redirectParam) {
    return decodeURIComponent(redirectParam);
  }
  
  // Default to P.A.T.R.I.O.T. dashboard
  const patriotAppUrl = import.meta.env.VITE_PATRIOT_APP_URL || 'http://localhost:5174';
  return `${patriotAppUrl}/dashboard`;
};

// After successful login
const redirectUrl = getRedirectUrl();
const separator = redirectUrl.includes('?') ? '&' : '?';
window.location.href = `${redirectUrl}${separator}token=${encodeURIComponent(data.access_token)}`;
```

### 3. Token Extraction

**Location:** Back in P.A.T.R.I.O.T. App (`http://localhost:5174/dashboard?token=eyJ...`)

**What Happens:**
- `TokenHandler` component detects token in URL
- Extracts token and stores in localStorage
- Removes token from URL (for security - don't keep in browser history)
- Redirects to clean URL: `http://localhost:5174/dashboard`

**Code:** `patriot/frontend/src/components/TokenHandler.jsx`
```javascript
const searchParams = new URLSearchParams(location.search);
const token = searchParams.get('token');

if (token) {
  // Store token
  localStorage.setItem('token', token);
  
  // Remove from URL
  searchParams.delete('token');
  const newSearch = searchParams.toString();
  const newPath = location.pathname + (newSearch ? `?${newSearch}` : '');
  window.history.replaceState({}, '', newPath);
}
```

### 4. Authenticated Access

**Location:** P.A.T.R.I.O.T. App (any protected route)

**What Happens:**
- `ProtectedRoute` validates token with backend
- If valid: renders protected content
- If invalid: redirects back to Sentinel Login (step 1)

## Environment Configuration

### Sentinel Login Frontend (`.env.development`)

```bash
# Where to redirect after successful login
VITE_PATRIOT_APP_URL=http://localhost:5174

# Backend API for authentication
VITE_API_URL=http://localhost:5001
```

### P.A.T.R.I.O.T. Frontend (`.env.development`)

```bash
# Where to redirect for authentication
VITE_SENTINEL_LOGIN_URL=http://localhost:5173

# Backend API for data
VITE_API_URL=http://localhost:5000
```

## Security Considerations

### ✅ Secure Practices

1. **Token in URL is temporary**
   - Token appears in URL only during redirect
   - Immediately extracted and removed from browser history
   - Prevents token from being saved in bookmarks or shared links

2. **HttpOnly Cookies for Refresh Token**
   - Refresh token never exposed to JavaScript
   - Automatic transmission with credentials: 'include'
   - Protected from XSS attacks

3. **URL Encoding**
   - All redirect URLs are properly encoded
   - Prevents injection attacks

4. **HTTPS in Production**
   - All environment variables should use HTTPS URLs
   - Tokens encrypted in transit

### ⚠️ Important Notes

- **Don't bookmark URLs with tokens** - They're single-use and temporary
- **Token validation** - P.A.T.R.I.O.T. backend validates every token
- **Token expiration** - Access tokens expire (1 day default, 30 days with remember_me)
- **Refresh flow** - Automatic refresh handled by AuthContext

## Testing the Flow

### Manual Test

1. **Start all services:**
   ```bash
   ./start_all_fixed.sh
   ```

2. **Clear browser storage:**
   - Open DevTools (F12)
   - Application → Storage → Clear site data

3. **Visit P.A.T.R.I.O.T. app:**
   ```
   http://localhost:5174/dashboard
   ```
   - Should redirect to Sentinel Login

4. **Login:**
   - Enter credentials
   - Check URL changes: 
     * Login page: `http://localhost:5173/patriot-login?redirect=...`
     * After login: `http://localhost:5174/dashboard?token=...` (brief)
     * Final: `http://localhost:5174/dashboard` (token removed)

5. **Verify authentication:**
   - Open DevTools → Application → Local Storage
   - Check for `token` key
   - Navigate to different pages - should stay authenticated

### Automated Test

```bash
# Create test script
cat > test_redirect_flow.sh << 'EOF'
#!/bin/bash

echo "Testing Cross-App Authentication Flow"
echo "======================================"

# Test 1: Unauthenticated user should be redirected
echo -e "\n1. Testing unauthenticated redirect..."
RESPONSE=$(curl -s -L -w "%{url_effective}" -o /dev/null "http://localhost:5174/dashboard")
if [[ $RESPONSE == *"localhost:5173"* ]]; then
  echo "✅ Redirects to Sentinel Login"
else
  echo "❌ Redirect failed: $RESPONSE"
fi

# Test 2: Login should return token
echo -e "\n2. Testing login endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test","remember_me":false}')

if [[ $LOGIN_RESPONSE == *"access_token"* ]]; then
  echo "✅ Login successful, token received"
else
  echo "❌ Login failed: $LOGIN_RESPONSE"
fi

# Test 3: Token validation
echo -e "\n3. Testing token validation..."
TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
VALIDATE_RESPONSE=$(curl -s -X GET http://localhost:5000/auth/validate \
  -H "Authorization: Bearer $TOKEN")

if [[ $VALIDATE_RESPONSE == *"user_id"* ]]; then
  echo "✅ Token validation successful"
else
  echo "❌ Token validation failed: $VALIDATE_RESPONSE"
fi

echo -e "\n======================================"
echo "Test complete"
EOF

chmod +x test_redirect_flow.sh
./test_redirect_flow.sh
```

## Troubleshooting

### Issue: Redirect loop

**Symptoms:** Browser keeps redirecting between apps

**Solutions:**
1. Clear browser storage (localStorage, cookies)
2. Check token validation endpoint is working
3. Verify environment variables are correct

### Issue: Token not being extracted

**Symptoms:** User stays on URL with token parameter

**Solutions:**
1. Check TokenHandler is wrapped around Routes in app.jsx
2. Verify useEffect in TokenHandler is running
3. Check browser console for errors

### Issue: "CORS error" during redirect

**Symptoms:** Login successful but redirect fails

**Solutions:**
1. Verify CORS configured with `supports_credentials=True`
2. Check both apps allow each other's origins
3. Ensure `credentials: 'include'` in fetch requests

### Issue: Token invalid after redirect

**Symptoms:** Redirected back to login immediately

**Solutions:**
1. Check token validation endpoint: `/auth/validate`
2. Verify P.A.T.R.I.O.T. backend accepts tokens from Sentinel backend
3. Ensure JWT_SECRET_KEY matches between backends (if shared)

## Production Configuration

For production deployment, update environment variables:

### Sentinel Login

```bash
VITE_PATRIOT_APP_URL=https://app.yourdomain.com
VITE_API_URL=https://auth.yourdomain.com
JWT_COOKIE_SECURE=True
```

### P.A.T.R.I.O.T. App

```bash
VITE_SENTINEL_LOGIN_URL=https://login.yourdomain.com
VITE_API_URL=https://api.yourdomain.com
```

## Secure Token Storage

### Token Storage Strategy

The application uses a secure two-token approach:
- **Access Token**: Stored in memory (React Context/state)
- **Refresh Token**: Stored as HttpOnly cookie (XSS protection)

### Security Benefits

#### Before (localStorage)
- ❌ Both tokens stored in localStorage
- ❌ Vulnerable to XSS attacks
- ❌ Accessible via JavaScript
- ❌ Can be stolen by malicious scripts

#### After (Memory + HttpOnly Cookie)
- ✅ Access token in React Context (memory only)
- ✅ Refresh token in HttpOnly cookie (not accessible to JavaScript)
- ✅ Protected from XSS attacks
- ✅ Automatic cookie transmission with `credentials: 'include'`
- ✅ SameSite=Lax for CSRF protection
- ✅ Token rotation on refresh (each refresh issues new tokens)

### Backend Configuration

#### Flask JWT Settings (`config.py`)
```python
JWT_TOKEN_LOCATION = ["headers", "cookies"]
JWT_COOKIE_SECURE = False  # Set to True in production with HTTPS
JWT_COOKIE_CSRF_PROTECT = False  # Using SameSite instead
```

#### CORS with Credentials (`app.py`)
```python
CORS(app, 
     supports_credentials=True, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173"])
```

### Cookie Attributes

```
Set-Cookie: refresh_token_cookie=eyJ...; 
  HttpOnly;           // Not accessible to JavaScript (XSS protection)
  Secure;             // Only sent over HTTPS (production)
  SameSite=Lax;       // CSRF protection, allows navigation
  Max-Age=7776000;    // 90 days with remember_me, 7 days without
  Path=/;             // Available to all routes
```

### Token Flow Details

#### Login Flow
1. User submits credentials + remember_me flag
2. Backend validates credentials
3. Backend creates access_token + refresh_token
4. Backend returns:
   - JSON body: `{ access_token, username, email, household_id, remember_me }`
   - Set-Cookie header: `refresh_token_cookie=...; HttpOnly; SameSite=Lax`
5. Frontend stores access_token in AuthContext (memory)
6. Frontend schedules token refresh 5 minutes before expiry

#### Refresh Flow (Automatic)
1. AuthContext schedules setTimeout 5 minutes before token expiry
2. Frontend calls `POST /auth/refresh` with `credentials: 'include'`
3. Browser automatically sends refresh_token_cookie
4. Backend validates refresh token from cookie
5. Backend issues new access_token + new refresh_token
6. Frontend updates access_token in AuthContext
7. Frontend schedules next refresh

#### Logout Flow
1. Frontend calls `POST /auth/logout` with `credentials: 'include'`
2. Backend sets cookie: `refresh_token_cookie=''; max_age=0`
3. Frontend clears AuthContext state
4. Frontend redirects to /patriot-login

#### Page Refresh / Cold Start
1. User navigates to app or refreshes page
2. AuthContext useEffect runs on mount
3. Frontend calls `POST /auth/refresh` with `credentials: 'include'`
4. Browser automatically sends refresh_token_cookie if present
5. If valid: Backend issues new access_token, user stays logged in
6. If invalid/missing: User redirected to login

### AuthContext Implementation

The `AuthContext` (`sentinel_login/frontend/src/contexts/AuthContext.jsx`) manages tokens in memory:

```javascript
// Key features:
- accessToken (state): Stored in memory, lost on page refresh
- scheduleTokenRefresh(): Decodes JWT, calculates expiry, schedules refresh
- refreshAccessToken(): Calls backend with credentials: 'include'
- logout(): Calls backend logout endpoint, clears memory state
```

### Security Testing

#### Verify HttpOnly Cookie Protection
```bash
# Login and save cookies
curl -c cookies.txt -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test","remember_me":true}'

# Verify cookie is set
cat cookies.txt

# Test refresh reads from cookie
curl -b cookies.txt -X POST http://localhost:5001/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"remember_me":true}'
```

#### Manual Browser Testing
1. Login with remember_me enabled
2. Open DevTools → Application → Cookies → Check for `refresh_token_cookie`
3. Verify HttpOnly flag is set
4. Open DevTools → Console → Type `document.cookie` → refresh token not visible
5. Check localStorage → only `remember_me` visible, no tokens
6. Refresh page → Should stay logged in via automatic token refresh
7. Logout → Cookie should be cleared

### Production Checklist

Before deploying to production with HTTPS:

1. ✅ Set environment variable: `JWT_COOKIE_SECURE=True`
2. ✅ Update CORS origins to production domain
3. ✅ Ensure HTTPS is enabled
4. ✅ Test cookie behavior in production environment
5. ✅ Verify SameSite policy works with your domain structure

## Related Documentation

- [sentinel_login/QUICK_REFERENCE.md](../sentinel_login/QUICK_REFERENCE.md) - API reference
- [START_SCRIPT_GUIDE.md](../START_SCRIPT_GUIDE.md) - How to start all services
- [PYTHON_IMPORTS.md](../PYTHON_IMPORTS.md) - Import structure guide

## File Inventory

### Sentinel Login
- `sentinel_login/frontend/src/pages/Patriot-Login/Patriot-Login.jsx` - Login page with redirect logic
- `sentinel_login/frontend/src/contexts/AuthContext.jsx` - Token management in memory
- `sentinel_login/backend/routes/auth_routes.py` - Login, refresh, logout with cookie handling
- `sentinel_login/frontend/.env.development` - Environment config

### P.A.T.R.I.O.T. App
- `patriot/frontend/src/components/ProtectedRoute.jsx` - Auth guard with redirect
- `patriot/frontend/src/components/TokenHandler.jsx` - Token extraction from URL
- `patriot/frontend/src/app.jsx` - App with TokenHandler wrapper
- `patriot/frontend/.env.development` - Environment config
