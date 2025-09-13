from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings
from app.services.model_service import AutoRestTestModel

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
def startup_event():
    app.state.model_service = AutoRestTestModel(settings.MODEL_PATH)

app.include_router(api_router, prefix="/api/v1")
