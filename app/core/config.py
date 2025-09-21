from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str = "some_secret"
    OPENAI_API_KEY: str = "openai-api-key"
    MODEL_PATH: str = "models_store/autorest_model.pkl"
    PROJECT_NAME: str = "AutoRestTest Model Service"

    class Config:
        env_file = ".env"


settings = Settings()
