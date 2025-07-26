#!/usr/bin/env python3
"""
Test script for Slack notification integration
"""

import sys
import os
from notification_service import test_slack_connection, notify_interested_email
from datetime import datetime

def test_slack_integration():
    """Test Slack notification functionality"""
    
    print("🧪 Testing Slack Integration")
    print("=" * 50)
    
    # Test 1: Connection test
    print("1️⃣  Testing Slack webhook connection...")
    connection_success = test_slack_connection()
    
    if not connection_success:
        print("❌ Slack connection failed. Please check webhook URL.")
        return False
    
    print("✅ Slack connection successful!")
    print()
    
    # Test 2: Interested email notification
    print("2️⃣  Testing interested email notification...")
    
    sample_interested_email = {
        "subject": "Re: Your AI Email Classification Solution",
        "sender": "potential.customer@techcorp.com",
        "content": """Hi there,

I saw your demo last week and I'm very impressed with your AI email classification system. 

We're looking for exactly this kind of solution for our customer service team. We process about 500 emails per day and manual classification is becoming a bottleneck.

Could you please send me:
1. Pricing information for 500+ emails/day
2. Implementation timeline 
3. Available customization options

I'd also like to schedule a call with our technical team next week to discuss integration details.

Looking forward to hearing from you!

Best regards,
Sarah Johnson
CTO, TechCorp Solutions""",
        "category": "Interested",
        "confidence_score": 0.92,
        "classification_method": "AI",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        results = notify_interested_email(sample_interested_email)
        
        print(f"Slack notification: {'✅ Sent successfully' if results['slack_sent'] else '❌ Failed'}")
        print(f"Webhook notification: {'✅ Sent successfully' if results['webhook_sent'] else '❌ Failed'}")
        
        if results['slack_sent']:
            print("\n🎉 Check your Slack channel for the notification!")
            print("You should see a rich message with:")
            print("  • Email subject and sender")
            print("  • Confidence score")
            print("  • Email preview")
            print("  • Action buttons")
            print("  • Timestamp")
        
        return results['slack_sent']
        
    except Exception as e:
        print(f"❌ Error testing notification: {e}")
        return False

def test_different_categories():
    """Test that only 'Interested' emails trigger notifications"""
    
    print("\n3️⃣  Testing category filtering...")
    
    test_emails = [
        {
            "subject": "Out of Office - Back Monday",
            "category": "Out of Office",
            "expected_notification": False
        },
        {
            "subject": "Spam: Win $1000 Now!!!",
            "category": "Spam", 
            "expected_notification": False
        },
        {
            "subject": "Meeting scheduled for tomorrow",
            "category": "Meeting Booked",
            "expected_notification": False
        },
        {
            "subject": "Not interested in your services",
            "category": "Not Interested",
            "expected_notification": False
        },
        {
            "subject": "Very interested in your product",
            "category": "Interested",
            "expected_notification": True
        }
    ]
    
    for test_email in test_emails:
        email_data = {
            "subject": test_email["subject"],
            "sender": "test@example.com",
            "content": "Test email content",
            "category": test_email["category"],
            "confidence_score": 0.85,
            "classification_method": "Test",
            "timestamp": datetime.now().isoformat()
        }
        
        results = notify_interested_email(email_data)
        notification_sent = results['slack_sent']
        expected = test_email["expected_notification"]
        
        status = "✅" if notification_sent == expected else "❌"
        print(f"  {status} {test_email['category']}: {'Notification sent' if notification_sent else 'No notification'} (Expected: {'Yes' if expected else 'No'})")
    
    print()

if __name__ == "__main__":
    print("🚀 Starting Slack Integration Tests")
    print("=" * 60)
    
    # Run tests
    success = test_slack_integration()
    
    if success:
        test_different_categories()
        
        print("=" * 60)
        print("🎉 SLACK INTEGRATION TESTS COMPLETE!")
        print()
        print("Next steps:")
        print("1. Check your Slack channel for test notifications")
        print("2. Run email classification to see live notifications")
        print("3. The system is now ready for production!")
    else:
        print("=" * 60)
        print("❌ SLACK INTEGRATION FAILED")
        print("Please check your webhook URL and try again.")
    
    print("=" * 60)
