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


# Available indicators metadata
AVAILABLE_INDICATORS = {
    "RSI": {
        "name": "RSI",
        "category": "momentum",
        "description": "Relative Strength Index",
        "parameters": {"period": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "MACD": {
        "name": "MACD",
        "category": "trend",
        "description": "Moving Average Convergence Divergence",
        "parameters": {
            "window_slow": {"default": 26, "min": 2, "max": 100},
            "window_fast": {"default": 12, "min": 2, "max": 100},
            "window_sign": {"default": 9, "min": 2, "max": 100}
        },
        "min_periods": 26
    },
    "EMA": {
        "name": "EMA",
        "category": "trend",
        "description": "Exponential Moving Average",
        "parameters": {"period": {"default": 20, "min": 2, "max": 500}},
        "min_periods": 20
    },
    "SMA": {
        "name": "SMA",
        "category": "trend",
        "description": "Simple Moving Average",
        "parameters": {"period": {"default": 20, "min": 2, "max": 500}},
        "min_periods": 20
    },
    "BB": {
        "name": "BollingerBands",
        "category": "volatility",
        "description": "Bollinger Bands",
        "parameters": {
            "window": {"default": 20, "min": 2, "max": 100},
            "window_dev": {"default": 2, "min": 1, "max": 5}
        },
        "min_periods": 20
    },
    "ATR": {
        "name": "ATR",
        "category": "volatility",
        "description": "Average True Range",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "ADX": {
        "name": "ADX",
        "category": "trend",
        "description": "Average Directional Index",
        "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
        "min_periods": 14
    },
    "Stochastic": {
        "name": "StochasticOscillator",
        "category": "momentum",
        "description": "Stochastic Oscillator",
        "parameters": {
            "window": {"default": 14, "min": 2, "max": 100},
            "smooth_window": {"default": 3, "min": 1, "max": 10}
        },
        "min_periods": 14
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
