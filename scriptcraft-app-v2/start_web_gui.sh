#!/bin/bash

echo "========================================"
echo "🚀 Starting ScriptCraft v2 Web GUI (Dual-Mode: v1 Classic / v2 Foundry)"
echo "========================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "📁 Script directory: $SCRIPT_DIR"
echo "📁 Repository root: $REPO_ROOT"
echo ""

VENV_PYTHON="python3"
if [ -d "$REPO_ROOT/venv314_v2" ]; then
    echo "🐍 Activating v2 virtual environment (venv314_v2)..."
    source "$REPO_ROOT/venv314_v2/bin/activate"
    VENV_PYTHON="$REPO_ROOT/venv314_v2/bin/python3"
    echo "✅ v2 virtual environment activated"
else
    echo "❌ venv314_v2 not found at $REPO_ROOT/venv314_v2"
    echo "   Create it with:  python3.14 -m venv $REPO_ROOT/venv314_v2"
    exit 1
fi
echo ""

if [ -n "$GOOGLE_API_KEY" ]; then
    echo "🔑 GOOGLE_API_KEY detected in environment"
else
    echo "⚠️ GOOGLE_API_KEY is not set; thumbnail generation will fail"
fi
echo ""

export FOUNDRY_API_MODE="${FOUNDRY_API_MODE:-v2}"
echo "🔀 Default Foundry agent API mode: $FOUNDRY_API_MODE  (toggle in the UI to switch)"
echo ""

cd "$SCRIPT_DIR"
echo "📂 Working directory: $(pwd)"
echo ""

if [ ! -f "web_gui.py" ]; then
    echo "❌ Error: web_gui.py not found!"
    exit 1
fi

echo "🐍 Python version:"
$VENV_PYTHON --version
echo ""

echo "📦 Checking key packages..."
$VENV_PYTHON -c "import flask; print('✅ Flask installed')" 2>/dev/null || echo "❌ Flask not installed"
$VENV_PYTHON -c "import azure.ai.projects, azure.ai.agents; print('✅ azure-ai-projects + azure-ai-agents installed')" 2>/dev/null || echo "❌ azure SDKs missing"
$VENV_PYTHON -c "from PIL import Image; print('✅ Pillow installed')" 2>/dev/null || echo "❌ Pillow not installed"
echo ""

TEMPLATE_PATH="$REPO_ROOT/tools/media/Thumbnail_Template_Canva.png"
if [ -f "$TEMPLATE_PATH" ]; then
    echo "✅ Thumbnail template found: $TEMPLATE_PATH"
else
    echo "❌ Thumbnail template NOT found: $TEMPLATE_PATH"
fi
echo ""

export PORT="${PORT:-8081}"

echo "========================================"
echo "🌐 Starting Flask server on port $PORT"
echo "========================================"
echo "📍 URL: http://localhost:$PORT"
echo "⏹️  Press Ctrl+C to stop"
echo ""

$VENV_PYTHON web_gui.py
