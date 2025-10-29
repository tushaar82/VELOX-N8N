"""
VELOX-N8N Logging Configuration
Centralized logging setup for the trading system
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional
from pathlib import Path

from app.core.config import settings


def setup_logging():
    """
    Setup application logging with proper formatters and handlers
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("velox_n8n")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=settings.LOG_FILE,
            maxBytes=_parse_size(settings.LOG_MAX_SIZE),
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Failed to create file handler: {e}")
    
    # Error file handler
    try:
        error_file = settings.LOG_FILE.replace('.log', '_error.log')
        error_handler = logging.handlers.RotatingFileHandler(
            filename=error_file,
            maxBytes=_parse_size(settings.LOG_MAX_SIZE),
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
    except Exception as e:
        logger.error(f"Failed to create error file handler: {e}")
    
    # Trading specific log handler
    try:
        trading_file = settings.LOG_FILE.replace('.log', '_trading.log')
        trading_handler = logging.handlers.RotatingFileHandler(
            filename=trading_file,
            maxBytes=_parse_size(settings.LOG_MAX_SIZE),
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        trading_handler.setLevel(logging.INFO)
        trading_handler.setFormatter(detailed_formatter)
        
        # Create trading logger
        trading_logger = logging.getLogger("velox_n8n.trading")
        trading_logger.setLevel(logging.INFO)
        trading_logger.addHandler(trading_handler)
        trading_logger.addHandler(console_handler)
        
    except Exception as e:
        logger.error(f"Failed to create trading file handler: {e}")
    
    # API request log handler
    try:
        api_file = settings.LOG_FILE.replace('.log', '_api.log')
        api_handler = logging.handlers.RotatingFileHandler(
            filename=api_file,
            maxBytes=_parse_size(settings.LOG_MAX_SIZE),
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(detailed_formatter)
        
        # Create API logger
        api_logger = logging.getLogger("velox_n8n.api")
        api_logger.setLevel(logging.INFO)
        api_logger.addHandler(api_handler)
        
    except Exception as e:
        logger.error(f"Failed to create API file handler: {e}")
    
    # Set specific logger levels
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if not settings.DEBUG_SQL else logging.INFO
    )
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logger.info("Logging system initialized")
    return logger


def _parse_size(size_str: str) -> int:
    """
    Parse size string (e.g., '10MB') to bytes
    """
    size_str = size_str.upper()
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # Assume bytes
        return int(size_str)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    """
    return logging.getLogger(f"velox_n8n.{name}")


def log_trading_event(event_type: str, data: dict, user_id: Optional[int] = None):
    """
    Log trading events with structured data
    """
    trading_logger = get_logger("trading")
    log_data = {
        "event_type": event_type,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=logging.INFO, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        )),
        "data": data
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    trading_logger.info(f"Trading Event: {event_type}", extra={"log_data": log_data})


def log_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    response_time: float,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None
):
    """
    Log API requests with structured data
    """
    api_logger = get_logger("api")
    log_data = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "response_time_ms": response_time * 1000,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=logging.INFO, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        ))
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if ip_address:
        log_data["ip_address"] = ip_address
    
    api_logger.info(f"API Request: {method} {endpoint}", extra={"log_data": log_data})


def log_system_event(event_type: str, message: str, data: Optional[dict] = None):
    """
    Log system events with structured data
    """
    system_logger = get_logger("system")
    log_data = {
        "event_type": event_type,
        "message": message,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=logging.INFO, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        ))
    }
    
    if data:
        log_data["data"] = data
    
    system_logger.info(f"System Event: {event_type}", extra={"log_data": log_data})


def log_security_event(
    event_type: str,
    user_id: Optional[int],
    ip_address: Optional[str],
    details: dict,
    severity: str = "INFO"
):
    """
    Log security events with structured data
    """
    security_logger = get_logger("security")
    log_data = {
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "details": details,
        "severity": severity,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=logging.INFO, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        ))
    }
    
    security_logger.info(f"Security Event: {event_type}", extra={"log_data": log_data})


def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str,
    tags: Optional[dict] = None
):
    """
    Log performance metrics
    """
    perf_logger = get_logger("performance")
    log_data = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=logging.INFO, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        ))
    }
    
    if tags:
        log_data["tags"] = tags
    
    perf_logger.info(f"Performance Metric: {metric_name}", extra={"log_data": log_data})


def log_error(
    error_type: str,
    message: str,
    exception: Optional[Exception] = None,
    context: Optional[dict] = None
):
    """
    Log errors with structured data
    """
    error_logger = get_logger("error")
    log_data = {
        "error_type": error_type,
        "message": message,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=logging.ERROR, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        ))
    }
    
    if exception:
        log_data["exception"] = {
            "type": type(exception).__name__,
            "message": str(exception),
            "traceback": exception.__traceback__
        }
    
    if context:
        log_data["context"] = context
    
    error_logger.error(f"Error: {error_type}", extra={"log_data": log_data}, exc_info=exception is not None)


def create_request_logger():
    """
    Create a request logger middleware for FastAPI
    """
    import time
    from fastapi import Request
    
    def log_request(request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log request
        log_api_request(
            method=request.method,
            endpoint=str(request.url.path),
            status_code=response.status_code,
            response_time=process_time,
            user_id=getattr(request.state, "user_id", None),
            ip_address=request.client.host if request.client else None
        )
        
        return response
    
    return log_request


def setup_structured_logging():
    """
    Setup structured logging with JSON formatter for production
    """
    if settings.ENVIRONMENT == "production":
        import json
        import logging
        
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_obj = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                
                # Add extra fields if present
                if hasattr(record, "log_data"):
                    log_obj.update(record.log_data)
                
                return json.dumps(log_obj)
        
        # Apply JSON formatter to all handlers
        for handler in logging.getLogger().handlers:
            handler.setFormatter(JSONFormatter())