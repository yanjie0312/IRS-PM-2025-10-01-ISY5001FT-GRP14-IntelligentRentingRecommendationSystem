from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    # PostgreSQL config
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # pgAdmin config
    PGADMIN_EMAIL: str
    PGADMIN_PASSWORD: str

    # openai
    OPENAI_API_KEY: str

    # cloud
    CLOUD_DB_HOST: str
    CLOUD_DB_PORT: str
    CLOUD_DB_DATABASE: str
    CLOUD_DB_USERNAME: str
    CLOUD_DB_PASSWORD: str

    class Config:
        env_file = ".env"

settings = Settings()