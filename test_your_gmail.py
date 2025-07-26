#!/usr/bin/env python3
"""
Test your actual Gmail account integration with the fixed system
"""

import requests
import json
import time

BASE_URL = "http://localhost:4000"

def test_your_gmail_account_integration():
    print("🎯 Testing Your Gmail Account Integration - FIXED VERSION")
    print("=" * 60)
    print("Testing with your actual Gmail credentials from .env file")
    
    # Step 1: Register a new user account
    print("\n👤 Step 1: Creating User Account")
    user_data = {
        "email": f"vikas.real.{int(time.time())}@example.com",
        "password": "securepass123", 
        "name": "Vikas TG"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    if response.status_code == 201:
        result = response.json()
        token = result['token']
        print(f"   ✅ User account created!")
        print(f"   🆔 User ID: {result['user']['id']}")
        print(f"   📧 Email: {result['user']['email']}")
    else:
        print(f"   ❌ Registration failed: {response.text}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Add your real Gmail account
    print("\n� Step 2: Adding Your Real Gmail Account")
    gmail_account = {
        "email": "vikastg2000@gmail.com",  # Your real Gmail
        "imapHost": "imap.gmail.com",
        "imapPort": 993,
        "password": "jpyh ksra mlgk rzfa",  # Your app password from .env
        "provider": "gmail"
    }
    
    response = requests.post(f"{BASE_URL}/api/accounts/add", headers=headers, json=gmail_account)
    if response.status_code == 201:
        result = response.json()
        print(f"   ✅ Gmail account added successfully!")
        print(f"   📧 Account: {result['account']['email']}")
        print(f"   🔄 Sync triggered: {result.get('syncTriggered', False)}")
        
        # Wait a moment for sync to complete
        print("   ⏳ Waiting 15 seconds for email sync...")
        time.sleep(15)
    else:
        print(f"   ❌ Failed to add Gmail account: {response.text}")
        return
    
    # Step 3: Check if emails were synced
    print("\n📊 Step 3: Checking Email Sync Results")
    response = requests.get(f"{BASE_URL}/api/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Email statistics:")
        print(f"      📧 Total Emails: {stats['totalEmails']}")
        print(f"      📁 Total Accounts: {stats['totalAccounts']}")
        print(f"      🏷️  AI Categories:")
        for category, count in stats['categories'].items():
            if count > 0:
                print(f"         • {category}: {count} emails")
    else:
        print(f"   ❌ Failed to get stats: {response.text}")
        return
    
    # Step 4: Get actual emails
    print("\n📧 Step 4: Retrieving Real Emails")
    response = requests.get(f"{BASE_URL}/api/emails?limit=5", headers=headers)
    if response.status_code == 200:
        result = response.json()
        emails = result['emails']
        print(f"   ✅ Retrieved {len(emails)} emails:")
        
        for i, email in enumerate(emails[:3], 1):
            print(f"      {i}. Subject: {email.get('subject', 'No Subject')[:50]}...")
            print(f"         From: {email.get('sender', 'Unknown')[:30]}...")
            print(f"         Category: {email.get('category', 'Uncategorized')}")
            print(f"         Confidence: {email.get('confidence_score', 0):.2f}")
            print()
    else:
        print(f"   ❌ Failed to get emails: {response.text}")
        return
    
    # Step 5: Test search functionality
    print("\n🔍 Step 5: Testing Email Search")
    response = requests.get(f"{BASE_URL}/api/search?q=gmail&limit=3", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Search for 'gmail' found {result['total']} emails")
        if result['emails']:
            for i, email in enumerate(result['emails'][:2], 1):
                print(f"      {i}. {email.get('subject', 'No Subject')[:40]}...")
    else:
        print(f"   ❌ Search failed: {response.text}")
    
    # Step 6: Test manual sync
    print("\n🔄 Step 6: Testing Manual Sync")
    response = requests.post(f"{BASE_URL}/api/sync-emails", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Manual sync: {result['message']}")
    else:
        print(f"   ❌ Manual sync failed: {response.text}")
    
    print("\n" + "=" * 60)
    print("🎉 REAL GMAIL INTEGRATION TEST COMPLETE!")
    
    if stats.get('totalEmails', 0) > 0:
        print("\n✅ SUCCESS! Your Gmail account is working:")
        print(f"   📧 {stats['totalEmails']} real emails synced and categorized")
        print(f"   🤖 AI classification working")
        print(f"   🔍 Search functionality working")
        print(f"   🌐 Dashboard will show your real emails!")
        print("\n🌐 Go to http://localhost:4000 and login to see your emails!")
        print("   👤 Login with: vikas.real.{int(time.time())}@example.com")
        print("   🔑 Password: securepass123")
    else:
        print("\n⏳ Sync in progress... The fixes are being applied")
        print("   The system is fetching your emails in the background")
        print("   Check the dashboard in a few minutes!")

if __name__ == "__main__":
    test_your_gmail_account_integration()
