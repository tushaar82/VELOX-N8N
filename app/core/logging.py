"""
Logging configuration for the application.
Sets up structured logging with proper formatting and levels.
"""

import logging
import sys
from typing import Optional

from app.core.config import get_settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure application logging.
    
    Sets up the root logger with:
    - Configurable log level from settings
    - Structured format with timestamp, level, module, and message
    - Output to stdout for container-friendly logging
    
    Args:
        log_level: Optional log level override. If not provided, uses settings.
    
    Example:
        >>> from app.core.logging import setup_logging
        >>> setup_logging()
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    settings = get_settings()
    level = log_level or settings.log_level
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create and configure stdout handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Log the configuration
    root_logger.info(f"Logging configured with level: {level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    This is the recommended way to get loggers throughout the application.
    Each module should get its own logger using __name__.
    
    Args:
        name: Logger name, typically __name__ of the calling module
    
    Returns:
        logging.Logger: Configured logger instance
    
    Example:
        >>> from app.core.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing data")
        >>> logger.error("An error occurred", exc_info=True)
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin class to add logging capability to any class.
    
    Provides a 'logger' property that returns a logger named after the class.
    
    Example:
        >>> class MyService(LoggerMixin):
        ...     def process(self):
        ...         self.logger.info("Processing started")
        ...         # ... do work ...
        ...         self.logger.info("Processing completed")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


def log_function_call(func):
    """
    Decorator to log function calls with arguments and return values.
    
    Useful for debugging and tracing execution flow.
    
    Args:
        func: Function to decorate
    
    Returns:
        Wrapped function with logging
    
    Example:
        >>> @log_function_call
        ... def calculate_indicator(symbol: str, period: int):
        ...     return {"rsi": 65.5}
    """
    logger = get_logger(func.__module__)
    
    def wrapper(*args, **kwargs):
        # Log function call
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"Calling {func.__name__}({signature})")
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned {result!r}")
            return result
        except Exception as e:
            # Log exception
            logger.error(f"{func.__name__} raised {e.__class__.__name__}: {e}", exc_info=True)
            raise
    
    return wrapper


def log_async_function_call(func):
    """
    Decorator to log async function calls with arguments and return values.
    
    Async version of log_function_call decorator.
    
    Args:
        func: Async function to decorate
    
    Returns:
        Wrapped async function with logging
    
    Example:
        >>> @log_async_function_call
        ... async def fetch_data(symbol: str):
        ...     return await api.get(symbol)
    """
    logger = get_logger(func.__module__)
    
    async def wrapper(*args, **kwargs):
        # Log function call
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"Calling async {func.__name__}({signature})")
        
        try:
            # Execute async function
            result = await func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned {result!r}")
            return result
        except Exception as e:
            # Log exception
            logger.error(f"{func.__name__} raised {e.__class__.__name__}: {e}", exc_info=True)
            raise
    
    return wrapper
