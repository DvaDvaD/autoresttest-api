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

    MINIO_ACCESS_KEY: str = "some_access_key"
    MINIO_SECRET_KEY: str = "some_secret_key"
    MINIO_ENDPOINT: str = "minio_endpoint"
    MINIO_BUCKET: str = "minio_bucket"

    NEXTJS_BACKEND_URL: str = "some_url"
    INTERNAL_API_SECRET: str = "some_secret"

    class Config:
        env_file = ".env"


settings = Settings()
