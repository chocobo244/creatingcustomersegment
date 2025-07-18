"""
Configuration management for Multi-Touch Attribution Platform.
"""
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = "postgresql://user:password@localhost:5432/attribution_db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    url: str = "redis://localhost:6379/0"
    max_connections: int = 20
    
    class Config:
        env_prefix = "REDIS_"


class APISettings(BaseSettings):
    """API configuration settings."""
    
    title: str = "Multi-Touch Attribution API"
    description: str = "Comprehensive attribution analytics platform"
    version: str = "1.0.0"
    debug: bool = False
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    class Config:
        env_prefix = "API_"


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/app.log"
    max_file_size: str = "10MB"
    backup_count: int = 5
    
    class Config:
        env_prefix = "LOG_"


class AttributionSettings(BaseSettings):
    """Attribution model configuration settings."""
    
    # Default attribution models to use
    default_models: List[str] = [
        "first_touch",
        "last_touch", 
        "linear",
        "time_decay",
        "u_shaped",
        "w_shaped"
    ]
    
    # Time decay model parameters
    time_decay_half_life: int = 7  # days
    
    # U-shaped model parameters
    u_shaped_first_touch_weight: float = 0.4
    u_shaped_last_touch_weight: float = 0.4
    u_shaped_middle_weight: float = 0.2
    
    # W-shaped model parameters
    w_shaped_first_touch_weight: float = 0.3
    w_shaped_lead_creation_weight: float = 0.3
    w_shaped_opportunity_creation_weight: float = 0.3
    w_shaped_middle_weight: float = 0.1
    
    # Data processing
    lookback_window_days: int = 90
    attribution_window_days: int = 30
    min_touchpoints: int = 1
    max_touchpoints: int = 50
    
    class Config:
        env_prefix = "ATTRIBUTION_"


class CelerySettings(BaseSettings):
    """Celery configuration settings."""
    
    broker_url: str = "redis://localhost:6379/1"
    result_backend: str = "redis://localhost:6379/1"
    task_serializer: str = "json"
    accept_content: List[str] = ["json"]
    result_serializer: str = "json"
    timezone: str = "UTC"
    enable_utc: bool = True
    
    # Task routing
    task_routes: Dict[str, Dict[str, str]] = {
        "attribution.tasks.process_touchpoints": {"queue": "attribution"},
        "attribution.tasks.calculate_attribution": {"queue": "attribution"},
        "data.tasks.ingest_data": {"queue": "data_processing"},
    }
    
    class Config:
        env_prefix = "CELERY_"


class StreamlitSettings(BaseSettings):
    """Streamlit frontend configuration settings."""
    
    title: str = "Multi-Touch Attribution Analytics"
    page_icon: str = "📊"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    
    # Backend API settings
    api_base_url: str = "http://localhost:8000"
    api_timeout: int = 30
    
    # UI settings
    theme_primary_color: str = "#FF6B6B"
    theme_background_color: str = "#FFFFFF"
    theme_secondary_background_color: str = "#F0F2F6"
    theme_text_color: str = "#262730"
    
    class Config:
        env_prefix = "STREAMLIT_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = "development"
    testing: bool = False
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    api: APISettings = APISettings()
    logging: LoggingSettings = LoggingSettings()
    attribution: AttributionSettings = AttributionSettings()
    celery: CelerySettings = CelerySettings()
    streamlit: StreamlitSettings = StreamlitSettings()
    
    # Feature flags
    enable_caching: bool = True
    enable_rate_limiting: bool = True
    enable_metrics: bool = True
    enable_tracing: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be development, staging, or production")
        return v
    
    def is_development(self) -> bool:
        return self.environment == "development"
    
    def is_production(self) -> bool:
        return self.environment == "production"
    
    def is_testing(self) -> bool:
        return self.testing


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience function to get specific setting groups
def get_db_settings() -> DatabaseSettings:
    """Get database settings."""
    return get_settings().database


def get_api_settings() -> APISettings:
    """Get API settings."""
    return get_settings().api


def get_attribution_settings() -> AttributionSettings:
    """Get attribution settings."""
    return get_settings().attribution


def get_logging_settings() -> LoggingSettings:
    """Get logging settings."""
    return get_settings().logging


def get_streamlit_settings() -> StreamlitSettings:
    """Get Streamlit settings."""
    return get_settings().streamlit