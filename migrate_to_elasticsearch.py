#!/usr/bin/env python3
"""
Migration script to transfer existing email data from JSON to Elasticsearch
"""

import json
import sys
import os
from datetime import datetime
from database import EmailStorage
from config import JSON_STORAGE_FILE

def migrate_json_to_elasticsearch():
    """Migrate emails from JSON storage to Elasticsearch"""
    print("🔄 Starting migration from JSON to Elasticsearch...")
    
    # Check if JSON file exists
    if not os.path.exists(JSON_STORAGE_FILE):
        print("❌ No JSON storage file found. Nothing to migrate.")
        return False
    
    try:
        # Read from JSON file
        with open(JSON_STORAGE_FILE, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        emails = json_data.get('emails', [])
        if not emails:
            print("❌ No emails found in JSON storage.")
            return False
        
        print(f"📊 Found {len(emails)} emails to migrate")
        
        # Initialize Elasticsearch storage
        storage = EmailStorage()
        
        if storage.storage_mode != "elasticsearch" or not storage.es_client:
            print("❌ Elasticsearch is not properly configured or not available")
            return False
        
        # Migrate emails in batches
        batch_size = 100
        migrated_count = 0
        
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i+batch_size]
            
            for email in batch:
                try:
                    # Insert email into Elasticsearch
                    success = storage.insert_email(
                        account_email=email.get('account_email', ''),
                        uid=email.get('uid', ''),
                        subject=email.get('subject', ''),
                        sender=email.get('sender', ''),
                        date_received=email.get('date_received', ''),
                        message_id=email.get('message_id', ''),
                        body=email.get('body', '')
                    )
                    
                    if success:
                        migrated_count += 1
                    
                except Exception as e:
                    print(f"⚠️  Error migrating email {email.get('uid', 'unknown')}: {e}")
            
            # Progress update
            print(f"📈 Migrated {migrated_count}/{len(emails)} emails...")
        
        print(f"✅ Migration completed! {migrated_count}/{len(emails)} emails migrated to Elasticsearch")
        
        # Backup original JSON file
        backup_file = JSON_STORAGE_FILE + '.backup.' + datetime.now().strftime('%Y%m%d_%H%M%S')
        os.rename(JSON_STORAGE_FILE, backup_file)
        print(f"📦 Original JSON file backed up to: {backup_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    storage = EmailStorage()
    
    # Get stats from Elasticsearch
    if storage.storage_mode == "elasticsearch" and storage.es_client:
        try:
            index_name = storage.es_client.indices.get_alias().keys()
            if 'emails' in index_name:
                # Get count from Elasticsearch
                result = storage.es_client.count(index='emails')
                count = result['count']
                print(f"✅ Elasticsearch contains {count} emails")
                
                # Test search
                test_emails = storage.get_emails(limit=5)
                print(f"✅ Successfully retrieved {len(test_emails)} test emails")
                return True
            else:
                print("❌ Emails index not found in Elasticsearch")
                return False
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    else:
        print("❌ Elasticsearch not available for verification")
        return False

if __name__ == "__main__":
    print("🚀 Email Migration Tool")
    print("=" * 50)
    
    # Run migration
    if migrate_json_to_elasticsearch():
        # Verify migration
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("Your emails are now stored in Elasticsearch and ready for advanced search!")
        else:
            print("\n⚠️  Migration completed but verification failed")
    else:
        print("\n❌ Migration failed")
        sys.exit(1)
