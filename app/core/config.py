from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str = "some_secret"
    OPENAI_API_KEY: str = "openai-api-key"
    OPENAI_BASE_URL: Optional[str] = None
    MODEL_PATH: str = "models_store/autorest_model.pkl"
    PROJECT_NAME: str = "AutoRestTest Model Service"
    UPSTASH_REDIS_REST_URL: str = "some_url"
    UPSTASH_REDIS_REST_TOKEN: str = "some_token"

    class Config:
        env_file = ".env"


settings = Settings()
