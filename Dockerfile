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

# Create nginx configuration using printf instead of heredoc
RUN printf 'events {\n\
    worker_connections 1024;\n\
}\n\
\n\
http {\n\
    include /etc/nginx/mime.types;\n\
    default_type application/octet-stream;\n\
    \n\
    sendfile on;\n\
    keepalive_timeout 65;\n\
    client_max_body_size 100M;\n\
    \n\
    gzip on;\n\
    gzip_vary on;\n\
    gzip_min_length 1024;\n\
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;\n\
\n\
    server {\n\
        listen 80;\n\
        server_name _;\n\
        \n\
        location / {\n\
            root /usr/share/nginx/html;\n\
            index index.html index.htm;\n\
            try_files $uri $uri/ /index.html;\n\
        }\n\
        \n\
        location /api/ {\n\
            proxy_pass http://127.0.0.1:8000;\n\
            proxy_set_header Host $host;\n\
            proxy_set_header X-Real-IP $remote_addr;\n\
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
            proxy_set_header X-Forwarded-Proto $scheme;\n\
            \n\
            proxy_read_timeout 300s;\n\
            proxy_connect_timeout 75s;\n\
            proxy_send_timeout 300s;\n\
        }\n\
        \n\
        location /health {\n\
            access_log off;\n\
            return 200 "healthy\\n";\n\
            add_header Content-Type text/plain;\n\
        }\n\
    }\n\
}\n' > /etc/nginx/nginx.conf

# Create supervisor configuration directories
RUN mkdir -p /etc/supervisor/conf.d /var/log/supervisor

# Create supervisor configuration file using printf
RUN printf '[supervisord]\n\
nodaemon=true\n\
user=root\n\
logfile=/var/log/supervisor/supervisord.log\n\
pidfile=/var/run/supervisord.pid\n\
childlogdir=/var/log/supervisor\n\
\n\
[unix_http_server]\n\
file=/var/run/supervisor.sock\n\
chmod=0700\n\
\n\
[rpcinterface:supervisor]\n\
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface\n\
\n\
[supervisorctl]\n\
serverurl=unix:///var/run/supervisor.sock\n\
\n\
[program:nginx]\n\
command=nginx -g "daemon off;"\n\
autostart=true\n\
autorestart=true\n\
startretries=3\n\
stderr_logfile=/var/log/supervisor/nginx.err.log\n\
stdout_logfile=/var/log/supervisor/nginx.out.log\n\
stderr_logfile_maxbytes=10MB\n\
stdout_logfile_maxbytes=10MB\n\
\n\
[program:backend]\n\
command=uvicorn main:app --host 127.0.0.1 --port 8000\n\
directory=/app\n\
autostart=true\n\
autorestart=true\n\
startretries=3\n\
stderr_logfile=/var/log/supervisor/backend.err.log\n\
stdout_logfile=/var/log/supervisor/backend.out.log\n\
stderr_logfile_maxbytes=10MB\n\
stdout_logfile_maxbytes=10MB\n\
environment=PYTHONPATH="/app"\n' > /etc/supervisor/conf.d/supervisord.conf

# Create necessary application directories
RUN mkdir -p data ffmpeg uploads credentials

# Set proper permissions for credentials directory
RUN chmod 755 /app/credentials

# Create a startup script using printf
RUN printf '#!/bin/bash\n\
set -e\n\
\n\
echo "=== App Reviewer Starting ==="\n\
echo "Checking system dependencies..."\n\
\n\
if command -v ffmpeg >/dev/null 2>&1; then\n\
    echo "✓ FFmpeg is available"\n\
    ffmpeg -version | head -n 1\n\
else\n\
    echo "✗ FFmpeg not found"\n\
    exit 1\n\
fi\n\
\n\
for dir in data ffmpeg uploads credentials; do\n\
    if [ -d "/app/$dir" ]; then\n\
        echo "✓ Directory /app/$dir exists"\n\
    else\n\
        echo "✗ Directory /app/$dir missing"\n\
        mkdir -p "/app/$dir"\n\
        echo "✓ Created directory /app/$dir"\n\
    fi\n\
done\n\
\n\
echo "Starting services with supervisor..."\n\
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf\n' > /start.sh

RUN chmod +x /start.sh

# Expose port 80 (Railway will map this to their PORT)
EXPOSE 80

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Use the startup script
CMD ["/start.sh"]