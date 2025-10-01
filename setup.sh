#!/bin/bash

echo "🚀 Quick Setup for Text2SQL API with Vanna"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found"

# Install dependencies
echo "📦 Installing dependencies..."
./install.sh

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Please configure your .env file with your Vanna API key and ClickHouse settings"
    echo "   Edit the .env file and replace 'your_vanna_api_key_here' with your actual API key"
    echo "   Get your API key from: https://vanna.ai"
    echo ""
fi

echo "🔧 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure your .env file with your Vanna API key"
echo "2. Start the API server: ./start.sh"
echo "3. Test the API: python3 example.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
