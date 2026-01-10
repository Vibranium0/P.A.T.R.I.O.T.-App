# Sentinel Login - Quick Reference

## 🚀 Quick Start

### Start Backend
```bash
cd /workspaces/P.A.T.R.I.O.T.-App/sentinel_login/backend
python app.py
# Runs on http://localhost:5001
```

### Start Frontend
```bash
cd /workspaces/P.A.T.R.I.O.T.-App/sentinel_login/frontend
npm run dev
# Runs on http://localhost:5173 (or next available port)
```

## 🔐 Authentication Flow

### Login
```javascript
POST http://localhost:5001/auth/login
Body: { username, password, remember_me }
Response: { access_token, username, email, household_id, remember_me }
Cookie: refresh_token_cookie (HttpOnly)
```

### Register
```javascript
POST http://localhost:5001/auth/register
Body: { username, password, security_question, security_answer }
Response: { message: "registered" }
```

### Password Reset (Step 1: Get Security Question)
```javascript
POST http://localhost:5001/auth/password-reset/request
Body: { username }
Response: { security_question }
```

### Password Reset (Step 2: Confirm New Password)
```javascript
POST http://localhost:5001/auth/password-reset/confirm
Body: { username, security_answer, new_password }
Response: { message: "password updated successfully" }
```

### Token Refresh
```javascript
POST http://localhost:5001/auth/refresh
Body: { remember_me }
Credentials: include (sends refresh_token_cookie automatically)
Response: { access_token }
Cookie: refresh_token_cookie (new token, HttpOnly)
```

### Logout
```javascript
POST http://localhost:5001/auth/logout
Credentials: include
Response: { message: "logged out successfully" }
Cookie: refresh_token_cookie cleared (max_age=0)
```

### Validate Token
```javascript
POST http://localhost:5001/auth/validate
Headers: { Authorization: "Bearer <access_token>" }
Response: { user_id, username, household_id }
```

## 🔑 Token Storage

| Token Type | Storage Location | Accessible to JS | XSS Safe | Duration (default) | Duration (remember_me) |
|------------|------------------|------------------|----------|-------------------|----------------------|
| Access Token | React Context (memory) | ✅ Yes (in-app only) | ✅ Yes (lost on refresh) | 1 day | 30 days |
| Refresh Token | HttpOnly Cookie | ❌ No | ✅ Yes | 7 days | 90 days |

## 📦 Component Usage

### Using AuthContext
```javascript
import { useAuth } from '../../contexts/AuthContext';

function MyComponent() {
  const { accessToken, user, loading, login, logout } = useAuth();
  
  // Check if user is logged in
  if (loading) return <div>Loading...</div>;
  if (!accessToken) return <div>Please log in</div>;
  
  // Use access token for API calls
  fetch('/api/data', {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  
  return <div>Welcome {user?.username}!</div>;
}
```

### Making Authenticated Requests
```javascript
// Frontend
const response = await fetch('http://localhost:5001/api/protected', {
  method: 'GET',
  credentials: 'include', // Important: sends cookies
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

## 🎨 Reusable Components

### Button
```javascript
<Button 
  variant="primary" // or secondary, success, danger, warning, info
  onClick={handleClick}
>
  Click Me
</Button>
```

### Checkbox (with star icon)
```javascript
<Checkbox
  checked={rememberMe}
  onChange={(e) => setRememberMe(e.target.checked)}
  label="Remember Me"
  variant="success"
  icon="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
/>
```

### TextBox
```javascript
<TextBox
  value={username}
  onChange={(e) => setUsername(e.target.value)}
  placeholder="Enter username"
  label="Username"
  required
/>
```

### PasswordTextBox
```javascript
<PasswordTextBox
  value={password}
  onChange={(e) => setPassword(e.target.value)}
  placeholder="Enter password"
  label="Password"
  required
/>
```

## 🐛 Debugging

### Check Token in Browser
```javascript
// Open DevTools Console

// Check localStorage (should only have remember_me)
console.log(localStorage.getItem('remember_me'));

// Try to access refresh token (should fail - HttpOnly)
console.log(document.cookie); // refresh_token_cookie not visible

// Check if logged in (requires React DevTools)
// Look for AuthContext → accessToken value
```

### Check Cookies in DevTools
1. Open DevTools (F12)
2. Go to Application tab
3. Storage → Cookies → http://localhost:5173
4. Look for `refresh_token_cookie`
5. Verify HttpOnly flag is checked

### Test Token Refresh
```bash
# Login and save cookies
curl -c cookies.txt -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test","remember_me":true}'

# Use cookies to refresh
curl -b cookies.txt -X POST http://localhost:5001/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"remember_me":true}'
```

## 🔒 Security Best Practices

### ✅ DO
- Use `credentials: 'include'` in fetch requests to send cookies
- Store only non-sensitive data in localStorage (like remember_me preference)
- Let browser handle HttpOnly cookies automatically
- Validate tokens on backend for every protected route
- Use HTTPS in production (set JWT_COOKIE_SECURE=True)

### ❌ DON'T
- Store tokens in localStorage (XSS vulnerability)
- Try to access HttpOnly cookies from JavaScript
- Send tokens in URL parameters
- Store sensitive user data in localStorage or cookies
- Use HTTP in production (cookies won't be secure)

## 📊 Token Lifecycle

```
User Logs In
    ↓
Access Token → Memory (React Context)
Refresh Token → HttpOnly Cookie
    ↓
Page Active (< 5 min before expiry)
    ↓
Auto-refresh scheduled
    ↓
5 Minutes Before Expiry
    ↓
Frontend calls /auth/refresh (cookies sent automatically)
    ↓
New Access Token → Memory
New Refresh Token → HttpOnly Cookie
    ↓
Repeat until logout or refresh token expires
    ↓
User Logs Out
    ↓
Access Token cleared from memory
Refresh Token cookie cleared (max_age=0)
    ↓
User Refreshes Page
    ↓
Try to restore session via /auth/refresh
    ↓
If cookie valid: New access token + stay logged in
If cookie invalid/missing: Redirect to login
```

## 📁 Key Files

### Backend
- `sentinel_login/backend/app.py` - Flask app with CORS
- `sentinel_login/backend/config.py` - JWT cookie config
- `sentinel_login/backend/routes/auth_routes.py` - All auth endpoints
- `sentinel_login/backend/models/user.py` - User model

### Frontend
- `sentinel_login/frontend/src/contexts/AuthContext.jsx` - Token management
- `sentinel_login/frontend/src/app.jsx` - App wrapper with AuthProvider
- `sentinel_login/frontend/src/pages/Patriot-Login/Patriot-Login.jsx` - Login page
- `sentinel_login/frontend/src/pages/Register/Register.jsx` - Registration page
- `sentinel_login/frontend/src/pages/PasswordReset/PasswordReset.jsx` - Password reset

### Shared Components
- `shared/ui/components/Button/` - Reusable button
- `shared/ui/components/Checkbox/` - Reusable checkbox
- `shared/ui/components/TextBox/` - Reusable text input
- `shared/ui/components/PasswordTextBox/` - Password input with toggle
- `shared/ui/components/ErrorBoundary/` - Error handling

## 🧪 Testing

### Run Tests
```bash
# Test secure token storage
python test_secure_token_storage.py

# Test Remember Me functionality
python test_remember_me.py

# Test logout functionality
python test_logout.py

# Test error boundaries
python test_error_boundaries.py
```

## 📚 Documentation

- [SECURE_TOKEN_STORAGE.md](./SECURE_TOKEN_STORAGE.md) - Detailed implementation guide
- [README.md](./sentinel_login/README.md) - Project overview
- [START_SCRIPT_GUIDE.md](./START_SCRIPT_GUIDE.md) - How to start all services

## 🆘 Common Issues

### Issue: "Missing cookie 'refresh_token_cookie'"
**Solution:** Make sure `credentials: 'include'` is set in fetch requests

### Issue: "CORS error"
**Solution:** Check that backend CORS allows credentials and frontend origin

### Issue: Token expired but not refreshing
**Solution:** Check that scheduleTokenRefresh is being called after login

### Issue: Logout not clearing cookie
**Solution:** Verify backend logout endpoint sets max_age=0

### Issue: Can't access token in browser
**Solution:** This is expected! Access token is in memory (React Context), refresh token is HttpOnly

## 🎯 Production Deployment

1. Set environment variables:
   ```bash
   JWT_COOKIE_SECURE=True
   JWT_SECRET_KEY=<strong-secret-key>
   FLASK_ENV=production
   ```

2. Update CORS origins in `app.py`:
   ```python
   CORS(app, 
        supports_credentials=True, 
        origins=["https://yourdomain.com"])
   ```

3. Enable HTTPS (required for secure cookies)

4. Test cookie behavior in production

5. Monitor token refresh logs
