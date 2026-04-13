#!/bin/bash

# 🚨 EMERGENCY WEB GUI RESTORE SCRIPT 🚨
# This script restores the LAST WORKING VERSION of the web GUI
# Use this if any changes break the script creation functionality

echo "🚨 RESTORING LAST WORKING WEB GUI VERSION..."
echo "📅 Working version from: $(date)"
echo ""

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Show current commit
echo "🔍 Current commit:"
git log --oneline -1

echo ""
echo "⚠️  This will HARD RESET to the working web GUI version."
echo "❌ Any uncommitted changes will be LOST!"
echo ""
read -p "🤔 Are you sure you want to proceed? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🔄 Restoring to working web GUI tag: working-web-gui-v1.0"
    
    # Reset to the working tag
    git reset --hard working-web-gui-v1.0
    
    echo ""
    echo "✅ WEB GUI RESTORED TO WORKING VERSION!"
    echo "🎉 Script creation should now work properly"
    echo ""
    echo "📋 Key files restored:"
    echo "   • scriptcraft-app/web_gui_console_fixed.py (with SSE completion fix)"
    echo "   • console_launcher_modular.py (baseline working version)"
    echo ""
    echo "🚀 To test: cd scriptcraft-app && python web_gui_console_fixed.py"
    echo ""
else
    echo "❌ Restore cancelled. No changes made."
fi