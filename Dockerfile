# Multi-stage build combining frontend and backend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies using npm (more reliable than bun for Docker builds)
RUN npm install

# Copy source code
COPY frontend/ ./

# Build the application
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

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy frontend build from the builder stage
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Create nginx configuration
RUN cat > /etc/nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 100M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    server {
        listen 80;
        server_name _;
        
        # Serve frontend static files
        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
            try_files $uri $uri/ /index.html;
        }
        
        # Proxy API requests to backend
        location /api/ {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Handle large file uploads and long processing times
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
            proxy_send_timeout 300s;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Create supervisor configuration directories
RUN mkdir -p /etc/supervisor/conf.d /var/log/supervisor

# Create supervisor configuration file
RUN cat > /etc/supervisor/conf.d/supervisord.conf << 'EOF'
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid
childlogdir=/var/log/supervisor

[unix_http_server]
file=/var/run/supervisor.sock
chmod=0700

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/supervisor/nginx.err.log
stdout_logfile=/var/log/supervisor/nginx.out.log
stderr_logfile_maxbytes=10MB
stdout_logfile_maxbytes=10MB

[program:backend]
command=uvicorn main:app --host 127.0.0.1 --port 8000
directory=/app
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
stderr_logfile_maxbytes=10MB
stdout_logfile_maxbytes=10MB
environment=PYTHONPATH="/app"
EOF

# Create necessary application directories
RUN mkdir -p data ffmpeg uploads credentials

# Set proper permissions for credentials directory
RUN chmod 755 /app/credentials

# Create a startup script for additional initialization if needed
RUN cat > /start.sh << 'EOF'
#!/bin/bash
set -e

echo "=== App Reviewer Starting ==="
echo "Checking system dependencies..."

# Check if ffmpeg is available
if command -v ffmpeg >/dev/null 2>&1; then
    echo "✓ FFmpeg is available"
    ffmpeg -version | head -n 1
else
    echo "✗ FFmpeg not found"
    exit 1
fi

# Check if required directories exist
for dir in data ffmpeg uploads credentials; do
    if [ -d "/app/$dir" ]; then
        echo "✓ Directory /app/$dir exists"
    else
        echo "✗ Directory /app/$dir missing"
        mkdir -p "/app/$dir"
        echo "✓ Created directory /app/$dir"
    fi
done

# Start supervisor
echo "Starting services with supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
EOF

RUN chmod +x /start.sh

# Expose port 80 (Railway will map this to their PORT)
EXPOSE 80

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Use the startup script
CMD ["/start.sh"]