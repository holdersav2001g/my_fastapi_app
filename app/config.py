from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()