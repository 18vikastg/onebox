#!/usr/bin/env python3
"""
Test script for AI email classification system
"""

import os
import sys
from email_classifier import classify_single_email

def test_classification():
    """Test the email classification with sample emails"""
    
    print("🧪 Testing AI Email Classification System")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI API key not found. Testing rule-based classification only.")
    else:
        print("✅ OpenAI API key found. Testing full AI classification.")
    
    print()
    
    # Test emails
    test_emails = [
        {
            "subject": "Out of Office: Vacation until Monday",
            "sender": "john@company.com",
            "content": "I am currently out of office and will return on Monday. For urgent matters, please contact my manager.",
            "expected": "Out of Office"
        },
        {
            "subject": "Meeting Invitation - Project Discussion",
            "sender": "sarah@client.com", 
            "content": "Hi, I'd like to schedule a meeting to discuss the project proposal. Are you available next Tuesday at 2 PM?",
            "expected": "Meeting Booked"
        },
        {
            "subject": "Re: Your Product Demo",
            "sender": "interested.customer@email.com",
            "content": "Thank you for the demo! I'm very interested in your solution. Can you send me pricing information?",
            "expected": "Interested"
        },
        {
            "subject": "Unsubscribe - No Longer Interested",
            "sender": "nothanks@company.com",
            "content": "Please remove me from your mailing list. I'm not interested in your services at this time.",
            "expected": "Not Interested"
        },
        {
            "subject": "🎉 AMAZING OFFER! Click here to win $1000!!!",
            "sender": "spam@suspicious.com",
            "content": "Congratulations! You've won our amazing prize! Click here now to claim your reward!",
            "expected": "Spam"
        }
    ]
    
    correct_predictions = 0
    total_tests = len(test_emails)
    
    for i, test_email in enumerate(test_emails, 1):
        print(f"Test {i}/{total_tests}: {test_email['subject'][:40]}...")
        
        try:
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
            
            print(f"  Expected: {test_email['expected']}")
            print(f"  Predicted: {predicted_category} ({confidence:.2f} confidence, {method})")
            print(f"  Result: {status}")
            print()
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            print()
    
    # Summary
    accuracy = (correct_predictions / total_tests) * 100
    print("=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("🎉 EXCELLENT! Classification system is working well.")
    elif accuracy >= 60:
        print("👍 GOOD! System is functioning, may need fine-tuning.")
    else:
        print("⚠️  NEEDS IMPROVEMENT! Check configuration and API key.")
    
    print("=" * 50)

if __name__ == "__main__":
    test_classification()
