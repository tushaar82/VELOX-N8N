"""
API endpoints for advanced technical analysis.
Provides pivot points, Fibonacci retracements, and pattern recognition.
"""

from typing import Dict, List, Optional, Tuple

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

import numpy as np
import pandas as pd

from app.core.logging import get_logger
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
    router = APIRouter(prefix="/analysis", tags=["technical-analysis"])
else:
    router = None


if FASTAPI_AVAILABLE:
    @router.post("/pivot-points")
    async def calculate_pivot_points(
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query(..., description="Timeframe"),
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        pivot_type: str = Query("standard", description="Pivot type: standard, fibonacci, woodie, camarilla"),
        lookback: int = Query(20, description="Number of periods for calculation")
    ):
        """
        Calculate pivot points for support/resistance analysis.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe
            start_date: Start date
            end_date: End date
            pivot_type: Type of pivot calculation
            lookback: Number of periods to look back
        
        Returns:
            Dict: Pivot points with support/resistance levels
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
            
            logger.info(f"Calculating {pivot_type} pivot points for {symbol}")
            
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
            
            # Calculate pivot points
            pivots = _calculate_pivots(df, pivot_type, lookback)
            
            return {
                "symbol": symbol,
                "exchange": exchange,
                "timeframe": interval,
                "pivot_type": pivot_type,
                "lookback": lookback,
                "current_price": float(df['close'].iloc[-1]),
                "pivots": pivots,
                "timestamp": df['timestamp'].iloc[-1].isoformat(),
                "metadata": {
                    "candles_used": len(df),
                    "calculation_method": pivot_type
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error calculating pivot points: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/fibonacci")
    async def calculate_fibonacci_retracements(
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query(..., description="Timeframe"),
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        swing_high: Optional[float] = Query(None, description="Manual swing high (auto if None)"),
        swing_low: Optional[float] = Query(None, description="Manual swing low (auto if None)"),
        trend: str = Query("up", description="Trend direction: up, down")
    ):
        """
        Calculate Fibonacci retracement levels.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe
            start_date: Start date
            end_date: End date
            swing_high: Manual swing high (optional)
            swing_low: Manual swing low (optional)
            trend: Trend direction
        
        Returns:
            Dict: Fibonacci retracement levels
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
            
            logger.info(f"Calculating Fibonacci retracements for {symbol}")
            
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
            
            # Calculate Fibonacci levels
            fib_levels = _calculate_fibonacci(
                df, swing_high, swing_low, trend
            )
            
            return {
                "symbol": symbol,
                "exchange": exchange,
                "timeframe": interval,
                "trend": trend,
                "swing_high": fib_levels["swing_high"],
                "swing_low": fib_levels["swing_low"],
                "current_price": float(df['close'].iloc[-1]),
                "retracement_levels": fib_levels["retracements"],
                "extension_levels": fib_levels["extensions"],
                "timestamp": df['timestamp'].iloc[-1].isoformat(),
                "metadata": {
                    "candles_used": len(df),
                    "auto_detect": swing_high is None or swing_low is None
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error calculating Fibonacci: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/price-patterns")
    async def detect_price_patterns(
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query(..., description="Timeframe"),
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        pattern_types: Optional[List[str]] = Query(None, description="Pattern types to detect"),
        lookback: int = Query(100, description="Number of candles to analyze")
    ):
        """
        Detect chart patterns in price data.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe
            start_date: Start date
            end_date: End date
            pattern_types: Types of patterns to detect
            lookback: Number of candles to analyze
        
        Returns:
            Dict: Detected patterns with confidence scores
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
            
            logger.info(f"Detecting price patterns for {symbol}")
            
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
            
            # Detect patterns
            patterns = _detect_patterns(df, pattern_types or [], lookback)
            
            return {
                "symbol": symbol,
                "exchange": exchange,
                "timeframe": interval,
                "patterns_detected": patterns,
                "current_price": float(df['close'].iloc[-1]),
                "timestamp": df['timestamp'].iloc[-1].isoformat(),
                "metadata": {
                    "candles_analyzed": min(len(df), lookback),
                    "pattern_types": pattern_types or ["all"]
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/market-sentiment")
    async def analyze_market_sentiment(
        symbol: str = Query(..., description="Trading symbol"),
        exchange: str = Query(..., description="Exchange code"),
        interval: str = Query(..., description="Timeframe"),
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        lookback: int = Query(50, description="Number of periods for analysis")
    ):
        """
        Analyze market sentiment using multiple indicators.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe
            start_date: Start date
            end_date: End date
            lookback: Number of periods for analysis
        
        Returns:
            Dict: Market sentiment analysis
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
            
            logger.info(f"Analyzing market sentiment for {symbol}")
            
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
            
            # Analyze sentiment
            sentiment = _analyze_sentiment(df.tail(lookback))
            
            return {
                "symbol": symbol,
                "exchange": exchange,
                "timeframe": interval,
                "sentiment": sentiment,
                "current_price": float(df['close'].iloc[-1]),
                "timestamp": df['timestamp'].iloc[-1].isoformat(),
                "metadata": {
                    "periods_analyzed": min(len(df), lookback),
                    "indicators_used": sentiment.get("indicators_used", [])
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


def _calculate_pivots(df: pd.DataFrame, pivot_type: str, lookback: int) -> Dict:
    """Calculate pivot points based on type."""
    recent_df = df.tail(lookback)
    high = recent_df['high'].max()
    low = recent_df['low'].min()
    close = recent_df['close'].iloc[-1]
    open_price = recent_df['open'].iloc[0]
    
    pivots = {}
    
    if pivot_type == "standard":
        # Standard pivot points
        pp = (high + low + close) / 3
        pivots = {
            "pivot": pp,
            "support_1": (2 * pp) - high,
            "support_2": pp - (high - low),
            "resistance_1": (2 * pp) - low,
            "resistance_2": pp + (high - low)
        }
    
    elif pivot_type == "fibonacci":
        # Fibonacci pivot points
        pp = (high + low + close) / 3
        pivots = {
            "pivot": pp,
            "support_1": pp - 0.382 * (high - low),
            "support_2": pp - 0.618 * (high - low),
            "resistance_1": pp + 0.382 * (high - low),
            "resistance_2": pp + 0.618 * (high - low)
        }
    
    elif pivot_type == "woodie":
        # Woodie pivot points
        pp = (high + low + 2 * close) / 4
        pivots = {
            "pivot": pp,
            "support_1": (2 * pp) - high,
            "support_2": pp - (high - low),
            "resistance_1": (2 * pp) - low,
            "resistance_2": pp + (high - low)
        }
    
    elif pivot_type == "camarilla":
        # Camarilla pivot points
        pivots = {
            "pivot": (high + low + close) / 3,
            "support_1": close - (high - low) * 1.1 / 12,
            "support_2": close - (high - low) * 1.1 / 6,
            "support_3": close - (high - low) * 1.1 / 4,
            "resistance_1": close + (high - low) * 1.1 / 12,
            "resistance_2": close + (high - low) * 1.1 / 6,
            "resistance_3": close + (high - low) * 1.1 / 4
        }
    
    return pivots


def _calculate_fibonacci(
    df: pd.DataFrame, 
    swing_high: Optional[float], 
    swing_low: Optional[float], 
    trend: str
) -> Dict:
    """Calculate Fibonacci retracement and extension levels."""
    
    # Auto-detect swing points if not provided
    if swing_high is None or swing_low is None:
        if trend == "up":
            # Find recent high and low for uptrend
            swing_high = df['high'].max()
            swing_low = df.loc[df['high'].idxmax(), 'low']
        else:
            # Find recent high and low for downtrend
            swing_low = df['low'].min()
            swing_high = df.loc[df['low'].idxmin(), 'high']
    
    diff = swing_high - swing_low
    
    # Fibonacci retracement levels
    retracements = {
        "0.0%": swing_high,
        "23.6%": swing_high - 0.236 * diff,
        "38.2%": swing_high - 0.382 * diff,
        "50.0%": swing_high - 0.5 * diff,
        "61.8%": swing_high - 0.618 * diff,
        "78.6%": swing_high - 0.786 * diff,
        "100.0%": swing_low
    }
    
    # Fibonacci extension levels
    extensions = {
        "127.2%": swing_high + 0.272 * diff,
        "161.8%": swing_high + 0.618 * diff,
        "200.0%": swing_high + 1.0 * diff,
        "261.8%": swing_high + 1.618 * diff
    }
    
    return {
        "swing_high": swing_high,
        "swing_low": swing_low,
        "retracements": retracements,
        "extensions": extensions
    }


def _detect_patterns(df: pd.DataFrame, pattern_types: List[str], lookback: int) -> List[Dict]:
    """Detect chart patterns in price data."""
    patterns = []
    analyze_df = df.tail(lookback)
    
    # Simple pattern detection (can be expanded)
    for i in range(2, len(analyze_df)):
        current = analyze_df.iloc[i]
        prev1 = analyze_df.iloc[i-1]
        prev2 = analyze_df.iloc[i-2]
        
        # Higher Highs and Higher Lows (Uptrend)
        if (current['high'] > prev1['high'] > prev2['high'] and
            current['low'] > prev1['low'] > prev2['low']):
            patterns.append({
                "type": "higher_highs_higher_lows",
                "direction": "bullish",
                "strength": "strong",
                "start_index": i-2,
                "end_index": i,
                "confidence": 0.8
            })
        
        # Lower Highs and Lower Lows (Downtrend)
        elif (current['high'] < prev1['high'] < prev2['high'] and
              current['low'] < prev1['low'] < prev2['low']):
            patterns.append({
                "type": "lower_highs_lower_lows",
                "direction": "bearish",
                "strength": "strong",
                "start_index": i-2,
                "end_index": i,
                "confidence": 0.8
            })
        
        # Double Top
        if (i >= 3 and 
            abs(prev1['high'] - prev2['high']) < 0.01 and
            current['high'] < prev1['high']):
            patterns.append({
                "type": "double_top",
                "direction": "bearish",
                "strength": "medium",
                "start_index": i-3,
                "end_index": i,
                "resistance_level": prev1['high'],
                "confidence": 0.7
            })
        
        # Double Bottom
        if (i >= 3 and 
            abs(prev1['low'] - prev2['low']) < 0.01 and
            current['low'] > prev1['low']):
            patterns.append({
                "type": "double_bottom",
                "direction": "bullish",
                "strength": "medium",
                "start_index": i-3,
                "end_index": i,
                "support_level": prev1['low'],
                "confidence": 0.7
            })
    
    return patterns


def _analyze_sentiment(df: pd.DataFrame) -> Dict:
    """Analyze market sentiment using multiple indicators."""
    close = df['close']
    volume = df['volume']
    
    # Calculate basic indicators
    sma_20 = close.rolling(window=20).mean()
    sma_50 = close.rolling(window=50).mean()
    
    # Price above/below moving averages
    above_sma20 = close.iloc[-1] > sma_20.iloc[-1]
    above_sma50 = close.iloc[-1] > sma_50.iloc[-1]
    
    # Volume analysis
    avg_volume = volume.rolling(window=20).mean()
    recent_volume = volume.tail(5).mean()
    volume_ratio = recent_volume / avg_volume.iloc[-1] if avg_volume.iloc[-1] > 0 else 1
    
    # Price momentum
    price_change_5 = (close.iloc[-1] / close.iloc[-6] - 1) * 100 if len(close) > 5 else 0
    price_change_10 = (close.iloc[-1] / close.iloc[-11] - 1) * 100 if len(close) > 10 else 0
    
    # Determine sentiment
    sentiment_score = 0
    factors = []
    
    # Trend factor
    if above_sma20 and above_sma50:
        sentiment_score += 2
        factors.append("Strong uptrend (above both MAs)")
    elif above_sma20:
        sentiment_score += 1
        factors.append("Moderate uptrend (above SMA20)")
    elif not above_sma20 and not above_sma50:
        sentiment_score -= 2
        factors.append("Strong downtrend (below both MAs)")
    else:
        sentiment_score -= 1
        factors.append("Moderate downtrend (below SMA20)")
    
    # Volume factor
    if volume_ratio > 1.5:
        sentiment_score += 1
        factors.append("High volume confirmation")
    elif volume_ratio < 0.5:
        sentiment_score -= 0.5
        factors.append("Low volume warning")
    
    # Momentum factor
    if price_change_5 > 2:
        sentiment_score += 0.5
        factors.append("Strong 5-day momentum")
    elif price_change_5 < -2:
        sentiment_score -= 0.5
        factors.append("Strong 5-day decline")
    
    # Classify sentiment
    if sentiment_score >= 2.5:
        sentiment = "very_bullish"
    elif sentiment_score >= 1:
        sentiment = "bullish"
    elif sentiment_score >= -0.5:
        sentiment = "neutral"
    elif sentiment_score >= -1.5:
        sentiment = "bearish"
    else:
        sentiment = "very_bearish"
    
    return {
        "sentiment": sentiment,
        "score": sentiment_score,
        "factors": factors,
        "indicators_used": ["SMA20", "SMA50", "Volume", "PriceMomentum"],
        "technical_summary": {
            "trend": "uptrend" if above_sma20 else "downtrend",
            "volume_status": "high" if volume_ratio > 1.5 else "normal" if volume_ratio > 0.5 else "low",
            "momentum_5d": f"{price_change_5:.2f}%",
            "momentum_10d": f"{price_change_10:.2f}%"
        }
    }