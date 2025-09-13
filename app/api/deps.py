from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
from app.core.config import settings

api_key_header = APIKeyHeader(name="x-api-key")

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == settings.API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
