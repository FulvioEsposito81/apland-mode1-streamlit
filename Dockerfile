FROM python:3.13-slim AS base
ENV PATH="/app/.venv/bin:/root/.local/bin/:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
#Change the working directory to the `app` directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libexpat1 \
    libexpat1-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml ./uv.lock /app/

# Install dependencies
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable --no-dev

FROM python:3.13-slim

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    libexpat1 \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=base /app /app
# Copy the application files
COPY ./*.py /app/

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Start the application using Streamlit
ENTRYPOINT ["streamlit", "run", "geotechnical_app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--browser.gatherUsageStats=false"]
 
