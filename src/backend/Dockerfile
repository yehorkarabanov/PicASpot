# Base stage - common dependencies for all services
FROM python:3.14.0-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libc-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --extra "test" --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /code/
WORKDIR /code/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra "test" --frozen --no-dev


# Backend stage - includes entrypoint for migrations
FROM base AS backend

# Copy and set up entrypoint script for running migrations at startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Don't run migrations at build time - they need env vars and a running database
# Migrations run at container startup via entrypoint.sh


# Worker stage - for Celery and Flower (no migrations needed)
FROM base AS worker

# No entrypoint script needed - workers don't run migrations
# Command will be specified in docker-compose.yaml

