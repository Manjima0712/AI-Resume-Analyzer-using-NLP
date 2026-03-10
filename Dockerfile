# Use Python 3.11-slim as a base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PyMuPDF and python-docx
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data packs (fix: stopwords not stopword)
RUN python -m nltk.downloader punkt stopwords words averaged_perceptron_tagger

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy all project files
COPY . .

# Create uploads folder with write permissions
RUN mkdir -p uploads && chmod 777 uploads

# Create data directory for SQLite database
RUN mkdir -p instance

# Expose Flask port
EXPOSE 5000

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Run using gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
