#!/bin/bash
# Real-Time Email Sync Startup Script

echo "🚀 Starting Real-Time Email Sync System..."

# Check if config is set up
if grep -q "your_app_password_here" config.py; then
    echo "⚠️  Please configure your email accounts in config.py first!"
    echo "1. Edit config.py"
    echo "2. Add your Gmail credentials"
    echo "3. Run this script again"
    exit 1
fi

# Start the email sync service in background
echo "📧 Starting email synchronization service..."
"$PWD/.venv/bin/python" email_sync_service.py &
SYNC_PID=$!

# Wait a moment for sync to start
sleep 3

# Start the web server
echo "🌐 Starting web dashboard..."
node index.js &
WEB_PID=$!

echo "✅ System started successfully!"
echo ""
echo "📊 Dashboard: http://localhost:4000"
echo "📧 Sync Service PID: $SYNC_PID"
echo "🌐 Web Server PID: $WEB_PID"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for interrupt
trap "echo '🛑 Stopping services...'; kill $SYNC_PID $WEB_PID; exit" INT
wait
