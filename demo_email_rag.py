#!/usr/bin/env python3
"""
Quick RAG Email Reply Demo
Shows emails from your system and generates AI replies
"""

import json
import time
import requests
from reply_suggestion_engine import suggest_email_reply

def print_header():
    print("🚀 ReachInbox Email & RAG Reply Demonstration")
    print("=" * 60)

def fetch_recent_emails():
    """Fetch recent emails from the API"""
    try:
        response = requests.get('http://localhost:4000/api/emails')
        if response.status_code == 200:
            data = response.json()
            return data.get('emails', [])[:5]  # Get first 5 emails
        else:
            print(f"❌ Failed to fetch emails: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return []

def display_email_and_reply(email, index):
    """Display email and its RAG-generated reply"""
    print(f"\n📧 EMAIL {index + 1}")
    print("-" * 50)
    print(f"📨 FROM: {email.get('sender', 'Unknown')}")
    print(f"📋 SUBJECT: {email.get('subject', 'No Subject')}")
    print(f"🏷️  CATEGORY: {email.get('category', 'Uncategorized')}")
    print(f"📅 DATE: {email.get('date_received', 'Unknown')}")
    print()
    
    # Show email content (truncated)
    content = email.get('body', 'No content')
    if len(content) > 200:
        content = content[:200] + "..."
    
    print("📝 EMAIL CONTENT:")
    print("~" * 30)
    print(content)
    print("~" * 30)
    print()
    
    # Generate RAG reply
    print("🤖 GENERATING AI REPLY...")
    start_time = time.time()
    
    reply_result = suggest_email_reply(
        email_content=email.get('body', ''),
        sender=email.get('sender', ''),
        subject=email.get('subject', '')
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    if reply_result['success']:
        print("✅ RAG ANALYSIS:")
        print(f"   🎯 Scenario: {reply_result['scenario']}")
        print(f"   📊 Confidence: {reply_result['confidence']:.3f}")
        print(f"   🔧 Method: {reply_result['method']}")
        print(f"   ⏱️  Processing Time: {processing_time:.2f}s")
        print()
        
        print("💬 SUGGESTED REPLY:")
        print("=" * 40)
        print(reply_result['suggestion'])
        print("=" * 40)
    else:
        print(f"❌ Failed to generate reply: {reply_result.get('error', 'Unknown error')}")
    
    print("\n" + "🔷" * 60 + "\n")

def main():
    print_header()
    
    # Fetch emails from your system
    print("📥 Fetching recent emails from your system...")
    emails = fetch_recent_emails()
    
    if not emails:
        print("❌ No emails found. Make sure your server is running on http://localhost:4000")
        return
    
    print(f"✅ Found {len(emails)} recent emails")
    print(f"🧠 Generating AI-powered replies using RAG...")
    print()
    
    # Process each email
    for i, email in enumerate(emails):
        display_email_and_reply(email, i)
        
        # Add a small pause between emails
        if i < len(emails) - 1:
            time.sleep(1)
    
    print("🎉 Demo completed! Check your frontend at http://localhost:4000 for the full interface.")
    print("💡 In the web interface, you can click on any email and use the 'AI Reply' button to generate suggestions.")

if __name__ == "__main__":
    main()
