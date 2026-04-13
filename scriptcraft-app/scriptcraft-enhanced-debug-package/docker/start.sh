#!/bin/bash
# ScriptCraft Docker Launcher
# Simple script to start ScriptCraft web app

cd "$(dirname "$0")"

echo "🎬 Starting ScriptCraft Web App..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.template .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your Azure credentials!"
    echo "   Required variables:"
    echo "   - AZURE_CLIENT_ID"
    echo "   - AZURE_CLIENT_SECRET" 
    echo "   - AZURE_TENANT_ID"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Start the application
docker-compose up -d

echo ""
echo "✅ ScriptCraft is starting..."
echo "🌐 Access at: http://localhost:5007"
echo "📋 View logs: docker-compose logs -f"
echo "🛑 Stop app: docker-compose down"
