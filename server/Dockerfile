FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies for image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage/assets /app/storage/badges /app/storage/qrcodes /app/storage/promoter /app/storage/email_incoming /app/storage/email_results

# Create non-root user for production
RUN groupadd -r pivs && useradd --no-log-init -r -g pivs pivs \
    && chown -R pivs:pivs /app
USER pivs

EXPOSE 8000

# Development: uvicorn directly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ---------- Production target ----------
FROM base AS production

# Install gunicorn for production
RUN pip install --no-cache-dir gunicorn==23.0.0

CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
