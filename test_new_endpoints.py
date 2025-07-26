#!/usr/bin/env python3
"""
Test the new API endpoints with authentication
"""

import requests
import json

BASE_URL = "http://localhost:4000"

def test_new_endpoints():
    print("🔍 Testing New API Endpoints")
    print("=" * 50)
    
    # First, login to get a token
    login_data = {
        "email": "debug_user@test.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print("❌ Failed to login")
        return
    
    token = response.json()['token']
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test /api/stats endpoint
    print("\n📊 Testing /api/stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Stats retrieved:")
            print(f"      Total Emails: {stats['totalEmails']}")
            print(f"      Total Accounts: {stats['totalAccounts']}")
            print(f"      Categories: {stats['categories']}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test /api/search endpoint
    print("\n🔍 Testing /api/search...")
    try:
        response = requests.get(f"{BASE_URL}/api/search?limit=10", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Search results:")
            print(f"      Total found: {result['total']}")
            print(f"      Emails returned: {len(result['emails'])}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test browser session with cookies for API calls
    print("\n🌐 Testing API calls with cookie authentication...")
    session = requests.Session()
    
    # Login to get cookie
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        print("   ✅ Cookie session established")
        
        # Test stats with cookie
        response = session.get(f"{BASE_URL}/api/stats")
        print(f"   Stats with cookie: {response.status_code}")
        
        # Test search with cookie
        response = session.get(f"{BASE_URL}/api/search")
        print(f"   Search with cookie: {response.status_code}")
    else:
        print("   ❌ Failed to establish cookie session")

if __name__ == "__main__":
    test_new_endpoints()
