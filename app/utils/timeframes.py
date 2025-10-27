"""
Timeframe utility functions for parsing, validating, and converting timeframe strings.
Supports standard formats like 1m, 5m, 1h, 1d, etc.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


# Timeframe aliases mapping
TIMEFRAME_ALIASES: Dict[str, str] = {
    # Minute aliases
    "1min": "1m",
    "3min": "3m",
    "5min": "5m",
    "10min": "10m",
    "15min": "15m",
    "30min": "30m",
    "1minute": "1m",
    "5minutes": "5m",
    
    # Hour aliases
    "1hour": "1h",
    "2hour": "2h",
    "4hour": "4h",
    "1hr": "1h",
    "2hr": "2h",
    "4hr": "4h",
    
    # Day aliases
    "1day": "1d",
    "daily": "1d",
    "day": "1d",
    
    # Week aliases
    "1week": "1w",
    "weekly": "1w",
    "week": "1w",
    
    # Month aliases
    "1month": "1M",
    "monthly": "1M",
    "month": "1M",
}


# Supported timeframes with their duration in seconds
TIMEFRAME_SECONDS: Dict[str, int] = {
    # Minutes
    "1m": 60,
    "3m": 180,
    "5m": 300,
    "10m": 600,
    "15m": 900,
    "30m": 1800,
    
    # Hours
    "1h": 3600,
    "2h": 7200,
    "4h": 14400,
    
    # Days
    "1d": 86400,
    
    # Weeks
    "1w": 604800,
    
    # Months (approximate - 30 days)
    "1M": 2592000,
}


# Pandas frequency mapping for resampling
TIMEFRAME_PANDAS_FREQ: Dict[str, str] = {
    "1m": "1T",
    "3m": "3T",
    "5m": "5T",
    "10m": "10T",
    "15m": "15T",
    "30m": "30T",
    "1h": "1H",
    "2h": "2H",
    "4h": "4H",
    "1d": "1D",
    "1w": "1W",
    "1M": "1M",
}


def normalize_timeframe(interval_str: str) -> str:
    """
    Normalize a timeframe string to standard format.
    
    Converts various timeframe representations to the standard format.
    For example: "1min" -> "1m", "1hour" -> "1h", "daily" -> "1d"
    
    Args:
        interval_str: Timeframe string to normalize
    
    Returns:
        str: Normalized timeframe string
    
    Raises:
        ValueError: If timeframe format is invalid
    
    Example:
        >>> normalize_timeframe("1min")
        '1m'
        >>> normalize_timeframe("1hour")
        '1h'
        >>> normalize_timeframe("daily")
        '1d'
    """
    interval_str = interval_str.strip().lower()
    
    # Check if it's an alias
    if interval_str in TIMEFRAME_ALIASES:
        return TIMEFRAME_ALIASES[interval_str]
    
    # Check if it's already in standard format
    if interval_str in TIMEFRAME_SECONDS:
        return interval_str
    
    raise ValueError(
        f"Invalid timeframe: {interval_str}. "
        f"Supported formats: {', '.join(TIMEFRAME_SECONDS.keys())}"
    )


def validate_timeframe(interval_str: str) -> bool:
    """
    Validate if a timeframe string is supported.
    
    Args:
        interval_str: Timeframe string to validate
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_timeframe("5m")
        True
        >>> validate_timeframe("99x")
        False
    """
    try:
        normalize_timeframe(interval_str)
        return True
    except ValueError:
        return False


def parse_timeframe(interval_str: str) -> int:
    """
    Parse timeframe string and return duration in seconds.
    
    Args:
        interval_str: Timeframe string (e.g., "1m", "5m", "1h", "1d")
    
    Returns:
        int: Duration in seconds
    
    Raises:
        ValueError: If timeframe is invalid
    
    Example:
        >>> parse_timeframe("5m")
        300
        >>> parse_timeframe("1h")
        3600
        >>> parse_timeframe("1d")
        86400
    """
    normalized = normalize_timeframe(interval_str)
    return TIMEFRAME_SECONDS[normalized]


def timeframe_to_pandas_freq(interval_str: str) -> str:
    """
    Convert timeframe string to pandas frequency string for resampling.
    
    Args:
        interval_str: Timeframe string
    
    Returns:
        str: Pandas frequency string
    
    Raises:
        ValueError: If timeframe is invalid
    
    Example:
        >>> timeframe_to_pandas_freq("5m")
        '5T'
        >>> timeframe_to_pandas_freq("1h")
        '1H'
        >>> timeframe_to_pandas_freq("1d")
        '1D'
    """
    normalized = normalize_timeframe(interval_str)
    return TIMEFRAME_PANDAS_FREQ[normalized]


def get_candle_count(
    start_date: datetime,
    end_date: datetime,
    interval: str
) -> int:
    """
    Calculate expected number of candles between two dates for a given interval.
    
    This is an approximation as it doesn't account for market holidays,
    weekends, or trading hours.
    
    Args:
        start_date: Start datetime
        end_date: End datetime
        interval: Timeframe string
    
    Returns:
        int: Approximate number of candles
    
    Example:
        >>> from datetime import datetime
        >>> start = datetime(2024, 1, 1)
        >>> end = datetime(2024, 1, 2)
        >>> get_candle_count(start, end, "1h")
        24
    """
    interval_seconds = parse_timeframe(interval)
    time_diff = (end_date - start_date).total_seconds()
    return int(time_diff / interval_seconds)


def get_timeframe_duration(interval: str) -> timedelta:
    """
    Get timedelta object for a timeframe.
    
    Args:
        interval: Timeframe string
    
    Returns:
        timedelta: Duration as timedelta object
    
    Example:
        >>> get_timeframe_duration("5m")
        timedelta(seconds=300)
        >>> get_timeframe_duration("1h")
        timedelta(seconds=3600)
    """
    seconds = parse_timeframe(interval)
    return timedelta(seconds=seconds)


def get_bucket_start(timestamp: datetime, interval: str) -> datetime:
    """
    Get the start time of the candle bucket for a given timestamp.
    
    This is useful for tick aggregation to determine which candle
    a tick belongs to.
    
    Args:
        timestamp: Timestamp to bucket
        interval: Timeframe string
    
    Returns:
        datetime: Start of the candle bucket
    
    Example:
        >>> from datetime import datetime
        >>> ts = datetime(2024, 1, 1, 10, 23, 45)
        >>> get_bucket_start(ts, "5m")
        datetime(2024, 1, 1, 10, 20, 0)
        >>> get_bucket_start(ts, "1h")
        datetime(2024, 1, 1, 10, 0, 0)
    """
    interval_seconds = parse_timeframe(interval)
    
    # Convert to Unix timestamp
    unix_timestamp = int(timestamp.timestamp())
    
    # Calculate bucket start
    bucket_start_unix = (unix_timestamp // interval_seconds) * interval_seconds
    
    # Convert back to datetime
    return datetime.fromtimestamp(bucket_start_unix, tz=timestamp.tzinfo)


def get_supported_timeframes() -> list[str]:
    """
    Get list of all supported timeframes.
    
    Returns:
        list[str]: List of supported timeframe strings
    
    Example:
        >>> timeframes = get_supported_timeframes()
        >>> '5m' in timeframes
        True
    """
    return list(TIMEFRAME_SECONDS.keys())


def is_intraday_timeframe(interval: str) -> bool:
    """
    Check if timeframe is intraday (less than 1 day).
    
    Args:
        interval: Timeframe string
    
    Returns:
        bool: True if intraday, False otherwise
    
    Example:
        >>> is_intraday_timeframe("5m")
        True
        >>> is_intraday_timeframe("1d")
        False
    """
    seconds = parse_timeframe(interval)
    return seconds < 86400  # Less than 1 day


def compare_timeframes(interval1: str, interval2: str) -> int:
    """
    Compare two timeframes.
    
    Args:
        interval1: First timeframe
        interval2: Second timeframe
    
    Returns:
        int: -1 if interval1 < interval2, 0 if equal, 1 if interval1 > interval2
    
    Example:
        >>> compare_timeframes("1m", "5m")
        -1
        >>> compare_timeframes("1h", "1h")
        0
        >>> compare_timeframes("1d", "1h")
        1
    """
    seconds1 = parse_timeframe(interval1)
    seconds2 = parse_timeframe(interval2)
    
    if seconds1 < seconds2:
        return -1
    elif seconds1 == seconds2:
        return 0
    else:
        return 1


def get_higher_timeframe(interval: str, multiplier: int = 2) -> Optional[str]:
    """
    Get a higher timeframe by multiplying the current one.
    
    Args:
        interval: Current timeframe
        multiplier: Multiplier for the timeframe
    
    Returns:
        Optional[str]: Higher timeframe if it exists in supported list, None otherwise
    
    Example:
        >>> get_higher_timeframe("1m", 5)
        '5m'
        >>> get_higher_timeframe("5m", 3)
        '15m'
    """
    current_seconds = parse_timeframe(interval)
    target_seconds = current_seconds * multiplier
    
    # Find matching timeframe
    for tf, seconds in TIMEFRAME_SECONDS.items():
        if seconds == target_seconds:
            return tf
    
    return None
