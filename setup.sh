#!/bin/bash
# Quick setup script for Gmail Email Fetcher

echo "🚀 Setting up Gmail Email Fetcher..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Please run this script from the onebox(1) directory"
    exit 1
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
./.venv/bin/pip install python-dateutil

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit get_messages.py and add your Gmail credentials"
echo "2. Run: node index.js"
echo "3. Open: http://localhost:4000"
echo ""
echo "⚠️  Remember to use Gmail App Password, not your regular password!"
