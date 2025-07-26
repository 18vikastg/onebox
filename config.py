# Email Configuration
# Add your email accounts here
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# Elasticsearch Configuration (for future implementation)
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

# For now, store emails in memory/JSON until Elasticsearch is implemented
EMAIL_STORAGE_MODE = os.getenv("EMAIL_STORAGE_MODE", "elasticsearch")
JSON_STORAGE_FILE = os.getenv("JSON_STORAGE_FILE", "emails_cache.json")

# OpenAI Configuration for AI Features
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

# User Context for Reply Suggestions
USER_CONTEXT = {
    "name": os.getenv("USER_NAME", "Vikas T G"),
    "email": os.getenv("USER_EMAIL", "vikastg2000@gmail.com"), 
    "phone": os.getenv("USER_PHONE", "+91-8792283829"),
    "calendar_link": os.getenv("USER_CALENDAR", "https://cal.com/vikastg"),
    "current_role": os.getenv("USER_ROLE", "Full Stack Developer"),
    "company": os.getenv("USER_COMPANY", "Available for opportunities"),
    "location": os.getenv("USER_LOCATION", "India")
}
