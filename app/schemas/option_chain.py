"""
Pydantic schemas for option chain data.
Defines models for option chain requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class OptionChainRequest(BaseModel):
    """
    Request model for fetching option chain data.
    """
    
    symbol: str = Field(
        ...,
        description="Symbol for option chain (index or stock)",
        examples=["NIFTY", "BANKNIFTY", "RELIANCE"]
    )
    is_index: bool = Field(
        default=True,
        description="Whether the symbol is an index or equity"
    )
    
    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Convert to uppercase."""
        return v.strip().upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "is_index": True
            }
        }


class OptionData(BaseModel):
    """
    Option data for a specific strike price.
    
    Contains call and put data including OI, volume, LTP, and IV.
    """
    
    strike_price: float = Field(
        ...,
        description="Strike price",
        gt=0
    )
    
    # Call Option Data
    call_oi: Optional[int] = Field(
        default=None,
        description="Call open interest",
        ge=0
    )
    call_volume: Optional[int] = Field(
        default=None,
        description="Call trading volume",
        ge=0
    )
    call_ltp: Optional[float] = Field(
        default=None,
        description="Call last traded price",
        ge=0
    )
    call_iv: Optional[float] = Field(
        default=None,
        description="Call implied volatility (%)",
        ge=0,
        le=500
    )
    call_change_oi: Optional[int] = Field(
        default=None,
        description="Change in call OI"
    )
    call_bid: Optional[float] = Field(
        default=None,
        description="Call bid price",
        ge=0
    )
    call_ask: Optional[float] = Field(
        default=None,
        description="Call ask price",
        ge=0
    )
    
    # Put Option Data
    put_oi: Optional[int] = Field(
        default=None,
        description="Put open interest",
        ge=0
    )
    put_volume: Optional[int] = Field(
        default=None,
        description="Put trading volume",
        ge=0
    )
    put_ltp: Optional[float] = Field(
        default=None,
        description="Put last traded price",
        ge=0
    )
    put_iv: Optional[float] = Field(
        default=None,
        description="Put implied volatility (%)",
        ge=0,
        le=500
    )
    put_change_oi: Optional[int] = Field(
        default=None,
        description="Change in put OI"
    )
    put_bid: Optional[float] = Field(
        default=None,
        description="Put bid price",
        ge=0
    )
    put_ask: Optional[float] = Field(
        default=None,
        description="Put ask price",
        ge=0
    )
    
    # Derived Metrics
    pcr_oi: Optional[float] = Field(
        default=None,
        description="Put-Call Ratio based on OI",
        ge=0
    )
    pcr_volume: Optional[float] = Field(
        default=None,
        description="Put-Call Ratio based on volume",
        ge=0
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "strike_price": 21500.0,
                "call_oi": 1500000,
                "call_volume": 50000,
                "call_ltp": 125.50,
                "call_iv": 18.5,
                "call_change_oi": 25000,
                "call_bid": 125.00,
                "call_ask": 126.00,
                "put_oi": 2000000,
                "put_volume": 75000,
                "put_ltp": 110.25,
                "put_iv": 19.2,
                "put_change_oi": 30000,
                "put_bid": 110.00,
                "put_ask": 110.50,
                "pcr_oi": 1.33,
                "pcr_volume": 1.50
            }
        }


class OptionChainResponse(BaseModel):
    """
    Response model for option chain data.
    
    Contains complete option chain with all strikes, expiry dates,
    and underlying value.
    """
    
    symbol: str = Field(..., description="Symbol")
    expiry_dates: List[str] = Field(
        ...,
        description="Available expiry dates"
    )
    underlying_value: float = Field(
        ...,
        description="Current value of underlying asset",
        gt=0
    )
    options: List[OptionData] = Field(
        ...,
        description="Option data for all strikes"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp when data was fetched"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "expiry_dates": [
                    "25-Jan-2024",
                    "01-Feb-2024",
                    "08-Feb-2024"
                ],
                "underlying_value": 21530.50,
                "options": [
                    {
                        "strike_price": 21500.0,
                        "call_oi": 1500000,
                        "call_volume": 50000,
                        "call_ltp": 125.50,
                        "call_iv": 18.5,
                        "put_oi": 2000000,
                        "put_volume": 75000,
                        "put_ltp": 110.25,
                        "put_iv": 19.2
                    }
                ],
                "timestamp": "2024-01-15T15:30:00",
                "metadata": {
                    "is_index": True,
                    "total_strikes": 50,
                    "atm_strike": 21500.0
                }
            }
        }


class OptionGreeks(BaseModel):
    """
    Option Greeks data (if available).
    """
    
    strike_price: float = Field(..., description="Strike price", gt=0)
    option_type: str = Field(
        ...,
        description="Option type (call or put)",
        examples=["call", "put"]
    )
    
    delta: Optional[float] = Field(
        default=None,
        description="Delta",
        ge=-1,
        le=1
    )
    gamma: Optional[float] = Field(
        default=None,
        description="Gamma",
        ge=0
    )
    theta: Optional[float] = Field(
        default=None,
        description="Theta"
    )
    vega: Optional[float] = Field(
        default=None,
        description="Vega",
        ge=0
    )
    rho: Optional[float] = Field(
        default=None,
        description="Rho"
    )
    
    @field_validator("option_type")
    @classmethod
    def validate_option_type(cls, v: str) -> str:
        """Validate option type."""
        v_lower = v.lower()
        if v_lower not in ["call", "put"]:
            raise ValueError("option_type must be 'call' or 'put'")
        return v_lower
    
    class Config:
        json_schema_extra = {
            "example": {
                "strike_price": 21500.0,
                "option_type": "call",
                "delta": 0.52,
                "gamma": 0.003,
                "theta": -15.5,
                "vega": 25.3,
                "rho": 12.8
            }
        }


class OptionChainAnalysis(BaseModel):
    """
    Analysis derived from option chain data.
    """
    
    symbol: str = Field(..., description="Symbol")
    atm_strike: float = Field(
        ...,
        description="At-the-money strike price",
        gt=0
    )
    max_pain: Optional[float] = Field(
        default=None,
        description="Max pain strike price",
        gt=0
    )
    pcr_oi: float = Field(
        ...,
        description="Overall Put-Call Ratio (OI)",
        ge=0
    )
    pcr_volume: float = Field(
        ...,
        description="Overall Put-Call Ratio (Volume)",
        ge=0
    )
    total_call_oi: int = Field(
        ...,
        description="Total call open interest",
        ge=0
    )
    total_put_oi: int = Field(
        ...,
        description="Total put open interest",
        ge=0
    )
    total_call_volume: int = Field(
        ...,
        description="Total call volume",
        ge=0
    )
    total_put_volume: int = Field(
        ...,
        description="Total put volume",
        ge=0
    )
    support_levels: List[float] = Field(
        default_factory=list,
        description="Support levels based on put OI"
    )
    resistance_levels: List[float] = Field(
        default_factory=list,
        description="Resistance levels based on call OI"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "atm_strike": 21500.0,
                "max_pain": 21450.0,
                "pcr_oi": 1.25,
                "pcr_volume": 1.15,
                "total_call_oi": 50000000,
                "total_put_oi": 62500000,
                "total_call_volume": 2000000,
                "total_put_volume": 2300000,
                "support_levels": [21400.0, 21300.0, 21200.0],
                "resistance_levels": [21600.0, 21700.0, 21800.0]
            }
        }


class OptionChainFilter(BaseModel):
    """
    Filter criteria for option chain data.
    """
    
    min_oi: Optional[int] = Field(
        default=None,
        description="Minimum open interest",
        ge=0
    )
    min_volume: Optional[int] = Field(
        default=None,
        description="Minimum volume",
        ge=0
    )
    strike_range: Optional[int] = Field(
        default=None,
        description="Number of strikes above and below ATM",
        ge=1,
        le=50
    )
    expiry_date: Optional[str] = Field(
        default=None,
        description="Specific expiry date to filter"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "min_oi": 10000,
                "min_volume": 1000,
                "strike_range": 10,
                "expiry_date": "25-Jan-2024"
            }
        }


class SupportedSymbol(BaseModel):
    """
    Information about a supported symbol for option chain.
    """
    
    symbol: str = Field(..., description="Symbol code")
    name: str = Field(..., description="Full name")
    is_index: bool = Field(..., description="Whether it's an index")
    lot_size: Optional[int] = Field(
        default=None,
        description="Lot size for futures/options",
        ge=1
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NIFTY",
                "name": "Nifty 50",
                "is_index": True,
                "lot_size": 50
            }
        }
