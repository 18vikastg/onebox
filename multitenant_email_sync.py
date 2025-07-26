import imaplib
import email
import threading
import time
import logging
from datetime import datetime, timedelta
from email.header import decode_header
from email import message_from_bytes
from python_models import Database
from email_classifier import classify_single_email
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MultiTenantEmailSyncService:
    def __init__(self):
        self.db = Database()
        self.active_connections = {}
        self.sync_threads = []
        self.running = True
        self.sync_days = 30  # Sync last 30 days of emails
        self.idle_timeout = 300  # 5 minutes
        self.reconnect_delay = 30  # 30 seconds
    
    def decode_header_safe(self, header_value):
        """Safely decode email headers"""
        if not header_value:
            return "Unknown"
        
        try:
            decoded = decode_header(header_value)[0][0]
            if isinstance(decoded, bytes):
                return decoded.decode('utf-8', errors='replace')
            return str(decoded)
        except Exception as e:
            logging.warning(f"Header decode error: {e}")
            return str(header_value)
    
    def connect_to_imap(self, account):
        """Connect to IMAP server for a specific email account"""
        try:
            # Create IMAP connection
            if account['imap_port'] == 993:
                mail = imaplib.IMAP4_SSL(account['imap_host'], account['imap_port'])
            else:
                mail = imaplib.IMAP4(account['imap_host'], account['imap_port'])
            
            # Login
            mail.login(account['email'], account['password'])
            logging.info(f"Connected to IMAP for {account['email']}")
            return mail
            
        except Exception as e:
            logging.error(f"Failed to connect to IMAP for {account['email']}: {e}")
            return None
    
    def sync_emails_for_account(self, account):
        """Sync emails for a specific user account"""
        emails_synced = 0
        try:
            mail = self.connect_to_imap(account)
            if not mail:
                return emails_synced
            
            # Select INBOX
            mail.select('INBOX')
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=self.sync_days)).strftime("%d-%b-%Y")
            
            # Search for emails since the date
            status, messages = mail.search(None, f'(SINCE "{since_date}")')
            
            if status != 'OK':
                logging.error(f"Failed to search emails for {account['email']}")
                return emails_synced
            
            email_ids = messages[0].split()
            logging.info(f"Found {len(email_ids)} emails for {account['email']}")
            
            # Process emails
            for i, email_id in enumerate(email_ids[-100:]):  # Limit to last 100 emails for demo
                try:
                    # Check if email already exists
                    existing_email = self.db.get_email_by_uid(account['user_id'], account['id'], email_id.decode())
                    if existing_email:
                        continue
                    
                    # Fetch email
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    email_message = message_from_bytes(msg_data[0][1])
                    
                    # Extract email data
                    subject = self.decode_header_safe(email_message.get('Subject', ''))
                    sender = self.decode_header_safe(email_message.get('From', ''))
                    date_str = email_message.get('Date', '')
                    
                    # Get email body
                    body = self.extract_email_body(email_message)
                    
                    # Classify email using AI
                    try:
                        email_data_for_classification = {
                            'subject': subject,
                            'content': body,
                            'sender': sender
                        }
                        classification_result = classify_single_email(email_data_for_classification)
                        category = classification_result.get('category', 'Uncategorized')
                        confidence = classification_result.get('confidence', 0.0)
                    except Exception as e:
                        logging.warning(f"Classification failed: {e}")
                        category, confidence = "Uncategorized", 0.0
                    
                    # Store email in database
                    email_data = {
                        'user_id': account['user_id'],
                        'account_id': account['id'],
                        'uid': email_id.decode(),
                        'subject': subject,
                        'sender': sender,
                        'content': body,
                        'category': category,
                        'confidence_score': confidence,
                        'date_received': date_str
                    }
                    
                    self.db.store_email(email_data)
                    emails_synced += 1
                    
                    if i % 10 == 0:
                        logging.info(f"Processed {i+1}/{len(email_ids[-100:])} emails for {account['email']}")
                
                except Exception as e:
                    logging.error(f"Error processing email {email_id} for {account['email']}: {e}")
                    continue
            
            mail.close()
            mail.logout()
            logging.info(f"Email sync completed for {account['email']}. Synced {emails_synced} new emails.")
            
        except Exception as e:
            logging.error(f"Email sync failed for {account['email']}: {e}")
        
        return emails_synced
    
    def extract_email_body(self, email_message):
        """Extract email body from email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                        break
                    except:
                        continue
                elif content_type == "text/html" and not body:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='replace')
            except:
                body = str(email_message.get_payload())
        
        return body[:5000]  # Limit body length
    
    def sync_user_accounts(self, user_id):
        """Sync all email accounts for a specific user"""
        try:
            accounts = self.db.get_user_email_accounts(user_id)
            
            if not accounts:
                logging.info(f"No email accounts found for user {user_id}")
                return {'success': True, 'emails_synced': 0, 'message': 'No email accounts found'}
            
            logging.info(f"Starting sync for user {user_id} with {len(accounts)} accounts")
            
            total_emails_synced = 0
            
            for account in accounts:
                if not account['is_active']:
                    continue
                
                logging.info(f"Syncing emails for {account['email']}")
                emails_synced = self.sync_emails_for_account(account)
                total_emails_synced += emails_synced
            
            logging.info(f"Sync completed for user {user_id}. Total emails synced: {total_emails_synced}")
            
            return {
                'success': True, 
                'emails_synced': total_emails_synced,
                'accounts_synced': len([a for a in accounts if a['is_active']]),
                'message': f'Successfully synced {total_emails_synced} emails from {len([a for a in accounts if a["is_active"]])} accounts'
            }
            
        except Exception as e:
            logging.error(f"Failed to sync accounts for user {user_id}: {e}")
            return {'success': False, 'error': str(e), 'emails_synced': 0}
    
    def sync_all_users(self):
        """Sync emails for all users in the system"""
        try:
            users = self.db.get_all_users()
            
            for user in users:
                logging.info(f"Starting sync for user: {user['email']}")
                self.sync_user_accounts(user['id'])
                
                # Small delay between users to prevent overwhelming
                time.sleep(2)
            
            logging.info("Completed sync for all users")
            
        except Exception as e:
            logging.error(f"Failed to sync all users: {e}")
    
    def start_periodic_sync(self, interval_minutes=30):
        """Start periodic sync for all users"""
        def sync_loop():
            while self.running:
                try:
                    logging.info("Starting periodic sync for all users")
                    self.sync_all_users()
                    logging.info(f"Sleeping for {interval_minutes} minutes")
                    
                    # Sleep in small chunks to allow for clean shutdown
                    for _ in range(interval_minutes * 60):
                        if not self.running:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    logging.error(f"Error in sync loop: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        sync_thread = threading.Thread(target=sync_loop, daemon=True)
        sync_thread.start()
        self.sync_threads.append(sync_thread)
        logging.info(f"Started periodic sync service (every {interval_minutes} minutes)")
    
    def stop(self):
        """Stop the sync service"""
        self.running = False
        logging.info("Email sync service stopped")

def main():
    """Main function to run the multi-tenant email sync service"""
    logging.info("Starting Multi-Tenant Email Sync Service")
    
    sync_service = MultiTenantEmailSyncService()
    
    try:
        # Run one-time sync for all users
        sync_service.sync_all_users()
        
        # Start periodic sync (every 30 minutes)
        sync_service.start_periodic_sync(30)
        
        # Keep the service running
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        sync_service.stop()

if __name__ == "__main__":
    main()
