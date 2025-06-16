#!/bin/bash
set -e

echo "🔧 Starting local development environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please create one based on .env.example"
    exit 1
fi

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

echo "✅ Development environment ready!"
echo "🌐 Frontend: http://localhost"
echo "🔗 Backend API: http://localhost/api"
echo "📚 API Docs: http://localhost/api/docs"

# Show logs
echo "📋 Service logs:"
docker-compose logs -f