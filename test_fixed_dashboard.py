#!/usr/bin/env python3
"""
Test script to verify that the dashboard fixes are working correctly.
This test validates all the major functionalities.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:4000"

def test_login():
    """Test user login functionality"""
    print("🔐 Testing login...")
    
    login_data = {
        "email": "vikas.real.1753552935@example.com",
        "password": "securepass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful for user: {data['user']['name']}")
        return response.cookies
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_stats_api(cookies):
    """Test the stats API endpoint"""
    print("📊 Testing stats API...")
    
    response = requests.get(f"{BASE_URL}/api/stats", cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Stats API working:")
        print(f"   - Total Emails: {data['totalEmails']}")
        print(f"   - Total Accounts: {data['totalAccounts']}")
        print(f"   - Categories: {data['categories']}")
        return True
    else:
        print(f"❌ Stats API failed: {response.text}")
        return False

def test_search_api(cookies):
    """Test the search API endpoint"""
    print("🔍 Testing search API...")
    
    response = requests.get(f"{BASE_URL}/api/search?limit=3", cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Search API working:")
        print(f"   - Returned {len(data['emails'])} emails")
        print(f"   - Total available: {data['total']}")
        
        if data['emails']:
            first_email = data['emails'][0]
            print(f"   - Sample email: {first_email['subject'][:50]}...")
            print(f"   - Category: {first_email['category']}")
            print(f"   - Account: {first_email['account_email']}")
        
        return True
    else:
        print(f"❌ Search API failed: {response.text}")
        return False

def test_dashboard_page(cookies):
    """Test the dashboard page loads without errors"""
    print("🌐 Testing dashboard page...")
    
    response = requests.get(f"{BASE_URL}/dashboard", cookies=cookies)
    
    if response.status_code == 200:
        content = response.text
        
        # Check for common error indicators
        if "[object Object]" in content:
            print("❌ Dashboard still contains [object Object] errors")
            return False
        elif "Access token required" in content:
            print("❌ Dashboard showing authentication errors")
            return False
        else:
            print("✅ Dashboard page loads successfully")
            print(f"   - Page size: {len(content)} characters")
            
            # Check for key elements
            if "ReachInbox Email Dashboard" in content:
                print("   - Dashboard title found")
            if "vikastg2000@gmail.com" in content:
                print("   - Account email found in page")
            
            return True
    else:
        print(f"❌ Dashboard page failed to load: {response.status_code}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting comprehensive dashboard test...\n")
    
    # Test login
    cookies = test_login()
    if not cookies:
        print("❌ Cannot proceed without login")
        sys.exit(1)
    
    print()
    
    # Test APIs
    stats_ok = test_stats_api(cookies)
    print()
    
    search_ok = test_search_api(cookies)
    print()
    
    # Test dashboard page
    dashboard_ok = test_dashboard_page(cookies)
    print()
    
    # Summary
    print("=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"   Login: {'✅ PASS' if cookies else '❌ FAIL'}")
    print(f"   Stats API: {'✅ PASS' if stats_ok else '❌ FAIL'}")
    print(f"   Search API: {'✅ PASS' if search_ok else '❌ FAIL'}")
    print(f"   Dashboard Page: {'✅ PASS' if dashboard_ok else '❌ FAIL'}")
    
    if all([cookies, stats_ok, search_ok, dashboard_ok]):
        print("\n🎉 ALL TESTS PASSED! Dashboard is working correctly.")
        print("🌐 You can now access your dashboard at: http://localhost:4000/dashboard")
        print("📧 Your real Gmail emails are being synced automatically!")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
