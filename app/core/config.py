"""
Configuration management using pydantic-settings.
Loads settings from environment variables and .env file.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be configured via .env file or environment variables.
    """
    
    # OpenAlgo Configuration
    openalgo_api_key: str = Field(
        ...,
        description="OpenAlgo API key for authentication"
    )
    openalgo_host: str = Field(
        default="http://127.0.0.1:5000",
        description="OpenAlgo server URL"
    )
    openalgo_version: str = Field(
        default="v1",
        description="OpenAlgo API version"
    )
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # WebSocket Configuration
    max_websocket_connections: int = Field(
        default=100,
        description="Maximum number of concurrent WebSocket connections",
        ge=1,
        le=10000
    )
    tick_buffer_size: int = Field(
        default=1000,
        description="Size of tick buffer per symbol",
        ge=100,
        le=100000
    )
    
    # Timeframe Configuration
    default_timeframes: str = Field(
        default="1m,5m,15m,1h,1d",
        description="Comma-separated list of default timeframes"
    )
    
    # Application Configuration
    app_host: str = Field(
        default="0.0.0.0",
        description="Application host"
    )
    app_port: int = Field(
        default=8000,
        description="Application port",
        ge=1,
        le=65535
    )
    app_workers: int = Field(
        default=4,
        description="Number of worker processes for production",
        ge=1,
        le=32
    )
    
    # Optional: Redis Configuration
    redis_host: str = Field(
        default="localhost",
        description="Redis host for caching"
    )
    redis_port: int = Field(
        default=6379,
        description="Redis port",
        ge=1,
        le=65535
    )
    redis_db: int = Field(
        default=0,
        description="Redis database number",
        ge=0,
        le=15
    )
    redis_enabled: bool = Field(
        default=False,
        description="Enable Redis caching"
    )
    
    # Optional: Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        description="API rate limit per minute per client",
        ge=1,
        le=10000
    )
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    def get_default_timeframes(self) -> List[str]:
        """Parse default timeframes from comma-separated string."""
        return [tf.strip() for tf in self.default_timeframes.split(",") if tf.strip()]
    
    @property
    def openalgo_base_url(self) -> str:
        """Get the full OpenAlgo base URL."""
        return f"{self.openalgo_host}/api/{self.openalgo_version}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are loaded only once.
    This is the recommended way to access settings throughout the application.
    
    Returns:
        Settings: Application settings instance
    
    Example:
        >>> from app.core.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.openalgo_host)
    """
    return Settings()


# Convenience function to reload settings (useful for testing)
def reload_settings() -> Settings:
    """
    Reload settings by clearing the cache.
    
    This is primarily useful for testing when you need to reload
    settings after modifying environment variables.
    
    Returns:
        Settings: Fresh settings instance
    """
    get_settings.cache_clear()
    return get_settings()
