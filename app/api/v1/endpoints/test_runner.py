from fastapi import APIRouter, Depends
from app.models.test_config import TestConfiguration, TestResult
from app.services.model_service import AutoRestTestModel
from app.api.deps import get_api_key
from app.core.config import settings

router = APIRouter()

# This is a placeholder for the model service dependency
# A more robust solution would use a dependency injection container
# or a global variable initialized on startup.
model_service = AutoRestTestModel(settings.MODEL_PATH)

@router.post("/run", response_model=TestResult)
def run_test(
    config: TestConfiguration,
    api_key: str = Depends(get_api_key)
):
    """
    Run a test using the AutoRestTest model.
    """
    return model_service.run_test(config)
