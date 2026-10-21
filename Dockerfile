FROM python:3.11-slim

# Reject the roots behind the compromised eMudhra intermediate CAs.
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && sed -i -e 's|^mozilla/emSign_ECC_Root_CA_-_G3.crt|!&|' \
              -e 's|^mozilla/Comodo_AAA_Services_root.crt|!&|' /etc/ca-certificates.conf \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt


WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==21.2.0

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application with Gunicorn
CMD ["gunicorn", "github_issues.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"] 