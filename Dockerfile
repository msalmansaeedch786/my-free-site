FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run with single worker to stay safely within the free tier memory limits
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 0 main:app
