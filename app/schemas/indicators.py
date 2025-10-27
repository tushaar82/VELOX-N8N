"""
Pydantic schemas for technical indicators.
Defines models for indicator requests, responses, and support/resistance levels.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class IndicatorRequest(BaseModel):
    """
    Request model for calculating technical indicators.
    """
    
    symbol: str = Field(
        ...,
        description="Trading symbol",
        examples=["NIFTY", "RELIANCE"]
    )
    exchange: str = Field(
        ...,
        description="Exchange code",
        examples=["NSE", "BSE", "NFO"]
    )
    interval: str = Field(
        ...,
        description="Timeframe for analysis",
        examples=["1m", "5m", "1h", "1d"]
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date in YYYY-MM-DD format",
        examples=["2024-01-01"]
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date in YYYY-MM-DD format",
        examples=["2024-01-31"]
    )
    indicators: Optional[List[str]] = Field(
        default=None,
        description="List of specific indicators to calculate. If None, calculates all.",
        examples=[["RSI", "MACD", "EMA"]]
    )
    indicator_params: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="Custom parameters for specific indicators",
        examples=[{"RSI": {"period": 14}, "EMA": {"period": 20}}]
    )
    
    @field_validator("symbol", "exchange")
    @classmethod
    def validate_uppercase(cls, v: str) -> str:
        """Convert to uppercase."""
        return v.strip().upper()
    
    @field_validator("interval")
    @classmethod
    def validate_interval(cls, v: str) -> str:
        """Convert to lowercase."""
        return v.strip().lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "exchange": "NSE",
                "interval": "5m",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "indicators": ["RSI", "MACD", "EMA"],
                "indicator_params": {
                    "RSI": {"period": 14},
                    "EMA": {"period": 20}
                }
            }
        }


class IndicatorValue(BaseModel):
    """
    Single indicator value at a specific timestamp.
    """
    
    name: str = Field(..., description="Indicator name")
    value: Union[float, Dict[str, float]] = Field(
        ...,
        description="Indicator value (single float or dict for multi-value indicators)"
    )
    timestamp: datetime = Field(..., description="Timestamp of the value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "RSI",
                "value": 65.5,
                "timestamp": "2024-01-15T15:25:00"
            }
        }


class IndicatorResponse(BaseModel):
    """
    Response model for calculated indicators.
    
    Contains indicator values organized by indicator name,
    along with timestamps and metadata.
    """
    
    symbol: str = Field(..., description="Trading symbol")
    timeframe: str = Field(..., description="Timeframe used")
    indicators: Dict[str, List[float]] = Field(
        ...,
        description="Indicator values organized by name"
    )
    timestamps: List[datetime] = Field(
        ...,
        description="Timestamps corresponding to indicator values"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "timeframe": "5m",
                "indicators": {
                    "RSI": [65.5, 64.2, 63.8],
                    "MACD": [12.5, 13.2, 14.1],
                    "EMA_20": [21500.0, 21510.0, 21520.0]
                },
                "timestamps": [
                    "2024-01-15T15:15:00",
                    "2024-01-15T15:20:00",
                    "2024-01-15T15:25:00"
                ],
                "metadata": {
                    "count": 3,
                    "exchange": "NSE",
                    "calculated_at": "2024-01-15T15:26:00"
                }
            }
        }


class SupportResistanceLevel(BaseModel):
    """
    Individual support or resistance level.
    """
    
    price: float = Field(
        ...,
        description="Price level",
        gt=0
    )
    level_type: str = Field(
        ...,
        description="Type of level (support or resistance)",
        examples=["support", "resistance"]
    )
    strength: float = Field(
        ...,
        description="Strength of the level (0-1)",
        ge=0,
        le=1
    )
    touches: int = Field(
        ...,
        description="Number of times price touched this level",
        ge=1
    )
    last_touch: datetime = Field(
        ...,
        description="Timestamp of last touch"
    )
    
    @field_validator("level_type")
    @classmethod
    def validate_level_type(cls, v: str) -> str:
        """Validate level type."""
        v_lower = v.lower()
        if v_lower not in ["support", "resistance"]:
            raise ValueError("level_type must be 'support' or 'resistance'")
        return v_lower
    
    class Config:
        json_schema_extra = {
            "example": {
                "price": 21500.0,
                "level_type": "support",
                "strength": 0.85,
                "touches": 5,
                "last_touch": "2024-01-15T14:30:00"
            }
        }


class SupportResistanceResponse(BaseModel):
    """
    Response model for support and resistance levels.
    """
    
    symbol: str = Field(..., description="Trading symbol")
    timeframe: str = Field(..., description="Timeframe analyzed")
    support_levels: List[SupportResistanceLevel] = Field(
        ...,
        description="Identified support levels"
    )
    resistance_levels: List[SupportResistanceLevel] = Field(
        ...,
        description="Identified resistance levels"
    )
    tolerance: float = Field(
        ...,
        description="Price tolerance used for clustering (in price units)",
        gt=0
    )
    current_price: float = Field(
        ...,
        description="Current market price",
        gt=0
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "timeframe": "1d",
                "support_levels": [
                    {
                        "price": 21450.0,
                        "level_type": "support",
                        "strength": 0.85,
                        "touches": 5,
                        "last_touch": "2024-01-15T14:30:00"
                    }
                ],
                "resistance_levels": [
                    {
                        "price": 21650.0,
                        "level_type": "resistance",
                        "strength": 0.78,
                        "touches": 3,
                        "last_touch": "2024-01-15T13:00:00"
                    }
                ],
                "tolerance": 25.0,
                "current_price": 21530.0,
                "metadata": {
                    "lookback_days": 90,
                    "method": "swing_extrema_atr_clustering"
                }
            }
        }


class WebSocketSubscription(BaseModel):
    """
    WebSocket subscription request model.
    """
    
    action: str = Field(
        ...,
        description="Action to perform",
        examples=["subscribe", "unsubscribe"]
    )
    symbols: List[str] = Field(
        ...,
        description="List of symbols to subscribe/unsubscribe",
        examples=[["NIFTY", "BANKNIFTY"]]
    )
    timeframes: List[str] = Field(
        ...,
        description="List of timeframes",
        examples=[["1m", "5m", "15m"]]
    )
    indicators: Optional[List[str]] = Field(
        default=None,
        description="Optional list of indicators to calculate in real-time",
        examples=[["RSI", "MACD", "EMA"]]
    )
    
    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Validate action."""
        v_lower = v.lower()
        if v_lower not in ["subscribe", "unsubscribe"]:
            raise ValueError("action must be 'subscribe' or 'unsubscribe'")
        return v_lower
    
    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, v: List[str]) -> List[str]:
        """Convert symbols to uppercase."""
        return [s.strip().upper() for s in v]
    
    @field_validator("timeframes")
    @classmethod
    def validate_timeframes(cls, v: List[str]) -> List[str]:
        """Convert timeframes to lowercase."""
        return [tf.strip().lower() for tf in v]
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "subscribe",
                "symbols": ["NIFTY", "BANKNIFTY"],
                "timeframes": ["1m", "5m"],
                "indicators": ["RSI", "MACD"]
            }
        }


class WebSocketMessage(BaseModel):
    """
    Generic WebSocket message model.
    """
    
    type: str = Field(
        ...,
        description="Message type",
        examples=["candle", "indicator", "error", "ack"]
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Message data"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Message timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "candle",
                "data": {
                    "symbol": "NIFTY",
                    "timeframe": "1m",
                    "candle": {
                        "open": 21500.0,
                        "high": 21510.0,
                        "low": 21495.0,
                        "close": 21505.0,
                        "volume": 100000.0
                    }
                },
                "timestamp": "2024-01-15T15:25:00"
            }
        }


class MultiTimeframeIndicators(BaseModel):
    """
    Indicators calculated across multiple timeframes.
    """
    
    symbol: str = Field(..., description="Trading symbol")
    exchange: str = Field(..., description="Exchange code")
    timeframes: Dict[str, IndicatorResponse] = Field(
        ...,
        description="Indicators organized by timeframe"
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
                    "1m": {
                        "symbol": "NIFTY",
                        "timeframe": "1m",
                        "indicators": {"RSI": [65.5]},
                        "timestamps": ["2024-01-15T15:25:00"],
                        "metadata": {}
                    },
                    "5m": {
                        "symbol": "NIFTY",
                        "timeframe": "5m",
                        "indicators": {"RSI": [64.2]},
                        "timestamps": ["2024-01-15T15:25:00"],
                        "metadata": {}
                    }
                },
                "metadata": {
                    "calculated_at": "2024-01-15T15:26:00"
                }
            }
        }


class IndicatorMetadata(BaseModel):
    """
    Metadata about available indicators.
    """
    
    name: str = Field(..., description="Indicator name")
    category: str = Field(
        ...,
        description="Indicator category",
        examples=["volume", "volatility", "trend", "momentum", "others"]
    )
    description: str = Field(..., description="Indicator description")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default and required parameters"
    )
    min_periods: int = Field(
        ...,
        description="Minimum number of periods required",
        ge=1
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "RSI",
                "category": "momentum",
                "description": "Relative Strength Index",
                "parameters": {
                    "period": {"default": 14, "min": 2, "max": 100}
                },
                "min_periods": 14
            }
        }
