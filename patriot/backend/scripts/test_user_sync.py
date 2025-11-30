#!/usr/bin/env python3
"""
Test script for Sentinel Systems user sync.
Tests that users can be synced between Sentinel apps.
"""

import requests
import json
import time
from typing import Dict, Optional

# Configuration
APP_1_URL = "http://localhost:5001"
APP_2_URL = "http://localhost:5002"  # You'll need to run a second instance

# Test user
TEST_USER = {
    "username": "synctest",
    "email": "synctest@example.com",
    "password": "synctest123"
}


def print_step(step: str, message: str):
    """Print a test step"""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {message}")
    print('='*60)


def register_user(app_url: str, user: Dict) -> bool:
    """Register a user on an app"""
    try:
        response = requests.post(
            f"{app_url}/api/auth/register",
            json=user,
            timeout=5
        )
        
        if response.status_code == 201:
            print(f"✅ User registered successfully on {app_url}")
            return True
        else:
            print(f"❌ Registration failed: {response.json()}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
        return False


def login_user(app_url: str, identifier: str, password: str) -> Optional[str]:
    """Login user and return JWT token"""
    try:
        response = requests.post(
            f"{app_url}/api/auth/login",
            json={"email": identifier, "password": password},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful on {app_url}")
            print(f"   Username: {data.get('username')}")
            print(f"   Email: {data.get('email')}")
            return data.get('access_token')
        else:
            error = response.json().get('error', 'Unknown error')
            print(f"❌ Login failed: {error}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
        return None


def check_health(app_url: str) -> bool:
    """Check if app is online and part of Sentinel"""
    try:
        response = requests.get(
            f"{app_url}/api/sentinel/health",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {app_url} is online")
            print(f"   App Name: {data.get('app_name')}")
            print(f"   Sentinel System: {data.get('sentinel_system')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
        print(f"   Make sure {app_url} is running!")
        return False


def main():
    """Run the sync test"""
    print("\n" + "="*60)
    print("SENTINEL SYSTEMS - USER SYNC TEST")
    print("="*60)
    
    # Step 1: Check both apps are online
    print_step("1", "Checking if both apps are online")
    
    app1_online = check_health(APP_1_URL)
    
    print()
    
    if not app1_online:
        print("\n⚠️  App 1 is not running. Starting minimal test...")
        print("   Run: cd backend && python app.py")
        return
    
    # For now, we'll just test with one app
    print("\nℹ️  To test user sync between apps:")
    print("   1. Copy your patriot-app folder to patriot-app-copy")
    print("   2. Edit patriot-app-copy/backend/.env:")
    print("      CURRENT_APP_URL=http://localhost:5002")
    print("      SENTINEL_APPS=http://localhost:5001")
    print("   3. Run second instance: cd patriot-app-copy/backend && python app.py")
    print("   4. Run this test script again")
    
    # Step 2: Register user on App 1
    print_step("2", "Registering user on App 1")
    if not register_user(APP_1_URL, TEST_USER):
        return
    
    print("\n⏳ Waiting 2 seconds...")
    time.sleep(2)
    
    # Step 3: Login to App 1 to verify
    print_step("3", "Logging in to App 1 (should work)")
    token1 = login_user(APP_1_URL, TEST_USER["email"], TEST_USER["password"])
    if not token1:
        return
    
    print("\n✅ TEST PASSED: User can register and login to App 1")
    print("\nℹ️  To test cross-app sync:")
    print("   1. Set up App 2 as described above")
    print("   2. Try to login to App 2 with the same credentials")
    print("   3. App 2 should automatically sync the user from App 1")


if __name__ == "__main__":
    main()
