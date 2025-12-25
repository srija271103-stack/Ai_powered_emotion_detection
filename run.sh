#!/bin/bash
# Mental Wellness Companion - Quick Start Script

echo "================================================"
echo "   💙 Mental Wellness Companion"
echo "   Voice-Based Emotional Support System"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📥 Installing dependencies (this may take a few minutes)..."
    pip install -r requirements.txt
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "   Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    echo "   Please edit .env and add your API keys:"
    echo "   - ANTHROPIC_API_KEY (required)"
    echo "   - HUME_API_KEY (required)"
    echo ""
    read -p "   Press Enter to continue after adding keys, or Ctrl+C to exit..."
fi

echo ""
echo "🚀 Starting the application..."
echo "   Open http://localhost:8501 in your browser"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Run the application
python main.py --streamlit
