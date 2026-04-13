#!/bin/bash
# Quick rebuild with fixed __init__.py

echo "🔧 Rebuilding container with fixed __init__.py..."

cd docker

# Stop container
docker-compose down

# Rebuild and start
echo "🐳 Rebuilding..."
docker-compose build --no-cache

echo "🚀 Starting..."
docker-compose up -d

echo ""
echo "✅ Container rebuilt and restarted"
echo "🌐 Try: http://localhost:5007"

# Check status
sleep 3
echo ""
echo "📋 Container status:"
docker ps --filter "name=scriptcraft" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📋 Recent logs:"
docker-compose logs --tail 5
