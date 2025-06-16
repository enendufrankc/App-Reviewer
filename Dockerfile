# Multi-stage build combining frontend and backend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
COPY frontend/bun.lockb ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Python backend with nginx
FROM python:3.11-slim

# Install system dependencies
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

# Create nginx config
RUN echo 'events { worker_connections 1024; } \
http { \
    include /etc/nginx/mime.types; \
    default_type application/octet-stream; \
    client_max_body_size 100M; \
    server { \
        listen 80; \
        location / { \
            root /usr/share/nginx/html; \
            try_files $uri $uri/ /index.html; \
        } \
        location /api/ { \
            proxy_pass http://127.0.0.1:8000; \
            proxy_set_header Host $host; \
            proxy_read_timeout 300s; \
        } \
        location /health { \
            return 200 "healthy"; \
            add_header Content-Type text/plain; \
        } \
    } \
}' > /etc/nginx/nginx.conf

# Create supervisor config
RUN echo '[supervisord] \
nodaemon=true \
[program:nginx] \
command=nginx -g "daemon off;" \
[program:backend] \
command=uvicorn main:app --host 127.0.0.1 --port 8000 \
directory=/app' > /etc/supervisor/conf.d/supervisord.conf

# Create directories
RUN mkdir -p data ffmpeg credentials

# Expose port
EXPOSE $PORT

# Start both services
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]