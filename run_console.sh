#!/bin/bash

# LineDrive Console Launcher with Virtual Environment
# This script ensures the virtual environment is activated before running the console

echo "🚀 Starting LineDrive Console..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists (look for venv312 in same directory)
if [ ! -d "$SCRIPT_DIR/venv312" ]; then
    echo "❌ Virtual environment not found at $SCRIPT_DIR/venv312"
    echo "💡 Please create the virtual environment first:"
    echo "   python3 -m venv venv312"
    echo "   source venv312/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Use the venv Python directly (no need to activate for script execution)
VENV_PYTHON="$SCRIPT_DIR/venv312/bin/python"

echo "✅ Using virtual environment"
echo "� Python path: $VENV_PYTHON"
echo "🐍 Python version: $($VENV_PYTHON --version)"

# Run the modular console launcher with venv Python
$VENV_PYTHON console_launcher_modular.py

echo "👋 LineDrive Console session ended"
