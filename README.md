# AutoRestTest Model Service

This project is a dedicated FastAPI service that wraps the Python-based AutoRestTest Multi-Agent Reinforcement Learning model. Its sole purpose is to expose the model's functionality via a secure HTTP API. It will receive a test configuration, execute the test using the model, and return the results.

The service is designed to be stateless and easily containerized for deployment on serverless platforms like Google Cloud Run or Railway.

## Setup

1.  **Install dependencies:**

    ```bash
    poetry install
    ```

2.  **Set up environment variables:**

    Create a `.env` file in the root of the project and add the following:

    ```
    API_KEY=your-secret-api-key
    ```

3.  **Run the application:**

    ```bash
    poetry run uvicorn app.main:app --reload
    ```

## API Usage

To run a test, send a POST request to `/api/v1/tests/run` with your API key in the `x-api-key` header.

**Request Body:**

```json
{
  "spec_file_content": "...",
  "api_url_override": "http://localhost:8080",
  "llm_engine": "gpt-4",
  "llm_engine_temperature": 0.7,
  "use_cached_graph": true,
  "use_cached_q_tables": true,
  "rl_agent_learning_rate": 0.1,
  "rl_agent_discount_factor": 0.9,
  "rl_agent_max_exploration": 0.5,
  "time_duration_seconds": 3600,
  "mutation_rate": 0.1
}
```

**Response Body:**

```json
{
  "status": "completed",
  "total_requests": 100,
  "failed_requests": 5,
  "coverage": 95.5,
  "details": {
    "message": "Test completed successfully"
  }
}
```
