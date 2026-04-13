#!/bin/bash
# Monitor Azure Container Registry Build Status

echo "🔍 Checking Azure Container Registry build status..."
echo ""

# Get latest build
BUILD_INFO=$(az acr task list-runs --registry scriptcraftregistry --top 1 --output table)

echo "$BUILD_INFO"
echo ""

# Get the latest run ID
RUN_ID=$(az acr task list-runs --registry scriptcraftregistry --top 1 --query "[0].runId" -o tsv)

if [ -z "$RUN_ID" ]; then
    echo "❌ No build runs found"
    exit 1
fi

# Check if build is still running
STATUS=$(az acr task list-runs --registry scriptcraftregistry --top 1 --query "[0].status" -o tsv)

echo "📊 Build Run ID: $RUN_ID"
echo "📈 Status: $STATUS"
echo ""

if [ "$STATUS" = "Running" ]; then
    echo "⏳ Build is still in progress..."
    echo ""
    echo "💡 To monitor live logs:"
    echo "   az acr task logs --registry scriptcraftregistry --run-id $RUN_ID --no-format"
    echo ""
    echo "💡 To check status again:"
    echo "   ./check-build-status.sh"
elif [ "$STATUS" = "Succeeded" ]; then
    echo "✅ Build completed successfully!"
    echo ""
    echo "🎯 The deployment script should continue automatically."
    echo "   Check the terminal where you ran deploy-azure.sh"
elif [ "$STATUS" = "Failed" ]; then
    echo "❌ Build failed!"
    echo ""
    echo "🔍 To see error logs:"
    echo "   az acr task logs --registry scriptcraftregistry --run-id $RUN_ID"
else
    echo "ℹ️  Status: $STATUS"
fi
