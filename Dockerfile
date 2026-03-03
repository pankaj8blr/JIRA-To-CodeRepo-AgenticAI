FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Install build tools required for tree-sitter
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get install -y git build-essential && \
    rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "workers.tasks", "worker", "--loglevel=info"]
