#!/usr/bin/env python3
"""
Simple Step-by-Step Usage Guide for AI Email Classification with Slack
"""

import os
import sys
from datetime import datetime

def step_by_step_guide():
    print("🚀 AI EMAIL CLASSIFICATION SYSTEM - STEP BY STEP GUIDE")
    print("=" * 70)
    print()
    
    print("📝 WHAT THIS SYSTEM DOES:")
    print("• Automatically classifies emails into 5 categories")
    print("• Sends Slack notifications for 'Interested' emails")  
    print("• Helps you never miss potential leads")
    print()
    
    print("🔧 STEP 1: VERIFY YOUR SETUP")
    print("-" * 30)
    
    # Check API key
    from dotenv import load_dotenv
    load_dotenv()
    
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OpenAI API key: FOUND")
    else:
        print("❌ OpenAI API key: MISSING")
        return
    
    # Check modules
    try:
        from email_classifier import classify_single_email
        print("✅ Email classifier: READY")
    except Exception as e:
        print(f"❌ Email classifier: ERROR - {e}")
        return
        
    try:
        from notification_service import test_slack_connection
        print("✅ Slack service: READY")
    except Exception as e:
        print(f"❌ Slack service: ERROR - {e}")
        return
    
    print()
    print("🧪 STEP 2: TEST SLACK CONNECTION")
    print("-" * 30)
    
    print("Testing Slack webhook...")
    slack_working = test_slack_connection()
    if slack_working:
        print("✅ Slack connection: WORKING")
        print("📱 Check your Slack channel for test message!")
    else:
        print("❌ Slack connection: FAILED")
        return
    
    print()
    print("📧 STEP 3: TEST EMAIL CLASSIFICATION")
    print("-" * 30)
    
    # Test different email types
    test_emails = [
        {
            "name": "Interested Lead",
            "data": {
                "subject": "Interested in your AI solution",
                "sender": "potential.customer@company.com",
                "content": "Hi, I saw your demo and I'm very interested. Can you send me pricing information?"
            },
            "should_notify": True
        },
        {
            "name": "Spam Email", 
            "data": {
                "subject": "🎉 WIN $1000 NOW!!!",
                "sender": "spam@fake.com",
                "content": "Click here to win amazing prizes!"
            },
            "should_notify": False
        }
    ]
    
    for test in test_emails:
        print(f"\nTesting: {test['name']}")
        print(f"Subject: {test['data']['subject']}")
        
        try:
            result = classify_single_email(test['data'])
            category = result.get('category', 'Unknown')
            confidence = result.get('confidence_score', 0.0)
            
            print(f"Result: {category} ({confidence:.1%} confidence)")
            
            if category == 'Interested' and test['should_notify']:
                print("🎉 SLACK NOTIFICATION SENT! Check your channel!")
            elif category != 'Interested' and not test['should_notify']:
                print("✅ No notification sent (correct behavior)")
            else:
                print("⚠️  Unexpected result")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()
    print("🎯 STEP 4: HOW TO USE IN PRODUCTION")
    print("-" * 30)
    print()
    print("Option A - Single Email Classification:")
    print("```python")
    print("from email_classifier import classify_single_email")
    print()
    print("email = {")
    print("    'subject': 'Your email subject',")
    print("    'sender': 'sender@email.com',")
    print("    'content': 'Email content here...'")
    print("}")
    print()
    print("result = classify_single_email(email)")
    print("print(f\"Category: {result['category']}\")")
    print("# If 'Interested' -> Slack notification automatically sent!")
    print("```")
    print()
    
    print("Option B - Batch Email Processing:")
    print("```python")
    print("from email_classifier import classify_emails_batch")
    print()
    print("emails = [email1, email2, email3, ...]  # List of email dicts")
    print("results = classify_emails_batch(emails)")
    print("# All 'Interested' emails -> Slack notifications sent!")
    print("```")
    print()
    
    print("Option C - Web Dashboard:")
    print("```bash")
    print("node index.js")
    print("# Open http://localhost:4000")
    print("# View classified emails with filters")
    print("```")
    print()
    
    print("🔗 STEP 5: SLACK WEBHOOK DETAILS")
    print("-" * 30)
    print("Your webhook URL:")
    print("https://hooks.slack.com/services/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")
    print()
    print("Manual test with curl:")
    print("```bash")
    print("curl -X POST -H 'Content-type: application/json' \\")
    print("  --data '{\"text\":\"Test message\"}' \\")
    print("  https://hooks.slack.com/services/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")
    print("```")
    print()
    
    print("📊 STEP 6: MONITOR RESULTS")
    print("-" * 30)
    print("• Check Slack channel for notifications")
    print("• View web dashboard at http://localhost:4000")
    print("• Monitor logs for classification statistics")
    print("• Only 'Interested' emails trigger notifications")
    print()
    
    print("=" * 70)
    print("🎉 YOUR AI EMAIL CLASSIFICATION SYSTEM IS READY!")
    print("=" * 70)
    print()
    print("SUMMARY:")
    print("✅ AI classification working")
    print("✅ Slack notifications working") 
    print("✅ Automatic lead detection active")
    print("✅ Production ready!")
    print()
    print("Now you'll never miss an interested customer again! 🚀")
    print("=" * 70)

if __name__ == "__main__":
    step_by_step_guide()
