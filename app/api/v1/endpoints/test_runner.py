from fastapi import APIRouter, Depends
from app.models.test_config import TestConfiguration, TestRunResult
from app.services.model_service import AutoRestTestModel
from app.api.deps import get_api_key, get_model_service

router = APIRouter()


@router.post("/run", response_model=TestRunResult)
async def run_test(
    config: TestConfiguration,
    model_service: AutoRestTestModel = Depends(get_model_service),
    _: str = Depends(get_api_key),
):
    """
    Run a test using the AutoRestTest model.
    """
    return await model_service.run_test(config)
