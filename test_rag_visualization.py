#!/usr/bin/env python3
"""
RAG Email Reply Visualization Tool
Shows incoming emails and their AI-generated replies side by side
"""

import json
import time
import sys
from datetime import datetime
from reply_suggestion_engine import suggest_email_reply

def print_separator():
    print("=" * 80)

def print_email_card(email_data, reply_result):
    """Display email and reply in a formatted card"""
    print_separator()
    print(f"📧 EMAIL ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    # Email Details
    print(f"📨 FROM: {email_data['sender']}")
    print(f"📋 SUBJECT: {email_data['subject']}")
    print(f"📅 DATE: {email_data.get('date', 'Now')}")
    print()
    
    # Email Content
    print("📝 EMAIL CONTENT:")
    print("-" * 40)
    print(email_data['content'])
    print("-" * 40)
    print()
    
    # RAG Analysis
    if reply_result['success']:
        print("🤖 RAG ANALYSIS:")
        print(f"   ✅ Success: {reply_result['success']}")
        print(f"   🎯 Scenario: {reply_result['scenario']}")
        print(f"   📊 Confidence: {reply_result['confidence']:.3f}")
        print(f"   🔧 Method: {reply_result['method']}")
        print(f"   📚 Similar Contexts: {reply_result['similar_contexts_count']}")
        print()
        
        # Generated Reply
        print("💬 SUGGESTED REPLY:")
        print("-" * 40)
        print(reply_result['suggestion'])
        print("-" * 40)
    else:
        print("❌ RAG ANALYSIS FAILED:")
        print(f"   Error: {reply_result['error']}")
    
    print_separator()
    print()

def test_multiple_scenarios():
    """Test RAG with different email scenarios"""
    
    test_emails = [
        {
            "sender": "hr@techcorp.com",
            "subject": "Technical Interview Invitation",
            "content": """Hi Vikas,

Thank you for your interest in our Senior Backend Developer position. We have reviewed your profile and are pleased to inform you that you have been shortlisted for the technical interview round.

When would be a good time for you to attend the technical interview? Please let us know your availability for next week.

Best regards,
Sarah Johnson
HR Team""",
            "date": "2025-07-25"
        },
        {
            "sender": "project.manager@startup.io",
            "subject": "Project Collaboration Opportunity",
            "content": """Hello Vikas,

We came across your profile and are impressed with your full-stack development skills. We have an exciting project that could benefit from your expertise.

Would you be interested in collaborating with us on a new fintech application? We'd love to discuss the project scope, timeline, and compensation.

Are you available for a call this week to explore this opportunity?

Best,
Alex Chen
Project Manager""",
            "date": "2025-07-25"
        },
        {
            "sender": "mentor@company.com",
            "subject": "Code Review and Feedback",
            "content": """Hi Vikas,

I've had a chance to review your recent assignment submission. Overall, the implementation looks solid and shows good understanding of the requirements.

I'd like to provide some detailed feedback and suggestions for improvement. Would you be open to a feedback session where we can discuss the code architecture and best practices?

Let me know when you're available.

Regards,
Michael Roberts
Senior Developer""",
            "date": "2025-07-25"
        },
        {
            "sender": "client@business.com",
            "subject": "Meeting Reschedule Request",
            "content": """Dear Vikas,

I hope this email finds you well. Unfortunately, I need to reschedule our meeting that was planned for tomorrow due to an unexpected urgent matter.

Could we please move it to next week? I'm flexible with the timing and can accommodate your schedule.

Sorry for the short notice and thank you for your understanding.

Best regards,
Emily Davis
Business Development""",
            "date": "2025-07-25"
        }
    ]
    
    print("🚀 RAG EMAIL REPLY TESTING - MULTIPLE SCENARIOS")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_start = time.time()
    
    for i, email in enumerate(test_emails, 1):
        print(f"🔄 Processing Email {i}/{len(test_emails)}...")
        
        start_time = time.time()
        
        # Generate RAG reply
        reply_result = suggest_email_reply(
            email_content=email['content'],
            sender=email['sender'],
            subject=email['subject']
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Display results
        print_email_card(email, reply_result)
        print(f"⏱️ Processing Time: {processing_time:.2f} seconds")
        print()
        
        # Add small delay between requests
        if i < len(test_emails):
            time.sleep(1)
    
    total_time = time.time() - total_start
    print(f"🏁 TESTING COMPLETED")
    print(f"📊 Total Time: {total_time:.2f} seconds")
    print(f"📈 Average Time per Email: {total_time/len(test_emails):.2f} seconds")

def interactive_mode():
    """Interactive mode for custom email testing"""
    print("🔍 INTERACTIVE RAG TESTING MODE")
    print("Enter email details to get AI-powered reply suggestions")
    print("Type 'quit' to exit")
    print()
    
    while True:
        try:
            print_separator()
            sender = input("📨 Enter sender email: ").strip()
            if sender.lower() == 'quit':
                break
                
            subject = input("📋 Enter email subject: ").strip()
            if subject.lower() == 'quit':
                break
                
            print("📝 Enter email content (type 'END' on a new line to finish):")
            content_lines = []
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                content_lines.append(line)
            
            content = '\n'.join(content_lines)
            
            if not content.strip():
                print("❌ Email content cannot be empty!")
                continue
            
            print("\n🔄 Generating RAG reply...")
            start_time = time.time()
            
            reply_result = suggest_email_reply(
                email_content=content,
                sender=sender,
                subject=subject
            )
            
            end_time = time.time()
            
            email_data = {
                'sender': sender,
                'subject': subject,
                'content': content,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print_email_card(email_data, reply_result)
            print(f"⏱️ Processing Time: {end_time - start_time:.2f} seconds")
            
            print("\n🔄 Test another email? (Press Enter to continue, 'quit' to exit)")
            if input().strip().lower() == 'quit':
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function with menu options"""
    print("🤖 RAG EMAIL REPLY VISUALIZATION TOOL")
    print("Choose an option:")
    print("1. Test predefined email scenarios")
    print("2. Interactive mode (enter custom emails)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                test_multiple_scenarios()
            elif choice == '2':
                interactive_mode()
            elif choice == '3':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
