# Finance Agent Dockerfile - Boardroom TEE Finance Agent
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget git build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# In production, would download and cache AdaptLLM/finance-LLM (7B model)
RUN python -c "import os; os.environ['HF_HOME'] = '/app/models'; print('Finance model (AdaptLLM/finance-LLM) cache setup complete (mocked for development)')"

# Copy source code
COPY src/ /app/src/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/crypto /app/models /app/config

# Set environment variables
ENV PYTHONPATH=/app/src
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

# Create non-root user
RUN useradd -m -u 1000 financeuser && chown -R financeuser:financeuser /app
USER financeuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
  CMD curl -f http://localhost:8081/health || exit 1

# Start finance agent
CMD ["python", "/app/src/agents/finance/main.py"]