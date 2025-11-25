# 0RB_AETHER - Multi-stage Docker Build
FROM python:3.11-slim as base

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 orb && chown -R orb:orb /app
USER orb

# Expose ports
EXPOSE 8080 8081 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "launcher.py"]

# =============================================================================
# Development stage
# =============================================================================
FROM base as dev

USER root
RUN pip install --no-cache-dir pytest pytest-asyncio ipython
USER orb

CMD ["python", "-m", "pytest", "-v"]

# =============================================================================
# Production stage
# =============================================================================
FROM base as prod

ENV PYTHONUNBUFFERED=1
ENV ORB_ENV=production

CMD ["python", "launcher.py", "--production"]
