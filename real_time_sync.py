import threading
import time
import logging
from datetime import datetime, timedelta
from multitenant_email_sync import MultiTenantEmailSyncService
from python_models import Database
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RealTimeEmailSyncManager:
    """
    Real-time email sync manager that automatically syncs emails for all users
    """
    def __init__(self):
        self.db = Database()
        self.sync_service = MultiTenantEmailSyncService()
        self.running = False
        self.sync_thread = None
        self.sync_interval = int(os.getenv('SYNC_INTERVAL_MINUTES', 5)) * 60  # Default 5 minutes
        self.auto_sync_enabled = os.getenv('AUTO_SYNC_ENABLED', 'true').lower() == 'true'
        
        logging.info(f"🔄 Auto-sync enabled: {self.auto_sync_enabled}")
        logging.info(f"⏰ Sync interval: {self.sync_interval // 60} minutes")
    
    def start_auto_sync(self):
        """Start the automatic email synchronization"""
        if not self.auto_sync_enabled:
            logging.info("Auto-sync is disabled")
            return
            
        if self.running:
            logging.warning("Auto-sync is already running")
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        logging.info("🚀 Real-time email sync started")
    
    def stop_auto_sync(self):
        """Stop the automatic email synchronization"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join()
        logging.info("⏹️ Real-time email sync stopped")
    
    def _sync_loop(self):
        """Main sync loop that runs continuously"""
        while self.running:
            try:
                self._sync_all_users()
                
                # Wait for next sync interval
                for _ in range(self.sync_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logging.error(f"Error in sync loop: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying on error
    
    def _sync_all_users(self):
        """Sync emails for all users who have email accounts"""
        try:
            # Get all users who have email accounts
            users_with_accounts = self.db.get_all_users_with_email_accounts()
            
            if not users_with_accounts:
                logging.info("No users with email accounts found")
                return
            
            logging.info(f"🔄 Starting sync for {len(users_with_accounts)} users")
            
            for user in users_with_accounts:
                try:
                    user_id = user['id']
                    user_email = user['email']
                    
                    logging.info(f"📧 Syncing emails for user: {user_email} (ID: {user_id})")
                    
                    # Sync this user's email accounts
                    result = self.sync_service.sync_user_accounts(user_id)
                    
                    if result.get('success'):
                        emails_synced = result.get('emails_synced', 0)
                        logging.info(f"✅ Synced {emails_synced} emails for {user_email}")
                    else:
                        error = result.get('error', 'Unknown error')
                        logging.error(f"❌ Sync failed for {user_email}: {error}")
                        
                except Exception as e:
                    logging.error(f"❌ Error syncing user {user.get('email', 'unknown')}: {e}")
                    
        except Exception as e:
            logging.error(f"❌ Error in _sync_all_users: {e}")
    
    def sync_user_immediately(self, user_id):
        """Immediately sync emails for a specific user (when they add an account)"""
        try:
            logging.info(f"🚀 Immediate sync requested for user ID: {user_id}")
            
            result = self.sync_service.sync_user_accounts(user_id)
            
            if result.get('success'):
                emails_synced = result.get('emails_synced', 0)
                logging.info(f"✅ Immediate sync completed: {emails_synced} emails")
                return result
            else:
                error = result.get('error', 'Unknown error')
                logging.error(f"❌ Immediate sync failed: {error}")
                return result
                
        except Exception as e:
            logging.error(f"❌ Error in immediate sync: {e}")
            return {'success': False, 'error': str(e)}

# Global instance
email_sync_manager = RealTimeEmailSyncManager()

def start_email_sync_service():
    """Start the email sync service"""
    email_sync_manager.start_auto_sync()

def stop_email_sync_service():
    """Stop the email sync service"""
    email_sync_manager.stop_auto_sync()

def sync_user_now(user_id):
    """Sync a specific user immediately"""
    return email_sync_manager.sync_user_immediately(user_id)

if __name__ == "__main__":
    # Test the sync manager
    logging.info("🧪 Testing Real-Time Email Sync Manager")
    
    try:
        # Start the sync service
        start_email_sync_service()
        
        # Let it run for a bit
        time.sleep(10)
        
        # Stop the service
        stop_email_sync_service()
        
        logging.info("✅ Test completed successfully")
        
    except KeyboardInterrupt:
        logging.info("Test interrupted by user")
        stop_email_sync_service()
    except Exception as e:
        logging.error(f"Test failed: {e}")
        stop_email_sync_service()
