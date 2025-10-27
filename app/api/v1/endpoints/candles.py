"""
API endpoints for historical candle data.
"""

from typing import List, Optional

try:
    from fastapi import APIRouter, HTTPException, Query
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None
    HTTPException = Exception
    Query = None

from app.core.logging import get_logger
from app.schemas.candles import CandleRequest, CandleResponse, MultiTimeframeCandles
from app.services.market_data import get_market_data_service
from app.utils.validators import (
    validate_symbol,
    validate_exchange,
    validate_timeframe_input,
    validate_date_range
)

logger = get_logger(__name__)

# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/candles", tags=["candles"])
else:
    router = None


if FASTAPI_AVAILABLE:
    @router.post("/", response_model=CandleResponse)
    async def get_candles(request: CandleRequest):
        """
        Get historical candle data for a symbol.
        
        Args:
            request: CandleRequest with symbol, exchange, interval, dates
        
        Returns:
            CandleResponse: Historical candles with optional current candle
        
        Example:
            POST /api/v1/candles/
            {
                "symbol": "NIFTY",
                "exchange": "NSE",
                "interval": "5m",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "include_current": true
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
            
            is_valid, error = validate_date_range(
                request.start_date, request.end_date
            )
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(
                f"Fetching candles for {request.symbol} {request.exchange} "
                f"{request.interval} from {request.start_date} to {request.end_date}"
            )
            
            # Fetch market data
            market_service = get_market_data_service()
            df, current_candle_dict = await market_service.fetch_candles_with_current(
                symbol=request.symbol,
                exchange=request.exchange,
                interval=request.interval,
                start_date=request.start_date,
                end_date=request.end_date,
                include_current=request.include_current
            )
            
            if df.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for {request.symbol}"
                )
            
            # Convert to Candle models
            candles = market_service.dataframe_to_candles(
                df, request.symbol, request.interval
            )
            
            # Convert current candle if present
            current_candle = None
            if current_candle_dict:
                from app.schemas.candles import Candle
                current_candle = Candle(
                    symbol=request.symbol,
                    timestamp=current_candle_dict['timestamp'],
                    open=current_candle_dict['open'],
                    high=current_candle_dict['high'],
                    low=current_candle_dict['low'],
                    close=current_candle_dict['close'],
                    volume=current_candle_dict['volume'],
                    timeframe=request.interval
                )
            
            response = CandleResponse(
                candles=candles,
                current_candle=current_candle,
                metadata={
                    "symbol": request.symbol,
                    "exchange": request.exchange,
                    "interval": request.interval,
                    "count": len(candles),
                    "start_date": request.start_date,
                    "end_date": request.end_date
                }
            )
            
            logger.info(f"Returning {len(candles)} candles")
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching candles: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/{symbol}")
    async def get_candles_simple(
        symbol: str,
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query("5m", description="Timeframe"),
        start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
        end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
        include_current: bool = Query(True, description="Include current forming candle")
    ):
        """
        Get historical candles (simplified GET endpoint).
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe
            start_date: Start date
            end_date: End date
            include_current: Include current candle
        
        Returns:
            CandleResponse: Historical candles
        
        Example:
            GET /api/v1/candles/NIFTY?exchange=NSE&interval=5m&start_date=2024-01-01&end_date=2024-01-31
        """
        request = CandleRequest(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            include_current=include_current
        )
        return await get_candles(request)


    @router.get("/{symbol}/latest")
    async def get_latest_candle(
        symbol: str,
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query("5m", description="Timeframe")
    ):
        """
        Get the latest candle for a symbol.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe
        
        Returns:
            Dict: Latest candle data
        
        Example:
            GET /api/v1/candles/NIFTY/latest?exchange=NSE&interval=5m
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
            
            logger.info(f"Fetching latest candle for {symbol} {exchange} {interval}")
            
            # Fetch recent data
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
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
            
            # Get latest candle
            latest = df.iloc[-1]
            
            return {
                "symbol": symbol,
                "exchange": exchange,
                "timeframe": interval,
                "timestamp": latest['timestamp'].isoformat(),
                "open": float(latest['open']),
                "high": float(latest['high']),
                "low": float(latest['low']),
                "close": float(latest['close']),
                "volume": float(latest['volume'])
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching latest candle: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.post("/multi-timeframe", response_model=MultiTimeframeCandles)
    async def get_multi_timeframe_candles(
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        timeframes: List[str] = Query(..., description="List of timeframes"),
        start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
        end_date: str = Query(..., description="End date (YYYY-MM-DD)")
    ):
        """
        Get candles across multiple timeframes.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            timeframes: List of timeframes
            start_date: Start date
            end_date: End date
        
        Returns:
            MultiTimeframeCandles: Candles for each timeframe
        
        Example:
            POST /api/v1/candles/multi-timeframe?symbol=NIFTY&exchange=NSE&timeframes=1m&timeframes=5m&start_date=2024-01-01&end_date=2024-01-31
        """
        try:
            # Validate inputs
            is_valid, error = validate_symbol(symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            is_valid, error = validate_exchange(exchange)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            is_valid, error = validate_date_range(start_date, end_date)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(
                f"Fetching multi-timeframe candles for {symbol} {exchange}"
            )
            
            # Fetch candles for each timeframe
            timeframe_candles = {}
            market_service = get_market_data_service()
            
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
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if df.empty:
                        continue
                    
                    # Convert to Candle models
                    candles = market_service.dataframe_to_candles(
                        df, symbol, timeframe
                    )
                    
                    timeframe_candles[timeframe] = candles
                
                except Exception as e:
                    logger.error(f"Error for timeframe {timeframe}: {e}")
                    continue
            
            if not timeframe_candles:
                raise HTTPException(
                    status_code=404,
                    detail="No data found for any timeframe"
                )
            
            response = MultiTimeframeCandles(
                symbol=symbol,
                exchange=exchange,
                timeframes=timeframe_candles,
                metadata={
                    "timeframe_count": len(timeframe_candles),
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            logger.info(
                f"Returning candles for {len(timeframe_candles)} timeframes"
            )
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in multi-timeframe fetch: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
