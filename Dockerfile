# Multi-stage build combining frontend and backend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies using npm
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

# Create nginx configuration that uses PORT environment variable
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
        listen $PORT;\n\
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
}' > /etc/nginx/nginx.conf.template

# Create supervisor configuration directories
RUN mkdir -p /etc/supervisor/conf.d /var/log/supervisor

# Create supervisor configuration file
RUN printf '[supervisord]\n\
nodaemon=true\n\
user=root\n\
logfile=/var/log/supervisor/supervisord.log\n\
pidfile=/var/run/supervisord.pid\n\
childlogdir=/var/log/supervisor\n\
loglevel=info\n\
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
command=python -m uvicorn main:app --host 127.0.0.1 --port 8000\n\
directory=/app\n\
autostart=true\n\
autorestart=true\n\
startretries=3\n\
stderr_logfile=/var/log/supervisor/backend.err.log\n\
stdout_logfile=/var/log/supervisor/backend.out.log\n\
stderr_logfile_maxbytes=10MB\n\
stdout_logfile_maxbytes=10MB\n\
environment=PYTHONPATH="/app",PYTHONUNBUFFERED="1"\n' > /etc/supervisor/conf.d/supervisord.conf

# Create necessary application directories
RUN mkdir -p data ffmpeg uploads credentials

# Set proper permissions for credentials directory
RUN chmod 755 /app/credentials

# Create a startup script that handles PORT environment variable
RUN printf '#!/bin/bash\n\
set -e\n\
\n\
echo "=== App Reviewer Starting ==="\n\
echo "PORT: ${PORT:-8000}"\n\
echo "Environment: ${RAILWAY_ENVIRONMENT:-local}"\n\
\n\
# Set default port if not provided\n\
export PORT=${PORT:-8000}\n\
\n\
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
echo "✓ Checking Python environment..."\n\
python --version\n\
pip list | grep -E "(fastapi|uvicorn)" || echo "Warning: FastAPI/Uvicorn not found in pip list"\n\
\n\
echo "✓ Checking FastAPI app..."\n\
cd /app\n\
python -c "from main import app; print(\\"FastAPI app imported successfully\\")" || {\n\
    echo "❌ Failed to import FastAPI app"\n\
    echo "Contents of /app:"\n\
    ls -la /app/\n\
    echo "Python path:"\n\
    python -c "import sys; print(sys.path)"\n\
    exit 1\n\
}\n\
\n\
echo "✓ Checking file structure..."\n\
ls -la /app/\n\
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
# Replace PORT placeholder in nginx config\n\
echo "Configuring nginx for port $PORT..."\n\
envsubst \047$PORT\047 < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf\n\
\n\
echo "Testing nginx configuration..."\n\
nginx -t\n\
\n\
echo "Starting services with supervisor..."\n\
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf\n' > /start.sh

RUN chmod +x /start.sh

# Install envsubst for environment variable substitution
RUN apt-get update && apt-get install -y gettext-base && rm -rf /var/lib/apt/lists/*

# Expose PORT (Railway will set this dynamically)
EXPOSE $PORT

# Add health check that uses the PORT environment variable
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Use the startup script
CMD ["/start.sh"]