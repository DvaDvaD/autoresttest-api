from fastapi import APIRouter, Depends, Request
from app.models.test_config import TestRunRequest, TestRunResult
from app.services.model_service import AutoRestTestModel
from app.api.deps import cancel_on_disconnect, get_api_key, get_model_service

router = APIRouter()


@router.post("/run", response_model=TestRunResult)
async def run_test(
    request: Request,
    request_body: TestRunRequest,
    model_service: AutoRestTestModel = Depends(get_model_service),
    _: str = Depends(get_api_key),
):
    """
    Run a test using the AutoRestTest model.
    """
    async with cancel_on_disconnect(request):
        return await model_service.run_test(request_body=request_body)
