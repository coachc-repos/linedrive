#!/bin/bash
# Prepare ScriptCraft deployment package with thumbnail support

set -e

echo "📦 Preparing ScriptCraft deployment package with thumbnail support..."

# Source and destination directories
SRC_DIR="/Users/christhi/Dev/Github/linedrive/scriptcraft-app"
DEST_DIR="/Users/christhi/Dev/Github/linedrive/scriptcraft-app/scriptcraft-enhanced-debug-package"

# Copy updated files
echo "📄 Copying updated web_gui.py..."
cp "$SRC_DIR/web_gui.py" "$DEST_DIR/web_gui.py"

echo "📄 Copying updated templates..."
cp -r "$SRC_DIR/templates" "$DEST_DIR/"

echo "📄 Copying updated requirements.txt..."
cp "$SRC_DIR/requirements.txt" "$DEST_DIR/requirements.txt"

echo "📁 Copying tools directory (includes thumbnail generator)..."
cp -r /Users/christhi/Dev/Github/linedrive/tools "$DEST_DIR/"

echo "📁 Copying console_ui directory..."
cp -r "$SRC_DIR/console_ui" "$DEST_DIR/"

echo "📁 Copying linedrive_azure directory..."
cp -r "$SRC_DIR/linedrive_azure" "$DEST_DIR/"

echo ""
echo "✅ Deployment package prepared!"
echo ""
echo "📋 Next steps:"
echo "   1. cd $DEST_DIR"
echo "   2. Edit .env file to add/verify GOOGLE_API_KEY"
echo "   3. Run: ./deploy-azure.sh"
echo ""
echo "🔑 Required in .env:"
echo "   AI_PROJECT_API_KEY=your-azure-ai-project-api-key"
echo "   GOOGLE_API_KEY=AIzaSyAiFFlgDokz-s4U8UrV73Fhdnl8Ukx2jCM"
