from fastapi import APIRouter, Depends, HTTPException, Request
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
    config = request_body.config
    job_id = request_body.job_id

    # 1. Perform synchronous validation first. This will raise a 400 HTTPException on failure.
    prepared_data = model_service.validate_and_prepare_config(config)

    # 2. If validation succeeds, proceed to the long-running, cancellable task.
    result, error_detail = None, None
    async with cancel_on_disconnect(request):
        result, error_detail = await model_service.execute_test_process(
            prepared_data, job_id
        )

    if error_detail:
        raise HTTPException(status_code=500, detail=error_detail)

    return result
