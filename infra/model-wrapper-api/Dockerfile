# Stage 1: Build Stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry==2.0.1

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Copy only dependency files first to leverage Docker caching
COPY poetry.lock pyproject.toml ./

# Install dependencies (no-interaction is better for CI/Docker)
RUN poetry install --no-root --no-interaction --no-ansi

# Stage 2: Runtime Stage
FROM python:3.11-slim

WORKDIR /app

# Copy the virtualenv from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Set virtualenv environment variables
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code and models
# (Keeping your original structure)
COPY app/ ./app
COPY lib/ ./lib
COPY models_store/ ./models_store
COPY .env ./.env

CMD ["fastapi", "run", "app/main.py", "--port", "8080"]
