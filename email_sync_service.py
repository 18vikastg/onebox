import imaplib
import email
import threading
import time
import logging
from datetime import datetime, timedelta
from email.header import decode_header
from email import message_from_bytes
from database import email_storage
from config import ACCOUNTS, SYNC_DAYS, IDLE_TIMEOUT, RECONNECT_DELAY
from email_classifier import classify_single_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmailSyncService:
    def __init__(self):
        self.storage = email_storage
        self.active_connections = {}
        self.sync_threads = []
        self.running = True
    
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
            logging.warning(f"Error decoding header: {e}")
            return str(header_value)
    
    def connect_to_account(self, account):
        """Establish IMAP connection for an account"""
        try:
            mail = imaplib.IMAP4_SSL(account['imap_server'])
            mail.login(account['email'], account['password'])
            mail.select('INBOX')
            
            logging.info(f"Connected to {account['email']}")
            return mail
        except Exception as e:
            logging.error(f"Failed to connect to {account['email']}: {e}")
            return None
    
    def fetch_last_30_days(self, account):
        """Fetch emails from the last 30 days for initial sync"""
        mail = self.connect_to_account(account)
        if not mail:
            return
        
        try:
            # Calculate date 30 days ago
            since_date = (datetime.now() - timedelta(days=SYNC_DAYS)).strftime("%d-%b-%Y")
            
            # Search for emails from last 30 days
            status, data = mail.search(None, f'(SINCE "{since_date}")')
            email_ids = data[0].split()
            
            logging.info(f"Found {len(email_ids)} emails in last {SYNC_DAYS} days for {account['email']}")
            
            # Fetch emails in batches to avoid overwhelming the server
            batch_size = 50
            for i in range(0, len(email_ids), batch_size):
                batch = email_ids[i:i+batch_size]
                self.fetch_emails_batch(mail, batch, account['email'])
                time.sleep(1)  # Small delay between batches
            
            self.storage.update_sync_status(account['email'], email_ids[-1].decode() if email_ids else None)
            
        except Exception as e:
            logging.error(f"Error during initial sync for {account['email']}: {e}")
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass
    
    def fetch_emails_batch(self, mail, email_ids, account_email):
        """Fetch a batch of emails"""
        for email_id in email_ids:
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                msg = message_from_bytes(msg_data[0][1])
                
                # Extract email details
                subject = self.decode_header_safe(msg.get('Subject'))
                sender = self.decode_header_safe(msg.get('From'))
                date_received = msg.get('Date', 'Unknown')
                message_id = msg.get('Message-ID')
                
                # Extract email body for better classification
                body = self.extract_email_body(msg)
                
                # Clean up data
                subject = subject.replace('\n', ' ').replace('\r', ' ').strip()
                sender = sender.replace('\n', ' ').replace('\r', ' ').strip()
                date_received = date_received.replace('\n', ' ').replace('\r', ' ').strip()
                
                # Prepare email data for classification
                email_data_for_classification = {
                    'subject': subject,
                    'sender': sender,
                    'content': body or subject,  # Use body if available, otherwise subject
                    'account_email': account_email
                }
                
                # Classify the email using AI
                try:
                    classification_result = classify_single_email(email_data_for_classification)
                    logging.info(f"📋 Email classified as: {classification_result.get('category', 'Unknown')}")
                except Exception as e:
                    logging.warning(f"⚠️ Classification failed for email {email_id}: {e}")
                    classification_result = {
                        'category': 'Uncategorized',
                        'confidence_score': 0.0,
                        'classification_method': 'Failed',
                        'classified_at': datetime.now().isoformat()
                    }
                
                # Store in storage system with classification
                self.storage.insert_email(
                    account_email=account_email,
                    uid=email_id.decode(),
                    subject=subject,
                    sender=sender,
                    date_received=date_received,
                    message_id=message_id,
                    body=body,
                    classification=classification_result
                )
                
            except Exception as e:
                logging.warning(f"Error processing email {email_id}: {e}")
    
    def extract_email_body(self, msg):
        """Extract text content from email message"""
        try:
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='replace')
                    elif part.get_content_type() == "text/html" and not body:
                        # Use HTML as fallback if no plain text
                        payload = part.get_payload(decode=True)
                        if payload:
                            import re
                            html_content = payload.decode('utf-8', errors='replace')
                            # Basic HTML tag removal
                            body = re.sub(r'<[^>]+>', '', html_content)
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='replace')
            
            # Clean and limit body length
            body = body.strip()[:2000]  # Limit to 2000 characters
            return body
        except Exception as e:
            logging.warning(f"Error extracting email body: {e}")
            return ""
    
    def idle_monitor(self, account):
        """Monitor account for new emails using Gmail-compatible polling"""
        while self.running:
            mail = self.connect_to_account(account)
            if not mail:
                logging.warning(f"Reconnecting to {account['email']} in {RECONNECT_DELAY} seconds...")
                time.sleep(RECONNECT_DELAY)
                continue
            
            try:
                # Gmail-compatible approach: check for new emails every 30 seconds
                # This is more efficient than IDLE for Gmail
                self.fetch_new_emails(mail, account)
                
                # Keep connection alive and wait
                for i in range(6):  # 6 * 5 = 30 seconds
                    if not self.running:
                        break
                    time.sleep(5)
                
            except Exception as e:
                logging.error(f"Monitor error for {account['email']}: {e}")
            finally:
                try:
                    mail.close()
                    mail.logout()
                except:
                    pass
                
                if self.running:
                    time.sleep(5)  # Brief wait before reconnecting
    
    def fetch_new_emails(self, mail, account):
        """Fetch new emails using UID-based detection"""
        try:
            # Get the last UID we processed
            last_uid = self.storage.get_last_uid(account['email'])
            
            # Search for all emails (we'll filter by UID)
            status, data = mail.search(None, 'ALL')
            if status == 'OK' and data[0]:
                all_uids = [int(uid) for uid in data[0].split()]
                
                # Find new emails (UIDs greater than last processed)
                last_uid_int = int(last_uid) if last_uid else 0
                new_uids = [str(uid) for uid in all_uids if uid > last_uid_int]
                
                if new_uids:
                    # Fetch only the new emails
                    self.fetch_emails_batch(mail, [uid.encode() for uid in new_uids], account['email'])
                    self.storage.update_sync_status(account['email'], new_uids[-1])
                    logging.info(f"Synced {len(new_uids)} new emails for {account['email']}")
                    
        except Exception as e:
            logging.error(f"Error fetching new emails for {account['email']}: {e}")
    
    def start_sync(self):
        """Start the email synchronization service"""
        logging.info("Starting Email Sync Service...")
        
        # First, do initial sync for all accounts
        for account in ACCOUNTS:
            logging.info(f"Starting initial sync for {account['email']}")
            self.fetch_last_30_days(account)
        
        # Then start IDLE monitoring threads
        for account in ACCOUNTS:
            thread = threading.Thread(target=self.idle_monitor, args=(account,))
            thread.daemon = True
            thread.start()
            self.sync_threads.append(thread)
            logging.info(f"Started IDLE thread for {account['email']}")
        
        logging.info("Email Sync Service started successfully!")
    
    def stop_sync(self):
        """Stop the email synchronization service"""
        logging.info("Stopping Email Sync Service...")
        self.running = False
        
        # Close all connections
        for connection in self.active_connections.values():
            try:
                connection.close()
                connection.logout()
            except:
                pass
        
        logging.info("Email Sync Service stopped")
    
    def get_sync_stats(self):
        """Get synchronization statistics"""
        stats = {}
        for account in ACCOUNTS:
            email_count = self.storage.get_email_count(account['email'])
            sync_status = self.storage.get_sync_status(account['email'])
            stats[account['email']] = {
                'email_count': email_count,
                'sync_status': sync_status
            }
        return stats

if __name__ == "__main__":
    sync_service = EmailSyncService()
    
    try:
        sync_service.start_sync()
        
        # Keep the service running
        while True:
            time.sleep(60)  # Check every minute
            stats = sync_service.get_sync_stats()
            logging.info(f"Sync stats: {stats}")
            
    except KeyboardInterrupt:
        logging.info("Received interrupt signal")
    finally:
        sync_service.stop_sync()
