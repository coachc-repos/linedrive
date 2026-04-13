#!/bin/bash

# ScriptCraft Azure Service Principal Setup Script
# This script helps create an Azure service principal for ScriptCraft

set -e

echo "🚀 ScriptCraft Azure Service Principal Setup"
echo "============================================="
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo "🔐 Please log in to Azure CLI first:"
    echo "    az login"
    exit 1
fi

echo "✅ Azure CLI found and authenticated"

# Get current subscription info
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)

echo ""
echo "📋 Current Azure subscription:"
echo "   Name: $SUBSCRIPTION_NAME"
echo "   ID: $SUBSCRIPTION_ID"
echo ""

read -p "Do you want to use this subscription? (y/n): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "Please change to the desired subscription with: az account set --subscription <subscription-id>"
    exit 1
fi

# Ask for service principal name
echo ""
read -p "Enter a name for the service principal (default: scriptcraft-sp): " SP_NAME
SP_NAME=${SP_NAME:-scriptcraft-sp}

echo ""
echo "🔧 Creating service principal '$SP_NAME'..."

# Create service principal
SP_OUTPUT=$(az ad sp create-for-rbac \
    --name "$SP_NAME" \
    --role Contributor \
    --scopes "/subscriptions/$SUBSCRIPTION_ID" \
    --output json)

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to create service principal"
    exit 1
fi

# Parse the output
CLIENT_ID=$(echo $SP_OUTPUT | jq -r '.appId')
CLIENT_SECRET=$(echo $SP_OUTPUT | jq -r '.password')
TENANT_ID=$(echo $SP_OUTPUT | jq -r '.tenant')

echo "✅ Service principal created successfully!"
echo ""

# Create .env file
ENV_FILE="./docker/.env"
echo "📝 Creating $ENV_FILE with your credentials..."

if [[ -f "$ENV_FILE" ]]; then
    echo "⚠️  $ENV_FILE already exists. Creating backup..."
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Copy template to .env
cp "./docker/.env.template" "$ENV_FILE"

# Update the .env file with actual values
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/your_azure_client_id_here/$CLIENT_ID/g" "$ENV_FILE"
    sed -i '' "s/your_azure_client_secret_here/$CLIENT_SECRET/g" "$ENV_FILE"
    sed -i '' "s/your_azure_tenant_id_here/$TENANT_ID/g" "$ENV_FILE"
else
    # Linux
    sed -i "s/your_azure_client_id_here/$CLIENT_ID/g" "$ENV_FILE"
    sed -i "s/your_azure_client_secret_here/$CLIENT_SECRET/g" "$ENV_FILE"
    sed -i "s/your_azure_tenant_id_here/$TENANT_ID/g" "$ENV_FILE"
fi

echo "✅ $ENV_FILE updated with your credentials"
echo ""

echo "🔐 Your Azure credentials:"
echo "========================="
echo "AZURE_CLIENT_ID=$CLIENT_ID"
echo "AZURE_CLIENT_SECRET=$CLIENT_SECRET"
echo "AZURE_TENANT_ID=$TENANT_ID"
echo ""

echo "⚠️  IMPORTANT SECURITY NOTES:"
echo "   • Keep these credentials secure and private"
echo "   • Never commit the .env file to version control"
echo "   • Consider rotating the secret regularly"
echo "   • Delete the service principal when no longer needed"
echo ""

echo "🎯 Next Steps:"
echo "1. The service principal needs access to the Azure AI Foundry project"
echo "2. Contact your Azure AI Foundry administrator to grant access"
echo "3. Run './start-scriptcraft.sh' to launch the application"
echo ""

echo "🚀 Setup complete! Your ScriptCraft is ready to launch."
