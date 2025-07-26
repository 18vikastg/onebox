#!/usr/bin/env python3
"""
Test authentication flow to debug "Access token required" error
"""

import requests
import json

BASE_URL = "http://localhost:4000"

def test_auth_flow():
    print("🔍 Testing Authentication Flow")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Server Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Server Health Check Failed: {e}")
        return
    
    # Test 2: Try to access dashboard without authentication
    print("\n🔓 Testing unauthorized dashboard access...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print(f"   ✅ Correctly redirected to login (Location: {response.headers.get('Location', 'Not specified')})")
        else:
            print(f"   ❌ Unexpected response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Try to access API without authentication
    print("\n🔓 Testing unauthorized API access...")
    try:
        response = requests.get(f"{BASE_URL}/api/emails")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            result = response.json()
            print(f"   ✅ Correctly returned 401: {result}")
        else:
            print(f"   ❌ Unexpected response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Register a test user
    print("\n📝 Testing user registration...")
    test_user = {
        "email": "debug_user@test.com",
        "password": "testpass123",
        "name": "Debug User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"   ✅ Registration successful!")
            print(f"   User ID: {result['user']['id']}")
            print(f"   Token: {result['token'][:20]}...")
            return result['token']
        elif response.status_code == 400:
            result = response.json()
            if "User already exists" in result.get('error', ''):
                print(f"   ℹ️  User already exists, trying login...")
                return test_login(test_user)
            else:
                print(f"   ❌ Registration failed: {result}")
        else:
            print(f"   ❌ Unexpected registration response: {response.text}")
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
    
    return None

def test_login(user_data):
    """Test user login"""
    print("\n🔑 Testing user login...")
    
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login successful!")
            print(f"   User: {result['user']['email']}")
            print(f"   Token: {result['token'][:20]}...")
            return result['token']
        else:
            result = response.json()
            print(f"   ❌ Login failed: {result}")
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    return None

def test_authenticated_requests(token):
    """Test authenticated API requests"""
    print("\n🔐 Testing authenticated requests...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test getting user profile
    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        print(f"   Profile API Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Profile retrieved: {result['user']['email']}")
        else:
            print(f"   ❌ Profile failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Profile error: {e}")
    
    # Test getting emails
    try:
        response = requests.get(f"{BASE_URL}/api/emails", headers=headers)
        print(f"   Emails API Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Emails retrieved: {len(result['emails'])} emails")
        else:
            print(f"   ❌ Emails failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Emails error: {e}")
    
    # Test getting accounts
    try:
        response = requests.get(f"{BASE_URL}/api/accounts", headers=headers)
        print(f"   Accounts API Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Accounts retrieved: {len(result['accounts'])} accounts")
        else:
            print(f"   ❌ Accounts failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Accounts error: {e}")

def test_browser_session():
    """Test browser session with cookies"""
    print("\n🌐 Testing browser session with cookies...")
    
    session = requests.Session()
    
    # Try to access dashboard (should redirect to login)
    try:
        response = session.get(f"{BASE_URL}/dashboard", allow_redirects=False)
        print(f"   Dashboard access (no auth): {response.status_code}")
        
        if response.status_code == 302:
            print(f"   ✅ Redirected to: {response.headers.get('Location')}")
        
        # Login via API to get cookie
        login_data = {
            "email": "debug_user@test.com",
            "password": "testpass123"
        }
        
        response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            # Now try dashboard with cookie
            response = session.get(f"{BASE_URL}/dashboard")
            print(f"   Dashboard with cookie: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Dashboard access successful with cookie!")
            else:
                print(f"   ❌ Dashboard access failed: {response.text[:200]}...")
        
    except Exception as e:
        print(f"   ❌ Browser session error: {e}")

if __name__ == "__main__":
    try:
        # Run authentication tests
        token = test_auth_flow()
        
        if token:
            test_authenticated_requests(token)
        
        test_browser_session()
        
        print("\n" + "=" * 50)
        print("🔍 DEBUGGING TIPS:")
        print("1. Make sure you're logged in at http://localhost:4000/login")
        print("2. Check browser cookies for 'auth_token'")
        print("3. For API calls, include 'Authorization: Bearer <token>' header")
        print("4. Check browser console for any JavaScript errors")
        print("5. Try logging out and logging back in")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
