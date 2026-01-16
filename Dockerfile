# GNC Calculations - Production Dockerfile
#
# This Dockerfile builds a single container that serves both the
# FastAPI backend and the React frontend (as static files).
#
# Build stages:
#   1. Frontend build (Node.js)
#   2. Backend runtime (Python)
#
# The final image serves the frontend via FastAPI's static file mounting.

# =============================================================================
# Stage 1: Build Frontend
# =============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies first (better layer caching)
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy source and build
COPY frontend/ ./
RUN npm run build

# =============================================================================
# Stage 2: Python Runtime
# =============================================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Install Python dependencies
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy backend source
COPY backend/app ./app

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./static

# Create production entry point that serves frontend static files
COPY <<'EOF' /app/app/main_prod.py
"""
Production entry point - serves API + static frontend.

In production, this module extends the base FastAPI app to also serve
the built React frontend as static files.
"""
import os
from pathlib import Path

from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.main import app

STATIC_DIR = Path("/app/static")


class SPAStaticFiles(StaticFiles):
    """Custom StaticFiles that falls back to index.html for SPA routing."""
    
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except Exception:
            # For any missing file, serve index.html (SPA routing)
            return await super().get_response("index.html", scope)


if STATIC_DIR.exists():
    # Serve the SPA with fallback to index.html
    # This is mounted last so API routes take precedence
    app.mount("/", SPAStaticFiles(directory=STATIC_DIR, html=True), name="static")
EOF

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main_prod:app", "--host", "0.0.0.0", "--port", "8000"]
