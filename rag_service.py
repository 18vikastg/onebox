#!/usr/bin/env python3
"""
Persistent RAG Service
Keeps the RAG engine loaded and responds to HTTP requests
"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging
from reply_suggestion_engine import suggest_email_reply

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for reply suggestions"""
        try:
            # Parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            email_content = request_data.get('emailContent', '')
            sender = request_data.get('sender', '')
            subject = request_data.get('subject', '')
            context = request_data.get('context', {})
            
            if not email_content or not sender:
                self.send_error_response(400, "Email content and sender are required")
                return
            
            # Generate reply suggestion
            logger.info(f"🤖 Processing RAG request for email from {sender}")
            result = suggest_email_reply(email_content, sender, subject, context)
            
            # Send response
            self.send_json_response(result)
            logger.info(f"✅ RAG response sent successfully")
            
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON in request")
        except Exception as e:
            logger.error(f"❌ RAG service error: {e}")
            self.send_error_response(500, f"RAG service error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests for health check"""
        if self.path == '/health':
            self.send_json_response({
                "status": "healthy",
                "service": "RAG Reply Engine",
                "version": "1.0.0"
            })
        else:
            self.send_error_response(404, "Not found")
    
    def send_json_response(self, data):
        """Send JSON response"""
        response_data = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.end_headers()
        self.wfile.write(response_data)
    
    def send_error_response(self, status_code, message):
        """Send error response"""
        error_data = {"success": False, "error": message}
        response_data = json.dumps(error_data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.end_headers()
        self.wfile.write(response_data)
    
    def log_message(self, format, *args):
        """Override to reduce noise in logs"""
        pass

def start_rag_service(port=5001):
    """Start the RAG service"""
    try:
        logger.info("🚀 Starting RAG Service...")
        logger.info("📡 RAG service will listen on port 5001")
        
        server = HTTPServer(('localhost', port), RAGRequestHandler)
        logger.info("✅ RAG Service started successfully!")
        logger.info(f"🔗 RAG Service URL: http://localhost:{port}")
        logger.info("🤖 RAG engine is ready for requests")
        
        # Keep the service running
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("🛑 RAG Service stopped")
    except Exception as e:
        logger.error(f"❌ Failed to start RAG service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_rag_service()
