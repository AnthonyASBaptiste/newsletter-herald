# Multi-stage lightweight Dockerfile for Newsletter Herald on GCP Cloud Run
FROM python:3.11-slim as builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production image
FROM python:3.11-slim

WORKDIR /app

# Copy installed python packages from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/lib /usr/lib

# Ensure local bin is in PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Copy application source code
COPY backend/ /app/backend/
COPY main.py /app/main.py

EXPOSE 8080

# Run Uvicorn listening on $PORT (injected dynamically by GCP Cloud Run)
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
