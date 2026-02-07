"""
Gunicorn configuration for production deployment.
Run with: gunicorn app.main:app -c gunicorn.conf.py
"""

import multiprocessing
import os

# Bind
bind = os.getenv("BIND", "0.0.0.0:8000")

# Workers - use uvicorn workers for async support
worker_class = "uvicorn.workers.UvicornWorker"
workers = int(os.getenv("WEB_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Timeouts
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "pivs-api"

# Preload app for faster worker startup
preload_app = True
