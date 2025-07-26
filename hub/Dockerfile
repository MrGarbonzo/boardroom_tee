# Hub Dockerfile - Boardroom TEE Hub
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget git build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# In production, would download and cache Llama-3.2-1B-Instruct
RUN python -c "import os; os.environ['HF_HOME'] = '/app/models'; print('Hub model cache setup complete (mocked for development)')"

# Copy source code
COPY ../src/ /app/src/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/crypto /app/models /app/config

# Set environment variables
ENV PYTHONPATH=/app/src
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

# Create non-root user
RUN useradd -m -u 1000 hubuser && chown -R hubuser:hubuser /app
USER hubuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start hub service
CMD ["python", "/app/src/hub/main.py"]