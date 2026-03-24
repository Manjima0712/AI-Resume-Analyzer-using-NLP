# Use Python 3.11-slim as a base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# libgl1 and libglib2.0-0 are for PyMuPDF/OpenCV if needed
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data packs
RUN python -m nltk.downloader punkt stopwords words averaged_perceptron_tagger

# Copy environment variables and application code
COPY .env .env
COPY . .

# Create essential folders with correct permissions
RUN mkdir -p uploads instance && chmod 777 uploads instance

# Expose Flask port
EXPOSE 5000

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Run using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
