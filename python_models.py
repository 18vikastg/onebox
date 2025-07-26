import sqlite3
import bcrypt
import logging
from datetime import datetime

class Database:
    def __init__(self, db_path='reachinbox.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create email_accounts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    imap_host TEXT NOT NULL,
                    imap_port INTEGER NOT NULL,
                    password TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Create emails table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    account_id INTEGER NOT NULL,
                    uid TEXT NOT NULL,
                    subject TEXT,
                    sender TEXT,
                    content TEXT,
                    category TEXT,
                    confidence_score REAL,
                    date_received TEXT,
                    raw_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(account_id, uid),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (account_id) REFERENCES email_accounts(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Run migrations to ensure all columns exist
            self.run_migrations()
            
            logging.info("Database initialized successfully")
            
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
    
    def run_migrations(self):
        """Run database migrations to add missing columns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if raw_message column exists
            cursor.execute("PRAGMA table_info(emails)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'raw_message' not in columns:
                logging.info("Adding raw_message column to emails table")
                cursor.execute('ALTER TABLE emails ADD COLUMN raw_message TEXT')
                conn.commit()
            
            conn.close()
            logging.info("Database migrations completed")
            
        except Exception as e:
            logging.error(f"Database migration failed: {e}")
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_all_users(self):
        """Get all users in the system"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, email, created_at FROM users')
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'created_at': row[3]
                })
            conn.close()
            return users
        except Exception as e:
            logging.error(f"Failed to get users: {e}")
            return []
    
    def get_user_email_accounts(self, user_id):
        """Get all email accounts for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, user_id, email, imap_host, imap_port, password, provider, is_active 
                FROM email_accounts 
                WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            
            accounts = []
            for row in cursor.fetchall():
                accounts.append({
                    'id': row[0],
                    'user_id': row[1],
                    'email': row[2],
                    'imap_host': row[3],
                    'imap_port': row[4],
                    'password': row[5],
                    'provider': row[6],
                    'is_active': row[7]
                })
            conn.close()
            return accounts
        except Exception as e:
            logging.error(f"Failed to get email accounts for user {user_id}: {e}")
            return []
    
    def get_email_by_uid(self, user_id, account_id, uid):
        """Check if email already exists"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM emails 
                WHERE user_id = ? AND account_id = ? AND uid = ?
            ''', (user_id, account_id, uid))
            
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logging.error(f"Failed to check email existence: {e}")
            return False
    
    def store_email(self, email_data):
        """Store email in database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO emails 
                (user_id, account_id, uid, subject, sender, content, category, confidence_score, date_received, raw_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                email_data['user_id'],
                email_data['account_id'],
                email_data['uid'],
                email_data['subject'],
                email_data['sender'],
                email_data['content'],
                email_data['category'],
                email_data['confidence_score'],
                email_data['date_received'],
                email_data.get('raw_message', '')
            ))
            
            conn.commit()
            email_id = cursor.lastrowid
            conn.close()
            
            logging.info(f"Stored email: {email_data['subject'][:50]}... (Category: {email_data['category']})")
            return email_id
            
        except Exception as e:
            logging.error(f"Failed to store email: {e}")
            return None
    
    def get_user_emails(self, user_id, limit=50):
        """Get user's emails"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT e.*, ea.email as account_email 
                FROM emails e 
                JOIN email_accounts ea ON e.account_id = ea.id 
                WHERE e.user_id = ? 
                ORDER BY e.date_received DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            emails = []
            for row in cursor.fetchall():
                emails.append({
                    'id': row[0],
                    'user_id': row[1],
                    'account_id': row[2],
                    'uid': row[3],
                    'subject': row[4],
                    'sender': row[5],
                    'content': row[6],
                    'category': row[7],
                    'confidence_score': row[8],
                    'date_received': row[9],
                    'account_email': row[11]
                })
            conn.close()
            return emails
        except Exception as e:
            logging.error(f"Failed to get user emails: {e}")
            return []
    
    def get_emails_by_category(self, user_id, category):
        """Get user's emails by category"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT e.*, ea.email as account_email 
                FROM emails e 
                JOIN email_accounts ea ON e.account_id = ea.id 
                WHERE e.user_id = ? AND e.category = ?
                ORDER BY e.date_received DESC
            ''', (user_id, category))
            
            emails = []
            for row in cursor.fetchall():
                emails.append({
                    'id': row[0],
                    'user_id': row[1],
                    'account_id': row[2],
                    'uid': row[3],
                    'subject': row[4],
                    'sender': row[5],
                    'content': row[6],
                    'category': row[7],
                    'confidence_score': row[8],
                    'date_received': row[9],
                    'account_email': row[11]
                })
            conn.close()
            return emails
        except Exception as e:
            logging.error(f"Failed to get emails by category: {e}")
            return []
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, email FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2]
                }
            return None
        except Exception as e:
            logging.error(f"Failed to get user: {e}")
            return None
    
    def get_all_users_with_email_accounts(self):
        """Get all users who have email accounts set up"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT u.id, u.name, u.email
                FROM users u
                INNER JOIN email_accounts ea ON u.id = ea.user_id
                WHERE ea.is_active = 1
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                users.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2]
                })
            
            return users
        except Exception as e:
            logging.error(f"Failed to get users with email accounts: {e}")
            return []
