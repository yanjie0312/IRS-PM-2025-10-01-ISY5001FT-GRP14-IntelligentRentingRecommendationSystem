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

    class Config:
        env_file = ".env"

settings = Settings()