"""
Simple Reply Suggestion Engine
Lightweight alternative to RAG for immediate response
"""

import json
import sys
import re
from datetime import datetime

def get_simple_reply_suggestions(email_content, sender="", subject=""):
    """Generate simple reply suggestions based on keywords and patterns"""
    
    email_content_lower = email_content.lower()
    subject_lower = subject.lower() if subject else ""
    
    # User context
    user_info = {
        "name": "Vikas T G",
        "calendar_link": "https://cal.com/vikastg",
        "email": "vikastg2000@gmail.com",
        "phone": "+91-8792283829"
    }
    
    suggestions = []
    
    # Job/Internship opportunity patterns
    if any(keyword in email_content_lower for keyword in [
        'internship', 'job', 'opportunity', 'position', 'career', 'hiring', 
        'interview', 'backend', 'frontend', 'developer', 'engineer'
    ]):
        suggestions.extend([
            {
                "type": "professional",
                "tone": "enthusiastic",
                "template": f"Thank you for reaching out about this opportunity! I'm very interested in learning more about the position. I'd be happy to schedule a call to discuss how my skills align with your requirements. You can book a time that works for you at {user_info['calendar_link']}.\n\nBest regards,\n{user_info['name']}",
                "confidence": 0.9
            },
            {
                "type": "professional",
                "tone": "formal",
                "template": f"Dear {sender if sender else 'Hiring Manager'},\n\nThank you for considering me for this opportunity. I would be delighted to discuss my background and how I can contribute to your team. Please let me know when would be a convenient time for a conversation.\n\nLooking forward to hearing from you.\n\nBest regards,\n{user_info['name']}\n{user_info['email']}\n{user_info['phone']}",
                "confidence": 0.85
            }
        ])
    
    # Meeting/Schedule patterns
    elif any(keyword in email_content_lower for keyword in [
        'meeting', 'schedule', 'call', 'discuss', 'time', 'available', 'calendar'
    ]):
        suggestions.extend([
            {
                "type": "scheduling",
                "tone": "friendly",
                "template": f"Hi {sender if sender else 'there'},\n\nThanks for reaching out! I'd be happy to schedule a time to chat. You can book a convenient slot at {user_info['calendar_link']} or let me know what times work best for you.\n\nLooking forward to our conversation!\n\nBest,\n{user_info['name']}",
                "confidence": 0.9
            }
        ])
    
    # Thank you patterns
    elif any(keyword in email_content_lower for keyword in [
        'thank', 'thanks', 'appreciate', 'grateful'
    ]):
        suggestions.extend([
            {
                "type": "acknowledgment",
                "tone": "warm",
                "template": f"You're very welcome! I'm glad I could help. Please don't hesitate to reach out if you need anything else.\n\nBest regards,\n{user_info['name']}",
                "confidence": 0.8
            }
        ])
    
    # Question patterns
    elif any(pattern in email_content_lower for pattern in [
        '?', 'question', 'wondering', 'clarification', 'help', 'assistance'
    ]):
        suggestions.extend([
            {
                "type": "helpful",
                "tone": "supportive",
                "template": f"Hi {sender if sender else 'there'},\n\nThanks for your question! I'd be happy to help clarify this for you. Could you provide a bit more context about what specifically you'd like to know?\n\nBest regards,\n{user_info['name']}",
                "confidence": 0.75
            }
        ])
    
    # Follow-up patterns
    elif any(keyword in email_content_lower for keyword in [
        'follow up', 'following up', 'checking in', 'update', 'status'
    ]):
        suggestions.extend([
            {
                "type": "follow_up",
                "tone": "professional",
                "template": f"Hi {sender if sender else 'there'},\n\nThanks for following up! I appreciate your continued interest. I'll get back to you with an update by [specific date/time]. If you have any urgent questions in the meantime, feel free to reach out.\n\nBest regards,\n{user_info['name']}",
                "confidence": 0.8
            }
        ])
    
    # Default general responses
    if not suggestions:
        suggestions.extend([
            {
                "type": "general",
                "tone": "friendly",
                "template": f"Hi {sender if sender else 'there'},\n\nThank you for your email. I've received your message and will get back to you soon.\n\nBest regards,\n{user_info['name']}",
                "confidence": 0.6
            },
            {
                "type": "general",
                "tone": "professional",
                "template": f"Dear {sender if sender else 'Sender'},\n\nThank you for reaching out. I will review your message and respond accordingly.\n\nBest regards,\n{user_info['name']}\n{user_info['email']}",
                "confidence": 0.5
            }
        ])
    
    # Sort by confidence score
    suggestions.sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        "success": True,
        "suggestions": suggestions[:3],  # Return top 3 suggestions
        "analysis": {
            "email_length": len(email_content),
            "detected_patterns": _detect_patterns(email_content_lower),
            "processing_time": "< 1 second",
            "engine": "simple_template_based"
        }
    }

def _detect_patterns(email_content_lower):
    """Detect patterns in email content for analysis"""
    patterns = []
    
    if any(word in email_content_lower for word in ['job', 'internship', 'position']):
        patterns.append("job_opportunity")
    if any(word in email_content_lower for word in ['meeting', 'schedule', 'call']):
        patterns.append("scheduling")
    if '?' in email_content_lower:
        patterns.append("question")
    if any(word in email_content_lower for word in ['thank', 'thanks']):
        patterns.append("gratitude")
    if any(word in email_content_lower for word in ['follow', 'update']):
        patterns.append("follow_up")
    
    return patterns

def suggest_email_reply(email_content, sender="", subject="", context=""):
    """Main function compatible with existing interface"""
    return get_simple_reply_suggestions(email_content, sender, subject)

if __name__ == "__main__":
    # Handle command line usage
    if len(sys.argv) > 1:
        email_content = sys.argv[1]
        sender = sys.argv[2] if len(sys.argv) > 2 else ""
        subject = sys.argv[3] if len(sys.argv) > 3 else ""
        
        result = suggest_email_reply(email_content, sender, subject)
        print(json.dumps(result))
    else:
        # Test example
        test_email = "Hi Vikas, We have an exciting Backend Engineering Internship opportunity at ReachInbox. Would you be interested in discussing this role?"
        result = suggest_email_reply(test_email, "HR Team", "Opportunity with ReachInbox")
        print(json.dumps(result, indent=2))
