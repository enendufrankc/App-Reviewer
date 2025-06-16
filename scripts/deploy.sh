#!/bin/bash
set -e

echo "🚀 Deploying App Reviewer..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please create one based on .env.example"
    exit 1
fi

# Build and start services with production config
echo "🏗️ Building production images..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service health
echo "🔍 Checking service health..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ Deployment completed!"
echo "🌐 Application available at: http://localhost"

# Show logs
echo "📋 Production logs:"
docker-compose -f docker-compose.prod.yml logs -f