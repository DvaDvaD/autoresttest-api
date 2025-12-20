import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def valid_api_key():
    return settings.API_KEY

@pytest.fixture
def auth_headers(valid_api_key):
    return {"x-api-key": valid_api_key}

@pytest.fixture
def mock_settings(monkeypatch):
    """
    Fixture to allow mocking settings values.
    """
    def _mock_settings(name, value):
        monkeypatch.setattr(settings, name, value)
    return _mock_settings
