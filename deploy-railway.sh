#!/bin/bash
# Railway Deployment Script for ReachInbox with RAG

echo "🚀 Starting Railway deployment for ReachInbox with RAG..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway login

# Create new project or link existing
echo "📋 Creating/linking Railway project..."
railway link

# Set environment variables
echo "🔧 Setting up environment variables..."
echo "Please set the following environment variables in Railway dashboard:"
echo "- GMAIL_PRIMARY_EMAIL: Your primary Gmail address"
echo "- GMAIL_PRIMARY_PASSWORD: Gmail App Password"
echo "- OPENAI_API_KEY: Your OpenAI API key"
echo "- RAG_ENABLED: true"

# Deploy the project
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment initiated!"
echo ""
echo "📊 Monitor deployment progress:"
echo "- Railway Dashboard: https://railway.app/dashboard"
echo "- Service Logs: railway logs"
echo ""
echo "🔗 Your RAG-enabled ReachInbox will be available at:"
echo "https://[your-domain].railway.app"
echo ""
echo "📋 Post-deployment checklist:"
echo "1. Verify all services are running (web, rag-service, email-sync, elasticsearch, redis)"
echo "2. Test RAG system via dashboard"
echo "3. Check service logs for any errors"
echo "4. Configure domain if needed"
