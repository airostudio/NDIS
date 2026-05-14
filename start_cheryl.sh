#!/bin/bash

# Start Cheryl - NDIS Virtual AI Executive Suite
# This script starts the Cheryl API server with frontend

echo "🚀 Starting Cheryl - NDIS Virtual AI Executive Suite"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
if [ ! -f "venv/.dependencies_installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.dependencies_installed
else
    echo "✅ Dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
    echo "   Press Enter when ready..."
    read
fi

# Start the server
echo ""
echo "🌟 Starting Cheryl API Server..."
echo ""
echo "   Frontend: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health:   http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

python scripts/run_api.py
