# Use Python 3.11 slim image for production
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend directory
COPY backend/ ./backend/

# Copy database and websocket test file (if they exist)
COPY database.db* ./
COPY websocket_test.html ./

# Create directory for database if it doesn't exist
RUN mkdir -p /app/data

# Copy entrypoint script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --shell /bin/bash user && \
    chown -R user:user /app
USER user

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=10)"

# Use entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command
CMD ["uvicorn", "backend.backend:app", "--host", "0.0.0.0", "--port", "8000"]