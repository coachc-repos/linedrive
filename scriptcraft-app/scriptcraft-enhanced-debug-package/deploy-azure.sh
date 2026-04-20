#!/bin/bash
# ScriptCraft Azure Container Apps Deployment Script

set -e

# Change to the script directory
cd "$(dirname "$0")"

# Configuration
RESOURCE_GROUP="scriptcraft-rg"
LOCATION="eastus"
CONTAINER_APP_NAME="scriptcraft-app"
CONTAINER_APP_ENV="linedrive-env"
CONTAINER_REGISTRY="scriptcraftregistry"
IMAGE_NAME="scriptcraft"
BUILD_VERSION="2.1.$(date +%Y%m%d%H%M)"
IMAGE_TAG="$BUILD_VERSION"

echo "🚀 ScriptCraft Azure Container Apps Deployment"
echo "=============================================="
echo "📋 Build Version: $BUILD_VERSION"
echo "🏷️  Image Tag: $IMAGE_TAG"

# Check if Azure CLI is installed and user is logged in
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo "❌ Please log in to Azure CLI: az login"
    exit 1
fi

echo "✅ Azure CLI ready"

# Get or create resource group
echo "📁 Checking resource group..."
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "Creating resource group..."
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --output table
else
    echo "✅ Resource group exists"
fi

# Get or create container registry
echo "🐳 Checking container registry..."
if ! az acr show --name $CONTAINER_REGISTRY &> /dev/null; then
    echo "Creating container registry..."
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_REGISTRY \
        --sku Basic \
        --admin-enabled true \
        --output table
else
    echo "✅ Container registry exists"
fi

# Get registry credentials
echo "🔑 Getting registry credentials..."
REGISTRY_SERVER=$(az acr show --name $CONTAINER_REGISTRY --query loginServer --output tsv)
REGISTRY_USERNAME=$(az acr credential show --name $CONTAINER_REGISTRY --query username --output tsv)
REGISTRY_PASSWORD=$(az acr credential show --name $CONTAINER_REGISTRY --query passwords[0].value --output tsv)

echo "📦 Registry: $REGISTRY_SERVER"

# Build using Azure Container Registry (no local Docker needed)
echo "🔨 Building Docker image in Azure..."
az acr build --registry $CONTAINER_REGISTRY --image $IMAGE_NAME:$IMAGE_TAG -f docker/Dockerfile --build-arg BUILD_VERSION=$BUILD_VERSION .

# Get or create Container Apps environment
echo "🌍 Checking Container Apps environment..."
if ! az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating Container Apps environment..."
    az containerapp env create \
        --name $CONTAINER_APP_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --output table
else
    echo "✅ Container Apps environment exists"
fi

# Read API key from .env file
if [ -f ".env" ]; then
    AI_PROJECT_API_KEY=$(grep "AI_PROJECT_API_KEY=" .env | cut -d= -f2)
    GOOGLE_API_KEY=$(grep "GOOGLE_API_KEY=" .env | cut -d= -f2)
    echo "✅ Found API keys in .env file"
    
    # Check if GOOGLE_API_KEY was found
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo "⚠️  GOOGLE_API_KEY not found in .env file"
        echo "   Thumbnail generation will use hardcoded fallback"
        GOOGLE_API_KEY="AIzaSyDRyFKaGX1aBTya9Ljb_CaCM6-7I0USVhg"
    fi
else
    echo "❌ .env file not found. Please create it with AI_PROJECT_API_KEY and GOOGLE_API_KEY"
    exit 1
fi

# Create or update the container app
echo "🚀 Deploying container app..."
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image $REGISTRY_SERVER/$IMAGE_NAME:$IMAGE_TAG \
    --registry-server $REGISTRY_SERVER \
    --registry-username $REGISTRY_USERNAME \
    --registry-password $REGISTRY_PASSWORD \
    --target-port 5007 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 3 \
    --cpu 0.5 \
    --memory 1Gi \
    --env-vars "PYTHONPATH=/app" "AI_PROJECT_API_KEY=$AI_PROJECT_API_KEY" "GOOGLE_API_KEY=$GOOGLE_API_KEY" \
    --output table || \
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $REGISTRY_SERVER/$IMAGE_NAME:$IMAGE_TAG \
    --env-vars "PYTHONPATH=/app" "AI_PROJECT_API_KEY=$AI_PROJECT_API_KEY" "GOOGLE_API_KEY=$GOOGLE_API_KEY" \
    --output table

# Configure single revision mode to automatically manage revisions
echo "⚙️  Configuring single revision mode..."
az containerapp revision set-mode \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --mode Single > /dev/null 2>&1 || echo "Note: Single revision mode may already be set"

# Clean up old revisions - keep only the latest
echo "🧹 Cleaning up old revisions..."
LATEST_REVISION=$(az containerapp revision list \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "max_by([], &properties.createdTime).name" \
    --output tsv)

echo "📌 Latest revision: $LATEST_REVISION"

# Deactivate all revisions except the latest
OLD_REVISIONS=$(az containerapp revision list \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "[?properties.active && name != '$LATEST_REVISION'].name" \
    --output tsv)

if [ ! -z "$OLD_REVISIONS" ]; then
    echo "🗑️  Deactivating old revisions..."
    for revision in $OLD_REVISIONS; do
        echo "   Deactivating: $revision"
        az containerapp revision deactivate \
            --name $CONTAINER_APP_NAME \
            --resource-group $RESOURCE_GROUP \
            --revision $revision > /dev/null 2>&1
    done
    echo "✅ Old revisions deactivated"
else
    echo "✅ No old revisions to clean up"
fi

# Get the app URL
echo "🌐 Getting application URL..."
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo ""
# 🔥 CRITICAL: Restore managed identity after deployment
echo "🔐 Restoring managed identity..."
az containerapp identity assign --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --system-assigned
echo "✅ Managed identity restored"

# Restart the container app to pick up the identity
echo "🔄 Restarting container app to apply identity..."
CURRENT_REVISION=$(az containerapp revision list --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "[0].name" -o tsv)
az containerapp revision restart --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --revision $CURRENT_REVISION
echo "✅ Container app restarted"

echo "✅ Deployment completed!"
echo "🌍 Application URL: https://$APP_URL"
echo "📊 Resource Group: $RESOURCE_GROUP"
echo "🐳 Registry: $REGISTRY_SERVER"
echo ""
echo "📋 Next steps:"
echo "   1. Test the app at: https://$APP_URL"
echo "   2. Integrate with your static web app"
echo "   3. Add CORS configuration if needed"
echo ""
echo "🔧 Update commands:"
echo "   # To update the app:"
echo "   docker build -t $IMAGE_NAME:$IMAGE_TAG -f docker/Dockerfile ."
echo "   docker tag $IMAGE_NAME:$IMAGE_TAG $REGISTRY_SERVER/$IMAGE_NAME:$IMAGE_TAG"
echo "   docker push $REGISTRY_SERVER/$IMAGE_NAME:$IMAGE_TAG"
echo "   az containerapp update --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --image $REGISTRY_SERVER/$IMAGE_NAME:$IMAGE_TAG"
