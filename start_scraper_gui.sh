#!/bin/bash
# Start the LineDrive Scraper Web GUI
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VENV_PYTHON="$SCRIPT_DIR/venv314/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found at venv314/"
    echo "   Run: python3 -m venv venv314 && venv314/bin/pip install flask selenium beautifulsoup4"
    exit 1
fi

echo "🏆 Starting LineDrive Scraper Web GUI..."
echo "📍 http://localhost:8081"
echo ""
$VENV_PYTHON scraper_web_gui.py
