import pytest
from fastapi import HTTPException
from app.api.deps import get_api_key
from app.core.config import settings

def test_get_api_key_valid():
    key = settings.API_KEY
    assert get_api_key(api_key=key) == key

def test_get_api_key_invalid():
    with pytest.raises(HTTPException) as exc:
        get_api_key(api_key="invalid-key")
    assert exc.value.status_code == 403
    assert exc.value.detail == "Could not validate credentials"
