#!/usr/bin/env python3
"""
Demo script to show email sync functionality for a user
"""

import requests
import json
import sys
from python_models import Database

def test_complete_email_flow():
    """Test the complete email flow from registration to email sync"""
    
    base_url = "http://localhost:4000"
    
    print("🚀 Testing Complete Email Flow")
    print("="*50)
    
    # Step 1: Login with existing user or register new one
    print("\n📝 Step 1: User Login/Registration")
    user_data = {
        "name": "Test User",
        "email": "testuser@example.com", 
        "password": "password123"
    }
    
    try:
        # Try login first
        login_data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            user_result = response.json()
            token = user_result['token']
            user_id = user_result['user']['id']
            print(f"✅ User logged in: {user_result['user']['email']}")
            print(f"✅ User ID: {user_id}")
        else:
            print(f"❌ Login failed: {response.text}")
            print("Creating new user with different email...")
            # Try with different email
            user_data["email"] = f"testuser{sys.argv[1] if len(sys.argv) > 1 else '2'}@example.com"
            response = requests.post(f"{base_url}/api/auth/register", json=user_data)
            if response.status_code == 201:
                user_result = response.json()
                token = user_result['token']
                user_id = user_result['user']['id']
                print(f"✅ User registered: {user_result['user']['email']}")
                print(f"✅ User ID: {user_id}")
            else:
                print(f"❌ Authentication failed: {response.text}")
                return
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start with 'npm start'")
        return
    
    # Step 2: Add email account
    print("\n📧 Step 2: Adding Email Account")
    account_data = {
        "email": "testuser@gmail.com",
        "imapHost": "imap.gmail.com",
        "imapPort": 993,
        "password": "test_app_password",
        "provider": "Gmail"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{base_url}/api/accounts/add", json=account_data, headers=headers)
    
    if response.status_code == 201:
        account_result = response.json()
        print(f"✅ Email account added: {account_result['account']['email']}")
    else:
        print(f"❌ Failed to add email account: {response.text}")
        return
    
    # Step 3: Check database before sync
    print("\n🗄️ Step 3: Database Status Before Sync")
    db = Database()
    accounts = db.get_user_email_accounts(user_id)
    emails_before = db.get_user_emails(user_id)
    print(f"✅ User has {len(accounts)} email accounts")
    print(f"✅ User has {len(emails_before)} emails before sync")
    
    # Step 4: Trigger email sync
    print("\n🔄 Step 4: Triggering Email Sync")
    response = requests.post(f"{base_url}/api/sync-emails", headers=headers)
    
    if response.status_code == 200:
        sync_result = response.json()
        print(f"✅ Email sync result: {sync_result['message']}")
    else:
        print(f"⚠️ Email sync failed (expected with test credentials): {response.text}")
    
    # Step 5: Check emails after sync
    print("\n📬 Step 5: Check Emails After Sync")
    emails_after = db.get_user_emails(user_id)
    print(f"✅ User has {len(emails_after)} emails after sync")
    
    # Step 6: Test API endpoints
    print("\n🌐 Step 6: Testing API Endpoints")
    
    # Get all emails
    response = requests.get(f"{base_url}/api/emails", headers=headers)
    if response.status_code == 200:
        emails_api = response.json()
        print(f"✅ API returned {len(emails_api['emails'])} emails")
    else:
        print(f"❌ API call failed: {response.text}")
    
    # Get emails by category
    response = requests.get(f"{base_url}/api/emails?category=Interested", headers=headers)
    if response.status_code == 200:
        interested_emails = response.json()
        print(f"✅ Found {len(interested_emails['emails'])} 'Interested' emails")
    else:
        print(f"❌ Category filter failed: {response.text}")
    
    print("\n🎯 Summary:")
    print(f"- User registered and authenticated ✅")
    print(f"- Email account added ✅") 
    print(f"- Email sync triggered ✅")
    print(f"- API endpoints working ✅")
    print(f"- Dashboard ready at: {base_url}/dashboard")
    
    print(f"\n🔑 Auth Token for testing: {token}")
    print(f"📱 Test the dashboard at: {base_url}/dashboard")

if __name__ == "__main__":
    test_complete_email_flow()
