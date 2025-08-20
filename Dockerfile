# Use official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Collect static files for production
RUN python manage.py collectstatic --noinput

# Run migrations on container start (optional, can be overridden)
CMD ["gunicorn", "notiflow.wsgi:application", "--bind", "0.0.0.0:8000"]

# Expose port
EXPOSE 8000
