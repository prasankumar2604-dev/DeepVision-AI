# ==========================================================
# DeepVision AI — Production Dockerfile
# Optimized for free-tier cloud containers (Render / Koyeb)
# ==========================================================

FROM python:3.11-slim

# Prevent Python bytecode generation and ensure unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PORT=5000 \
    FLASK_ENV=production \
    MALLOC_TRIM_THRESHOLD_=100000

WORKDIR /app

# Install minimal system dependencies required by TensorFlow CPU runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list first for Docker layer caching
COPY requirements.txt .

# Install production Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code (excluding items in .dockerignore)
COPY . .

# Ensure runtime directories exist and have open permissions
RUN mkdir -p database static/uploads model/plots && \
    chmod -R 777 database static/uploads model/plots

# Expose default application port
EXPOSE 5000

# Container healthcheck using standard Python library
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD python -c "import urllib.request, os; port = os.environ.get('PORT', '5000'); urllib.request.urlopen(f'http://localhost:{port}/').read()" || exit 1

# Production WSGI server: 1 worker + 2 threads with automatic worker recycling to stay well below 512MB RAM
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 2 --timeout 120 --max-requests 100 --max-requests-jitter 20 app:app"]
