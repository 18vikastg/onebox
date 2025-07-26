#!/bin/bash

echo "🚀 Starting Complete Email System..."

# 1. Start Elasticsearch & Kibana
echo "📊 Starting Elasticsearch & Kibana..."
docker-compose up -d

# Wait for Elasticsearch to be ready
echo "⏳ Waiting for Elasticsearch to be ready..."
until curl -s http://localhost:9200 > /dev/null; do
    sleep 2
done

# 2. Start the system
echo "🔄 Starting email sync and web dashboard..."
./start_system.sh

echo "✅ System started successfully!"
echo ""
echo "📊 Dashboard: http://localhost:4000"
echo "🔍 Kibana: http://localhost:5601"
echo "🗃️ Elasticsearch: http://localhost:9200"
echo ""
echo "Press Ctrl+C to stop all services..."
