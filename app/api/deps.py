from contextlib import asynccontextmanager
from fastapi import Request, Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
from app.core.config import settings
from app.services.model_service import AutoRestTestModel
from anyio import create_task_group

api_key_header = APIKeyHeader(name="x-api-key")


def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == settings.API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


def get_model_service() -> AutoRestTestModel:
    return AutoRestTestModel()


@asynccontextmanager
async def cancel_on_disconnect(request: Request):
    """
    Async context manager for async code that needs to be cancelled if client disconnects prematurely.
    The client disconnect is monitored through the Request object.
    """
    async with create_task_group() as tg:

        async def watch_disconnect():
            while True:
                message = await request.receive()

                if message["type"] == "http.disconnect":
                    client = (
                        f"{request.client.host}:{request.client.port}"
                        if request.client
                        else "-:-"
                    )
                    print(
                        f'{client} - "{request.method} {request.url.path}" 499 DISCONNECTED'
                    )

                    tg.cancel_scope.cancel()
                    break

        tg.start_soon(watch_disconnect)

        try:
            yield
        finally:
            tg.cancel_scope.cancel()
