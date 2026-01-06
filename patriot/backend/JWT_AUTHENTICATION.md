# P.A.T.R.I.O.T. Backend Authentication Implementation

## Overview

The P.A.T.R.I.O.T. backend now requires JWT authentication on all protected routes with proper user-based data filtering.

## ✅ What Was Implemented

### 1. **JWT Middleware**
- Updated `shared/auth/token_required.py` to use Flask-JWT-Extended
- All routes now use `@jwt_required()` decorator
- Proper 401 error responses for missing/invalid tokens

### 2. **User Context Extraction**
- New function `get_current_user_id()` - Gets user ID from JWT token
- New function `get_user_claims()` - Gets all JWT claims
- All routes use `get_current_household_id()` - Gets household from JWT

### 3. **Data Filtering by User**
- All queries filter by `household_id` from JWT claims
- Routes verify user has access to household
- Return 404 if household not found for user

### 4. **Proper Error Handling**
- 401 Unauthorized - Missing or invalid token
- 404 Not Found - Household not found for user
- 400 Bad Request - Invalid input
- 500 Server Error - Database errors

### 5. **Applied to All Routes**
```
✅ /api/dashboard/*        - All dashboard routes protected
✅ /api/accounts/*         - All account routes protected
✅ /api/financial-accounts/* - All financial account routes protected
✅ /api/bills/*            - All bill routes protected
✅ /api/funds/*            - All fund routes protected (already using jwt_required)
✅ /api/transactions/*     - All transaction routes protected
✅ /api/income/*           - All income routes protected
✅ /api/reports/*          - All report routes protected
✅ /api/debts/*            - All debt routes protected
✅ /api/households/*       - All household routes protected (shared routes)
```

## 🔐 How It Works

### Request Flow

```
1. Frontend sends request with Authorization header
   GET /api/bills/ 
   Authorization: Bearer <jwt_token>

2. @jwt_required() decorator validates token
   - Checks Authorization header format
   - Verifies JWT signature using JWT_SECRET_KEY
   - Extracts claims (user_id, household_id, username)
   - Returns 401 if invalid

3. Route handler accesses user context
   household_id = get_current_household_id()  # From JWT claims
   user_id = get_current_user_id()            # From JWT identity

4. Database queries filtered by household_id
   bills = Bill.query.filter_by(
       household_id=household_id,
       is_active=True
   ).all()

5. Return user-specific data
   {
     "bills": [...],
     "total": 5
   }
```

### JWT Token Claims

Tokens issued by Sentinel include:

```json
{
  "sub": "user_id",           // JWT subject (unique identifier)
  "username": "john_doe",     // Username
  "household_id": "456",      // Household association
  "iat": 1704326400,          // Issued at
  "exp": 1704330000           // Expiration (30 min default)
}
```

## 📋 Protected Routes

### Dashboard Routes
```
GET /api/dashboard/summary              - Get dashboard summary
GET /api/dashboard/charts/bills         - Get bills chart data
GET /api/dashboard/charts/funds         - Get funds chart data  
GET /api/dashboard/charts/income        - Get income chart data
GET /api/dashboard/recent-transactions  - Get recent transactions
```

### Bill Routes
```
GET /api/bills/                - List all bills
POST /api/bills/               - Create new bill
PUT /api/bills/<id>            - Update bill
DELETE /api/bills/<id>         - Delete bill
GET /api/bills/<id>/schedule   - Get bill schedule
GET /api/bills/forecast        - Get bill forecast
```

### Fund Routes
```
GET /api/funds/                - List all funds
POST /api/funds/               - Create new fund
PUT /api/funds/<id>            - Update fund
DELETE /api/funds/<id>         - Delete fund
POST /api/funds/<id>/deposit   - Deposit to fund
POST /api/funds/<id>/withdraw  - Withdraw from fund
```

### Transaction Routes
```
GET /api/transactions/         - List all transactions
POST /api/transactions/        - Create transaction
PUT /api/transactions/<id>     - Update transaction
DELETE /api/transactions/<id>  - Delete transaction
```

### Other Routes
```
GET /api/accounts/             - List financial accounts
GET /api/income/               - List income entries
GET /api/reports/              - Get financial reports
GET /api/debts/                - List debts
GET /api/households/           - List user's households
```

## 🧪 Testing Authentication

### 1. Test with Valid Token

```bash
# Get token from Sentinel login first
TOKEN="<jwt_token_from_login>"

# Test protected route
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/bills/

# Response (200):
# {
#   "bills": [...],
#   "total": 5
# }
```

### 2. Test without Token

```bash
# Request without Authorization header
curl http://localhost:5000/api/bills/

# Response (401):
# {
#   "msg": "Missing Authorization Header"
# }
```

### 3. Test with Invalid Token

```bash
# Request with invalid token
curl -H "Authorization: Bearer invalid_token_here" \
  http://localhost:5000/api/bills/

# Response (401):
# {
#   "msg": "Signature verification failed"
# }
```

### 4. Test Expired Token

```bash
# Request with expired token (older than 30 minutes)
curl -H "Authorization: Bearer <expired_token>" \
  http://localhost:5000/api/bills/

# Response (401):
# {
#   "msg": "Token has expired"
# }
```

### 5. Test No Household

```bash
# If user has no household_id in JWT claims
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/bills/

# Response (404):
# {
#   "error": "No household found for user"
# }
```

## 🔌 Using Authentication in Code

### Getting User Context

```python
from shared.auth.token_required import get_current_user_id, get_user_claims
from shared.utils.household_helpers import get_current_household_id
from flask_jwt_extended import jwt_required

@app.route("/api/example")
@jwt_required()
def example_route():
    # Get user information
    user_id = get_current_user_id()
    household_id = get_current_household_id()
    claims = get_user_claims()
    
    print(f"User ID: {user_id}")
    print(f"Household: {household_id}")
    print(f"Username: {claims.get('username')}")
    
    # Query filtered by household
    items = Item.query.filter_by(
        household_id=household_id
    ).all()
    
    return jsonify([item.to_dict() for item in items]), 200
```

### Manual Token Verification

```python
from shared.auth.token_required import verify_token

# Only use this if you need manual verification
result = verify_token()
if result:
    user_id, claims = result
    print(f"Token valid for user {user_id}")
else:
    print("Token invalid or missing")
```

## 📁 Files Modified

### Core Auth Files
- `shared/auth/token_required.py` - Updated middleware with Flask-JWT-Extended
- `shared/utils/household_helpers.py` - Already has user context functions

### Route Files (All Updated)
- `patriot/backend/routes/dashboard_routes.py` - `@jwt_required()`
- `patriot/backend/routes/bills_routes.py` - `@jwt_required()`
- `patriot/backend/routes/funds_routes.py` - Already using `@jwt_required()`
- `patriot/backend/routes/transactions_routes.py` - `@jwt_required()`
- `patriot/backend/routes/income_routes.py` - `@jwt_required()`
- `patriot/backend/routes/debts_routes.py` - `@jwt_required()`
- `patriot/backend/routes/financial_accounts_routes.py` - `@jwt_required()`
- `patriot/backend/routes/reports_routes.py` - `@jwt_required()`

## 🔒 Security Features

1. **JWT Signature Validation** - Flask-JWT-Extended verifies token signature
2. **Token Expiration** - Default 30 minutes (configurable via `JWT_ACCESS_MINUTES`)
3. **Household Isolation** - All data filtered by household_id
4. **401 Responses** - Proper error codes for missing/invalid tokens
5. **User Context** - All operations tracked to user_id

## ⚠️ Important Notes

1. **JWT_SECRET_KEY Must Match** - Both Sentinel and P.A.T.R.I.O.T. must use same key
2. **Token in Authorization Header** - Must be: `Authorization: Bearer <token>`
3. **Household Required** - All users must have household_id in JWT claims
4. **No Token in URL** - Never send tokens via URL parameters
5. **HTTPS in Production** - Always use HTTPS for token transmission

## 🚀 Verification Checklist

- [x] All routes use `@jwt_required()` decorator
- [x] All queries filter by `household_id`
- [x] All routes check for household existence
- [x] Proper 401/404 error handling
- [x] User context functions available
- [x] JWT token validation working
- [x] Token expiration enforced
- [x] Sentinel integration enabled

## 🧪 Full Integration Test

```bash
# 1. Start backends
python -m flask --app sentinel_login.backend.app run --port 5001 &
python -m flask --app patriot.backend.app run --port 5000 &

# 2. Start frontend
cd patriot/frontend && npm run dev &

# 3. Test flow
# - Navigate to http://localhost:5174
# - Login via Sentinel
# - Create a bill
# - Check network tab: Authorization header present
# - Verify response is user-specific
# - Logout and access route: should redirect to login

# 4. Test via curl
TOKEN="<from_login>"
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/bills/
curl http://localhost:5000/api/bills/  # Should be 401
```

## 📚 Additional Resources

- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## 🎯 Next Steps (Optional)

1. **Token Refresh** - Implement `/auth/refresh` endpoint
2. **Logout Tracking** - Track token revocation
3. **Audit Logging** - Log all API access
4. **Rate Limiting** - Limit requests per user
5. **Role-Based Access** - Add permissions/roles to JWT

---

**Status**: ✅ COMPLETE AND TESTED  
**Date**: January 5, 2026  
**All P.A.T.R.I.O.T. Routes Protected with JWT**
