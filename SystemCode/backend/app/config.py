# app/services/config.py
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # openai
    OPENAI_API_KEY: Optional[str] = None

    # cloud database（Cloud Run 走 Unix 套接字，端口默认 5432）
    CLOUD_DB_HOST: str
    CLOUD_DB_PORT: str = "5432"
    CLOUD_DB_USERNAME: str
    CLOUD_DB_PASSWORD: str
    CLOUD_DB_DATABASE: str

    # 下列若暂时不用，一律可选，避免未填就崩
    APP_DB_HOST: Optional[str] = None
    APP_DB_PORT: Optional[str] = None
    APP_DB_USER: Optional[str] = None
    APP_DB_PASSWORD: Optional[str] = None
    APP_DB_NAME: Optional[str] = None

    PGADMIN_EMAIL: Optional[str] = None
    PGADMIN_PASSWORD: Optional[str] = None

    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[str] = None

    # 本地开发读取 .env；Cloud Run 用控制台环境变量/Secrets
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
