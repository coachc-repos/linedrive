#!/bin/bash
# ScriptCraft - Simple Launcher (Fixed)

# Always run from the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "🎬 ScriptCraft Web App"
echo "====================="
echo "📂 Running from: $(pwd)"

# Verify package structure
echo "🔍 Checking package structure..."
if [[ ! -d "docker" ]]; then
    echo "❌ docker/ directory missing"
    echo "Contents of current directory:"
    ls -la
    exit 1
fi

if [[ ! -f "web_gui.py" ]]; then
    echo "❌ web_gui.py missing"
    exit 1
fi

if [[ ! -f "docker/docker-compose.yml" ]]; then
    echo "❌ docker/docker-compose.yml missing"
    exit 1
fi

echo "✅ Package structure OK"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found"
    echo "Install: brew install azure-cli"
    echo "Then run: az login"
    exit 1
fi

if ! az account show &> /dev/null; then
    echo "❌ Azure CLI not authenticated"
    echo "Run: az login"
    exit 1
fi

echo "✅ Azure CLI authenticated"

# Create .env file if needed
if [[ ! -f "docker/.env" ]]; then
    echo "🔧 Creating .env file..."
    cat > docker/.env << 'EOF'
# ScriptCraft - Azure CLI Authentication
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_TENANT_ID=
AZURE_AI_ENDPOINT=https://linedrive-ai-foundry.services.ai.azure.com/api/projects/linedriveAgents
LOG_LEVEL=INFO
DEBUG=false
EOF
    echo "✅ .env file created"
fi

# Start ScriptCraft
echo "🚀 Starting ScriptCraft..."
cd docker
./start.sh

echo "✅ ScriptCraft startup complete!"
echo "🌐 Access at: http://localhost:5007"
