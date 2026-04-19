#!/bin/bash
# ScriptCraft Web Server Launcher
# This script starts the ScriptCraft web application

echo "🚀 Starting ScriptCraft Web Server..."
cd "$(dirname "$0")/scriptcraft-app"
source ../venv314/bin/activate
echo "✅ Virtual environment activated"
echo "🌐 Starting web server at http://localhost:5005"
python web_gui.py
