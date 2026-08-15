from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    huggingface_api_key: str
    celery_broker_url: str
    celery_result_backend: str

settings = Settings()