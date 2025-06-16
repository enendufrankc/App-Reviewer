# Railway-optimized Dockerfile
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./static

# Create a simple startup script for Railway
RUN printf '#!/bin/bash\n\
export PORT=${PORT:-8000}\n\
echo "Starting on port $PORT"\n\
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT\n' > /start.sh

RUN chmod +x /start.sh

# Use Railway PORT environment variable
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

CMD ["/start.sh"]