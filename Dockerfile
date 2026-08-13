# ==========================================================
# DeepVision AI - Dockerfile
# AI-Powered Deepfake Image Detection System
# ==========================================================

FROM python:3.11-slim

# Prevent Python from creating .pyc files
# and ensure logs appear immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# System dependencies required by OpenCV and TensorFlow
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create required directories
RUN mkdir -p database static/uploads model/plots

# Flask application port
EXPOSE 5000

# Start DeepVision AI
CMD ["python", "app.py"]
