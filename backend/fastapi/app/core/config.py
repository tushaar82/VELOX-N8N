"""
VELOX-N8N Configuration Settings
Centralized configuration management for the trading system
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    TESTING: bool = False
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FASTAPI_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/velo_trading_dev"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Authentication Configuration
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OpenAlgo Configuration
    OPENALGO_URL: str = "http://localhost:3000"
    OPENALGO_API_KEY: Optional[str] = None
    OPENALGO_ENV: str = "development"
    
    # Broker Configuration
    BROKER_NAME: Optional[str] = None
    BROKER_API_KEY: Optional[str] = None
    BROKER_API_SECRET: Optional[str] = None
    BROKER_ENVIRONMENT: str = "development"
    
    # Market Data Configuration
    MARKET_DATA_API_KEY: Optional[str] = None
    MARKET_DATA_URL: str = "https://api.market-data.com"
    MARKET_DATA_TIMEOUT: int = 30
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/velo-trading.log"
    LOG_MAX_SIZE: str = "10MB"
    LOG_BACKUP_COUNT: int = 5
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    SSL_DISABLE: bool = True
    
    # Performance Configuration
    MAX_WORKERS: int = 4
    WORKER_CONNECTIONS: int = 1000
    KEEP_ALIVE: int = 2
    TIMEOUT: int = 30
    
    # Cache Configuration
    CACHE_TTL: int = 3600
    CACHE_MAX_SIZE: int = 1000
    CACHE_ENABLED: bool = True
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000
    WS_MESSAGE_QUEUE_SIZE: int = 10000
    
    # Trading Configuration
    MAX_POSITION_SIZE: float = 100000.0
    MAX_DAILY_LOSS: float = 10000.0
    MAX_CORRELATION: float = 0.7
    RISK_PER_TRADE: float = 2.0
    MAX_OPEN_POSITIONS: int = 10
    
    # Data Configuration
    MAX_HISTORY_DAYS: int = 365
    TICK_BUFFER_SIZE: int = 1000
    UPDATE_INTERVAL: float = 0.1
    DATA_RETENTION_DAYS: int = 90
    
    # Monitoring Configuration
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL: int = 60
    
    # Development Configuration
    HOT_RELOAD: bool = True
    DEBUG_SQL: bool = False
    PROFILING_ENABLED: bool = False
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()

# Derived settings
class DatabaseSettings:
    """Database-specific settings"""
    URL = settings.DATABASE_URL
    ECHO = settings.DEBUG_SQL
    POOL_SIZE = settings.WORKER_CONNECTIONS
    MAX_OVERFLOW = settings.WORKER_CONNECTIONS * 2
    POOL_TIMEOUT = settings.TIMEOUT
    POOL_RECYCLE = 3600


class RedisSettings:
    """Redis-specific settings"""
    URL = settings.REDIS_URL
    DECODE_RESPONSES = True
    SOCKET_TIMEOUT = 5
    SOCKET_CONNECT_TIMEOUT = 5
    HEALTH_CHECK_INTERVAL = 30


class WebSocketSettings:
    """WebSocket-specific settings"""
    HEARTBEAT_INTERVAL = settings.WS_HEARTBEAT_INTERVAL
    MAX_CONNECTIONS = settings.WS_MAX_CONNECTIONS
    MESSAGE_QUEUE_SIZE = settings.WS_MESSAGE_QUEUE_SIZE
    PING_TIMEOUT = 10
    PONG_TIMEOUT = 10


class TradingSettings:
    """Trading-specific settings"""
    MAX_POSITION_SIZE = settings.MAX_POSITION_SIZE
    MAX_DAILY_LOSS = settings.MAX_DAILY_LOSS
    MAX_CORRELATION = settings.MAX_CORRELATION
    RISK_PER_TRADE = settings.RISK_PER_TRADE
    MAX_OPEN_POSITIONS = settings.MAX_OPEN_POSITIONS
    DEFAULT_RISK_PERCENT = 2.0
    DEFAULT_STOP_LOSS_ATR_MULTIPLIER = 2.0
    DEFAULT_TAKE_PROFIT_RISK_REWARD_RATIO = 2.0


class MarketDataSettings:
    """Market data-specific settings"""
    API_KEY = settings.MARKET_DATA_API_KEY
    BASE_URL = settings.MARKET_DATA_URL
    TIMEOUT = settings.MARKET_DATA_TIMEOUT
    MAX_HISTORY_DAYS = settings.MAX_HISTORY_DAYS
    TICK_BUFFER_SIZE = settings.TICK_BUFFER_SIZE
    UPDATE_INTERVAL = settings.UPDATE_INTERVAL
    DATA_RETENTION_DAYS = settings.DATA_RETENTION_DAYS


class SecuritySettings:
    """Security-specific settings"""
    SECRET_KEY = settings.FASTAPI_SECRET_KEY
    JWT_SECRET_KEY = settings.JWT_SECRET_KEY
    JWT_ALGORITHM = settings.JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15


class EmailSettings:
    """Email-specific settings"""
    HOST = settings.SMTP_HOST
    PORT = settings.SMTP_PORT
    USER = settings.SMTP_USER
    PASSWORD = settings.SMTP_PASSWORD
    TLS = settings.SMTP_TLS
    FROM_EMAIL = "noreply@velox-n8n.com"
    FROM_NAME = "VELOX-N8N"


# Create settings instances
db_settings = DatabaseSettings()
redis_settings = RedisSettings()
ws_settings = WebSocketSettings()
trading_settings = TradingSettings()
market_data_settings = MarketDataSettings()
security_settings = SecuritySettings()
email_settings = EmailSettings()