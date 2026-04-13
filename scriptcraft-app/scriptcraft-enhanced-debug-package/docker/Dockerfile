# ScriptCraft Web App Dockerfile
# Production-ready containerized AI script creation application

FROM python:3.11-slim

# Build argument for version
ARG BUILD_VERSION=2.1.0
ENV APP_VERSION=${BUILD_VERSION}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash scriptcraft

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code - use the enhanced debug version
COPY web_gui.py ./web_gui.py
COPY templates/ ./templates/
COPY README.md .

# Copy console_ui for text and word processing
COPY console_ui/ ./console_ui/

# Copy the Azure agents (now included in package)
COPY linedrive_azure/ ./linedrive_azure/

# Copy tools directory for thumbnail generation
COPY tools/ ./tools/

# Create necessary directories and set permissions
RUN mkdir -p /app/output /app/logs /app/thumbnails && \
    chown -R scriptcraft:scriptcraft /app

# Switch to non-root user
USER scriptcraft

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=web_gui.py
ENV FLASK_ENV=production
ENV PORT=5007

# Expose port
EXPOSE 5007

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5007/ || exit 1

# Start the application (PORT env var controls which port to use)
CMD ["python", "web_gui.py"]
