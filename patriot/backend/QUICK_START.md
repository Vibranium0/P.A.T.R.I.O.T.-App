# P.A.T.R.I.O.T. Backend - Sentinel Integration (QUICK START)

## ✅ What's New

P.A.T.R.I.O.T. backend now fully communicates with Sentinel Login backend.

## 🔧 Setup (3 Steps)

### 1. Set Shared Secret
Create `.env` in project root:
```bash
JWT_SECRET_KEY=your-shared-secret-key-here
```

### 2. Start Backends
```bash
# Terminal 1: Sentinel (port 5001)
python -m flask --app sentinel_login.backend.app run --port 5001

# Terminal 2: P.A.T.R.I.O.T. (port 5000)
python -m flask --app patriot.backend.app run --port 5000
```

### 3. Verify Connection
```bash
# Should return 200 with "status": "online"
curl http://localhost:5000/auth/sentinel/health
```

## 📡 New Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/validate` | GET | Validate JWT token (main endpoint) |
| `/auth/sentinel/health` | GET | Health check for Sentinel systems |
| `/auth/sentinel/token-info` | POST | Validate token for Sentinel backend |
| `/auth/debug/sentinel-status` | GET | Debug connection status |

## 🚀 How to Use in Code

```python
from patriot.backend.utils.sentinel_client import get_sentinel_client

sentinel = get_sentinel_client()

# Check if Sentinel is online
if sentinel.health_check():
    print("✅ Connected to Sentinel")

# Validate a token
result = sentinel.validate_token(token)
if result['valid']:
    print(f"User: {result['username']}")
```

## 🧪 Test Full Flow

1. Go to `http://localhost:5174`
2. Redirects to Sentinel login ✅
3. Log in successfully ✅
4. Returns to P.A.T.R.I.O.T. with token ✅
5. Check localStorage has `user_id` ✅

## 📚 Full Documentation

See `SENTINEL_INTEGRATION.md` for:
- Complete API documentation
- Architecture diagrams
- Testing procedures
- Troubleshooting guide
- Security considerations

## 🔍 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Is Sentinel running on port 5001? |
| Token validation fails | Is JWT_SECRET_KEY the same in both backends? |
| Unknown endpoint | Did you restart the backend after changes? |
| localhost:5000 not found | Is P.A.T.R.I.O.T. backend running? |

## ✨ Files Changed

- **Created**: `patriot/backend/utils/sentinel_client.py` (new utility)
- **Created**: `patriot/backend/SENTINEL_INTEGRATION.md` (docs)
- **Modified**: `patriot/backend/routes/auth_routes.py` (new endpoints)
- **Modified**: `patriot/backend/config.py` (Sentinel config)

---

**Status**: ✅ READY TO USE  
**Next**: Test the full authentication flow!
