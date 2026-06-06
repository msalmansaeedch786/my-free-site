FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser

COPY . .

# Switch to non-root user
USER appuser

# Expose the expected port
EXPOSE 8080

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run with single worker to stay safely within the free tier memory limits
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 0 main:app
