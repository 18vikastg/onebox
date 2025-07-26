import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email Configuration using environment variables
ACCOUNTS = [
    {
        "email": os.getenv("GMAIL_PRIMARY_EMAIL", ""),
        "password": os.getenv("GMAIL_PRIMARY_PASSWORD", ""),
        "imap_server": "imap.gmail.com",
        "name": "Primary Gmail"
    },
    {
        "email": os.getenv("GMAIL_SECONDARY_EMAIL", ""), 
        "password": os.getenv("GMAIL_SECONDARY_PASSWORD", ""),
        "imap_server": "imap.gmail.com", 
        "name": "Secondary Gmail"
    }
]

# Filter out empty accounts
ACCOUNTS = [acc for acc in ACCOUNTS if acc["email"] and acc["password"]]

# Elasticsearch Configuration
ELASTICSEARCH_CONFIG = {
    "host": os.getenv("ELASTICSEARCH_HOST", "localhost"),
    "port": int(os.getenv("ELASTICSEARCH_PORT", "9200")),
    "index_name": os.getenv("ELASTICSEARCH_INDEX", "emails"),
    "enabled": os.getenv("ELASTICSEARCH_ENABLED", "True").lower() == "true"
}

# Sync Configuration
SYNC_DAYS = int(os.getenv("SYNC_DAYS", "30"))
IDLE_TIMEOUT = int(os.getenv("IDLE_TIMEOUT", "300"))
RECONNECT_DELAY = int(os.getenv("RECONNECT_DELAY", "60"))

# Storage Configuration
EMAIL_STORAGE_MODE = os.getenv("EMAIL_STORAGE_MODE", "elasticsearch")
JSON_STORAGE_FILE = os.getenv("JSON_STORAGE_FILE", "emails_cache.json")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# AI Classification Configuration  
AI_CLASSIFICATION_ENABLED = os.getenv("AI_CLASSIFICATION_ENABLED", "False").lower() == "true"
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "150"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))

# RAG Reply Suggestion Configuration
RAG_ENABLED = os.getenv("RAG_ENABLED", "True").lower() == "true"
RAG_MODEL = os.getenv("RAG_MODEL", "gpt-3.5-turbo")
RAG_MAX_TOKENS = int(os.getenv("RAG_MAX_TOKENS", "300"))
RAG_TEMPERATURE = float(os.getenv("RAG_TEMPERATURE", "0.7"))
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./reply_vector_db")

# Slack Integration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#email-notifications")

# Security Configuration
SESSION_SECRET = os.getenv("SESSION_SECRET", "default-session-secret")
JWT_SECRET = os.getenv("JWT_SECRET", "default-jwt-secret")

# Application Configuration
NODE_ENV = os.getenv("NODE_ENV", "development")
PORT = int(os.getenv("PORT", "4000"))
HOST = os.getenv("HOST", "localhost")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "True").lower() == "true"

# Validate required environment variables
def validate_config():
    """Validate that all required configuration is present"""
    errors = []
    
    if not ACCOUNTS:
        errors.append("No valid email accounts configured. Please set GMAIL_PRIMARY_EMAIL and GMAIL_PRIMARY_PASSWORD.")
    
    if RAG_ENABLED and not OPENAI_API_KEY:
        errors.append("RAG is enabled but OPENAI_API_KEY is not set.")
    
    if AI_CLASSIFICATION_ENABLED and not OPENAI_API_KEY:
        errors.append("AI Classification is enabled but OPENAI_API_KEY is not set.")
    
    return errors

# User Context for RAG (can be customized per deployment)
USER_CONTEXT = {
    "name": os.getenv("USER_NAME", "Assistant"),
    "current_role": os.getenv("USER_ROLE", "Email Manager"),
    "email": os.getenv("USER_EMAIL", ""),
    "calendar_link": os.getenv("USER_CALENDAR", "")
}
