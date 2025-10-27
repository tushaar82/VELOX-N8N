"""
Input validation utilities for symbols, exchanges, dates, and other inputs.
Provides validation functions to ensure data integrity throughout the application.
"""

import re
from datetime import datetime
from typing import Optional, Tuple

from app.core.logging import get_logger
from app.utils.timeframes import validate_timeframe

logger = get_logger(__name__)


# Supported exchanges (based on OpenAlgo)
SUPPORTED_EXCHANGES = {
    "NSE": "National Stock Exchange",
    "BSE": "Bombay Stock Exchange",
    "NFO": "NSE Futures & Options",
    "BFO": "BSE Futures & Options",
    "MCX": "Multi Commodity Exchange",
    "CDS": "Currency Derivatives Segment",
}


# NSE indices
NSE_INDICES = {
    "NIFTY",
    "BANKNIFTY",
    "FINNIFTY",
    "MIDCPNIFTY",
    "NIFTYIT",
    "NIFTYNXT50",
    "NIFTY500",
}


# Symbol validation pattern (alphanumeric, hyphens, underscores)
SYMBOL_PATTERN = re.compile(r'^[A-Z0-9\-_&]+$')


def validate_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
    """
    Validate trading symbol format.
    
    Checks if symbol contains only valid characters (uppercase letters,
    numbers, hyphens, underscores, ampersands).
    
    Args:
        symbol: Trading symbol to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    
    Example:
        >>> validate_symbol("RELIANCE")
        (True, None)
        >>> validate_symbol("NIFTY")
        (True, None)
        >>> validate_symbol("invalid@symbol")
        (False, "Symbol contains invalid characters...")
    """
    if not symbol:
        return False, "Symbol cannot be empty"
    
    if len(symbol) > 50:
        return False, "Symbol is too long (max 50 characters)"
    
    # Convert to uppercase for validation
    symbol_upper = symbol.upper()
    
    if not SYMBOL_PATTERN.match(symbol_upper):
        return False, (
            "Symbol contains invalid characters. "
            "Only letters, numbers, hyphens, underscores, and ampersands are allowed."
        )
    
    return True, None


def sanitize_symbol(symbol: str) -> str:
    """
    Clean and standardize a symbol string.
    
    Converts to uppercase and strips whitespace.
    
    Args:
        symbol: Symbol to sanitize
    
    Returns:
        str: Sanitized symbol
    
    Example:
        >>> sanitize_symbol("  reliance  ")
        'RELIANCE'
        >>> sanitize_symbol("nifty")
        'NIFTY'
    """
    return symbol.strip().upper()


def validate_exchange(exchange: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if exchange is supported.
    
    Args:
        exchange: Exchange code to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    
    Example:
        >>> validate_exchange("NSE")
        (True, None)
        >>> validate_exchange("INVALID")
        (False, "Unsupported exchange...")
    """
    if not exchange:
        return False, "Exchange cannot be empty"
    
    exchange_upper = exchange.upper()
    
    if exchange_upper not in SUPPORTED_EXCHANGES:
        return False, (
            f"Unsupported exchange: {exchange}. "
            f"Supported exchanges: {', '.join(SUPPORTED_EXCHANGES.keys())}"
        )
    
    return True, None


def validate_date_string(date_str: str, date_format: str = "%Y-%m-%d") -> Tuple[bool, Optional[str]]:
    """
    Validate date string format.
    
    Args:
        date_str: Date string to validate
        date_format: Expected date format (default: YYYY-MM-DD)
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    
    Example:
        >>> validate_date_string("2024-01-15")
        (True, None)
        >>> validate_date_string("invalid-date")
        (False, "Invalid date format...")
    """
    if not date_str:
        return False, "Date string cannot be empty"
    
    try:
        datetime.strptime(date_str, date_format)
        return True, None
    except ValueError as e:
        return False, f"Invalid date format. Expected {date_format}: {str(e)}"


def validate_date_range(
    start_date: str,
    end_date: str,
    date_format: str = "%Y-%m-%d"
) -> Tuple[bool, Optional[str]]:
    """
    Validate date range ensuring start is before end.
    
    Args:
        start_date: Start date string
        end_date: End date string
        date_format: Date format (default: YYYY-MM-DD)
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    
    Example:
        >>> validate_date_range("2024-01-01", "2024-01-31")
        (True, None)
        >>> validate_date_range("2024-01-31", "2024-01-01")
        (False, "Start date must be before end date")
    """
    # Validate individual dates
    is_valid_start, error_start = validate_date_string(start_date, date_format)
    if not is_valid_start:
        return False, f"Start date error: {error_start}"
    
    is_valid_end, error_end = validate_date_string(end_date, date_format)
    if not is_valid_end:
        return False, f"End date error: {error_end}"
    
    # Parse dates
    start_dt = datetime.strptime(start_date, date_format)
    end_dt = datetime.strptime(end_date, date_format)
    
    # Check order
    if start_dt >= end_dt:
        return False, "Start date must be before end date"
    
    # Check if range is reasonable (not more than 10 years)
    days_diff = (end_dt - start_dt).days
    if days_diff > 3650:  # ~10 years
        return False, "Date range is too large (maximum 10 years)"
    
    return True, None


def validate_strike_price(strike: float) -> Tuple[bool, Optional[str]]:
    """
    Validate option strike price.
    
    Args:
        strike: Strike price to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    
    Example:
        >>> validate_strike_price(18000.0)
        (True, None)
        >>> validate_strike_price(-100.0)
        (False, "Strike price must be positive")
    """
    if strike <= 0:
        return False, "Strike price must be positive"
    
    if strike > 1000000:
        return False, "Strike price is unreasonably high"
    
    return True, None


def validate_indicator_params(
    indicator_name: str,
    params: dict
) -> Tuple[bool, Optional[str]]:
    """
    Validate indicator-specific parameters.
    
    Checks common parameters like period, window, etc.
    
    Args:
        indicator_name: Name of the indicator
        params: Dictionary of parameters
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    
    Example:
        >>> validate_indicator_params("RSI", {"period": 14})
        (True, None)
        >>> validate_indicator_params("RSI", {"period": -5})
        (False, "Period must be positive")
    """
    if not params:
        return True, None  # No params to validate
    
    # Validate common parameters
    if "period" in params:
        period = params["period"]
        if not isinstance(period, int) or period <= 0:
            return False, "Period must be a positive integer"
        if period > 500:
            return False, "Period is too large (maximum 500)"
    
    if "window" in params:
        window = params["window"]
        if not isinstance(window, int) or window <= 0:
            return False, "Window must be a positive integer"
        if window > 500:
            return False, "Window is too large (maximum 500)"
    
    if "std_dev" in params:
        std_dev = params["std_dev"]
        if not isinstance(std_dev, (int, float)) or std_dev <= 0:
            return False, "Standard deviation must be a positive number"
    
    if "multiplier" in params:
        multiplier = params["multiplier"]
        if not isinstance(multiplier, (int, float)) or multiplier <= 0:
            return False, "Multiplier must be a positive number"
    
    return True, None


def validate_timeframe_input(interval: str) -> Tuple[bool, Optional[str]]:
    """
    Validate timeframe string.
    
    Args:
        interval: Timeframe string to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    
    Example:
        >>> validate_timeframe_input("5m")
        (True, None)
        >>> validate_timeframe_input("invalid")
        (False, "Invalid timeframe...")
    """
    if not interval:
        return False, "Timeframe cannot be empty"
    
    if not validate_timeframe(interval):
        return False, f"Invalid timeframe: {interval}"
    
    return True, None


def validate_positive_integer(value: int, name: str, max_value: Optional[int] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a positive integer.
    
    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)
        max_value: Optional maximum allowed value
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    
    Example:
        >>> validate_positive_integer(10, "count")
        (True, None)
        >>> validate_positive_integer(-5, "count")
        (False, "count must be a positive integer")
    """
    if not isinstance(value, int) or value <= 0:
        return False, f"{name} must be a positive integer"
    
    if max_value is not None and value > max_value:
        return False, f"{name} must not exceed {max_value}"
    
    return True, None


def validate_percentage(value: float, name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a valid percentage (0-100).
    
    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    
    Example:
        >>> validate_percentage(50.5, "threshold")
        (True, None)
        >>> validate_percentage(150.0, "threshold")
        (False, "threshold must be between 0 and 100")
    """
    if not isinstance(value, (int, float)):
        return False, f"{name} must be a number"
    
    if value < 0 or value > 100:
        return False, f"{name} must be between 0 and 100"
    
    return True, None


def is_index_symbol(symbol: str) -> bool:
    """
    Check if symbol is a known index.
    
    Args:
        symbol: Symbol to check
    
    Returns:
        bool: True if symbol is a known index
    
    Example:
        >>> is_index_symbol("NIFTY")
        True
        >>> is_index_symbol("RELIANCE")
        False
    """
    return sanitize_symbol(symbol) in NSE_INDICES


def get_supported_exchanges() -> list[str]:
    """
    Get list of supported exchanges.
    
    Returns:
        list[str]: List of exchange codes
    
    Example:
        >>> exchanges = get_supported_exchanges()
        >>> "NSE" in exchanges
        True
    """
    return list(SUPPORTED_EXCHANGES.keys())


def get_exchange_name(exchange_code: str) -> Optional[str]:
    """
    Get full name of an exchange from its code.
    
    Args:
        exchange_code: Exchange code (e.g., "NSE")
    
    Returns:
        Optional[str]: Full exchange name or None if not found
    
    Example:
        >>> get_exchange_name("NSE")
        'National Stock Exchange'
    """
    return SUPPORTED_EXCHANGES.get(exchange_code.upper())
