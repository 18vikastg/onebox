# Railway Production Deployment Configuration

## Overview
This configuration deploys the ReachInbox Email Management Platform with RAG (Retrieval-Augmented Generation) capabilities to Railway.

## Services Architecture

### 1. Web Service (Node.js)
- **Port**: 4000 (main application)
- **Image**: node:18-alpine
- **Purpose**: Main web server with dashboard and API endpoints
- **Environment Variables**:
  - NODE_ENV=production
  - RAG_SERVICE_URL=http://rag-service:5001

### 2. RAG Service (Python FastAPI)
- **Port**: 5001 (RAG microservice)
- **Image**: python:3.11-slim  
- **Purpose**: AI-powered reply suggestions using vector database
- **Features**:
  - ChromaDB vector database with 16 training templates
  - Sentence transformer embeddings
  - OpenAI integration for personalized responses
  - Sub-second response times

### 3. Email Sync Service (Python)
- **Image**: python:3.11-slim
- **Purpose**: Real-time Gmail synchronization
- **Features**: 
  - Multi-tenant email processing
  - Real-time notifications
  - Elasticsearch integration

### 4. Elasticsearch
- **Image**: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
- **Purpose**: Email search and indexing
- **Configuration**: Single-node, security disabled for Railway

### 5. Redis
- **Image**: redis:7-alpine  
- **Purpose**: Caching and session management

## Required Environment Variables

### Core Authentication
- `GMAIL_PRIMARY_EMAIL`: Your primary Gmail address
- `GMAIL_PRIMARY_PASSWORD`: Gmail App Password (not regular password)
- `OPENAI_API_KEY`: OpenAI API key for AI features

### Optional Configuration  
- `GMAIL_SECONDARY_EMAIL`: Secondary Gmail address
- `GMAIL_SECONDARY_PASSWORD`: Secondary Gmail App Password
- `RAG_ENABLED`: Enable RAG AI reply suggestions (default: true)
- `AI_CLASSIFICATION_ENABLED`: Enable AI email classification (default: false)

## Deployment Steps

1. **Prepare Repository**: Ensure all files are pushed to your GitHub repository
2. **Create Railway Project**: Import from GitHub repository  
3. **Set Environment Variables**: Configure all required variables in Railway dashboard
4. **Deploy Services**: Railway will automatically deploy all services defined in railway.json
5. **Test RAG System**: Verify AI reply suggestions are working via the dashboard

## RAG System Features

### Vector Database
- **Technology**: ChromaDB with persistent storage
- **Embeddings**: Sentence transformers for semantic search
- **Training Data**: 16 pre-configured email templates for common scenarios

### AI Reply Engine
- **Response Time**: Sub-second AI reply generation
- **Personalization**: Calendar link integration (vikas.srivastava.is@gmail.com)
- **Fallback**: Multiple fallback mechanisms for reliability

### API Integration
- **Endpoint**: `/api/suggest-reply`
- **Method**: POST with email content
- **Response**: Personalized AI-generated reply suggestions

## Monitoring and Debugging

### Health Checks
- RAG Service: `GET /health` endpoint
- Web Service: Main dashboard accessibility
- Email Sync: Real-time synchronization logs

### Logs Access
- Railway provides centralized logging for all services
- Use Railway CLI or dashboard to monitor service health
- RAG service includes detailed request/response logging

## Production Considerations

### Performance
- RAG service runs on dedicated microservice for isolation
- Vector database persistence ensures fast startup
- Caching mechanisms reduce API calls

### Security
- Environment variables for sensitive data
- JWT-based authentication system
- Secure inter-service communication

### Scalability
- Microservice architecture allows independent scaling
- Database services (Elasticsearch, Redis) can be scaled separately
- RAG service can handle concurrent requests efficiently

## Troubleshooting

### Common Issues
1. **RAG Service Not Responding**: Check OPENAI_API_KEY environment variable
2. **Email Sync Issues**: Verify Gmail App Passwords and permissions
3. **Database Connection**: Ensure Elasticsearch and Redis services are healthy

### Debug Mode
- Set NODE_ENV=development for additional logging
- RAG service includes comprehensive error handling
- Check Railway service logs for detailed error information
