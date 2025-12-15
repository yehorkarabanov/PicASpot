# Email Service Dockerfile
FROM python:3.13-slim

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libc-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy application code
COPY . /code/
WORKDIR /code

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project


# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Run the email service
CMD ["sh", "-c", "uv run fastapi dev --port ${EMAIL_SERVICE_PORT_INTERNAL} --reload"]
