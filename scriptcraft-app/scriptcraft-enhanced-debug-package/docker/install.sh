#!/bin/bash
# ScriptCraft Web App Installation Script
# Installs and starts ScriptCraft as a Docker container

set -e

echo "🎬 ScriptCraft Web App Installer"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please edit the .env file with your Azure credentials before starting"
    echo "   Required: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID"
fi

# Build and start the application
echo "🔨 Building ScriptCraft Docker image..."
docker-compose build

echo "🚀 Starting ScriptCraft Web App..."
docker-compose up -d

# Wait for the application to start
echo "⏳ Waiting for ScriptCraft to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost:5007/ &> /dev/null; then
    echo "✅ ScriptCraft is running successfully!"
    echo ""
    echo "🌐 Access ScriptCraft at: http://localhost:5007"
    echo "📁 Output files will be saved to Docker volume: scriptcraft-output"
    echo "📋 View logs with: docker-compose logs -f"
    echo "🛑 Stop with: docker-compose down"
else
    echo "❌ ScriptCraft failed to start. Check logs with:"
    echo "   docker-compose logs"
fi

echo ""
echo "📖 For more information, see README.md"
