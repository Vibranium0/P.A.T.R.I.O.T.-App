# Sentinel Systems - User Sync Guide

## Overview

The Sentinel Systems user sync allows multiple self-hosted apps to share user accounts automatically. When a user registers on one app (e.g., PATRIOT), they can login to any other Sentinel app without re-registering.

## How It Works

1. **User registers on App A** (e.g., PATRIOT)
   - Account is created in App A's database
   
2. **User tries to login to App B** (e.g., another Sentinel app)
   - App B doesn't find the user locally
   - App B queries other Sentinel apps via API
   - Finds user in App A's database
   - Automatically creates a copy in App B's database
   - User is logged in successfully

3. **Subsequent logins** work normally (user now exists in both databases)

## Architecture

```
┌─────────────────────────────────────────────────┐
│  User registers on PATRIOT                      │
│  Email: user@example.com                        │
└─────────────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  PATRIOT Database     │
        │  Port: 5001           │
        │  Users table          │
        └───────────────────────┘
                    │
        User tries to login to App 2
                    │
                    ▼
        ┌───────────────────────┐
        │  App 2 Database       │
        │  Port: 5002           │
        │  No user found!       │
        └───────────────────────┘
                    │
        App 2 queries PATRIOT API:
        GET /api/sentinel/user-lookup?identifier=user@example.com
                    │
                    ▼
        ┌───────────────────────┐
        │  Auto-sync happens    │
        │  User copied to App 2 │
        │  Login succeeds!      │
        └───────────────────────┘
```

## Setup Instructions

### Step 1: Configure Environment Variables

Add these to your `.env` file for each Sentinel app:

```bash
# PATRIOT (.env)
CURRENT_APP_URL=http://localhost:5001
SENTINEL_APPS=http://localhost:5002,http://localhost:5003

# App 2 (.env)
CURRENT_APP_URL=http://localhost:5002
SENTINEL_APPS=http://localhost:5001,http://localhost:5003

# App 3 (.env)
CURRENT_APP_URL=http://localhost:5003
SENTINEL_APPS=http://localhost:5001,http://localhost:5002
```

**Important:** 
- `CURRENT_APP_URL` = This app's backend API URL
- `SENTINEL_APPS` = Comma-separated list of OTHER apps' backend API URLs
- Don't include the current app in SENTINEL_APPS

### Step 2: Copy Shared Module

Copy the `backend/shared/` folder to each new Sentinel app:

```bash
# When creating a new Sentinel app
cp -r patriot-app/backend/shared/ new-app/backend/shared/
```

### Step 3: Add Sync Endpoints

In your new app's `auth_routes.py`, add these endpoints (already included in PATRIOT):

```python
@auth_bp.route("/sentinel/user-lookup", methods=["GET"])
def sentinel_user_lookup():
    # ... (see auth_routes.py for implementation)

@auth_bp.route("/sentinel/health", methods=["GET"])
def sentinel_health():
    # ... (see auth_routes.py for implementation)
```

### Step 4: Update Login Route

In your login route, add the auto-sync logic (already included in PATRIOT):

```python
if not user:
    from shared.user_sync import get_sync_service
    sync_service = get_sync_service(current_app.config)
    
    if sync_service:
        user = sync_service.auto_sync_on_login(identifier, db.session, User)
```

## Testing the Sync

### Test with 2 Instances of PATRIOT

1. **Start first instance** (port 5001):
```bash
cd patriot-app/backend
python app.py
```

2. **Start second instance** (port 5002):
```bash
# Edit .env:
# CURRENT_APP_URL=http://localhost:5002
# SENTINEL_APPS=http://localhost:5001

cd patriot-app-copy/backend
python app.py
```

3. **Register on port 5001**:
```bash
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "test1234"}'
```

4. **Login on port 5002** (should auto-sync):
```bash
curl -X POST http://localhost:5002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test1234"}'
```

Check the logs - you should see:
```
User test@example.com not found locally, attempting Sentinel sync...
Found user test@example.com in app: http://localhost:5001
Successfully synced user test@example.com to local database
```

## Security Considerations

✅ **Password hashes are shared** - Already hashed, so secure
✅ **Verification tokens NOT shared** - Single-use, not synced
✅ **5 second timeout** - Won't hang if an app is offline
✅ **Each app validates independently** - Full auth on each app

## Production Deployment

For production with multiple servers:

```bash
# PATRIOT (on server 1)
CURRENT_APP_URL=https://patriot.yourserver.com/api
SENTINEL_APPS=https://app2.yourserver.com/api,https://app3.yourserver.com/api

# App 2 (on server 2)
CURRENT_APP_URL=https://app2.yourserver.com/api
SENTINEL_APPS=https://patriot.yourserver.com/api,https://app3.yourserver.com/api
```

## Troubleshooting

### User not syncing?

Check logs for errors:
```bash
tail -f backend/logs/app.log | grep sentinel
```

Common issues:
- Wrong URLs in SENTINEL_APPS
- Apps not running
- Firewall blocking requests
- Database permissions

### Test connectivity:

```bash
# Check if App 2 can reach PATRIOT
curl http://localhost:5001/api/sentinel/health

# Should return:
# {"status": "online", "app_name": "Patriot", "sentinel_system": true}
```

## Disabling Sync

To disable user sync (run app standalone):

```bash
# Don't set SENTINEL_APPS in .env
# Or set it to empty string
SENTINEL_APPS=
```

App will work normally but won't sync users.

## Future Enhancements

Potential additions:
- [ ] Bulk user sync script
- [ ] Admin panel to view synced users
- [ ] Real-time sync webhook (instead of on-demand)
- [ ] User profile updates sync across apps
- [ ] Centralized user management dashboard
