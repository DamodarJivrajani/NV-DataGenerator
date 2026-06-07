# syntax=docker/dockerfile:1

# Backend: FastAPI app served by uvicorn on Cloud Run.
FROM python:3.10-slim

# Fail fast, skip .pyc files, stream logs unbuffered (so Cloud Logging captures
# output live), and keep pip quiet/cacheless to slim the image.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

WORKDIR /app

# Copy only what the package build needs. Dependencies are installed in this
# layer so it stays cached whenever only application code changes.
COPY pyproject.toml ./
COPY app ./app

RUN pip install --no-cache-dir .

# Run as an unprivileged user. /app must stay writable because the app creates
# jobs.db (SQLite) and ./artifacts at runtime — these are ephemeral on Cloud Run.
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/artifacts \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Honour Cloud Run's $PORT (defaults to 8080). A single worker is intentional:
# the app uses in-process BackgroundTasks plus a local SQLite job store, so extra
# workers would not share that state.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
