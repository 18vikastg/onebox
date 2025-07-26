#!/usr/bin/env python3
"""
Feature 4: Slack & Webhook Integration
Complete implementation as specified in requirements
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Feature4SlackWebhookIntegration:
    """
    Feature 4: Slack & Webhook Integration
    
    - Send Slack notifications for every new Interested email
    - Trigger webhooks (webhook.site) for external automation when email is marked as Interested
    """
    
    def __init__(self):
        """Initialize Feature 4 integration"""
        # Your Slack webhook URL
        self.slack_webhook_url = "https://hooks.slack.com/services/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"
        
        # webhook.site URL for external automation (as specified in Feature 4)
        self.webhook_site_url = "https://webhook.site/f8b5c3d2-4a1e-4d6f-9c8b-2e5a7f3d1c9e"
        
        logger.info("🚀 Feature 4: Slack & Webhook Integration initialized")
    
    def send_slack_notification_for_interested_email(self, email_data: Dict[str, Any]) -> bool:
        """
        Send Slack notification for every new Interested email
        Feature 4 Requirement: Send Slack notifications for every new Interested email
        
        Args:
            email_data: Email information dictionary
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            # Only process Interested emails as per Feature 4
            if email_data.get('category') != 'Interested':
                logger.info("Email not classified as 'Interested', skipping Slack notification")
                return True
            
            subject = email_data.get('subject', 'No Subject')
            sender = email_data.get('sender', 'Unknown Sender')
            content = email_data.get('content', '')
            confidence = email_data.get('confidence_score', 0.0)
            timestamp = email_data.get('timestamp', datetime.now().isoformat())
            
            # Create professional Slack message for interested emails
            slack_message = {
                "text": f"🎯 NEW INTERESTED LEAD DETECTED! - {subject}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🎯 NEW INTERESTED LEAD DETECTED!",
                            "emoji": True
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*🔥 HIGH-PRIORITY LEAD ALERT*\nA potential customer has expressed strong interest in your services!"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*📧 Subject:*\n{subject}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*👤 From:*\n{sender}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*🎯 Confidence:*\n{confidence:.1%}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*⏰ Detected:*\n{timestamp[:19].replace('T', ' ')}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*📄 Email Preview:*\n```{content[:300]}{'...' if len(content) > 300 else ''}```"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "🎯 View Lead in Dashboard",
                                    "emoji": True
                                },
                                "style": "primary",
                                "url": "http://localhost:4000?filter=Interested"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "📞 Contact Lead",
                                    "emoji": True
                                },
                                "style": "danger"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "📊 View Analytics",
                                    "emoji": True
                                }
                            }
                        ]
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"🤖 AI Email Classification System | Feature 4: Slack Integration | Lead #{uuid.uuid4().hex[:8].upper()}"
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
                logger.info(f"✅ Feature 4: Slack notification sent successfully for interested email: {subject[:50]}...")
                return True
            else:
                logger.error(f"❌ Feature 4: Failed to send Slack notification. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Feature 4: Error sending Slack notification: {e}")
            return False
    
    def trigger_webhook_for_external_automation(self, email_data: Dict[str, Any]) -> bool:
        """
        Trigger webhooks (webhook.site) for external automation when email is marked as Interested
        Feature 4 Requirement: Trigger webhooks for external automation
        
        Args:
            email_data: Email information dictionary
            
        Returns:
            bool: True if webhook triggered successfully
        """
        try:
            # Only trigger webhook for Interested emails as per Feature 4
            if email_data.get('category') != 'Interested':
                logger.info("Email not classified as 'Interested', skipping webhook trigger")
                return True
            
            # Create webhook payload for external automation
            webhook_payload = {
                "event": "new_interested_email_detected",
                "timestamp": datetime.now().isoformat(),
                "lead_id": uuid.uuid4().hex[:8].upper(),
                "priority": "HIGH",
                "email_classification": {
                    "category": email_data.get('category'),
                    "confidence_score": email_data.get('confidence_score', 0.0),
                    "classification_method": email_data.get('classification_method', 'AI')
                },
                "email_details": {
                    "subject": email_data.get('subject'),
                    "sender": email_data.get('sender'),
                    "content_preview": email_data.get('content', '')[:500],  # Truncate for webhook
                    "full_content_length": len(email_data.get('content', '')),
                    "received_at": email_data.get('timestamp', datetime.now().isoformat())
                },
                "automation_triggers": {
                    "send_auto_response": True,
                    "create_crm_lead": True,
                    "notify_sales_team": True,
                    "schedule_follow_up": True
                },
                "system_metadata": {
                    "source": "AI Email Classification System",
                    "feature": "Feature 4: Slack & Webhook Integration",
                    "version": "1.0",
                    "webhook_url": self.webhook_site_url
                }
            }
            
            # Send to webhook.site for external automation
            response = requests.post(
                self.webhook_site_url,
                json=webhook_payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'AI-Email-Classification-System-Feature-4',
                    'X-Event-Type': 'interested-email-detected'
                },
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Feature 4: Webhook triggered successfully for external automation")
                logger.info(f"🔗 Webhook.site URL: {self.webhook_site_url}")
                return True
            else:
                logger.error(f"❌ Feature 4: Failed to trigger webhook. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Feature 4: Error triggering webhook for external automation: {e}")
            return False
    
    def execute_feature_4_for_interested_email(self, email_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Execute complete Feature 4 implementation for Interested emails
        
        Feature 4 Requirements:
        1. Send Slack notifications for every new Interested email ✅
        2. Trigger webhooks (webhook.site) for external automation ✅
        
        Args:
            email_data: Email information dictionary
            
        Returns:
            dict: Status of both Feature 4 components
        """
        results = {
            'slack_notification_sent': False,
            'webhook_triggered': False,
            'feature_4_complete': False
        }
        
        # Only execute Feature 4 for Interested emails
        if email_data.get('category') != 'Interested':
            logger.info("Feature 4: Email not classified as 'Interested', skipping all Feature 4 actions")
            return results
        
        logger.info(f"🚀 Feature 4: Executing complete integration for interested email: {email_data.get('subject', 'No Subject')[:50]}...")
        
        # 1. Send Slack notification for every new Interested email
        results['slack_notification_sent'] = self.send_slack_notification_for_interested_email(email_data)
        
        # 2. Trigger webhook for external automation
        results['webhook_triggered'] = self.trigger_webhook_for_external_automation(email_data)
        
        # Mark Feature 4 as complete if both components succeeded
        results['feature_4_complete'] = results['slack_notification_sent'] and results['webhook_triggered']
        
        if results['feature_4_complete']:
            logger.info("🎉 Feature 4: Complete! Slack notification sent AND webhook triggered for external automation")
        else:
            logger.warning("⚠️ Feature 4: Partial failure - check individual component status")
        
        return results
    
    def test_feature_4_integration(self) -> bool:
        """
        Test complete Feature 4 integration
        
        Returns:
            bool: True if all Feature 4 components are working
        """
        logger.info("🧪 Testing Feature 4: Slack & Webhook Integration")
        logger.info("=" * 60)
        
        # Test email data
        test_email = {
            "subject": "Very interested in your AI solution - Let's talk!",
            "sender": "ceo@bigcorp.com",
            "content": """Hi there,

I saw your AI email classification demo and I'm extremely interested in implementing this for our company.

We process 1000+ emails daily and need exactly what you've built. This could save us hours of manual work.

Can we schedule a call this week to discuss:
1. Pricing for enterprise usage
2. Implementation timeline
3. Custom integration options

I'm ready to move forward quickly if this fits our budget.

Best regards,
Sarah Johnson
CEO, BigCorp Solutions""",
            "category": "Interested",
            "confidence_score": 0.96,
            "classification_method": "AI",
            "timestamp": datetime.now().isoformat()
        }
        
        # Test Feature 4 execution
        results = self.execute_feature_4_for_interested_email(test_email)
        
        # Report results
        logger.info("📊 Feature 4 Test Results:")
        logger.info(f"  Slack Notification: {'✅ SUCCESS' if results['slack_notification_sent'] else '❌ FAILED'}")
        logger.info(f"  Webhook Triggered: {'✅ SUCCESS' if results['webhook_triggered'] else '❌ FAILED'}")
        logger.info(f"  Feature 4 Complete: {'✅ SUCCESS' if results['feature_4_complete'] else '❌ FAILED'}")
        
        if results['feature_4_complete']:
            logger.info("🎉 Feature 4: Slack & Webhook Integration is working perfectly!")
            logger.info("📱 Check your Slack channel for the notification")
            logger.info(f"🔗 Check webhook.site: {self.webhook_site_url}")
        
        logger.info("=" * 60)
        return results['feature_4_complete']


# Global instance for easy import
feature_4_integration = Feature4SlackWebhookIntegration()

def execute_feature_4_for_interested_email(email_data: Dict[str, Any]) -> Dict[str, bool]:
    """Convenience function to execute Feature 4 for interested emails"""
    return feature_4_integration.execute_feature_4_for_interested_email(email_data)

def test_feature_4_integration() -> bool:
    """Convenience function to test Feature 4 integration"""
    return feature_4_integration.test_feature_4_integration()


if __name__ == "__main__":
    # Test Feature 4 implementation
    print("🚀 Feature 4: Slack & Webhook Integration")
    print("=" * 50)
    print("Requirements:")
    print("1. Send Slack notifications for every new Interested email ✅")
    print("2. Trigger webhooks (webhook.site) for external automation ✅")
    print("=" * 50)
    
    # Run comprehensive test
    success = test_feature_4_integration()
    
    if success:
        print("\n🎉 FEATURE 4 IMPLEMENTATION COMPLETE!")
        print("Your AI Email Classification System now includes:")
        print("✅ Slack notifications for interested emails")
        print("✅ Webhook.site integration for external automation")
        print("✅ Complete lead detection and notification system")
    else:
        print("\n❌ Feature 4 implementation needs attention")
        print("Check the logs above for specific issues")
