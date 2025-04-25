FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# # Collect static files
RUN python manage.py collectstatic --noinput

# Run as non-root user for security
RUN useradd -m appuser
USER appuser

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Copy entrypoint script and set permissions BEFORE switching user
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run as non-root user for security
RUN useradd -m appuser
USER appuser

ENTRYPOINT ["/entrypoint.sh"]
# Run gunicorn
CMD gunicorn ecommerce.wsgi:application --bind 0.0.0.0:$PORT