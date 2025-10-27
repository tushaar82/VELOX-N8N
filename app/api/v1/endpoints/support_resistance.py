"""
API endpoints for support and resistance level calculations.
"""

from typing import Optional

try:
    from fastapi import APIRouter, HTTPException, Query
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None
    HTTPException = Exception
    Query = None

from app.core.logging import get_logger
from app.schemas.indicators import SupportResistanceResponse
from app.services.market_data import get_market_data_service
from app.services.support_resistance import get_support_resistance_service
from app.utils.validators import (
    validate_symbol,
    validate_exchange,
    validate_timeframe_input,
    validate_positive_integer
)

logger = get_logger(__name__)

# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/support-resistance", tags=["support-resistance"])
else:
    router = None


if FASTAPI_AVAILABLE:
    @router.get("/{symbol}", response_model=SupportResistanceResponse)
    async def get_support_resistance(
        symbol: str,
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query("1d", description="Timeframe for analysis"),
        lookback_days: int = Query(90, description="Number of days to analyze", ge=7, le=365),
        max_levels: int = Query(5, description="Maximum levels to return", ge=1, le=20),
        window: int = Query(3, description="Peak detection window", ge=2, le=10),
        prominence_mult: float = Query(0.5, description="ATR multiplier for prominence", ge=0.1, le=2.0),
        atr_mult: float = Query(1.0, description="ATR multiplier for clustering", ge=0.1, le=5.0)
    ):
        """
        Calculate support and resistance levels for a symbol.
        
        Uses advanced algorithm with:
        - Swing extrema detection
        - ATR-based dynamic prominence
        - Recency and volume weighting
        - Level clustering
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe (default: 1d)
            lookback_days: Days to analyze (default: 90)
            max_levels: Max levels to return (default: 5)
            window: Peak detection window (default: 3)
            prominence_mult: ATR multiplier for prominence (default: 0.5)
            atr_mult: ATR multiplier for clustering (default: 1.0)
        
        Returns:
            SupportResistanceResponse: Support and resistance levels
        
        Example:
            GET /api/v1/support-resistance/NIFTY?exchange=NSE&interval=1d&lookback_days=90
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
            
            logger.info(
                f"Calculating S/R for {symbol} {exchange} {interval} "
                f"(lookback: {lookback_days} days)"
            )
            
            # Calculate date range
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Fetch market data
            market_service = get_market_data_service()
            df = await market_service.fetch_historical_candles(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            
            if df.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for {symbol}"
                )
            
            if len(df) < 20:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient data: {len(df)} candles (minimum 20 required)"
                )
            
            # Calculate support/resistance
            sr_service = get_support_resistance_service()
            response = sr_service.compute_support_resistance(
                df,
                params={
                    'symbol': symbol,
                    'timeframe': interval,
                    'window': window,
                    'prominence_mult': prominence_mult,
                    'atr_mult': atr_mult,
                    'max_levels': max_levels
                }
            )
            
            logger.info(
                f"Found {len(response.support_levels)} support and "
                f"{len(response.resistance_levels)} resistance levels"
            )
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error calculating S/R: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/{symbol}/pivots")
    async def get_pivot_points(
        symbol: str,
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query("1d", description="Timeframe"),
        method: str = Query("standard", description="Pivot method (standard, fibonacci, woodie)")
    ):
        """
        Calculate pivot points for a symbol.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe
            method: Pivot calculation method
        
        Returns:
            Dict: Pivot points (PP, R1, R2, R3, S1, S2, S3)
        
        Example:
            GET /api/v1/support-resistance/NIFTY/pivots?exchange=NSE&method=standard
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
            
            if method not in ["standard", "fibonacci", "woodie"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid method: {method}. Use: standard, fibonacci, or woodie"
                )
            
            logger.info(f"Calculating {method} pivots for {symbol} {exchange} {interval}")
            
            # Fetch recent data
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            market_service = get_market_data_service()
            df = await market_service.fetch_historical_candles(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            
            if df.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for {symbol}"
                )
            
            # Calculate pivots
            sr_service = get_support_resistance_service()
            pivots = sr_service.calculate_pivot_points(df, method=method)
            
            return {
                "symbol": symbol,
                "exchange": exchange,
                "timeframe": interval,
                "method": method,
                "pivots": pivots,
                "timestamp": df['timestamp'].iloc[-1].isoformat(),
                "metadata": {
                    "high": float(df.iloc[-1]['high']),
                    "low": float(df.iloc[-1]['low']),
                    "close": float(df.iloc[-1]['close'])
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error calculating pivots: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/{symbol}/nearest")
    async def get_nearest_levels(
        symbol: str,
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query("1d", description="Timeframe"),
        count: int = Query(3, description="Number of nearest levels", ge=1, le=10)
    ):
        """
        Get nearest support and resistance levels to current price.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe
            count: Number of levels above and below
        
        Returns:
            Dict: Nearest support and resistance levels
        
        Example:
            GET /api/v1/support-resistance/NIFTY/nearest?exchange=NSE&count=3
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
            
            logger.info(f"Getting nearest levels for {symbol} {exchange}")
            
            # Calculate date range
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            # Fetch market data
            market_service = get_market_data_service()
            df = await market_service.fetch_historical_candles(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            
            if df.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for {symbol}"
                )
            
            # Calculate support/resistance
            sr_service = get_support_resistance_service()
            response = sr_service.compute_support_resistance(
                df,
                params={
                    'symbol': symbol,
                    'timeframe': interval,
                    'max_levels': 20  # Get more levels to find nearest
                }
            )
            
            current_price = response.current_price
            
            # Find nearest support levels (below current price)
            support_below = [
                level for level in response.support_levels
                if level.price < current_price
            ]
            support_below.sort(key=lambda x: abs(x.price - current_price))
            nearest_support = support_below[:count]
            
            # Find nearest resistance levels (above current price)
            resistance_above = [
                level for level in response.resistance_levels
                if level.price > current_price
            ]
            resistance_above.sort(key=lambda x: abs(x.price - current_price))
            nearest_resistance = resistance_above[:count]
            
            return {
                "symbol": symbol,
                "exchange": exchange,
                "timeframe": interval,
                "current_price": current_price,
                "nearest_support": [
                    {
                        "price": level.price,
                        "distance": current_price - level.price,
                        "distance_pct": ((current_price - level.price) / current_price) * 100,
                        "strength": level.strength,
                        "touches": level.touches
                    }
                    for level in nearest_support
                ],
                "nearest_resistance": [
                    {
                        "price": level.price,
                        "distance": level.price - current_price,
                        "distance_pct": ((level.price - current_price) / current_price) * 100,
                        "strength": level.strength,
                        "touches": level.touches
                    }
                    for level in nearest_resistance
                ],
                "metadata": {
                    "total_support_levels": len(response.support_levels),
                    "total_resistance_levels": len(response.resistance_levels),
                    "tolerance": response.tolerance
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting nearest levels: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
