"""Configuration settings for the Face Attendance application."""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App settings
    app_name: str = "Face Attendance System"
    debug: bool = False

    # Supabase settings
    supabase_url: str = ""
    supabase_key: str = ""

    # Face recognition settings
    face_detection_confidence: float = 0.7
    face_recognition_threshold: float = 0.45  # Cosine similarity threshold
    embedding_dimension: int = 512

    # Liveness detection settings
    liveness_threshold: float = 0.5

    # Performance settings
    max_faces_per_image: int = 1
    image_max_size: int = 1024  # Max dimension in pixels

    # Model paths (relative to backend directory)
    model_dir: str = "models"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
