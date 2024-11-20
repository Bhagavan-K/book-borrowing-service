from pydantic import BaseModel
from functools import lru_cache
import os

class Settings(BaseModel):
    SERVICE_NAME: str = "borrowing_service"
    ENVIRONMENT: str = "development"
    
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27018")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "book_borrowing")
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6380")
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "ScalableAs123!")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:3000")
    CATALOG_SERVICE_URL: str = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8000")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()