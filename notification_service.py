#!/usr/bin/env python3
"""
Notification Service for Email Classification System
Handles Slack notifications for "Interested" emails
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        """Initialize the notification service"""
        # Slack webhook URL
        self.slack_webhook_url = "https://hooks.slack.com/services/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"
        
    def send_slack_notification(self, email_data: Dict[str, Any]) -> bool:
        """
        Send a rich Slack notification for an interested email
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        try:
            # Extract email information
            subject = email_data.get('subject', 'No Subject')
            sender = email_data.get('sender', 'Unknown Sender')
            content = email_data.get('content', '')
            category = email_data.get('category', 'Unknown')
            confidence = email_data.get('confidence_score', 0.0)
            timestamp = email_data.get('timestamp', datetime.now().isoformat())
            
            # Only send notifications for "Interested" emails
            if category != 'Interested':
                logger.info(f"Skipping notification for category: {category}")
                return True
            
            # Truncate content for Slack message
            content_preview = content[:200] + "..." if len(content) > 200 else content
            
            # Create rich Slack message
            slack_message = {
                "text": "🎯 New Interested Lead Detected!",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🎯 New Interested Lead!"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Subject:*\n{subject}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*From:*\n{sender}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Confidence:*\n{confidence:.1%}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Detected:*\n{timestamp[:19]}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Email Preview:*\n```{content_preview}```"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View in Dashboard"
                                },
                                "style": "primary",
                                "url": "http://localhost:4000"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Mark as Follow-up"
                                },
                                "style": "danger"
                            }
                        ]
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "📧 AI Email Classification System | Confidence: High Interest"
                            }
                        ]
                    }
                ]
            }
            
            # Send to Slack
            response = requests.post(
                self.slack_webhook_url,
                json=slack_message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Slack notification sent successfully for email: {subject[:50]}...")
                return True
            else:
                logger.error(f"❌ Failed to send Slack notification. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error sending Slack notification: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending Slack notification: {e}")
            return False
    
    def send_webhook_notification(self, email_data: Dict[str, Any], webhook_url: Optional[str] = None) -> bool:
        """
        Send a webhook notification for external automation
        
        Args:
            email_data: Dictionary containing email information
            webhook_url: Optional custom webhook URL (defaults to webhook.site for testing)
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        if not webhook_url:
            # Use webhook.site for testing as specified in Feature 4
            webhook_url = "https://webhook.site/#!/view/f8b5c3d2-4a1e-4d6f-9c8b-2e5a7f3d1c9e"
            
        try:
            # Only send webhooks for "Interested" emails
            if email_data.get('category') != 'Interested':
                return True
            
            # Create webhook payload
            webhook_payload = {
                "event": "email_classified",
                "category": email_data.get('category'),
                "confidence_score": email_data.get('confidence_score', 0.0),
                "email": {
                    "subject": email_data.get('subject'),
                    "sender": email_data.get('sender'),
                    "content": email_data.get('content', '')[:500],  # Limit content size
                    "timestamp": email_data.get('timestamp', datetime.now().isoformat())
                },
                "metadata": {
                    "classification_method": email_data.get('classification_method', 'unknown'),
                    "system": "AI Email Classification System",
                    "version": "1.0"
                }
            }
            
            # Send webhook
            response = requests.post(
                webhook_url,
                json=webhook_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Webhook notification sent successfully to: {webhook_url}")
                return True
            else:
                logger.error(f"❌ Failed to send webhook notification. Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error sending webhook notification: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending webhook notification: {e}")
            return False
    
    def notify_interested_email(self, email_data: Dict[str, Any], webhook_url: Optional[str] = None) -> Dict[str, bool]:
        """
        Send notifications for an interested email (both Slack and webhook)
        
        Args:
            email_data: Dictionary containing email information
            webhook_url: Optional webhook URL for external notifications
            
        Returns:
            dict: Status of each notification type
        """
        results = {
            'slack_sent': False,
            'webhook_sent': False
        }
        
        # Only process "Interested" emails
        if email_data.get('category') != 'Interested':
            logger.info("Email not classified as 'Interested', skipping notifications")
            return results
        
        logger.info(f"🚀 Sending notifications for interested email: {email_data.get('subject', 'No Subject')[:50]}...")
        
        # Send Slack notification
        results['slack_sent'] = self.send_slack_notification(email_data)
        
        # Send webhook notification
        results['webhook_sent'] = self.send_webhook_notification(email_data, webhook_url)
        
        return results
    
    def test_slack_connection(self) -> bool:
        """
        Test the Slack webhook connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        test_message = {
            "text": "🧪 Test message from AI Email Classification System",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "🧪 *Test Notification*\n\nThis is a test message to verify Slack integration is working correctly.\n\n✅ If you can see this message, the integration is successful!"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"📧 AI Email Classification System | Test sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                self.slack_webhook_url,
                json=test_message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Slack test message sent successfully!")
                return True
            else:
                logger.error(f"❌ Slack test failed. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing Slack connection: {e}")
            return False


# Convenience functions for easy import
notification_service = NotificationService()

def notify_interested_email(email_data: Dict[str, Any], webhook_url: Optional[str] = None) -> Dict[str, bool]:
    """Convenience function to send notifications for interested emails"""
    return notification_service.notify_interested_email(email_data, webhook_url)

def test_slack_connection() -> bool:
    """Convenience function to test Slack connection"""
    return notification_service.test_slack_connection()


if __name__ == "__main__":
    # Test the notification service
    print("🧪 Testing Notification Service")
    print("=" * 50)
    
    # Test Slack connection
    print("Testing Slack connection...")
    slack_success = test_slack_connection()
    
    if slack_success:
        print("✅ Slack integration working!")
        
        # Test with sample interested email
        sample_email = {
            "subject": "Interested in your AI email solution",
            "sender": "potential.client@company.com",
            "content": "Hi, I saw your demo and I'm very interested in implementing your AI email classification system for our company. Can we schedule a call to discuss pricing and implementation?",
            "category": "Interested",
            "confidence_score": 0.95,
            "classification_method": "AI",
            "timestamp": datetime.now().isoformat()
        }
        
        print("\nTesting notification for sample interested email...")
        results = notify_interested_email(sample_email)
        
        print(f"Slack notification: {'✅ Sent' if results['slack_sent'] else '❌ Failed'}")
        print(f"Webhook notification: {'✅ Sent' if results['webhook_sent'] else '❌ Failed'}")
        
    else:
        print("❌ Slack integration failed. Please check webhook URL.")
    
    print("=" * 50)
