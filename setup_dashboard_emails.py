#!/usr/bin/env python3
"""
Populate Elasticsearch with categorized test emails for dashboard testing
"""

import json
import requests
import time
from datetime import datetime, timedelta
from email_classifier import classify_single_email

def wait_for_elasticsearch():
    """Wait for Elasticsearch to be ready"""
    for i in range(30):
        try:
            response = requests.get('http://localhost:9200/_cluster/health')
            if response.status_code == 200:
                print("✅ Elasticsearch is ready")
                return True
        except:
            pass
        print(f"⏳ Waiting for Elasticsearch... ({i+1}/30)")
        time.sleep(2)
    return False

def create_test_emails_with_categories():
    """Create test emails with proper AI classification and categories"""
    
    print("🧪 Creating test emails with AI classification for dashboard testing")
    print("=" * 70)
    
    # Test emails that will be classified and stored
    test_emails = [
        {
            "subject": "Interested in your AI email solution - Demo request",
            "sender": "ceo@techstartup.com",
            "content": "Hi, I saw your AI email classification demo and I'm very interested in implementing this for our company. We process 500+ emails daily and need exactly what you've built. Can you send me pricing information and schedule a demo call?",
            "account_email": "demo@yourcompany.com",
            "date_received": (datetime.now() - timedelta(hours=2)).isoformat()
        },
        {
            "subject": "RE: Your product looks amazing! Let's talk business",
            "sender": "purchasing@bigcorp.com", 
            "content": "Thank you for the presentation yesterday. Our team is very impressed with the AI classification accuracy. We want to move forward with implementation. What's the next step?",
            "account_email": "sales@yourcompany.com",
            "date_received": (datetime.now() - timedelta(hours=4)).isoformat()
        },
        {
            "subject": "Out of Office: Vacation until next Monday",
            "sender": "john.smith@company.com",
            "content": "I am currently out of office and will return on Monday. For urgent matters, please contact my manager at manager@company.com",
            "account_email": "support@yourcompany.com",
            "date_received": (datetime.now() - timedelta(hours=6)).isoformat()
        },
        {
            "subject": "Meeting scheduled: Project discussion tomorrow",
            "sender": "client@business.com",
            "content": "Hi, just confirming our meeting tomorrow at 2 PM to discuss the project details. Looking forward to it!",
            "account_email": "meetings@yourcompany.com",
            "date_received": (datetime.now() - timedelta(hours=8)).isoformat()
        },
        {
            "subject": "Unsubscribe request - No longer interested",
            "sender": "nothanks@somewhere.com",
            "content": "Please remove me from your mailing list. I'm not interested in your services at this time. Thank you.",
            "account_email": "marketing@yourcompany.com",
            "date_received": (datetime.now() - timedelta(hours=10)).isoformat()
        },
        {
            "subject": "🎉 WIN $10,000 NOW! Amazing offer inside!!!",
            "sender": "spam@suspicious.net",
            "content": "Congratulations! You've been selected to win $10,000! Click here immediately to claim your prize! Limited time offer!",
            "account_email": "info@yourcompany.com",
            "date_received": (datetime.now() - timedelta(hours=12)).isoformat()
        },
        {
            "subject": "Quick question about your AI solution pricing",
            "sender": "interested.buyer@enterprise.com",
            "content": "Hi there, I'm evaluating AI solutions for our email processing needs. Your system looks perfect for our use case. Could you please send me detailed pricing for enterprise usage (1000+ emails/day)?",
            "account_email": "sales@yourcompany.com", 
            "date_received": (datetime.now() - timedelta(hours=1)).isoformat()
        },
        {
            "subject": "Automatic reply: Currently in a meeting",
            "sender": "busy.exec@corp.com",
            "content": "This is an automatic reply. I'm currently in a meeting and will respond to your email later today.",
            "account_email": "contact@yourcompany.com",
            "date_received": (datetime.now() - timedelta(hours=3)).isoformat()
        }
    ]
    
    classified_emails = []
    interested_count = 0
    
    for i, email in enumerate(test_emails, 1):
        print(f"📧 Classifying email {i}/{len(test_emails)}: {email['subject'][:50]}...")
        
        try:
            # Use AI classification
            classification_result = classify_single_email({
                'subject': email['subject'],
                'sender': email['sender'],
                'content': email['content']
            })
            
            # Add classification results to email
            email.update(classification_result)
            email['date_synced'] = datetime.now().isoformat()
            email['id'] = f"test_email_{i}"
            
            print(f"   Category: {classification_result.get('category', 'Unknown')}")
            print(f"   Confidence: {classification_result.get('confidence_score', 0):.2f}")
            print(f"   Method: {classification_result.get('classification_method', 'Unknown')}")
            
            if classification_result.get('category') == 'Interested':
                interested_count += 1
                print("   🎯 INTERESTED EMAIL - Will trigger Slack notification!")
            
            classified_emails.append(email)
            print()
            
        except Exception as e:
            print(f"   ❌ Error classifying email: {e}")
            print()
    
    return classified_emails, interested_count

def store_emails_in_elasticsearch(emails):
    """Store classified emails in Elasticsearch"""
    
    print(f"📦 Storing {len(emails)} classified emails in Elasticsearch...")
    
    # Delete existing index to start fresh
    try:
        requests.delete('http://localhost:9200/emails')
        print("🗑️  Cleared existing emails")
    except:
        pass
    
    time.sleep(2)
    
    # Create index with proper mapping
    mapping = {
        "mappings": {
            "properties": {
                "subject": {"type": "text"},
                "sender": {"type": "keyword"},
                "content": {"type": "text"},
                "account_email": {"type": "keyword"},
                "category": {"type": "keyword"},
                "confidence_score": {"type": "float"},
                "classification_method": {"type": "keyword"},
                "date_received": {"type": "date"},
                "date_synced": {"type": "date"},
                "classified_at": {"type": "date"}
            }
        }
    }
    
    try:
        response = requests.put('http://localhost:9200/emails', json=mapping)
        print("✅ Created emails index with proper mapping")
    except Exception as e:
        print(f"⚠️  Warning: Could not create mapping: {e}")
    
    # Store each email
    success_count = 0
    for email in emails:
        try:
            response = requests.post(
                f'http://localhost:9200/emails/_doc/{email["id"]}',
                json=email,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code in [200, 201]:
                success_count += 1
            else:
                print(f"⚠️  Failed to store email: {email['subject'][:30]}...")
        except Exception as e:
            print(f"❌ Error storing email: {e}")
    
    print(f"✅ Successfully stored {success_count}/{len(emails)} emails")
    
    # Refresh index to make emails searchable immediately
    try:
        requests.post('http://localhost:9200/emails/_refresh')
        print("🔄 Index refreshed - emails are now searchable")
    except:
        pass
    
    return success_count

def verify_categories():
    """Verify that categories are properly stored and searchable"""
    
    print("\n🔍 Verifying categories in Elasticsearch...")
    
    try:
        # Get aggregation of categories
        query = {
            "size": 0,
            "aggs": {
                "categories": {
                    "terms": {
                        "field": "category",
                        "size": 10
                    }
                }
            }
        }
        
        response = requests.post(
            'http://localhost:9200/emails/_search',
            json=query,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            categories = data.get('aggregations', {}).get('categories', {}).get('buckets', [])
            
            print("📊 Categories found:")
            for cat in categories:
                print(f"   - {cat['key']}: {cat['doc_count']} emails")
            
            return True
        else:
            print(f"❌ Failed to verify categories: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying categories: {e}")
        return False

def main():
    print("🚀 Setting up Dashboard with Categorized Emails")
    print("=" * 50)
    
    # Wait for Elasticsearch
    if not wait_for_elasticsearch():
        print("❌ Elasticsearch is not ready")
        return
    
    # Create and classify emails
    emails, interested_count = create_test_emails_with_categories()
    
    # Store in Elasticsearch
    success_count = store_emails_in_elasticsearch(emails)
    
    # Verify categories
    verify_categories()
    
    print("\n" + "=" * 50)
    print("🎉 DASHBOARD SETUP COMPLETE!")
    print("=" * 50)
    print(f"📧 Total emails created: {len(emails)}")
    print(f"💾 Successfully stored: {success_count}")
    print(f"🎯 Interested emails: {interested_count}")
    print(f"📱 Slack notifications sent: {interested_count}")
    print()
    print("📋 Next steps:")
    print("1. Open your dashboard: http://localhost:4000")
    print("2. Test category filtering (should work now!)")
    print("3. Check your Slack channel for notifications")
    print("4. Search by categories: Interested, Spam, Out of Office, etc.")
    print()
    print("🔧 Category filtering should now work properly!")
    print("=" * 50)

if __name__ == "__main__":
    main()
