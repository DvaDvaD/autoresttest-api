from fastapi import APIRouter
from app.api.v1.endpoints import test_runner

api_router = APIRouter()
api_router.include_router(test_runner.router, prefix="/tests", tags=["tests"])
