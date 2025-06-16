FROM python:3.11-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data ffmpeg uploads

# Create credentials directory with proper permissions (for dynamic upload)
RUN mkdir -p /app/credentials && chmod 755 /app/credentials

# Don't copy credentials.json - it will be uploaded dynamically via API
# RUN rm -f credentials.json  # Remove if accidentally copied

# Add health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Expose port (Railway will set PORT env var)
EXPOSE ${PORT:-8000}

# Run the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}