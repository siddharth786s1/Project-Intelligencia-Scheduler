import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with sensible defaults for development.
    Override with environment variables or .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Scheduler Service"
    
    # Server Settings
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Data Service Configuration
    DATA_SERVICE_URL: str = "http://data-service:8000/api/v1"
    
    # Security Settings
    AUTH_SERVICE_URL: str = "http://iam-service:8000/api/v1"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Scheduler Settings
    MAX_SCHEDULING_ATTEMPTS: int = 5
    TIMEOUT_SECONDS: int = 300  # 5 minutes
    POPULATION_SIZE: int = 100  # For genetic algorithm
    MAX_GENERATIONS: int = 200  # For genetic algorithm
    DEFAULT_MUTATION_RATE: float = 0.1
    DEFAULT_CROSSOVER_RATE: float = 0.8
    
    # Redis & Celery Settings (for async task processing)
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    CELERY_RESULT_BACKEND: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"


settings = Settings()
