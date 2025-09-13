# Stage 1: Install dependencies
FROM python:3.10-slim AS builder

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry configuration
COPY poetry.lock pyproject.toml ./

# Install dependencies
RUN poetry install --no-dev --no-root

# Stage 2: Create the final image
FROM python:3.10-slim

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /app/.venv ./.venv

# Set the path to include the virtual environment's binaries
ENV PATH="/.venv/bin:$PATH"

# Copy the application code
COPY app/ ./app
COPY models_store/ ./models_store

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
