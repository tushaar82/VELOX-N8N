"""
API endpoints for categorized technical indicators.
Provides separate endpoints for each indicator category.
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
    router = APIRouter(prefix="/indicators", tags=["indicators-categorized"])
else:
    router = None

# Category mappings
VOLUME_INDICATORS = [
    "MFI", "ADI", "OBV", "CMF", "ForceIndex", 
    "EaseOfMovement", "VPT", "NVI", "VWAP"
]

VOLATILITY_INDICATORS = [
    "ATR", "BB_High", "BB_Mid", "BB_Low", "BB_Width", "BB_Percent",
    "KC_High", "KC_Mid", "KC_Low", "DC_High", "DC_Mid", "DC_Low",
    "UlcerIndex"
]

TREND_INDICATORS = [
    "SMA_10", "SMA_20", "SMA_50", "SMA_200",
    "EMA_12", "EMA_20", "EMA_26", "EMA_50", "WMA",
    "MACD", "MACD_Signal", "MACD_Diff",
    "ADX", "ADX_Pos", "ADX_Neg",
    "VI_Pos", "VI_Neg",
    "TRIX", "MassIndex", "CCI", "DPO",
    "KST", "KST_Signal",
    "Ichimoku_A", "Ichimoku_B", "Ichimoku_Base", "Ichimoku_Conversion",
    "PSAR", "PSAR_Up", "PSAR_Down",
    "STC", "Aroon_Up", "Aroon_Down", "Aroon_Indicator"
]

MOMENTUM_INDICATORS = [
    "RSI", "StochRSI", "StochRSI_K", "StochRSI_D",
    "TSI", "UltimateOscillator",
    "Stoch_K", "Stoch_D", "WilliamsR", "AwesomeOscillator",
    "KAMA", "ROC",
    "PPO", "PPO_Signal", "PPO_Hist",
    "PVO", "PVO_Signal", "PVO_Hist"
]

OTHER_INDICATORS = [
    "DailyReturn", "DailyLogReturn", "CumulativeReturn"
]

STATISTICAL_INDICATORS = [
    "StdDev", "ZScore", "PriceROC", "ATRP", "BBWPercent", "PricePosition"
]

PATTERN_INDICATORS = [
    "Doji", "Hammer", "BullishEngulfing", "BearishEngulfing",
    "InsideBar", "OutsideBar"
]

ALL_INDICATORS = (
    VOLUME_INDICATORS + VOLATILITY_INDICATORS +
    TREND_INDICATORS + MOMENTUM_INDICATORS +
    STATISTICAL_INDICATORS + PATTERN_INDICATORS + OTHER_INDICATORS
)


if FASTAPI_AVAILABLE:
    @router.get("/volume", response_model=List[IndicatorMetadata])
    async def get_volume_indicators():
        """Get list of available volume indicators."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        indicators = []
        for indicator_name in VOLUME_INDICATORS:
            if indicator_name in AVAILABLE_INDICATORS:
                indicators.append(IndicatorMetadata(**AVAILABLE_INDICATORS[indicator_name]))
        
        return indicators

    @router.get("/volatility", response_model=List[IndicatorMetadata])
    async def get_volatility_indicators():
        """Get list of available volatility indicators."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        indicators = []
        for indicator_name in VOLATILITY_INDICATORS:
            if indicator_name in AVAILABLE_INDICATORS:
                indicators.append(IndicatorMetadata(**AVAILABLE_INDICATORS[indicator_name]))
        
        return indicators

    @router.get("/trend", response_model=List[IndicatorMetadata])
    async def get_trend_indicators():
        """Get list of available trend indicators."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        indicators = []
        for indicator_name in TREND_INDICATORS:
            if indicator_name in AVAILABLE_INDICATORS:
                indicators.append(IndicatorMetadata(**AVAILABLE_INDICATORS[indicator_name]))
        
        return indicators

    @router.get("/momentum", response_model=List[IndicatorMetadata])
    async def get_momentum_indicators():
        """Get list of available momentum indicators."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        indicators = []
        for indicator_name in MOMENTUM_INDICATORS:
            if indicator_name in AVAILABLE_INDICATORS:
                indicators.append(IndicatorMetadata(**AVAILABLE_INDICATORS[indicator_name]))
        
        return indicators

    @router.get("/statistical", response_model=List[IndicatorMetadata])
    async def get_statistical_indicators():
        """Get list of available statistical indicators."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        indicators = []
        for indicator_name in STATISTICAL_INDICATORS:
            if indicator_name in AVAILABLE_INDICATORS:
                indicators.append(IndicatorMetadata(**AVAILABLE_INDICATORS[indicator_name]))
        
        return indicators

    @router.get("/patterns", response_model=List[IndicatorMetadata])
    async def get_pattern_indicators():
        """Get list of available pattern indicators."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        indicators = []
        for indicator_name in PATTERN_INDICATORS:
            if indicator_name in AVAILABLE_INDICATORS:
                indicators.append(IndicatorMetadata(**AVAILABLE_INDICATORS[indicator_name]))
        
        return indicators

    @router.get("/others", response_model=List[IndicatorMetadata])
    async def get_other_indicators():
        """Get list of available other indicators."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        indicators = []
        for indicator_name in OTHER_INDICATORS:
            if indicator_name in AVAILABLE_INDICATORS:
                indicators.append(IndicatorMetadata(**AVAILABLE_INDICATORS[indicator_name]))
        
        return indicators

    @router.post("/volume/{indicator}", response_model=IndicatorResponse)
    async def calculate_volume_indicator(
        indicator: str,
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query(..., description="Timeframe"),
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        params: Optional[Dict] = None
    ):
        """Calculate a specific volume indicator."""
        if indicator not in VOLUME_INDICATORS:
            raise HTTPException(
                status_code=400,
                detail=f"Indicator '{indicator}' not found in volume category"
            )
        
        return await _calculate_single_indicator(
            indicator, symbol, exchange, interval, start_date, end_date, params
        )

    @router.post("/volatility/{indicator}", response_model=IndicatorResponse)
    async def calculate_volatility_indicator(
        indicator: str,
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query(..., description="Timeframe"),
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        params: Optional[Dict] = None
    ):
        """Calculate a specific volatility indicator."""
        if indicator not in VOLATILITY_INDICATORS:
            raise HTTPException(
                status_code=400,
                detail=f"Indicator '{indicator}' not found in volatility category"
            )
        
        return await _calculate_single_indicator(
            indicator, symbol, exchange, interval, start_date, end_date, params
        )

    @router.post("/trend/{indicator}", response_model=IndicatorResponse)
    async def calculate_trend_indicator(
        indicator: str,
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query(..., description="Timeframe"),
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        params: Optional[Dict] = None
    ):
        """Calculate a specific trend indicator."""
        if indicator not in TREND_INDICATORS:
            raise HTTPException(
                status_code=400,
                detail=f"Indicator '{indicator}' not found in trend category"
            )
        
        return await _calculate_single_indicator(
            indicator, symbol, exchange, interval, start_date, end_date, params
        )

    @router.post("/momentum/{indicator}", response_model=IndicatorResponse)
    async def calculate_momentum_indicator(
        indicator: str,
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query(..., description="Timeframe"),
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        params: Optional[Dict] = None
    ):
        """Calculate a specific momentum indicator."""
        if indicator not in MOMENTUM_INDICATORS:
            raise HTTPException(
                status_code=400,
                detail=f"Indicator '{indicator}' not found in momentum category"
            )
        
        return await _calculate_single_indicator(
            indicator, symbol, exchange, interval, start_date, end_date, params
        )

    @router.post("/others/{indicator}", response_model=IndicatorResponse)
    async def calculate_other_indicator(
        indicator: str,
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query(..., description="Timeframe"),
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        params: Optional[Dict] = None
    ):
        """Calculate a specific other indicator."""
        if indicator not in OTHER_INDICATORS:
            raise HTTPException(
                status_code=400,
                detail=f"Indicator '{indicator}' not found in others category"
            )
        
        return await _calculate_single_indicator(
            indicator, symbol, exchange, interval, start_date, end_date, params
        )


async def _calculate_single_indicator(
    indicator: str,
    symbol: str,
    exchange: str,
    interval: str,
    start_date: Optional[str],
    end_date: Optional[str],
    params: Optional[Dict]
) -> IndicatorResponse:
    """
    Helper function to calculate a single indicator.
    
    Args:
        indicator: Indicator name
        symbol: Trading symbol
        exchange: Exchange code
        interval: Timeframe
        start_date: Start date
        end_date: End date
        params: Optional parameters
    
    Returns:
        IndicatorResponse: Calculated indicator values
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
        
        if start_date and end_date:
            is_valid, error = validate_date_range(start_date, end_date)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
        
        logger.info(
            f"Calculating {indicator} for {symbol} {exchange} {interval}"
        )
        
        # Fetch market data
        market_service = get_market_data_service()
        df = await market_service.fetch_historical_candles(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start_date=start_date or "2024-01-01",
            end_date=end_date or "2024-12-31"
        )
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {symbol}"
            )
        
        # Calculate indicator
        indicator_service = get_indicator_service()
        
        # Build indicator params dict
        indicator_params = {indicator: params} if params else {}
        
        indicators = indicator_service.calculate_specific_indicators(
            df,
            [indicator],
            indicator_params
        )
        
        # Format response
        formatted_indicators = indicator_service.format_indicators_for_response(
            indicators
        )
        
        response = IndicatorResponse(
            symbol=symbol,
            timeframe=interval,
            indicators=formatted_indicators,
            timestamps=df['timestamp'].tolist(),
            metadata={
                "exchange": exchange,
                "start_date": start_date,
                "end_date": end_date,
                "candle_count": len(df),
                "indicator_count": len(formatted_indicators),
                "category": _get_indicator_category(indicator)
            }
        )
        
        logger.info(
            f"Calculated {indicator} with {len(df)} candles"
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating {indicator}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _get_indicator_category(indicator: str) -> str:
    """Get the category of an indicator."""
    if indicator in VOLUME_INDICATORS:
        return "volume"
    elif indicator in VOLATILITY_INDICATORS:
        return "volatility"
    elif indicator in TREND_INDICATORS:
        return "trend"
    elif indicator in MOMENTUM_INDICATORS:
        return "momentum"
    elif indicator in OTHER_INDICATORS:
        return "others"
    else:
        return "unknown"