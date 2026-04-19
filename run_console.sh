#!/bin/bash

# LineDrive Console Launcher with Virtual Environment
# This script ensures the virtual environment is activated before running the console

echo "🚀 Starting LineDrive Console..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists (look for venv314 in same directory)
if [ ! -d "$SCRIPT_DIR/venv314" ]; then
    echo "❌ Virtual environment not found at $SCRIPT_DIR/venv314"
    echo "💡 Please create the virtual environment first:"
    echo "   python3 -m venv venv314"
    echo "   source venv314/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Use the venv Python directly (no need to activate for script execution)
VENV_PYTHON="$SCRIPT_DIR/venv314/bin/python"

echo "✅ Using virtual environment"
echo "� Python path: $VENV_PYTHON"
echo "🐍 Python version: $($VENV_PYTHON --version)"

# Run the modular console launcher with venv Python
$VENV_PYTHON console_launcher_module.py

echo "👋 LineDrive Console session ended"
