# Email Service Dockerfile
FROM python:3.14.0-slim

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libc-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy application code
COPY . /app-service/
WORKDIR /app-service

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project


# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Run the email service
CMD ["uv", "run", "python", "-m", "app.main"]
