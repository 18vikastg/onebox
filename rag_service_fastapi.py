#!/usr/bin/env python3
"""
FastAPI RAG Service for Railway Deployment
Provides AI-powered email reply suggestions using vector database
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reply_suggestion_engine import RAGReplyEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Reply Suggestion Service", 
    version="1.0.0",
    description="AI-powered email reply suggestions using vector database and RAG"
)

# Add CORS middleware for Railway deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine
rag_engine = None

class EmailRequest(BaseModel):
    email_content: str
    sender_email: str = ""
    recipient_email: str = ""
    subject: str = ""
    context: dict = {}

class ReplyResponse(BaseModel):
    reply: str
    confidence: float = 0.0
    status: str = "success"

@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine on startup"""
    global rag_engine
    try:
        logger.info("🚀 Initializing RAG engine...")
        rag_engine = RAGReplyEngine()
        logger.info("✅ RAG engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG engine: {e}")
        raise e

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "RAG Reply Suggestion Engine",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway monitoring"""
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    return {
        "status": "healthy", 
        "service": "rag-reply-engine",
        "version": "1.0.0",
        "engine_status": "ready"
    }

@app.post("/suggest-reply", response_model=ReplyResponse)
async def suggest_reply(request: EmailRequest):
    """Generate AI reply suggestion using RAG"""
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    
    try:
        logger.info(f"🤖 Processing reply suggestion for email: {request.email_content[:100]}...")
        
        reply = rag_engine.suggest_email_reply(
            email_content=request.email_content,
            sender_email=request.sender_email or request.context.get('sender', ''),
            recipient_email=request.recipient_email
        )
        
        logger.info(f"✅ Generated reply: {reply[:100]}...")
        
        return ReplyResponse(
            reply=reply, 
            confidence=0.85,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating reply: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate reply: {str(e)}"
        )

@app.post("/suggest")
async def suggest_legacy(request: EmailRequest):
    """Legacy endpoint for backward compatibility"""
    return await suggest_reply(request)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    host = "0.0.0.0"  # Bind to all interfaces for Railway
    
    logger.info(f"🚀 Starting RAG service on {host}:{port}")
    logger.info(f"📡 Service will be available at http://{host}:{port}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info"
    )
