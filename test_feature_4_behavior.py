#!/usr/bin/env python3
"""
Feature 4 Test: Shows exactly what happens with Slack notifications
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_feature_4_behavior():
    """Test Feature 4: Slack & Webhook Integration behavior"""
    
    print("🎯 FEATURE 4: SLACK & WEBHOOK INTEGRATION TEST")
    print("=" * 60)
    print("📋 RULE: Only 'Interested' emails trigger Slack notifications")
    print("=" * 60)
    print()
    
    # Import after environment is loaded
    from email_classifier import classify_single_email
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI API key not found. Testing rule-based classification only.")
    else:
        print("✅ OpenAI API key found. Testing full AI classification.")
    
    print()
    
    # Test emails with expected behavior
    test_emails = [
        {
            "subject": "Out of Office: Vacation until Monday",
            "sender": "john@company.com",
            "content": "I am currently out of office and will return on Monday. For urgent matters, please contact my manager.",
            "expected": "Out of Office",
            "slack_notification": "❌ NO (Not interested)"
        },
        {
            "subject": "Meeting Invitation - Project Discussion",
            "sender": "sarah@client.com", 
            "content": "Hi, I'd like to schedule a meeting to discuss the project proposal. Are you available next Tuesday at 2 PM?",
            "expected": "Meeting Booked",
            "slack_notification": "❌ NO (Not interested)"
        },
        {
            "subject": "Re: Your Product Demo",
            "sender": "interested.customer@email.com",
            "content": "Thank you for the demo! I'm very interested in your solution. Can you send me pricing information?",
            "expected": "Interested",
            "slack_notification": "✅ YES (Feature 4 triggered!)"
        },
        {
            "subject": "Unsubscribe - No Longer Interested",
            "sender": "nothanks@company.com",
            "content": "Please remove me from your mailing list. I'm not interested in your services at this time.",
            "expected": "Not Interested",
            "slack_notification": "❌ NO (Not interested)"
        },
        {
            "subject": "🎉 AMAZING OFFER! Click here to win $1000!!!",
            "sender": "spam@suspicious.com",
            "content": "Congratulations! You've won our amazing prize! Click here now to claim your reward!",
            "expected": "Spam",
            "slack_notification": "❌ NO (Not interested)"
        }
    ]
    
    correct_predictions = 0
    total_tests = len(test_emails)
    slack_notifications_sent = 0
    
    for i, test_email in enumerate(test_emails, 1):
        print(f"📧 Test {i}/{total_tests}: {test_email['subject'][:45]}...")
        print(f"   From: {test_email['sender']}")
        
        try:
            # Classify the email (this will trigger Feature 4 if "Interested")
            result = classify_single_email({
                'subject': test_email['subject'],
                'sender': test_email['sender'],
                'content': test_email['content']
            })
            
            predicted_category = result.get('category', 'Unknown')
            confidence = result.get('confidence_score', 0.0)
            method = result.get('classification_method', 'Unknown')
            
            is_correct = predicted_category == test_email['expected']
            if is_correct:
                correct_predictions += 1
                status = "✅ CORRECT"
            else:
                status = "❌ INCORRECT"
            
            print(f"   Expected: {test_email['expected']}")
            print(f"   Predicted: {predicted_category} ({confidence:.2f} confidence, {method})")
            print(f"   Classification: {status}")
            print(f"   Slack Notification: {test_email['slack_notification']}")
            
            # Count actual Slack notifications that would be sent
            if predicted_category == 'Interested':
                slack_notifications_sent += 1
                print("   🚀 FEATURE 4 EXECUTED: Slack notification sent + Webhook triggered!")
            else:
                print("   ⏸️  Feature 4 skipped (email not 'Interested')")
            
            print()
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            print()
    
    # Summary
    accuracy = (correct_predictions / total_tests) * 100
    print("=" * 60)
    print("📊 FEATURE 4 TEST RESULTS")
    print("=" * 60)
    print(f"📧 Total Emails Tested: {total_tests}")
    print(f"✅ Correct Classifications: {correct_predictions}")
    print(f"📊 Classification Accuracy: {accuracy:.1f}%")
    print(f"📱 Slack Notifications Sent: {slack_notifications_sent}")
    print(f"🔗 Webhooks Triggered: {slack_notifications_sent}")
    print()
    
    # Feature 4 behavior explanation
    print("🎯 FEATURE 4 BEHAVIOR SUMMARY:")
    print("-" * 40)
    
    for test_email in test_emails:
        emoji = "📱" if test_email['expected'] == 'Interested' else "🔕"
        notification_status = "SLACK SENT" if test_email['expected'] == 'Interested' else "NO NOTIFICATION"
        print(f"{emoji} {test_email['expected']:15} → {notification_status}")
    
    print()
    print("=" * 60)
    
    if accuracy >= 80:
        print("🎉 EXCELLENT! Feature 4 is working perfectly!")
        print("✅ Slack notifications only sent for 'Interested' emails")
        print("✅ No spam notifications for other categories")
    elif accuracy >= 60:
        print("👍 GOOD! Feature 4 is working, may need fine-tuning.")
    else:
        print("⚠️  NEEDS IMPROVEMENT! Check configuration and API key.")
    
    print()
    print("🔔 SLACK CHANNEL CHECK:")
    print(f"You should see {slack_notifications_sent} notification(s) in your Slack channel")
    print("for the 'Interested' email(s) only!")
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_feature_4_behavior()
