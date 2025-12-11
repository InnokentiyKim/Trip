# Stage 1: Build the application with dependencies
FROM python:3.13-slim AS builder

WORKDIR app/

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR app/

COPY --from=builder /app/.venv /app/.venv

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY alembic.ini ./

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m src.main"]
