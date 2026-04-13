#!/bin/bash

echo "========================================"
echo "🚀 Starting ScriptCraft Web GUI"
echo "========================================"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "📁 Script directory: $SCRIPT_DIR"
echo "📁 Repository root: $REPO_ROOT"
echo ""

# Activate virtual environment if it exists
if [ -d "$REPO_ROOT/venv312" ]; then
    echo "🐍 Activating virtual environment..."
    source "$REPO_ROOT/venv312/bin/activate"
    echo "✅ Virtual environment activated"
elif [ -d "$REPO_ROOT/.venv" ]; then
    echo "🐍 Activating virtual environment..."
    source "$REPO_ROOT/.venv/bin/activate"
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found"
fi
echo ""

# Export Google API key
export GOOGLE_API_KEY="AIzaSyAiFFlgDokz-s4U8UrV73Fhdnl8Ukx2jCM"
echo "🔑 Google API key exported"
echo ""

# Change to scriptcraft-app directory
cd "$SCRIPT_DIR"
echo "📂 Working directory: $(pwd)"
echo ""

# Check if web_gui.py exists
if [ ! -f "web_gui.py" ]; then
    echo "❌ Error: web_gui.py not found!"
    exit 1
fi

# Check Python version
echo "🐍 Python version:"
python --version
echo ""

# Check if required packages are installed
echo "📦 Checking key packages..."
python -c "import flask; print('✅ Flask installed')" 2>/dev/null || echo "❌ Flask not installed"
python -c "import google.generativeai; print('✅ google-generativeai installed')" 2>/dev/null || echo "❌ google-generativeai not installed"
python -c "from PIL import Image; print('✅ Pillow installed')" 2>/dev/null || echo "❌ Pillow not installed"
echo ""

# Check if thumbnail template exists
TEMPLATE_PATH="$REPO_ROOT/tools/media/Thumbnail_Template_Canva.png"
if [ -f "$TEMPLATE_PATH" ]; then
    echo "✅ Thumbnail template found: $TEMPLATE_PATH"
else
    echo "❌ Thumbnail template NOT found: $TEMPLATE_PATH"
fi
echo ""

echo "========================================"
echo "🌐 Starting Flask server on port 5001"
echo "========================================"
echo "📍 URL: http://localhost:5001"
echo "⏹️  Press Ctrl+C to stop"
echo ""

# Run the web GUI
python web_gui.py
