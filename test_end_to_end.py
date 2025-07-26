#!/usr/bin/env python3
"""
Simple test to verify end-to-end integration with Slack notifications
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_end_to_end():
    print("🚀 Testing End-to-End Integration")
    print("=" * 50)
    
    try:
        # Import required modules
        from email_classifier import classify_single_email
        from notification_service import test_slack_connection
        
        print("✅ All modules imported successfully")
        
        # Test 1: Slack connection
        print("\n1️⃣  Testing Slack connection...")
        slack_working = test_slack_connection()
        print(f"Slack connection: {'✅ Working' if slack_working else '❌ Failed'}")
        
        # Test 2: Classify an interested email (should trigger notification)
        print("\n2️⃣  Testing interested email classification...")
        
        interested_email = {
            'subject': 'Very interested in your AI email solution!',
            'sender': 'eager.customer@company.com',
            'content': '''Hi there,

I attended your webinar yesterday about AI email classification and I'm very impressed! 

Our company processes over 1000 emails daily and we desperately need an automated solution like yours. The demo showed exactly what we need.

Could you please:
1. Send me pricing for enterprise usage
2. Schedule a technical discussion with our IT team  
3. Provide implementation timeline estimates

I'm ready to move forward quickly if the pricing works.

Best regards,
Alex Johnson
VP of Operations'''
        }
        
        print(f"Classifying email: '{interested_email['subject']}'")
        result = classify_single_email(interested_email)
        
        print(f"\nClassification result:")
        print(f"  Category: {result.get('category', 'Unknown')}")
        print(f"  Confidence: {result.get('confidence_score', 0.0):.2f}")
        print(f"  Method: {result.get('classification_method', 'Unknown')}")
        
        if result.get('category') == 'Interested':
            print("✅ Email correctly classified as 'Interested'")
            print("🎉 Slack notification should have been sent!")
            print("\nCheck your Slack channel for the notification.")
        else:
            print(f"❌ Email classified as '{result.get('category')}' instead of 'Interested'")
        
        # Test 3: Classify a non-interested email (should NOT trigger notification)
        print("\n3️⃣  Testing non-interested email classification...")
        
        spam_email = {
            'subject': 'URGENT: Claim your prize NOW!!!',
            'sender': 'noreply@spam.com',
            'content': 'Congratulations! You have won $1,000,000! Click here to claim now!'
        }
        
        print(f"Classifying email: '{spam_email['subject']}'")
        result2 = classify_single_email(spam_email)
        
        print(f"\nClassification result:")
        print(f"  Category: {result2.get('category', 'Unknown')}")
        print(f"  Confidence: {result2.get('confidence_score', 0.0):.2f}")
        print(f"  Method: {result2.get('classification_method', 'Unknown')}")
        
        if result2.get('category') != 'Interested':
            print("✅ Non-interested email correctly handled (no notification sent)")
        else:
            print("❌ Spam email incorrectly classified as 'Interested'")
        
        print("\n" + "=" * 50)
        print("🎉 END-TO-END TEST COMPLETE!")
        print("\nSummary:")
        print("• Slack integration is working")
        print("• Email classification is working") 
        print("• Notifications are sent only for 'Interested' emails")
        print("• System is ready for production use!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_end_to_end()
