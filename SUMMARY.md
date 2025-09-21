# Project Summary: AutoRestTest Model Service

## Description

This project is a dedicated FastAPI service that wraps the Python-based AutoRestTest Multi-Agent Reinforcement Learning model. Its sole purpose is to expose the model's functionality via a secure HTTP API. It will receive a test configuration, execute the test using the model, and return the results. The service is designed to be stateless and easily containerized for deployment on serverless platforms.

## Project Structure and File Explanations

### `pyproject.toml`

This file defines the project's metadata and dependencies. It uses `poetry` for dependency management. Key dependencies include:

*   **fastapi**: The web framework used to build the API.
*   **pydantic**: Used for data validation and settings management.
*   **joblib**, **scikit-learn**, **numpy**, **scipy**: Used for loading and running the machine learning model.
*   **openai**: Likely used for interacting with OpenAI's language models.
*   **prance**, **openapi-spec-validator**: Used for handling OpenAPI specifications.

### `Dockerfile`

This file contains the instructions for building the Docker image for the application. It's a multi-stage build that first installs the dependencies and then creates a lean final image with the application code and its environment.

### `app/main.py`

This is the main entry point of the FastAPI application. It initializes the FastAPI app, includes the API router, and loads the AutoRestTest model on startup.

### `app/core/config.py`

This file manages the application's configuration using `pydantic-settings`. It loads settings from a `.env` file, including the `API_KEY` for securing the API and the `MODEL_PATH` for locating the machine learning model.

### `app/api/v1/api.py`

This file defines the main API router for version 1 of the API. It includes the `test_runner` router, which contains the actual endpoint for running tests.

### `app/api/v1/endpoints/test_runner.py`

This file defines the `/run` endpoint for the API. It handles POST requests to trigger a test run. It depends on the `get_api_key` dependency to enforce API key authentication and uses the `model_service` to execute the test.

### `app/models/test_config.py`

This file defines the Pydantic models for the test configuration (`TestConfiguration`) and the test results (`TestResult`). These models are used for request body validation and response serialization.

### `app/services/model_service.py`

This file contains the business logic for interacting with the AutoRestTest model. The `AutoRestTestModel` class is responsible for loading the model and running tests based on the provided configuration. The current implementation is a mock that returns a dummy result.

### `README.md`

This file provides an overview of the project, setup instructions, and API usage examples.

## API Endpoints

The application has one main endpoint:

*   `POST /api/v1/tests/run`: This endpoint is used to run a test by providing a test configuration in the request body. The endpoint is protected by an API key that must be provided in the `x-api-key` header.

## Configuration

The application's configuration is managed by the `Settings` class in `app/core/config.py`. The configuration is loaded from a `.env` file and includes the following settings:

*   `API_KEY`: The secret API key used to protect the API.
*   `MODEL_PATH`: The path to the AutoRestTest model.
*   `PROJECT_NAME`: The name of the project.

## Application Startup

When the application starts up, it loads the AutoRestTest model from the path specified in the `MODEL_PATH` setting. The model is then stored in the application's state, where it can be accessed by the API endpoints.