import pytest
from app.main import app
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.model_service import AutoRestTestModel
from app.api.deps import get_model_service
from app.models.test_config import TestRunResult, TestConfiguration


# Mock Context Manager for cancel_on_disconnect
class AsyncContextManagerMock:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return None


@pytest.fixture
def mock_model_service():
    service = MagicMock(spec=AutoRestTestModel)
    return service


def test_run_test_unauthorized(client):
    response = client.post("/api/v1/tests/run", json={})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_run_test_invalid_auth(client):
    response = client.post(
        "/api/v1/tests/run", json={}, headers={"x-api-key": "wrong_key"}
    )
    assert response.status_code == 403


def test_run_test_success(client, auth_headers, mock_model_service):
    # Setup Data
    payload = {
        "job_id": "test-1",
        "config": {"spec_file_content": "{}", "time_duration_seconds": 10},
    }

    # Mock Service Responses
    mock_model_service.validate_and_prepare_config.return_value = {"some": "data"}

    expected_result = TestRunResult(
        summary={"status": "passed"},
        raw_file_urls={},
        config=TestConfiguration(**payload["config"]),
    )
    mock_model_service.execute_test_process = AsyncMock(
        return_value=(expected_result, None)
    )

    # Override Dependency and Patch Context Manager
    app.dependency_overrides[get_model_service] = lambda: mock_model_service

    with patch(
        "app.api.v1.endpoints.test_runner.cancel_on_disconnect",
        return_value=AsyncContextManagerMock(),
    ):
        response = client.post("/api/v1/tests/run", json=payload, headers=auth_headers)

    # Cleanup overrides
    app.dependency_overrides = {}

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["status"] == "passed"
    mock_model_service.validate_and_prepare_config.assert_called_once()
    mock_model_service.execute_test_process.assert_called_once()


def test_run_test_validation_error(client, auth_headers, mock_model_service):
    # Setup Data
    payload = {"job_id": "test-2", "config": {"spec_file_content": "{}"}}

    # Mock Validation Failure (Sync)
    from fastapi import HTTPException

    mock_model_service.validate_and_prepare_config.side_effect = HTTPException(
        status_code=400, detail="Bad Spec"
    )

    app.dependency_overrides[get_model_service] = lambda: mock_model_service

    response = client.post("/api/v1/tests/run", json=payload, headers=auth_headers)

    app.dependency_overrides = {}

    assert response.status_code == 400
    assert response.json()["detail"] == "Bad Spec"


def test_run_test_execution_error(client, auth_headers, mock_model_service):
    # Setup Data
    payload = {"job_id": "test-3", "config": {"spec_file_content": "{}"}}

    # Mock Success Validation but Failed Execution
    mock_model_service.validate_and_prepare_config.return_value = {}
    mock_model_service.execute_test_process = AsyncMock(
        return_value=(None, "Something exploded")
    )

    app.dependency_overrides[get_model_service] = lambda: mock_model_service

    with patch(
        "app.api.v1.endpoints.test_runner.cancel_on_disconnect",
        return_value=AsyncContextManagerMock(),
    ):
        response = client.post("/api/v1/tests/run", json=payload, headers=auth_headers)

    app.dependency_overrides = {}

    assert response.status_code == 500
    assert response.json()["detail"] == "Something exploded"
