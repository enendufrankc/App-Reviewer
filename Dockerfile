# Multi-stage build combining frontend and backend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
COPY frontend/bun.lockb ./

# Install dependencies using npm (Railway supports npm better than bun)
RUN npm install

COPY frontend/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Create nginx configuration
RUN echo 'events { worker_connections 1024; } \
http { \
    include /etc/nginx/mime.types; \
    default_type application/octet-stream; \
    client_max_body_size 100M; \
    gzip on; \
    gzip_types text/plain text/css application/json application/javascript; \
    server { \
        listen 80; \
        location / { \
            root /usr/share/nginx/html; \
            try_files $uri $uri/ /index.html; \
        } \
        location /api/ { \
            proxy_pass http://127.0.0.1:8000; \
            proxy_set_header Host $host; \
            proxy_set_header X-Real-IP $remote_addr; \
            proxy_read_timeout 300s; \
            proxy_connect_timeout 75s; \
        } \
        location /health { \
            return 200 "healthy"; \
            add_header Content-Type text/plain; \
        } \
    } \
}' > /etc/nginx/nginx.conf

# Create supervisor configuration
RUN echo '[supervisord] \
nodaemon=true \
[program:nginx] \
command=nginx -g "daemon off;" \
autostart=true \
autorestart=true \
[program:backend] \
command=uvicorn main:app --host 127.0.0.1 --port 8000 \
directory=/app \
autostart=true \
autorestart=true' > /etc/supervisor/conf.d/supervisord.conf

# Create necessary directories
RUN mkdir -p data ffmpeg credentials

# Expose port (Railway will set the PORT environment variable)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# Start both services
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]