import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from email.utils import parsedate_to_datetime
from config import EMAIL_STORAGE_MODE, JSON_STORAGE_FILE, ELASTICSEARCH_CONFIG

try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

class EmailStorage:
    """
    Email storage abstraction layer.
    Supports memory, JSON, and Elasticsearch storage.
    """
    
    def __init__(self):
        self.storage_mode = EMAIL_STORAGE_MODE
        self.emails = []  # In-memory storage
        self.sync_status = {}  # Track sync status per account
        self.es_client = None
        
        if self.storage_mode == "json":
            self.load_from_json()
        elif self.storage_mode == "elasticsearch" and ELASTICSEARCH_CONFIG["enabled"]:
            self.init_elasticsearch()
    
    def load_from_json(self):
        """Load emails from JSON file if it exists"""
        if os.path.exists(JSON_STORAGE_FILE):
            try:
                with open(JSON_STORAGE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.emails = data.get('emails', [])
                    self.sync_status = data.get('sync_status', {})
                print(f"Loaded {len(self.emails)} emails from JSON storage")
            except Exception as e:
                print(f"Error loading JSON storage: {e}")
                self.emails = []
                self.sync_status = {}
    
    def save_to_json(self):
        """Save emails to JSON file using atomic write"""
        if self.storage_mode == "json":
            try:
                data = {
                    'emails': self.emails,
                    'sync_status': self.sync_status,
                    'last_updated': datetime.now().isoformat()
                }
                # Use temporary file for atomic write
                temp_file = JSON_STORAGE_FILE + '.tmp'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                # Atomically replace the original file
                os.rename(temp_file, JSON_STORAGE_FILE)
            except Exception as e:
                print(f"Error saving to JSON: {e}")
                # Clean up temporary file if it exists
                temp_file = JSON_STORAGE_FILE + '.tmp'
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    
    def init_elasticsearch(self):
        """Initialize Elasticsearch connection"""
        if not ELASTICSEARCH_AVAILABLE:
            print("Elasticsearch library not available. Install with: pip install elasticsearch")
            return
        
        try:
            # Simple connection configuration
            self.es_client = Elasticsearch(
                hosts=[f"http://{ELASTICSEARCH_CONFIG['host']}:{ELASTICSEARCH_CONFIG['port']}"]
            )
            
            # Test connection with better error handling
            health = self.es_client.cluster.health()
            print(f"✅ Connected to Elasticsearch cluster: {health['cluster_name']}")
            
            # Create index if it doesn't exist
            index_name = ELASTICSEARCH_CONFIG['index_name']
            if not self.es_client.indices.exists(index=index_name):
                # Create index with mapping
                mapping = {
                    "mappings": {
                        "properties": {
                            "account_email": {"type": "keyword"},
                            "uid": {"type": "keyword"},
                            "subject": {"type": "text", "analyzer": "standard"},
                            "sender": {"type": "text", "analyzer": "standard"},
                            "date_received": {"type": "text"},  # Keep as text for now due to format variations
                            "date_synced": {"type": "date"},
                            "message_id": {"type": "keyword"},
                            "body": {"type": "text", "analyzer": "standard"}
                        }
                    }
                }
                self.es_client.indices.create(index=index_name, body=mapping)
                print(f"✅ Created Elasticsearch index: {index_name}")
            else:
                print(f"✅ Elasticsearch index exists: {index_name}")
                
        except Exception as e:
            print(f"❌ Elasticsearch initialization failed: {e}")
            print(f"❌ Error details: {type(e).__name__}: {str(e)}")
            self.es_client = None
    
    def insert_email(self, account_email: str, uid: str, subject: str, 
                    sender: str, date_received: str, message_id: str = None, 
                    body: str = None, classification: dict = None) -> bool:
        """Insert or update an email record"""
        try:
            # Parse and convert date to ISO format for Elasticsearch
            try:
                # Parse email date format to datetime
                if isinstance(date_received, str):
                    parsed_date = parsedate_to_datetime(date_received)
                    iso_date = parsed_date.isoformat()
                else:
                    iso_date = datetime.now().isoformat()
            except Exception as e:
                print(f"⚠️ Date parsing failed for '{date_received}': {e}")
                iso_date = datetime.now().isoformat()
            
            email_data = {
                'account_email': account_email,
                'uid': uid,
                'subject': subject,
                'sender': sender,
                'date_received': iso_date,  # Use parsed ISO format
                'date_synced': datetime.now().isoformat(),
                'message_id': message_id,
                'body': body
            }
            
            # Add classification data if provided
            if classification:
                email_data.update({
                    'category': classification.get('category', 'Uncategorized'),
                    'confidence_score': classification.get('confidence_score', 0.0),
                    'classification_method': classification.get('classification_method', 'Unknown'),
                    'classified_at': classification.get('classified_at'),
                    'processing_time_ms': classification.get('processing_time_ms', 0)
                })
            
            # Handle different storage modes
            if self.storage_mode == "elasticsearch" and self.es_client:
                # Store in Elasticsearch
                doc_id = f"{account_email}_{uid}"
                index_name = ELASTICSEARCH_CONFIG['index_name']
                
                self.es_client.index(
                    index=index_name,
                    id=doc_id,
                    body=email_data
                )
                print(f"✅ Stored email in Elasticsearch: {subject}")
                
            elif self.storage_mode == "json":
                # Store in JSON (existing logic)
                existing_email = next(
                    (email for email in self.emails 
                     if email['account_email'] == account_email and email['uid'] == uid),
                    None
                )
                
                if existing_email:
                    existing_email.update(email_data)
                else:
                    self.emails.append(email_data)
                
                self.save_to_json()
                
            else:
                # Store in memory only
                existing_email = next(
                    (email for email in self.emails 
                     if email['account_email'] == account_email and email['uid'] == uid),
                    None
                )
                
                if existing_email:
                    existing_email.update(email_data)
                else:
                    self.emails.append(email_data)
            
            return True
            
        except Exception as e:
            print(f"Error inserting email: {e}")
            return False
    
    def get_emails(self, account_email: str = None, limit: int = 100, 
                  subject_filter: str = None, date_from: str = None, 
                  date_to: str = None) -> List[Dict]:
        """Get emails with optional filtering"""
        try:
            if self.storage_mode == "elasticsearch" and self.es_client:
                # Query Elasticsearch
                return self._query_elasticsearch(account_email, limit, subject_filter, date_from, date_to)
            else:
                # Query in-memory/JSON storage
                return self._query_memory(account_email, limit, subject_filter, date_from, date_to)
                
        except Exception as e:
            print(f"Error getting emails: {e}")
            return []
    
    def _query_elasticsearch(self, account_email: str = None, limit: int = 100, 
                           subject_filter: str = None, date_from: str = None, 
                           date_to: str = None) -> List[Dict]:
        """Query emails from Elasticsearch"""
        try:
            query = {"match_all": {}}
            filters = []
            
            # Add filters
            if account_email:
                filters.append({"term": {"account_email": account_email}})
            
            if subject_filter:
                filters.append({"match": {"subject": subject_filter}})
            
            if date_from or date_to:
                date_range = {}
                if date_from:
                    date_range["gte"] = date_from
                if date_to:
                    date_range["lte"] = date_to
                filters.append({"range": {"date_received": date_range}})
            
            # Build query
            if filters:
                query = {
                    "bool": {
                        "must": filters
                    }
                }
            
            # Execute search
            index_name = ELASTICSEARCH_CONFIG['index_name']
            response = self.es_client.search(
                index=index_name,
                body={
                    "query": query,
                    "sort": [{"date_received": {"order": "desc"}}],
                    "size": limit
                }
            )
            
            # Extract emails from response
            emails = []
            for hit in response['hits']['hits']:
                emails.append(hit['_source'])
            
            return emails
            
        except Exception as e:
            print(f"Error querying Elasticsearch: {e}")
            return []
    
    def _query_memory(self, account_email: str = None, limit: int = 100, 
                     subject_filter: str = None, date_from: str = None, 
                     date_to: str = None) -> List[Dict]:
        """Query emails from memory/JSON storage"""
        try:
            filtered_emails = self.emails.copy()
            
            # Filter by account
            if account_email:
                filtered_emails = [
                    email for email in filtered_emails 
                    if email['account_email'] == account_email
                ]
            
            # Filter by subject
            if subject_filter:
                filtered_emails = [
                    email for email in filtered_emails 
                    if subject_filter.lower() in email.get('subject', '').lower()
                ]
            
            # Filter by date range (basic string comparison for now)
            if date_from:
                filtered_emails = [
                    email for email in filtered_emails 
                    if email.get('date_received', '') >= date_from
                ]
            
            if date_to:
                filtered_emails = [
                    email for email in filtered_emails 
                    if email.get('date_received', '') <= date_to
                ]
            
            # Sort by date (newest first) and limit
            filtered_emails.sort(
                key=lambda x: x.get('date_received', ''), 
                reverse=True
            )
            
            return filtered_emails[:limit]
            
        except Exception as e:
            print(f"Error filtering emails: {e}")
            return []
    
    def update_sync_status(self, account_email: str, last_uid: str = None, 
                          status: str = 'active'):
        """Update sync status for an account"""
        self.sync_status[account_email] = {
            'last_sync_time': datetime.now().isoformat(),
            'last_uid': last_uid,
            'status': status
        }
        
        if self.storage_mode == "json":
            self.save_to_json()
    
    def get_sync_status(self, account_email: str) -> Optional[Dict]:
        """Get sync status for an account"""
        return self.sync_status.get(account_email)
    
    def get_email_count(self, account_email: str = None) -> int:
        """Get total email count"""
        if account_email:
            return len([
                email for email in self.emails 
                if email['account_email'] == account_email
            ])
        return len(self.emails)
    
    def get_accounts(self) -> List[str]:
        """Get list of unique email accounts in storage"""
        return list(set(email['account_email'] for email in self.emails))
    
    def get_last_uid(self, account_email: str) -> Optional[str]:
        """Get the last processed UID for an account"""
        status = self.sync_status.get(account_email)
        if status:
            return status.get('last_uid')
        return None
    
    def clear_storage(self):
        """Clear all stored emails (useful for testing)"""
        self.emails = []
        self.sync_status = {}
        if self.storage_mode == "json" and os.path.exists(JSON_STORAGE_FILE):
            os.remove(JSON_STORAGE_FILE)
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        accounts = self.get_accounts()
        stats = {
            'total_emails': len(self.emails),
            'storage_mode': self.storage_mode,
            'accounts': {}
        }
        
        for account in accounts:
            stats['accounts'][account] = {
                'email_count': self.get_email_count(account),
                'sync_status': self.get_sync_status(account)
            }
        
        return stats

# Create a global instance
email_storage = EmailStorage()

# Backward compatibility for existing code
class EmailDatabase:
    """Legacy wrapper for backward compatibility"""
    
    def __init__(self, db_file=None):
        print("⚠️  SQLite database deprecated. Using new email storage system.")
        self.storage = email_storage
    
    def insert_email(self, account_email, uid, subject, sender, date_received, message_id=None, body=None):
        return self.storage.insert_email(account_email, uid, subject, sender, date_received, message_id, body)
    
    def get_emails(self, account_email=None, limit=100):
        emails = self.storage.get_emails(account_email, limit)
        # Convert to tuple format for backward compatibility
        return [
            (email['account_email'], email['uid'], email['subject'], 
             email['sender'], email['date_received'], email['date_synced'])
            for email in emails
        ]
    
    def update_sync_status(self, account_email, last_uid=None, status='active'):
        return self.storage.update_sync_status(account_email, last_uid, status)
    
    def get_sync_status(self, account_email):
        status = self.storage.get_sync_status(account_email)
        if status:
            return (status['last_sync_time'], status['last_uid'], status['status'])
        return None
    
    def get_email_count(self, account_email=None):
        return self.storage.get_email_count(account_email)
