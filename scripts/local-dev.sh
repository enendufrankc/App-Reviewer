#!/bin/bash
set -e

echo "🔧 Starting local development environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please create one with your environment variables"
    exit 1
fi

# Build and start services
echo "🏗️ Building and starting application..."
docker-compose up --build -d

echo "⏳ Waiting for application to be ready..."
sleep 10

# Check service health
echo "🔍 Checking application health..."
curl -f http://localhost:8000/health || echo "Health check failed"

echo "✅ Development environment ready!"
echo "🌐 Application: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"

# Show logs
echo "📋 Application logs:"
docker-compose logs -f