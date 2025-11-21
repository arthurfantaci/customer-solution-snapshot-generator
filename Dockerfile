# Customer Solution Snapshot Generator Docker Image
# Multi-stage build for optimized production image

# Build stage
FROM python:3.10-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=0.1.0

# Add labels for metadata
LABEL org.opencontainers.image.title="Customer Solution Snapshot Generator"
LABEL org.opencontainers.image.description="AI-powered transcript processing for customer success stories"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.source="https://github.com/arthurfantaci/customer-solution-snapshot-generator"
LABEL org.opencontainers.image.licenses="MIT"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt requirements-dev.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install build

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY pytest.ini ./

# Download required models and data
RUN python -m spacy download en_core_web_sm && \
    python -c "import nltk; nltk.download('punkt', quiet=True)"

# Build the package
RUN python -m build

# Production stage
FROM python:3.10-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/home/app/.local/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 app

# Set working directory
WORKDIR /app

# Copy built package from builder stage
COPY --from=builder /app/dist/*.whl /tmp/
COPY --from=builder /root/.cache/pip /root/.cache/pip

# Install the package
RUN pip install --upgrade pip && \
    pip install /tmp/*.whl && \
    rm -rf /tmp/*.whl /root/.cache/pip

# Copy required files
COPY --from=builder /app/src ./src
COPY docker-entrypoint.sh /usr/local/bin/
COPY healthcheck.py /usr/local/bin/

# Make scripts executable
RUN chmod +x /usr/local/bin/docker-entrypoint.sh /usr/local/bin/healthcheck.py

# Create data directories
RUN mkdir -p /app/data/{input,output,templates,logs} && \
    chown -R app:app /app

# Switch to non-root user
USER app

# Copy user-specific configuration
COPY --chown=app:app src/customer_snapshot/templates/ /app/data/templates/

# Download models as app user
RUN python -m spacy download en_core_web_sm && \
    python -c "import nltk; nltk.download('punkt', quiet=True)"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python /usr/local/bin/healthcheck.py

# Expose port for potential web interface
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command
CMD ["customer-snapshot", "--help"]

# Development stage
FROM builder as development

# Install development dependencies
RUN pip install -r requirements-dev.txt

# Install pre-commit
RUN pip install pre-commit

# Copy development configuration
COPY .pre-commit-config.yaml .flake8 pytest.ini ./

# Set up pre-commit hooks
RUN git init . && pre-commit install || true

# Switch to non-root user
USER app

# Override entrypoint for development
ENTRYPOINT ["bash"]

# Testing stage
FROM development as testing

# Switch back to root for test setup
USER root

# Copy test files
COPY tests/ ./tests/
COPY pytest.ini ./

# Run tests
RUN python -m pytest tests/ \
    --cov=src/customer_snapshot \
    --cov-report=html \
    --cov-report=term \
    --junit-xml=test-results.xml

# Security scanning stage
FROM builder as security

# Install security tools
RUN pip install bandit safety

# Run security scans
RUN bandit -r src/ -f json -o bandit-report.json || true && \
    safety check --json --output safety-report.json || true

# Create security report
RUN echo "Security scan completed. Reports generated:" && \
    ls -la *-report.json
