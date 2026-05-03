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
VENV_PYTHON="python3"
if [ -d "$REPO_ROOT/venv314" ]; then
    echo "🐍 Activating virtual environment..."
    source "$REPO_ROOT/venv314/bin/activate"
    VENV_PYTHON="$REPO_ROOT/venv314/bin/python3"
    echo "✅ Virtual environment activated"
elif [ -d "$REPO_ROOT/.venv" ]; then
    echo "🐍 Activating virtual environment..."
    source "$REPO_ROOT/.venv/bin/activate"
    VENV_PYTHON="$REPO_ROOT/.venv/bin/python3"
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found"
fi
echo ""

# Export Google API key
export GOOGLE_API_KEY="AIzaSyDRyFKaGX1aBTya9Ljb_CaCM6-7I0USVhg"
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
$VENV_PYTHON --version
echo ""

# Check if required packages are installed
echo "📦 Checking key packages..."
$VENV_PYTHON -c "import flask; print('✅ Flask installed')" 2>/dev/null || echo "❌ Flask not installed"
$VENV_PYTHON -c "import google.generativeai; print('✅ google-generativeai installed')" 2>/dev/null || echo "❌ google-generativeai not installed"
$VENV_PYTHON -c "from PIL import Image; print('✅ Pillow installed')" 2>/dev/null || echo "❌ Pillow not installed"
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
$VENV_PYTHON web_gui.py
