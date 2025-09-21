from fastapi import APIRouter, Depends
from app.models.test_config import TestConfiguration, TestRunResult
from app.services.model_service import AutoRestTestModel
from app.api.deps import get_api_key
from app.core.config import settings

router = APIRouter()

# This is a placeholder for the model service dependency
# A more robust solution would use a dependency injection container
# or a global variable initialized on startup.
model_service = AutoRestTestModel(settings.MODEL_PATH)


@router.post("/run", response_model=TestRunResult)
async def run_test(config: TestConfiguration, _: str = Depends(get_api_key)):
    """
    Run a test using the AutoRestTest model.
    """
    print("Endpoint /run invoked.")
    print("Calling model_service.run_test...")
    result = await model_service.run_test(config)
    print("Result received from model_service.")
    return result
