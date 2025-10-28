"""
API endpoints for technical indicator calculations.
"""

from typing import Dict, List, Optional

try:
    from fastapi import APIRouter, HTTPException, Query
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None
    HTTPException = Exception
    Query = None
    JSONResponse = None

from app.core.logging import get_logger
from app.schemas.indicators import (
    IndicatorRequest,
    IndicatorResponse,
    MultiTimeframeIndicators,
    IndicatorMetadata
)
from app.services.market_data import get_market_data_service
from app.services.indicators import get_indicator_service
from app.utils.validators import (
    validate_symbol,
    validate_exchange,
    validate_timeframe_input,
    validate_date_range
)

logger = get_logger(__name__)

# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/indicators", tags=["indicators"])
else:
    router = None


# Available indicators metadata - 70+ indicators
AVAILABLE_INDICATORS = {
    # Volume Indicators (9)
    "MFI": {
        "name": "MFI",
        "category": "volume",
        "description": "Money Flow Index",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "ADI": {
        "name": "ADI",
        "category": "volume",
        "description": "Accumulation/Distribution Index",
        "parameters": {},
        "min_periods": 1
    },
    "OBV": {
        "name": "OBV",
        "category": "volume",
        "description": "On-Balance Volume",
        "parameters": {},
        "min_periods": 1
    },
    "CMF": {
        "name": "CMF",
        "category": "volume",
        "description": "Chaikin Money Flow",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "ForceIndex": {
        "name": "ForceIndex",
        "category": "volume",
        "description": "Force Index",
        "parameters": {"window": {"default": 13, "min": 2, "max": 100}},
        "min_periods": 13
    },
    "EaseOfMovement": {
        "name": "EaseOfMovement",
        "category": "volume",
        "description": "Ease of Movement",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "VPT": {
        "name": "VPT",
        "category": "volume",
        "description": "Volume Price Trend",
        "parameters": {},
        "min_periods": 1
    },
    "NVI": {
        "name": "NVI",
        "category": "volume",
        "description": "Negative Volume Index",
        "parameters": {},
        "min_periods": 1
    },
    "VWAP": {
        "name": "VWAP",
        "category": "volume",
        "description": "Volume Weighted Average Price",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    
    # Volatility Indicators (14)
    "ATR": {
        "name": "ATR",
        "category": "volatility",
        "description": "Average True Range",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "BB_High": {
        "name": "BB_High",
        "category": "volatility",
        "description": "Bollinger Bands - Upper Band",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}, "window_dev": {"default": 2, "min": 1, "max": 5}},
        "min_periods": 20
    },
    "BB_Mid": {
        "name": "BB_Mid",
        "category": "volatility",
        "description": "Bollinger Bands - Middle Band",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "BB_Low": {
        "name": "BB_Low",
        "category": "volatility",
        "description": "Bollinger Bands - Lower Band",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}, "window_dev": {"default": 2, "min": 1, "max": 5}},
        "min_periods": 20
    },
    "BB_Width": {
        "name": "BB_Width",
        "category": "volatility",
        "description": "Bollinger Bands - Width",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "BB_Percent": {
        "name": "BB_Percent",
        "category": "volatility",
        "description": "Bollinger Bands - Percent B",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "KC_High": {
        "name": "KC_High",
        "category": "volatility",
        "description": "Keltner Channel - Upper Band",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "KC_Mid": {
        "name": "KC_Mid",
        "category": "volatility",
        "description": "Keltner Channel - Middle Band",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "KC_Low": {
        "name": "KC_Low",
        "category": "volatility",
        "description": "Keltner Channel - Lower Band",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "DC_High": {
        "name": "DC_High",
        "category": "volatility",
        "description": "Donchian Channel - Upper Band",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "DC_Mid": {
        "name": "DC_Mid",
        "category": "volatility",
        "description": "Donchian Channel - Middle Band",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "DC_Low": {
        "name": "DC_Low",
        "category": "volatility",
        "description": "Donchian Channel - Lower Band",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "UlcerIndex": {
        "name": "UlcerIndex",
        "category": "volatility",
        "description": "Ulcer Index",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    
    # Trend Indicators (30+)
    "SMA_10": {
        "name": "SMA_10",
        "category": "trend",
        "description": "Simple Moving Average (10 period)",
        "parameters": {"window": {"default": 10, "min": 2, "max": 500}},
        "min_periods": 10
    },
    "SMA_20": {
        "name": "SMA_20",
        "category": "trend",
        "description": "Simple Moving Average (20 period)",
        "parameters": {"window": {"default": 20, "min": 2, "max": 500}},
        "min_periods": 20
    },
    "SMA_50": {
        "name": "SMA_50",
        "category": "trend",
        "description": "Simple Moving Average (50 period)",
        "parameters": {"window": {"default": 50, "min": 2, "max": 500}},
        "min_periods": 50
    },
    "SMA_200": {
        "name": "SMA_200",
        "category": "trend",
        "description": "Simple Moving Average (200 period)",
        "parameters": {"window": {"default": 200, "min": 2, "max": 500}},
        "min_periods": 200
    },
    "EMA_12": {
        "name": "EMA_12",
        "category": "trend",
        "description": "Exponential Moving Average (12 period)",
        "parameters": {"window": {"default": 12, "min": 2, "max": 500}},
        "min_periods": 12
    },
    "EMA_20": {
        "name": "EMA_20",
        "category": "trend",
        "description": "Exponential Moving Average (20 period)",
        "parameters": {"window": {"default": 20, "min": 2, "max": 500}},
        "min_periods": 20
    },
    "EMA_26": {
        "name": "EMA_26",
        "category": "trend",
        "description": "Exponential Moving Average (26 period)",
        "parameters": {"window": {"default": 26, "min": 2, "max": 500}},
        "min_periods": 26
    },
    "EMA_50": {
        "name": "EMA_50",
        "category": "trend",
        "description": "Exponential Moving Average (50 period)",
        "parameters": {"window": {"default": 50, "min": 2, "max": 500}},
        "min_periods": 50
    },
    "WMA": {
        "name": "WMA",
        "category": "trend",
        "description": "Weighted Moving Average",
        "parameters": {"window": {"default": 20, "min": 2, "max": 500}},
        "min_periods": 20
    },
    "MACD": {
        "name": "MACD",
        "category": "trend",
        "description": "MACD Line",
        "parameters": {"window_slow": {"default": 26, "min": 2, "max": 100}, "window_fast": {"default": 12, "min": 2, "max": 100}, "window_sign": {"default": 9, "min": 2, "max": 100}},
        "min_periods": 26
    },
    "MACD_Signal": {
        "name": "MACD_Signal",
        "category": "trend",
        "description": "MACD Signal Line",
        "parameters": {"window_slow": {"default": 26, "min": 2, "max": 100}, "window_fast": {"default": 12, "min": 2, "max": 100}, "window_sign": {"default": 9, "min": 2, "max": 100}},
        "min_periods": 26
    },
    "MACD_Diff": {
        "name": "MACD_Diff",
        "category": "trend",
        "description": "MACD Histogram",
        "parameters": {"window_slow": {"default": 26, "min": 2, "max": 100}, "window_fast": {"default": 12, "min": 2, "max": 100}, "window_sign": {"default": 9, "min": 2, "max": 100}},
        "min_periods": 26
    },
    "ADX": {
        "name": "ADX",
        "category": "trend",
        "description": "Average Directional Index",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "ADX_Pos": {
        "name": "ADX_Pos",
        "category": "trend",
        "description": "ADX Positive Directional Indicator",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "ADX_Neg": {
        "name": "ADX_Neg",
        "category": "trend",
        "description": "ADX Negative Directional Indicator",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "VI_Pos": {
        "name": "VI_Pos",
        "category": "trend",
        "description": "Vortex Indicator Positive",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "VI_Neg": {
        "name": "VI_Neg",
        "category": "trend",
        "description": "Vortex Indicator Negative",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "TRIX": {
        "name": "TRIX",
        "category": "trend",
        "description": "Triple Exponential Average",
        "parameters": {"window": {"default": 15, "min": 2, "max": 100}},
        "min_periods": 15
    },
    "MassIndex": {
        "name": "MassIndex",
        "category": "trend",
        "description": "Mass Index",
        "parameters": {"window_fast": {"default": 9, "min": 2, "max": 50}, "window_slow": {"default": 25, "min": 2, "max": 100}},
        "min_periods": 25
    },
    "CCI": {
        "name": "CCI",
        "category": "trend",
        "description": "Commodity Channel Index",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "DPO": {
        "name": "DPO",
        "category": "trend",
        "description": "Detrended Price Oscillator",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 20
    },
    "KST": {
        "name": "KST",
        "category": "trend",
        "description": "Know Sure Thing",
        "parameters": {},
        "min_periods": 1
    },
    "KST_Signal": {
        "name": "KST_Signal",
        "category": "trend",
        "description": "KST Signal Line",
        "parameters": {},
        "min_periods": 1
    },
    "Ichimoku_A": {
        "name": "Ichimoku_A",
        "category": "trend",
        "description": "Ichimoku Cloud - Leading Span A",
        "parameters": {},
        "min_periods": 26
    },
    "Ichimoku_B": {
        "name": "Ichimoku_B",
        "category": "trend",
        "description": "Ichimoku Cloud - Leading Span B",
        "parameters": {},
        "min_periods": 52
    },
    "Ichimoku_Base": {
        "name": "Ichimoku_Base",
        "category": "trend",
        "description": "Ichimoku Cloud - Base Line",
        "parameters": {},
        "min_periods": 26
    },
    "Ichimoku_Conversion": {
        "name": "Ichimoku_Conversion",
        "category": "trend",
        "description": "Ichimoku Cloud - Conversion Line",
        "parameters": {},
        "min_periods": 9
    },
    "PSAR": {
        "name": "PSAR",
        "category": "trend",
        "description": "Parabolic SAR",
        "parameters": {"step": {"default": 0.02, "min": 0.01, "max": 0.2}, "max_step": {"default": 0.2, "min": 0.1, "max": 1.0}},
        "min_periods": 1
    },
    "PSAR_Up": {
        "name": "PSAR_Up",
        "category": "trend",
        "description": "Parabolic SAR - Uptrend",
        "parameters": {"step": {"default": 0.02, "min": 0.01, "max": 0.2}, "max_step": {"default": 0.2, "min": 0.1, "max": 1.0}},
        "min_periods": 1
    },
    "PSAR_Down": {
        "name": "PSAR_Down",
        "category": "trend",
        "description": "Parabolic SAR - Downtrend",
        "parameters": {"step": {"default": 0.02, "min": 0.01, "max": 0.2}, "max_step": {"default": 0.2, "min": 0.1, "max": 1.0}},
        "min_periods": 1
    },
    "STC": {
        "name": "STC",
        "category": "trend",
        "description": "Schaff Trend Cycle",
        "parameters": {"window_slow": {"default": 50, "min": 2, "max": 100}, "window_fast": {"default": 23, "min": 2, "max": 100}},
        "min_periods": 50
    },
    "Aroon_Up": {
        "name": "Aroon_Up",
        "category": "trend",
        "description": "Aroon Up",
        "parameters": {"window": {"default": 25, "min": 2, "max": 100}},
        "min_periods": 25
    },
    "Aroon_Down": {
        "name": "Aroon_Down",
        "category": "trend",
        "description": "Aroon Down",
        "parameters": {"window": {"default": 25, "min": 2, "max": 100}},
        "min_periods": 25
    },
    "Aroon_Indicator": {
        "name": "Aroon_Indicator",
        "category": "trend",
        "description": "Aroon Oscillator",
        "parameters": {"window": {"default": 25, "min": 2, "max": 100}},
        "min_periods": 25
    },
    
    # Momentum Indicators (20+)
    "RSI": {
        "name": "RSI",
        "category": "momentum",
        "description": "Relative Strength Index",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "StochRSI": {
        "name": "StochRSI",
        "category": "momentum",
        "description": "Stochastic RSI",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}, "smooth1": {"default": 3, "min": 1, "max": 10}, "smooth2": {"default": 3, "min": 1, "max": 10}},
        "min_periods": 14
    },
    "StochRSI_K": {
        "name": "StochRSI_K",
        "category": "momentum",
        "description": "Stochastic RSI %K",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}, "smooth1": {"default": 3, "min": 1, "max": 10}, "smooth2": {"default": 3, "min": 1, "max": 10}},
        "min_periods": 14
    },
    "StochRSI_D": {
        "name": "StochRSI_D",
        "category": "momentum",
        "description": "Stochastic RSI %D",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}, "smooth1": {"default": 3, "min": 1, "max": 10}, "smooth2": {"default": 3, "min": 1, "max": 10}},
        "min_periods": 14
    },
    "TSI": {
        "name": "TSI",
        "category": "momentum",
        "description": "True Strength Index",
        "parameters": {"window_slow": {"default": 25, "min": 2, "max": 100}, "window_fast": {"default": 13, "min": 2, "max": 100}},
        "min_periods": 25
    },
    "UltimateOscillator": {
        "name": "UltimateOscillator",
        "category": "momentum",
        "description": "Ultimate Oscillator",
        "parameters": {"window1": {"default": 7, "min": 2, "max": 50}, "window2": {"default": 14, "min": 2, "max": 50}, "window3": {"default": 28, "min": 2, "max": 100}},
        "min_periods": 28
    },
    "Stoch_K": {
        "name": "Stoch_K",
        "category": "momentum",
        "description": "Stochastic Oscillator %K",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}, "smooth_window": {"default": 3, "min": 1, "max": 10}},
        "min_periods": 14
    },
    "Stoch_D": {
        "name": "Stoch_D",
        "category": "momentum",
        "description": "Stochastic Oscillator %D",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}, "smooth_window": {"default": 3, "min": 1, "max": 10}},
        "min_periods": 14
    },
    "WilliamsR": {
        "name": "WilliamsR",
        "category": "momentum",
        "description": "Williams %R",
        "parameters": {"lbp": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "AwesomeOscillator": {
        "name": "AwesomeOscillator",
        "category": "momentum",
        "description": "Awesome Oscillator",
        "parameters": {},
        "min_periods": 34
    },
    "KAMA": {
        "name": "KAMA",
        "category": "momentum",
        "description": "Kaufman Adaptive Moving Average",
        "parameters": {"window": {"default": 10, "min": 2, "max": 100}, "pow1": {"default": 2, "min": 1, "max": 10}, "pow2": {"default": 30, "min": 10, "max": 100}},
        "min_periods": 10
    },
    "ROC": {
        "name": "ROC",
        "category": "momentum",
        "description": "Rate of Change",
        "parameters": {"window": {"default": 12, "min": 1, "max": 100}},
        "min_periods": 12
    },
    "PPO": {
        "name": "PPO",
        "category": "momentum",
        "description": "Percentage Price Oscillator",
        "parameters": {"window_slow": {"default": 26, "min": 2, "max": 100}, "window_fast": {"default": 12, "min": 2, "max": 100}, "window_sign": {"default": 9, "min": 2, "max": 100}},
        "min_periods": 26
    },
    "PPO_Signal": {
        "name": "PPO_Signal",
        "category": "momentum",
        "description": "PPO Signal Line",
        "parameters": {"window_slow": {"default": 26, "min": 2, "max": 100}, "window_fast": {"default": 12, "min": 2, "max": 100}, "window_sign": {"default": 9, "min": 2, "max": 100}},
        "min_periods": 26
    },
    "PPO_Hist": {
        "name": "PPO_Hist",
        "category": "momentum",
        "description": "PPO Histogram",
        "parameters": {"window_slow": {"default": 26, "min": 2, "max": 100}, "window_fast": {"default": 12, "min": 2, "max": 100}, "window_sign": {"default": 9, "min": 2, "max": 100}},
        "min_periods": 26
    },
    "PVO": {
        "name": "PVO",
        "category": "momentum",
        "description": "Percentage Volume Oscillator",
        "parameters": {"window_slow": {"default": 26, "min": 2, "max": 100}, "window_fast": {"default": 12, "min": 2, "max": 100}, "window_sign": {"default": 9, "min": 2, "max": 100}},
        "min_periods": 26
    },
    "PVO_Signal": {
        "name": "PVO_Signal",
        "category": "momentum",
        "description": "PVO Signal Line",
        "parameters": {"window_slow": {"default": 26, "min": 2, "max": 100}, "window_fast": {"default": 12, "min": 2, "max": 100}, "window_sign": {"default": 9, "min": 2, "max": 100}},
        "min_periods": 26
    },
    "PVO_Hist": {
        "name": "PVO_Hist",
        "category": "momentum",
        "description": "PVO Histogram",
        "parameters": {"window_slow": {"default": 26, "min": 2, "max": 100}, "window_fast": {"default": 12, "min": 2, "max": 100}, "window_sign": {"default": 9, "min": 2, "max": 100}},
        "min_periods": 26
    },
    
    # Other Indicators (3)
    "DailyReturn": {
        "name": "DailyReturn",
        "category": "others",
        "description": "Daily Return",
        "parameters": {},
        "min_periods": 1
    },
    "DailyLogReturn": {
        "name": "DailyLogReturn",
        "category": "others",
        "description": "Daily Log Return",
        "parameters": {},
        "min_periods": 1
    },
    "CumulativeReturn": {
        "name": "CumulativeReturn",
        "category": "others",
        "description": "Cumulative Return",
        "parameters": {},
        "min_periods": 1
    },
    
    # Statistical Indicators (7)
    "StdDev": {
        "name": "StdDev",
        "category": "statistical",
        "description": "Standard Deviation",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 2
    },
    "ZScore": {
        "name": "ZScore",
        "category": "statistical",
        "description": "Z-Score (Standard Score)",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}},
        "min_periods": 2
    },
    "PriceROC": {
        "name": "PriceROC",
        "category": "statistical",
        "description": "Price Rate of Change",
        "parameters": {"periods": {"default": 1, "min": 1, "max": 50}},
        "min_periods": 2
    },
    "ATRP": {
        "name": "ATRP",
        "category": "statistical",
        "description": "Average True Range Percentage",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "BBWPercent": {
        "name": "BBWPercent",
        "category": "statistical",
        "description": "Bollinger Band Width Percentage",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}, "window_dev": {"default": 2, "min": 1, "max": 5}},
        "min_periods": 20
    },
    "PricePosition": {
        "name": "PricePosition",
        "category": "statistical",
        "description": "Price Position within Bollinger Bands",
        "parameters": {"window": {"default": 20, "min": 2, "max": 100}, "window_dev": {"default": 2, "min": 1, "max": 5}},
        "min_periods": 20
    },
    
    # Pattern Indicators (7)
    "Doji": {
        "name": "Doji",
        "category": "pattern",
        "description": "Doji Candlestick Pattern",
        "parameters": {},
        "min_periods": 1
    },
    "Hammer": {
        "name": "Hammer",
        "category": "pattern",
        "description": "Hammer Candlestick Pattern",
        "parameters": {"body_ratio": {"default": 0.3, "min": 0.1, "max": 0.5}},
        "min_periods": 1
    },
    "BullishEngulfing": {
        "name": "BullishEngulfing",
        "category": "pattern",
        "description": "Bullish Engulfing Pattern",
        "parameters": {"lookback": {"default": 1, "min": 1, "max": 5}},
        "min_periods": 2
    },
    "BearishEngulfing": {
        "name": "BearishEngulfing",
        "category": "pattern",
        "description": "Bearish Engulfing Pattern",
        "parameters": {"lookback": {"default": 1, "min": 1, "max": 5}},
        "min_periods": 2
    },
    "InsideBar": {
        "name": "InsideBar",
        "category": "pattern",
        "description": "Inside Bar Pattern",
        "parameters": {},
        "min_periods": 2
    },
    "OutsideBar": {
        "name": "OutsideBar",
        "category": "pattern",
        "description": "Outside Bar Pattern",
        "parameters": {},
        "min_periods": 2
    }
}


if FASTAPI_AVAILABLE:
    @router.get("/available", response_model=List[IndicatorMetadata])
    async def get_available_indicators():
        """
        Get list of all available indicators with their metadata.
        
        Returns:
            List[IndicatorMetadata]: List of available indicators
        """
        indicators = []
        for indicator_data in AVAILABLE_INDICATORS.values():
            indicators.append(IndicatorMetadata(**indicator_data))
        
        return indicators


    @router.post("/calculate", response_model=IndicatorResponse)
    async def calculate_indicators(request: IndicatorRequest):
        """
        Calculate technical indicators for a symbol.
        
        Args:
            request: IndicatorRequest with symbol, exchange, interval, dates, indicators
        
        Returns:
            IndicatorResponse: Calculated indicator values
        
        Example:
            POST /api/v1/indicators/calculate
            {
                "symbol": "NIFTY",
                "exchange": "NSE",
                "interval": "5m",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "indicators": ["RSI", "MACD", "EMA_20"],
                "indicator_params": {
                    "RSI": {"period": 14}
                }
            }
        """
        try:
            # Validate inputs
            is_valid, error = validate_symbol(request.symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            is_valid, error = validate_exchange(request.exchange)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            is_valid, error = validate_timeframe_input(request.interval)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            if request.start_date and request.end_date:
                is_valid, error = validate_date_range(
                    request.start_date, request.end_date
                )
                if not is_valid:
                    raise HTTPException(status_code=400, detail=error)
            
            logger.info(
                f"Calculating indicators for {request.symbol} {request.exchange} "
                f"{request.interval}"
            )
            
            # Fetch market data
            market_service = get_market_data_service()
            df = await market_service.fetch_historical_candles(
                symbol=request.symbol,
                exchange=request.exchange,
                interval=request.interval,
                start_date=request.start_date or "2024-01-01",
                end_date=request.end_date or "2024-12-31"
            )
            
            if df.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for {request.symbol}"
                )
            
            # Calculate indicators
            indicator_service = get_indicator_service()
            
            if request.indicators:
                # Calculate specific indicators
                indicators = indicator_service.calculate_specific_indicators(
                    df,
                    request.indicators,
                    request.indicator_params
                )
            else:
                # Calculate all indicators
                indicators = indicator_service.calculate_all_indicators(
                    df,
                    request.indicator_params
                )
            
            # Format response
            formatted_indicators = indicator_service.format_indicators_for_response(
                indicators
            )
            
            response = IndicatorResponse(
                symbol=request.symbol,
                timeframe=request.interval,
                indicators=formatted_indicators,
                timestamps=df['timestamp'].tolist(),
                metadata={
                    "exchange": request.exchange,
                    "start_date": request.start_date,
                    "end_date": request.end_date,
                    "candle_count": len(df),
                    "indicator_count": len(formatted_indicators)
                }
            )
            
            logger.info(
                f"Calculated {len(formatted_indicators)} indicators "
                f"with {len(df)} candles"
            )
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.post("/multi-timeframe", response_model=MultiTimeframeIndicators)
    async def calculate_multi_timeframe_indicators(
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        timeframes: List[str] = Query(..., description="List of timeframes"),
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        indicators: Optional[List[str]] = Query(None, description="Specific indicators")
    ):
        """
        Calculate indicators across multiple timeframes.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            timeframes: List of timeframes (e.g., ["1m", "5m", "1h"])
            start_date: Start date
            end_date: End date
            indicators: Optional list of specific indicators
        
        Returns:
            MultiTimeframeIndicators: Indicators for each timeframe
        
        Example:
            POST /api/v1/indicators/multi-timeframe?symbol=NIFTY&exchange=NSE&timeframes=1m&timeframes=5m
        """
        try:
            # Validate inputs
            is_valid, error = validate_symbol(symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            is_valid, error = validate_exchange(exchange)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(
                f"Calculating multi-timeframe indicators for {symbol} {exchange}"
            )
            
            # Calculate for each timeframe
            timeframe_results = {}
            market_service = get_market_data_service()
            indicator_service = get_indicator_service()
            
            for timeframe in timeframes:
                # Validate timeframe
                is_valid, error = validate_timeframe_input(timeframe)
                if not is_valid:
                    logger.warning(f"Invalid timeframe {timeframe}: {error}")
                    continue
                
                try:
                    # Fetch data
                    df = await market_service.fetch_historical_candles(
                        symbol=symbol,
                        exchange=exchange,
                        interval=timeframe,
                        start_date=start_date or "2024-01-01",
                        end_date=end_date or "2024-12-31"
                    )
                    
                    if df.empty:
                        continue
                    
                    # Calculate indicators
                    if indicators:
                        calculated = indicator_service.calculate_specific_indicators(
                            df, indicators
                        )
                    else:
                        calculated = indicator_service.calculate_all_indicators(df)
                    
                    # Format response
                    formatted = indicator_service.format_indicators_for_response(
                        calculated
                    )
                    
                    timeframe_results[timeframe] = IndicatorResponse(
                        symbol=symbol,
                        timeframe=timeframe,
                        indicators=formatted,
                        timestamps=df['timestamp'].tolist(),
                        metadata={
                            "exchange": exchange,
                            "candle_count": len(df)
                        }
                    )
                
                except Exception as e:
                    logger.error(f"Error for timeframe {timeframe}: {e}")
                    continue
            
            if not timeframe_results:
                raise HTTPException(
                    status_code=404,
                    detail="No data found for any timeframe"
                )
            
            response = MultiTimeframeIndicators(
                symbol=symbol,
                exchange=exchange,
                timeframes=timeframe_results,
                metadata={
                    "timeframe_count": len(timeframe_results),
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            logger.info(
                f"Calculated indicators for {len(timeframe_results)} timeframes"
            )
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in multi-timeframe calculation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/latest/{symbol}")
    async def get_latest_indicators(
        symbol: str,
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query("5m", description="Timeframe"),
        indicators: Optional[List[str]] = Query(None, description="Specific indicators")
    ):
        """
        Get latest indicator values for a symbol.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe
            indicators: Optional list of specific indicators
        
        Returns:
            Dict: Latest indicator values
        
        Example:
            GET /api/v1/indicators/latest/NIFTY?exchange=NSE&interval=5m&indicators=RSI&indicators=MACD
        """
        try:
            # Validate inputs
            is_valid, error = validate_symbol(symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            is_valid, error = validate_exchange(exchange)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            is_valid, error = validate_timeframe_input(interval)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(f"Getting latest indicators for {symbol} {exchange} {interval}")
            
            # Fetch recent data (last 100 candles should be enough)
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            market_service = get_market_data_service()
            df = await market_service.fetch_historical_candles(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start_date=start_date,
                end_date=end_date
            )
            
            if df.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for {symbol}"
                )
            
            # Calculate indicators
            indicator_service = get_indicator_service()
            
            if indicators:
                calculated = indicator_service.calculate_specific_indicators(
                    df, indicators
                )
            else:
                calculated = indicator_service.calculate_all_indicators(df)
            
            # Get latest values (last non-NaN value)
            latest_values = {}
            for name, series in calculated.items():
                # Get last non-NaN value
                non_nan = series.dropna()
                if len(non_nan) > 0:
                    latest_values[name] = float(non_nan.iloc[-1])
            
            return {
                "symbol": symbol,
                "exchange": exchange,
                "timeframe": interval,
                "timestamp": df['timestamp'].iloc[-1].isoformat(),
                "indicators": latest_values,
                "metadata": {
                    "candles_used": len(df)
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting latest indicators: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
