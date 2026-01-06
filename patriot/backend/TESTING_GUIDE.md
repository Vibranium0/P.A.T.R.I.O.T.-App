# P.A.T.R.I.O.T. Backend Authentication - Testing Guide

## Quick Start Testing

### 1. Verify All Routes Are Protected

```bash
# Try accessing a route without token - should get 401
curl http://localhost:5000/api/bills/

# Response:
# {
#   "msg": "Missing Authorization Header"
# }
```

### 2. Get a Valid Token

```bash
# Login via frontend or Sentinel
# Copy the token from localStorage after login
TOKEN="<paste_token_here>"

# Test it's valid
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/bills/

# Should get 200 with bills data
```

### 3. Test All Routes

```bash
TOKEN="<your_valid_token>"

# Dashboard routes
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/dashboard/summary

# Bills routes
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/bills/

# Funds routes
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/funds/

# Transactions routes
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/transactions/

# Income routes
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/income/

# Debts routes
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/debts/

# Reports routes
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/reports/

# Financial accounts routes
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/financial-accounts/

# Households routes
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/households/
```

### 4. Test Error Cases

```bash
# Missing token
curl http://localhost:5000/api/bills/
# Expected: 401 Unauthorized

# Invalid token
curl -H "Authorization: Bearer invalid_token" http://localhost:5000/api/bills/
# Expected: 401 Signature verification failed

# Malformed header
curl -H "Authorization: invalid" http://localhost:5000/api/bills/
# Expected: 401 Invalid Authorization header

# Token from different secret
# (simulate by manually creating JWT with different secret)
# Expected: 401 Signature verification failed
```

## Full Integration Test

### Step 1: Start All Services

```bash
# Terminal 1: Sentinel
cd /workspaces/P.A.T.R.I.O.T.-App
python -m flask --app sentinel_login.backend.app run --port 5001

# Terminal 2: P.A.T.R.I.O.T. Backend
cd /workspaces/P.A.T.R.I.O.T.-App
python -m flask --app patriot.backend.app run --port 5000

# Terminal 3: P.A.T.R.I.O.T. Frontend
cd /workspaces/P.A.T.R.I.O.T.-App/patriot/frontend
npm run dev
```

### Step 2: Test via Frontend

1. Navigate to `http://localhost:5174`
2. Should redirect to Sentinel login at `http://localhost:5173`
3. Log in with test credentials
4. Should return to P.A.T.R.I.O.T. dashboard
5. Create a bill/fund/transaction
6. Open DevTools → Network tab
7. Verify all API requests have `Authorization: Bearer <token>` header
8. Check response includes only user's data

### Step 3: Test via API

```bash
# Get token from browser localStorage after login
# Copy the token value

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Create a bill
curl -X POST http://localhost:5000/api/bills/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electric Bill",
    "amount": 150,
    "due_date": "2026-01-15",
    "category": "Utilities"
  }'

# List bills
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/bills/

# Update bill (if you got an ID from create response)
curl -X PUT http://localhost:5000/api/bills/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 160}'

# Delete bill
curl -X DELETE http://localhost:5000/api/bills/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Step 4: Verify User Isolation

```bash
# Create two users in Sentinel
# User A: user_a
# User B: user_b

# Log in as User A
# Get token_a
# Create a bill as User A

# Log in as User B
# Get token_b
# Try to access User A's bill using token_b

TOKEN_A="<user_a_token>"
TOKEN_B="<user_b_token>"

# User B tries to access with their token
curl -H "Authorization: Bearer $TOKEN_B" http://localhost:5000/api/bills/

# Should only see User B's bills, not User A's
# (Even if bill IDs are known, household_id filtering prevents cross-user access)
```

## Expected Responses

### Success (200 OK)

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/bills/

# Response:
# {
#   "bills": [
#     {
#       "id": 1,
#       "name": "Electric Bill",
#       "amount": 150,
#       "due_date": "2026-01-15",
#       "household_id": 123,
#       ...
#     }
#   ],
#   "total": 1
# }
```

### Missing Token (401 Unauthorized)

```bash
curl http://localhost:5000/api/bills/

# Response:
# {
#   "msg": "Missing Authorization Header"
# }
# HTTP Status: 401
```

### Invalid Token (401 Unauthorized)

```bash
curl -H "Authorization: Bearer invalid" http://localhost:5000/api/bills/

# Response:
# {
#   "msg": "Signature verification failed"
# }
# HTTP Status: 401
```

### No Household (404 Not Found)

```bash
# If JWT doesn't have household_id

curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/bills/

# Response:
# {
#   "error": "No household found for user"
# }
# HTTP Status: 404
```

### Expired Token (401 Unauthorized)

```bash
# Token older than 30 minutes

curl -H "Authorization: Bearer $EXPIRED_TOKEN" http://localhost:5000/api/bills/

# Response:
# {
#   "msg": "Token has expired"
# }
# HTTP Status: 401
```

## Debugging

### Check Token Contents

```bash
# In browser console after login:
const token = localStorage.getItem('token');
console.log(token);

// Decode (without verification) at jwt.io
// Should see claims like:
// {
//   "sub": "123",
//   "username": "test_user",
//   "household_id": "456",
//   "iat": 1704326400,
//   "exp": 1704330000
// }
```

### Check Backend Logs

```bash
# When testing with curl, check P.A.T.R.I.O.T. backend logs for:
# - "GET /api/bills/ HTTP/1.1" - successful request
# - "401 UNAUTHORIZED" - token validation failed
# - "404 NOT FOUND" - household not found
```

### Verify Middleware is Active

```bash
# In backend Python code:
from patriot.backend.app import app

# Verify jwt is initialized
print(app.config['JWT_SECRET_KEY'])  # Should not be None
print(app.extensions.get('flask-jwt-extended'))  # Should exist
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Always 401 | JWT_SECRET_KEY doesn't match between backends | Verify .env has same key in both |
| Missing households | User not assigned to household | Create household and add user in Sentinel |
| Token expires quickly | JWT_ACCESS_MINUTES too low | Increase in config or .env |
| CORS errors | Frontend can't reach backend | Check CORS config in app.py |
| Authorization header not sent | Frontend not adding token | Check shared/api/client.js interceptor |

---

**Ready for Production Testing!**
