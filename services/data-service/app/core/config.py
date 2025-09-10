from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Data Service"
    
    # Database configuration
    POSTGRES_HOST: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "data_service_db"
    POSTGRES_PORT: str = "5432"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Security
    JWT_SECRET_KEY: str = "supersecretkey"  # Should be loaded from environment in production
    JWT_ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # Testing flag
    TESTING: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
