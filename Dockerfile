# =============================================================================
# Lucky Number — Multi-stage Dockerfile
# Stage 1: Build (dependencies)
# Stage 2: Runtime (non-root, OWASP A05)
# =============================================================================

# Stage 1: Build
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements*.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements-dev.txt && \
    pip install --no-cache-dir -e .

COPY src/ ./src/
COPY alembic.ini alembic/ ./
COPY scripts/ ./scripts/

# Stage 2: Runtime
FROM python:3.12-slim AS runtime

# Prevents CWE-522: no hardcoded secrets
# OWASP A05: non-root user
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

WORKDIR /app

# Copy only what's needed from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/ /app/

RUN mkdir -p /app/data /app/static && chown -R appuser:appgroup /app/data /app/static

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "lucky_number.main:app", "--host", "0.0.0.0", "--port", "8000"]
