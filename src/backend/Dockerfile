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
#RUN --mount=type=cache,target=/root/.cache/uv \
#    --mount=type=bind,source=uv.lock,target=uv.lock \
#    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
#    uv sync --frozen --no-install-project --no-dev
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /code/
WORKDIR /code/

#RUN --mount=type=cache,target=/root/.cache/uv \
#    uv sync --frozen --no-dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen


# Backend stage - includes entrypoint for migrations
FROM base AS backend

# Copy and set up entrypoint script for running migrations at startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["sh", "-c", "uv run fastapi dev --port ${BACKEND_PORT_INTERNAL} --host 0.0.0.0 --reload --proxy-headers"]


# Worker stage - for Celery worker (no migrations needed)
FROM base AS worker

CMD ["uv", "run", "celery", "--app", "app.celery.worker", "worker", "--loglevel=info", "--uid=nobody", "--gid=nogroup"]


# Flower stage - for Celery monitoring UI (no migrations needed)
FROM base AS flower

CMD ["sh", "-c", "uv run celery --broker=redis://:${REDIS_PASSWORD}@redis:${REDIS_PORT_INTERNAL}/0 flower --port=${FLOWER_PORT_INTERNAL} --url-prefix=/dev/flower"]

