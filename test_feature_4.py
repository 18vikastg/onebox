#!/usr/bin/env python3

from email_classifier import EmailClassifier

def test_feature_4():
    print("Testing Feature 4 Slack integration...")
    
    # Test an 'Interested' email to ensure Slack notifications work
    email_data = {
        'subject': 'Very interested in your AI email classification system!',
        'sender': 'potential.customer@bigcorp.com', 
        'content': 'Hi, I saw your demo and I am very interested in implementing this for our company. Can you send me pricing information?',
        'account_email': 'sales@yourcompany.com',
        'date_received': '2025-07-24T21:45:00Z'
    }

    # Initialize classifier
    classifier = EmailClassifier()

    # Classify the email (this should trigger Slack notification for 'Interested')
    result = classifier.classify_email(email_data)
    print(f'Classification result: {result}')
    
    if result['category'] == 'Interested':
        print("✅ SUCCESS: Email classified as 'Interested' - Slack notification should have been sent!")
    else:
        print(f"❌ UNEXPECTED: Email classified as '{result['category']}' instead of 'Interested'")

if __name__ == "__main__":
    test_feature_4()
