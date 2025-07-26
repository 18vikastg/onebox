#!/usr/bin/env python3
"""
Test the multi-tenant system by creating a user and testing email sync
"""

import requests
import json
import time
import logging
from python_models import Database
from multitenant_email_sync import MultiTenantEmailSyncService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_user_registration():
    """Test user registration via API"""
    try:
        # Test data
        user_data = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "testpassword123"
        }
        
        # Register user
        response = requests.post('http://localhost:4000/api/auth/register', json=user_data)
        
        if response.status_code == 201:
            logging.info("✅ User registration successful")
            return response.json()
        else:
            logging.error(f"❌ User registration failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"❌ Registration test failed: {e}")
        return None

def test_user_login():
    """Test user login via API"""
    try:
        # Login data
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword123"
        }
        
        # Login user
        response = requests.post('http://localhost:4000/api/auth/login', json=login_data)
        
        if response.status_code == 200:
            logging.info("✅ User login successful")
            return response.json()
        else:
            logging.error(f"❌ User login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"❌ Login test failed: {e}")
        return None

def test_add_email_account(auth_token):
    """Test adding email account via API"""
    try:
        # Email account data (using test configuration)
        account_data = {
            "email": "test@gmail.com",
            "imapHost": "imap.gmail.com",
            "imapPort": 993,
            "password": "test_app_password",
            "provider": "Gmail"
        }
        
        # Add email account
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = requests.post('http://localhost:4000/api/accounts/add', 
                               json=account_data, headers=headers)
        
        if response.status_code == 201:
            logging.info("✅ Email account added successfully")
            return response.json()
        else:
            logging.error(f"❌ Add email account failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"❌ Add email account test failed: {e}")
        return None

def test_database_directly():
    """Test database operations directly"""
    try:
        db = Database()
        
        # Get all users
        users = db.get_all_users()
        logging.info(f"✅ Found {len(users)} users in database")
        
        if users:
            user = users[0]
            logging.info(f"✅ Test user: {user['email']}")
            
            # Get user's email accounts
            accounts = db.get_user_email_accounts(user['id'])
            logging.info(f"✅ Found {len(accounts)} email accounts for user")
            
            # Get user's emails
            emails = db.get_user_emails(user['id'], limit=10)
            logging.info(f"✅ Found {len(emails)} emails for user")
            
            return user['id']
        
        return None
        
    except Exception as e:
        logging.error(f"❌ Database test failed: {e}")
        return None

def test_email_sync(user_id):
    """Test email sync service"""
    try:
        sync_service = MultiTenantEmailSyncService()
        
        logging.info(f"🔄 Starting email sync for user {user_id}")
        sync_service.sync_user_accounts(user_id)
        
        # Check if emails were synced
        emails = sync_service.db.get_user_emails(user_id, limit=5)
        logging.info(f"✅ Sync completed. Found {len(emails)} emails")
        
        if emails:
            for email in emails:
                logging.info(f"📧 Email: {email['subject'][:50]}... (Category: {email['category']})")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Email sync test failed: {e}")
        return False

def main():
    """Run comprehensive multi-tenant system test"""
    logging.info("🚀 Starting Multi-Tenant System Test")
    
    # Wait for server to be ready
    logging.info("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Test 1: User Registration
    logging.info("\n📝 Test 1: User Registration")
    user_result = test_user_registration()
    
    # Test 2: User Login
    logging.info("\n🔐 Test 2: User Login")
    login_result = test_user_login()
    
    if login_result:
        auth_token = login_result.get('token')
        
        # Test 3: Add Email Account
        logging.info("\n📧 Test 3: Add Email Account")
        account_result = test_add_email_account(auth_token)
    
    # Test 4: Database Operations
    logging.info("\n🗄️ Test 4: Database Operations")
    user_id = test_database_directly()
    
    # Test 5: Email Sync (only if we have a user)
    if user_id:
        logging.info("\n🔄 Test 5: Email Sync Service")
        test_email_sync(user_id)
    
    logging.info("\n✅ Multi-Tenant System Test Completed!")

if __name__ == "__main__":
    main()
