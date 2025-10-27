"""
Pydantic schemas for candle (OHLCV) data.
Defines models for candle requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class Candle(BaseModel):
    """
    Individual candle (OHLCV) data point.
    
    Represents a single candlestick with open, high, low, close, volume data.
    """
    
    symbol: str = Field(
        ...,
        description="Trading symbol",
        examples=["NIFTY", "RELIANCE"]
    )
    timestamp: datetime = Field(
        ...,
        description="Candle timestamp (start of the period)"
    )
    open: float = Field(
        ...,
        description="Opening price",
        gt=0
    )
    high: float = Field(
        ...,
        description="Highest price in the period",
        gt=0
    )
    low: float = Field(
        ...,
        description="Lowest price in the period",
        gt=0
    )
    close: float = Field(
        ...,
        description="Closing price",
        gt=0
    )
    volume: float = Field(
        ...,
        description="Trading volume",
        ge=0
    )
    timeframe: str = Field(
        ...,
        description="Timeframe of the candle",
        examples=["1m", "5m", "1h", "1d"]
    )
    
    @field_validator("high")
    @classmethod
    def validate_high(cls, v: float, info) -> float:
        """Ensure high is the highest price."""
        if "low" in info.data and v < info.data["low"]:
            raise ValueError("High must be >= low")
        return v
    
    @field_validator("close")
    @classmethod
    def validate_close(cls, v: float, info) -> float:
        """Ensure close is within high-low range."""
        if "high" in info.data and "low" in info.data:
            if v > info.data["high"] or v < info.data["low"]:
                raise ValueError("Close must be between low and high")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "timestamp": "2024-01-15T09:15:00",
                "open": 21500.50,
                "high": 21550.75,
                "low": 21480.25,
                "close": 21530.00,
                "volume": 1500000.0,
                "timeframe": "5m"
            }
        }


class CandleRequest(BaseModel):
    """
    Request model for fetching historical candles.
    """
    
    symbol: str = Field(
        ...,
        description="Trading symbol",
        examples=["NIFTY", "RELIANCE", "BANKNIFTY"]
    )
    exchange: str = Field(
        ...,
        description="Exchange code",
        examples=["NSE", "BSE", "NFO"]
    )
    interval: str = Field(
        ...,
        description="Candle timeframe",
        examples=["1m", "5m", "15m", "1h", "1d"]
    )
    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        examples=["2024-01-01"]
    )
    end_date: str = Field(
        ...,
        description="End date in YYYY-MM-DD format",
        examples=["2024-01-31"]
    )
    include_current: bool = Field(
        default=True,
        description="Include current forming candle in response"
    )
    
    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate and sanitize symbol."""
        return v.strip().upper()
    
    @field_validator("exchange")
    @classmethod
    def validate_exchange(cls, v: str) -> str:
        """Validate and sanitize exchange."""
        return v.strip().upper()
    
    @field_validator("interval")
    @classmethod
    def validate_interval(cls, v: str) -> str:
        """Validate and sanitize interval."""
        return v.strip().lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "exchange": "NSE",
                "interval": "5m",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "include_current": True
            }
        }


class CandleResponse(BaseModel):
    """
    Response model for candle data.
    
    Contains list of historical candles, optional current candle,
    and metadata about the request.
    """
    
    candles: List[Candle] = Field(
        ...,
        description="List of historical candles"
    )
    current_candle: Optional[Candle] = Field(
        default=None,
        description="Current forming candle (if include_current=True)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the response"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "candles": [
                    {
                        "symbol": "NIFTY",
                        "timestamp": "2024-01-15T09:15:00",
                        "open": 21500.50,
                        "high": 21550.75,
                        "low": 21480.25,
                        "close": 21530.00,
                        "volume": 1500000.0,
                        "timeframe": "5m"
                    }
                ],
                "current_candle": {
                    "symbol": "NIFTY",
                    "timestamp": "2024-01-15T15:25:00",
                    "open": 21530.00,
                    "high": 21545.00,
                    "low": 21525.00,
                    "close": 21540.00,
                    "volume": 500000.0,
                    "timeframe": "5m"
                },
                "metadata": {
                    "symbol": "NIFTY",
                    "exchange": "NSE",
                    "interval": "5m",
                    "count": 1,
                    "start_date": "2024-01-15",
                    "end_date": "2024-01-15"
                }
            }
        }


class PartialCandle(BaseModel):
    """
    Partial candle data for real-time updates.
    
    Used for WebSocket streaming of incomplete candles.
    """
    
    symbol: str = Field(..., description="Trading symbol")
    timestamp: datetime = Field(..., description="Candle start timestamp")
    open: float = Field(..., description="Opening price", gt=0)
    high: float = Field(..., description="Current high", gt=0)
    low: float = Field(..., description="Current low", gt=0)
    close: float = Field(..., description="Current close/last price", gt=0)
    volume: float = Field(..., description="Current volume", ge=0)
    timeframe: str = Field(..., description="Timeframe")
    tick_count: int = Field(
        default=0,
        description="Number of ticks aggregated",
        ge=0
    )
    vwap: Optional[float] = Field(
        default=None,
        description="Volume-weighted average price",
        gt=0
    )
    is_complete: bool = Field(
        default=False,
        description="Whether the candle is complete"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "timestamp": "2024-01-15T15:25:00",
                "open": 21530.00,
                "high": 21545.00,
                "low": 21525.00,
                "close": 21540.00,
                "volume": 500000.0,
                "timeframe": "5m",
                "tick_count": 150,
                "vwap": 21535.50,
                "is_complete": False
            }
        }


class MultiTimeframeCandles(BaseModel):
    """
    Candles across multiple timeframes for the same symbol.
    """
    
    symbol: str = Field(..., description="Trading symbol")
    exchange: str = Field(..., description="Exchange code")
    timeframes: Dict[str, List[Candle]] = Field(
        ...,
        description="Candles organized by timeframe"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "exchange": "NSE",
                "timeframes": {
                    "1m": [],
                    "5m": [],
                    "1h": []
                },
                "metadata": {
                    "start_date": "2024-01-15",
                    "end_date": "2024-01-15"
                }
            }
        }
