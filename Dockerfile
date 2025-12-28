# ============================================
# Dockerfile for Hugging Face Spaces (Docker SDK)
# Optimized for FastAPI + Heavy ML Model (>500MB)
# ============================================

FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*
    
# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user (REQUIRED by Hugging Face Spaces)
# HF Spaces runs containers as user ID 1000
RUN useradd -m -u 1000 user

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY --chown=user:user requirements.txt .

# Install Python dependencies as root (before switching to user)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=user:user . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/app/static/uploads/wordclouds && \
    mkdir -p /app/app/database && \
    chmod -R 777 /app/app/static/uploads && \
    chmod -R 777 /app/app/database

# Switch to non-root user
USER user

# Expose port 7860 (REQUIRED by Hugging Face Spaces)
EXPOSE 7860

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/docs')"

# Start the FastAPI application
# CRITICAL: Must listen on 0.0.0.0:7860 for Hugging Face Spaces
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
