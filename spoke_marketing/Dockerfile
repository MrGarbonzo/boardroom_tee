# Marketing Agent Dockerfile - Boardroom TEE Marketing Agent
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget git build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# In production, would download and cache Mistral-7B-Instruct-v0.3
RUN python -c "import os; os.environ['HF_HOME'] = '/app/models'; print('Marketing model (Mistral-7B-Instruct-v0.3) cache setup complete (mocked for development)')"

# Copy source code
COPY src/ /app/src/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/crypto /app/models /app/config

# Set environment variables
ENV PYTHONPATH=/app/src
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

# Create non-root user
RUN useradd -m -u 1000 marketinguser && chown -R marketinguser:marketinguser /app
USER marketinguser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
  CMD curl -f http://localhost:8082/health || exit 1

# Start marketing agent
CMD ["python", "/app/src/agents/marketing/main.py"]