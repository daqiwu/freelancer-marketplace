# ============================================
# Multi-stage Optimized Docker Build
# ============================================
# Stage 1: Builder - Install dependencies
# Stage 2: Runtime - Minimal production image
# ============================================

FROM python:3.12-slim as builder

# Set environment variables for optimal Python behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy dependency files first (for better layer caching)
COPY pyproject.toml ./

# Install dependencies in a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install dependencies directly (not editable)
# This installs packages from pyproject.toml without needing the source code
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy aiomysql pymysql \
    pydantic pydantic-settings python-dotenv bcrypt python-jose[cryptography] \
    cryptography pyjwt greenlet

# ============================================
# Stage 2: Runtime - Production Image
# ============================================
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000 \
    WORKERS=4

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    libmariadb3 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code (init_db.py excluded by .dockerignore for production)
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./pyproject.toml ./

# Switch to non-root user
USER appuser

# Expose port
EXPOSE ${PORT:-8000}

# Health check with faster startup - use /health endpoint instead of /docs
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run with uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-4} --log-level info"]
