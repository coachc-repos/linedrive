#!/bin/bash
# Deploy scriptcraft-app-v2-container (headless cloud variant) to the SAME
# Azure Container App that the v1 deploy-azure.sh script targets.
#
# Differences vs scriptcraft-app/scriptcraft-enhanced-debug-package/deploy-azure.sh:
#   - Builds from this folder's Dockerfile (no docker/ subfolder)
#   - Target port 8080 (not 5007) — explicitly updates ingress
#   - Reuses existing API keys from the current Container App env if no .env
#
# Resource group, registry, environment, and app name are intentionally kept
# identical so this REPLACES the running container.

set -e
cd "$(dirname "$0")"

# --- Config ---------------------------------------------------------------
RESOURCE_GROUP="scriptcraft-rg"
LOCATION="eastus"
CONTAINER_APP_NAME="scriptcraft-app"
CONTAINER_APP_ENV="linedrive-env"
CONTAINER_REGISTRY="scriptcraftregistry"
IMAGE_NAME="scriptcraft"
BUILD_VERSION="v2c.$(date +%Y%m%d%H%M)"
IMAGE_TAG="$BUILD_VERSION"
TARGET_PORT=8080

echo "🚀 ScriptCraft v2 Container Deployment"
echo "======================================"
echo "📋 Build Version: $BUILD_VERSION"
echo "🏷️  Image Tag:     $IMAGE_TAG"
echo "🎯 App:           $CONTAINER_APP_NAME (RG: $RESOURCE_GROUP)"
echo "🔌 Target port:   $TARGET_PORT"

command -v az >/dev/null || { echo "❌ Azure CLI not installed"; exit 1; }
az account show >/dev/null 2>&1 || { echo "❌ Run: az login"; exit 1; }

# --- Resource group -------------------------------------------------------
if ! az group show --name "$RESOURCE_GROUP" >/dev/null 2>&1; then
    echo "📁 Creating resource group $RESOURCE_GROUP ..."
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION" -o table
fi

# --- Container registry ---------------------------------------------------
if ! az acr show --name "$CONTAINER_REGISTRY" >/dev/null 2>&1; then
    echo "🐳 Creating registry $CONTAINER_REGISTRY ..."
    az acr create --resource-group "$RESOURCE_GROUP" --name "$CONTAINER_REGISTRY" \
        --sku Basic --admin-enabled true -o table
fi
REGISTRY_SERVER=$(az acr show --name "$CONTAINER_REGISTRY" --query loginServer -o tsv)
REGISTRY_USERNAME=$(az acr credential show --name "$CONTAINER_REGISTRY" --query username -o tsv)
REGISTRY_PASSWORD=$(az acr credential show --name "$CONTAINER_REGISTRY" --query passwords[0].value -o tsv)
echo "📦 Registry: $REGISTRY_SERVER"

# --- Build image in ACR (no local docker required) -----------------------
echo "🔨 Building image in Azure Container Registry ..."
az acr build \
    --registry "$CONTAINER_REGISTRY" \
    --image "$IMAGE_NAME:$IMAGE_TAG" \
    -f Dockerfile \
    --build-arg BUILD_VERSION="$BUILD_VERSION" \
    .

# --- Container Apps environment ------------------------------------------
if ! az containerapp env show --name "$CONTAINER_APP_ENV" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    echo "🌍 Creating Container Apps environment ..."
    az containerapp env create --name "$CONTAINER_APP_ENV" \
        --resource-group "$RESOURCE_GROUP" --location "$LOCATION" -o table
fi

# --- API keys: prefer .env, otherwise pull from current container -------
if [ -f ".env" ]; then
    echo "🔑 Reading API keys from .env ..."
    AI_PROJECT_API_KEY=$(grep '^AI_PROJECT_API_KEY=' .env | cut -d= -f2-)
    GOOGLE_API_KEY=$(grep '^GOOGLE_API_KEY=' .env | cut -d= -f2-)
fi

if [ -z "$AI_PROJECT_API_KEY" ] || [ -z "$GOOGLE_API_KEY" ]; then
    if az containerapp show --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
        echo "🔑 Reusing API keys from existing container app env ..."
        AI_PROJECT_API_KEY=$(az containerapp show --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" \
            --query "properties.template.containers[0].env[?name=='AI_PROJECT_API_KEY'].value | [0]" -o tsv)
        GOOGLE_API_KEY=$(az containerapp show --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" \
            --query "properties.template.containers[0].env[?name=='GOOGLE_API_KEY'].value | [0]" -o tsv)
    fi
fi

if [ -z "$AI_PROJECT_API_KEY" ] || [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Missing AI_PROJECT_API_KEY or GOOGLE_API_KEY (no .env, no existing app)"
    exit 1
fi
echo "✅ API keys resolved"

# --- Optional extra keys (passed through if present) ---------------------
GROK_API_KEY="${GROK_API_KEY:-}"
HEYGEN_API_KEY="${HEYGEN_API_KEY:-}"
AI_PROJECT_ENDPOINT="${AI_PROJECT_ENDPOINT:-}"
FINISHED_VIDEOS_BLOB_ACCOUNT="${FINISHED_VIDEOS_BLOB_ACCOUNT:-linedrivestorage}"
FINISHED_VIDEOS_BLOB_CONTAINER="${FINISHED_VIDEOS_BLOB_CONTAINER:-finished-videos}"

ENV_VARS_ARGS=("PYTHONPATH=/app" "AI_PROJECT_API_KEY=$AI_PROJECT_API_KEY" "GOOGLE_API_KEY=$GOOGLE_API_KEY")
[ -n "$GROK_API_KEY" ] && ENV_VARS_ARGS+=("GROK_API_KEY=$GROK_API_KEY")
[ -n "$HEYGEN_API_KEY" ] && ENV_VARS_ARGS+=("HEYGEN_API_KEY=$HEYGEN_API_KEY")
[ -n "$AI_PROJECT_ENDPOINT" ] && ENV_VARS_ARGS+=("AI_PROJECT_ENDPOINT=$AI_PROJECT_ENDPOINT")
ENV_VARS_ARGS+=("FINISHED_VIDEOS_BLOB_ACCOUNT=$FINISHED_VIDEOS_BLOB_ACCOUNT")
ENV_VARS_ARGS+=("FINISHED_VIDEOS_BLOB_CONTAINER=$FINISHED_VIDEOS_BLOB_CONTAINER")

# --- Create or update the container app ----------------------------------
FULL_IMAGE="$REGISTRY_SERVER/$IMAGE_NAME:$IMAGE_TAG"
echo "🚀 Deploying $FULL_IMAGE ..."

if az containerapp show --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    echo "♻️  Updating existing container app ..."
    az containerapp update \
        --name "$CONTAINER_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --image "$FULL_IMAGE" \
        --set-env-vars "${ENV_VARS_ARGS[@]}" \
        -o table

    # Ensure ingress targets the new port (was 5007 in v1)
    CURRENT_PORT=$(az containerapp show --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" \
        --query "properties.configuration.ingress.targetPort" -o tsv)
    if [ "$CURRENT_PORT" != "$TARGET_PORT" ]; then
        echo "🔌 Updating ingress port $CURRENT_PORT -> $TARGET_PORT ..."
        az containerapp ingress update \
            --name "$CONTAINER_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --target-port "$TARGET_PORT" \
            --type external \
            -o table
    fi
else
    echo "🆕 Creating container app ..."
    az containerapp create \
        --name "$CONTAINER_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --environment "$CONTAINER_APP_ENV" \
        --image "$FULL_IMAGE" \
        --registry-server "$REGISTRY_SERVER" \
        --registry-username "$REGISTRY_USERNAME" \
        --registry-password "$REGISTRY_PASSWORD" \
        --target-port "$TARGET_PORT" \
        --ingress external \
        --min-replicas 1 \
        --max-replicas 3 \
        --cpu 0.5 \
        --memory 1Gi \
        --env-vars "${ENV_VARS_ARGS[@]}" \
        -o table
fi

# --- Single revision mode + clean up old revisions -----------------------
echo "⚙️  Setting single revision mode ..."
az containerapp revision set-mode --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" --mode Single >/dev/null 2>&1 || true

LATEST_REVISION=$(az containerapp revision list \
    --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" \
    --query "max_by([], &properties.createdTime).name" -o tsv)
echo "📌 Latest revision: $LATEST_REVISION"

OLD_REVISIONS=$(az containerapp revision list \
    --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" \
    --query "[?properties.active && name != '$LATEST_REVISION'].name" -o tsv)
if [ -n "$OLD_REVISIONS" ]; then
    echo "🧹 Deactivating old revisions ..."
    for r in $OLD_REVISIONS; do
        echo "   - $r"
        az containerapp revision deactivate --name "$CONTAINER_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" --revision "$r" >/dev/null 2>&1 || true
    done
fi

# --- Managed identity -----------------------------------------------------
echo "🔐 Ensuring system-assigned managed identity ..."
az containerapp identity assign --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" --system-assigned >/dev/null
CURRENT_REVISION=$(az containerapp revision list --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv)
az containerapp revision restart --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" --revision "$CURRENT_REVISION" >/dev/null

# --- Done -----------------------------------------------------------------
APP_URL=$(az containerapp show --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.configuration.ingress.fqdn -o tsv)

echo ""
echo "✅ Deployment complete!"
echo "🌍 https://$APP_URL"
echo "💓 https://$APP_URL/healthz"
