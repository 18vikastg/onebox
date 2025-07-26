import os
import openai
import json
import logging
from typing import Dict, Any, Optional
import re
from datetime import datetime
from dotenv import load_dotenv

# Import notification service
try:
    from feature_4_slack_webhook import execute_feature_4_for_interested_email
    FEATURE_4_ENABLED = True
    logging.info("✅ Feature 4: Slack & Webhook Integration enabled")
except ImportError:
    FEATURE_4_ENABLED = False
    logging.warning("Feature 4: Slack & Webhook Integration not available")

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailClassifier:
    def __init__(self):
        """Initialize the email classifier with OpenAI API"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found. AI classification will be disabled.")
            self.ai_enabled = False
        else:
            openai.api_key = self.openai_api_key
            self.ai_enabled = True
            logger.info("✅ AI email classifier initialized successfully")
        
        # Define classification categories
        self.categories = [
            "Interested",
            "Meeting Booked", 
            "Not Interested",
            "Spam",
            "Out of Office"
        ]
    
    def rule_based_classify(self, email_data: Dict[str, Any]) -> Optional[str]:
        """
        Pre-classify emails using rule-based detection
        Returns category if confident, None if needs AI classification
        """
        subject = email_data.get('subject', '').lower()
        content = email_data.get('content', '').lower()
        sender = email_data.get('sender', '').lower()
        
        # Out of Office detection
        ooo_patterns = [
            'out of office', 'currently away', 'vacation', 'holiday',
            'automatic reply', 'auto reply', 'away from office',
            'not available', 'on leave', 'traveling'
        ]
        if any(pattern in subject or pattern in content for pattern in ooo_patterns):
            return "Out of Office"
        
        # Spam detection
        spam_patterns = [
            'unsubscribe', 'click here', 'limited time offer', 'act now',
            'free gift', 'congratulations', 'you have won', 'claim now',
            'viagra', 'casino', 'lottery', 'millionaire', 'inheritance'
        ]
        spam_domains = ['noreply', 'no-reply', 'donotreply']
        
        if (any(pattern in subject or pattern in content for pattern in spam_patterns) or
            any(domain in sender for domain in spam_domains)):
            return "Spam"
        
        # Meeting detection
        meeting_patterns = [
            'meeting', 'calendar', 'scheduled', 'appointment', 'invite',
            'zoom', 'teams', 'google meet', 'conference call', 'call scheduled',
            'booking confirmed', 'meeting request', 'reschedule'
        ]
        if any(pattern in subject or pattern in content for pattern in meeting_patterns):
            return "Meeting Booked"
        
        # Interest indicators
        interested_patterns = [
            'interested', 'tell me more', 'looking forward', 'sounds good',
            'please send', 'would like to', 'can you', 'more information',
            'demo', 'trial', 'proposal'
        ]
        if any(pattern in content for pattern in interested_patterns):
            return "Interested"
        
        # Not interested indicators
        not_interested_patterns = [
            'not interested', 'no thank you', 'remove me', 'stop emailing',
            'not at this time', 'pass on this', 'not a good fit'
        ]
        if any(pattern in content for pattern in not_interested_patterns):
            return "Not Interested"
        
        # Return None if no clear rule match - needs AI classification
        return None
    
    def ai_classify(self, email_data: Dict[str, Any]) -> tuple[str, float]:
        """
        Use OpenAI GPT to classify email
        Returns (category, confidence_score)
        """
        if not self.ai_enabled:
            return "Uncategorized", 0.0
        
        try:
            # Prepare email content for AI
            subject = email_data.get('subject', '')
            sender = email_data.get('sender', '')
            content = email_data.get('content', '')[:1500]  # Limit content length
            
            prompt = f"""
Classify this email into exactly one of these categories:
- Interested
- Meeting Booked
- Not Interested  
- Spam
- Out of Office

Email Details:
Subject: {subject}
Sender: {sender}
Content: {content}

Instructions:
- Analyze the tone, intent, and content carefully
- "Interested" = Shows interest in product/service, asks questions, wants more info
- "Meeting Booked" = Contains meeting invites, calendar links, scheduled calls
- "Not Interested" = Explicitly declines, says no, asks to be removed
- "Spam" = Promotional content, suspicious offers, unrelated marketing
- "Out of Office" = Automatic replies indicating absence

Return only the category name, nothing else.
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert email classifier. Respond with only the category name."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0.1
            )
            
            category = response.choices[0].message.content.strip()
            
            # Validate category
            if category in self.categories:
                confidence = 0.85  # High confidence for AI classification
                logger.info(f"✅ AI classified email as: {category}")
                return category, confidence
            else:
                logger.warning(f"⚠️ AI returned invalid category: {category}")
                return "Uncategorized", 0.0
                
        except Exception as e:
            logger.error(f"❌ AI classification failed: {e}")
            return "Uncategorized", 0.0
    
    def classify_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main classification method that combines rule-based and AI classification
        Returns classification result with metadata
        """
        start_time = datetime.now()
        
        # Try rule-based classification first
        rule_category = self.rule_based_classify(email_data)
        
        if rule_category:
            # Rule-based classification successful
            result = {
                "category": rule_category,
                "confidence_score": 0.95,  # High confidence for rule-based
                "classification_method": "Rule",
                "classified_at": datetime.now().isoformat(),
                "processing_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
            logger.info(f"✅ Rule-based classification: {rule_category}")
        else:
            # Use AI classification for complex cases
            ai_category, confidence = self.ai_classify(email_data)
            result = {
                "category": ai_category,
                "confidence_score": confidence,
                "classification_method": "AI",
                "classified_at": datetime.now().isoformat(),
                "processing_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
            logger.info(f"✅ AI classification: {ai_category} (confidence: {confidence})")
        
        return result
    
    def _send_notification_if_interested(self, email_data: Dict[str, Any], classification_result: Dict[str, Any]):
        """
        Execute Feature 4: Slack & Webhook Integration if email is classified as 'Interested'
        """
        if not FEATURE_4_ENABLED:
            return
            
        if classification_result.get('category') == 'Interested':
            try:
                # Combine email data with classification result for Feature 4
                notification_data = {**email_data, **classification_result}
                
                logger.info(f"🚀 Feature 4: Executing Slack & Webhook integration for interested email: {email_data.get('subject', 'No Subject')[:50]}...")
                results = execute_feature_4_for_interested_email(notification_data)
                
                if results['slack_notification_sent']:
                    logger.info("✅ Feature 4: Slack notification sent successfully")
                else:
                    logger.warning("⚠️ Feature 4: Failed to send Slack notification")
                    
                if results['webhook_triggered']:
                    logger.info("✅ Feature 4: Webhook triggered successfully for external automation")
                else:
                    logger.warning("⚠️ Feature 4: Failed to trigger webhook for external automation")
                
                if results['feature_4_complete']:
                    logger.info("🎉 Feature 4: Complete! Both Slack notification and webhook automation executed")
                    
            except Exception as e:
                logger.error(f"❌ Feature 4: Error executing Slack & Webhook integration: {e}")
    
    def classify_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main classification method that combines rule-based and AI classification
        Returns classification result with metadata
        """
        start_time = datetime.now()
        
        # Try rule-based classification first
        rule_category = self.rule_based_classify(email_data)
        
        if rule_category:
            # Rule-based classification successful
            result = {
                "category": rule_category,
                "confidence_score": 0.95,  # High confidence for rule-based
                "classification_method": "Rule",
                "classified_at": datetime.now().isoformat(),
                "processing_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
            logger.info(f"✅ Rule-based classification: {rule_category}")
        else:
            # Use AI classification
            ai_category, confidence = self.ai_classify(email_data)
            result = {
                "category": ai_category,
                "confidence_score": confidence,
                "classification_method": "AI",
                "classified_at": datetime.now().isoformat(),
                "processing_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
            logger.info(f"✅ AI classification: {ai_category} (confidence: {confidence})")
        
        # Send notification if email is classified as 'Interested'
        self._send_notification_if_interested(email_data, result)
        
        return result
    
    def batch_classify(self, emails: list) -> list:
        """
        Classify multiple emails in batch
        Returns list of emails with classification data added
        """
        logger.info(f"🔄 Starting batch classification of {len(emails)} emails...")
        
        classified_emails = []
        stats = {"Rule": 0, "AI": 0, "Failed": 0}
        interested_count = 0
        
        for i, email in enumerate(emails):
            try:
                classification = self.classify_email(email)
                email.update(classification)
                classified_emails.append(email)
                
                stats[classification["classification_method"]] += 1
                
                # Count interested emails
                if classification.get("category") == "Interested":
                    interested_count += 1
                
                if (i + 1) % 10 == 0:
                    logger.info(f"📊 Progress: {i + 1}/{len(emails)} emails classified (Interested: {interested_count})")
                    
            except Exception as e:
                logger.error(f"❌ Failed to classify email {i}: {e}")
                email.update({
                    "category": "Uncategorized",
                    "confidence_score": 0.0,
                    "classification_method": "Failed",
                    "classified_at": datetime.now().isoformat(),
                    "error": str(e)
                })
                classified_emails.append(email)
                stats["Failed"] += 1
        
        logger.info(f"✅ Batch classification complete: {stats}")
        logger.info(f"🎯 Found {interested_count} interested emails with notifications sent")
        return classified_emails

# Global classifier instance
classifier = EmailClassifier()

def classify_single_email(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to classify a single email"""
    return classifier.classify_email(email_data)

def classify_emails_batch(emails: list) -> list:
    """Convenience function to classify multiple emails"""
    return classifier.batch_classify(emails)

if __name__ == "__main__":
    # Test the classifier
    test_email = {
        "subject": "Meeting invitation - Project Discussion",
        "sender": "john@company.com",
        "content": "Hi, I'd like to schedule a meeting to discuss the project. Please let me know your availability."
    }
    
    result = classify_single_email(test_email)
    print("Test Classification Result:")
    print(json.dumps(result, indent=2))
