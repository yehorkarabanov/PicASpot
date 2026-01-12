# Image Service Dockerfile with NVIDIA CUDA support
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04

# Copy uv binary first (doesn't require system packages)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python 3.13 and system dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.13 \
    python3.13-dev \
    python3.13-venv \
    gcc \
    g++ \
    make \
    libc-dev \
    zlib1g-dev \
    curl \
    git \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1 \
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

# Run the image service
CMD ["sh", "-c", "uv run fastapi dev --port ${IMAGE_SERVICE_PORT_INTERNAL} --reload"]
