"""
Tick stream service for real-time candle aggregation.
Aggregates tick data into candles across multiple timeframes.
"""

import asyncio
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Optional, Set

import pandas as pd

from app.core.config import get_settings
from app.core.logging import LoggerMixin
from app.schemas.candles import PartialCandle
from app.utils.timeframes import (
    get_bucket_start,
    parse_timeframe,
    normalize_timeframe
)


class TickData:
    """Individual tick data point."""
    
    def __init__(
        self,
        symbol: str,
        price: float,
        volume: float,
        timestamp: datetime
    ):
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.timestamp = timestamp


class CandleAggregator:
    """
    Aggregates ticks into candles for a specific symbol and timeframe.
    """
    
    def __init__(self, symbol: str, timeframe: str, buffer_size: int = 1000):
        """
        Initialize candle aggregator.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (e.g., "1m", "5m")
            buffer_size: Maximum number of ticks to buffer
        """
        self.symbol = symbol
        self.timeframe = normalize_timeframe(timeframe)
        self.buffer_size = buffer_size
        
        # Tick buffer
        self.tick_buffer: deque = deque(maxlen=buffer_size)
        
        # Current candle data
        self.current_candle: Optional[Dict] = None
        self.current_bucket_start: Optional[datetime] = None
        
        # Statistics
        self.total_ticks = 0
        self.candles_completed = 0
    
    def add_tick(self, tick: TickData) -> Optional[PartialCandle]:
        """
        Add a tick and update candle.
        
        Args:
            tick: Tick data
        
        Returns:
            Optional[PartialCandle]: Updated candle if available
        """
        self.total_ticks += 1
        self.tick_buffer.append(tick)
        
        # Determine which candle bucket this tick belongs to
        bucket_start = get_bucket_start(tick.timestamp, self.timeframe)
        
        # Check if we need to start a new candle
        if self.current_bucket_start is None or bucket_start != self.current_bucket_start:
            # Complete previous candle if exists
            if self.current_candle is not None:
                self.candles_completed += 1
            
            # Start new candle
            self.current_bucket_start = bucket_start
            self.current_candle = {
                'open': tick.price,
                'high': tick.price,
                'low': tick.price,
                'close': tick.price,
                'volume': tick.volume,
                'tick_count': 1,
                'volume_sum': tick.price * tick.volume,  # For VWAP
            }
        else:
            # Update existing candle
            self.current_candle['high'] = max(self.current_candle['high'], tick.price)
            self.current_candle['low'] = min(self.current_candle['low'], tick.price)
            self.current_candle['close'] = tick.price
            self.current_candle['volume'] += tick.volume
            self.current_candle['tick_count'] += 1
            self.current_candle['volume_sum'] += tick.price * tick.volume
        
        # Create partial candle
        vwap = None
        if self.current_candle['volume'] > 0:
            vwap = self.current_candle['volume_sum'] / self.current_candle['volume']
        
        partial_candle = PartialCandle(
            symbol=self.symbol,
            timestamp=self.current_bucket_start,
            open=self.current_candle['open'],
            high=self.current_candle['high'],
            low=self.current_candle['low'],
            close=self.current_candle['close'],
            volume=self.current_candle['volume'],
            timeframe=self.timeframe,
            tick_count=self.current_candle['tick_count'],
            vwap=vwap,
            is_complete=False
        )
        
        return partial_candle
    
    def get_current_candle(self) -> Optional[PartialCandle]:
        """Get current forming candle."""
        if self.current_candle is None:
            return None
        
        vwap = None
        if self.current_candle['volume'] > 0:
            vwap = self.current_candle['volume_sum'] / self.current_candle['volume']
        
        return PartialCandle(
            symbol=self.symbol,
            timestamp=self.current_bucket_start,
            open=self.current_candle['open'],
            high=self.current_candle['high'],
            low=self.current_candle['low'],
            close=self.current_candle['close'],
            volume=self.current_candle['volume'],
            timeframe=self.timeframe,
            tick_count=self.current_candle['tick_count'],
            vwap=vwap,
            is_complete=False
        )
    
    def get_stats(self) -> Dict:
        """Get aggregator statistics."""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'total_ticks': self.total_ticks,
            'candles_completed': self.candles_completed,
            'buffer_size': len(self.tick_buffer),
            'current_candle': self.current_candle is not None
        }


class TickStreamService(LoggerMixin):
    """
    Service for managing real-time tick streams and candle aggregation.
    
    Handles:
    - Multiple symbols
    - Multiple timeframes per symbol
    - Tick buffering
    - Candle aggregation
    - Subscriber notifications
    """
    
    def __init__(self):
        """Initialize tick stream service."""
        settings = get_settings()
        
        # Aggregators: {symbol: {timeframe: CandleAggregator}}
        self.aggregators: Dict[str, Dict[str, CandleAggregator]] = defaultdict(dict)
        
        # Subscribers: {symbol: {timeframe: set(callback_ids)}}
        self.subscribers: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        
        # Callbacks: {callback_id: async_callback_function}
        self.callbacks: Dict[str, callable] = {}
        
        # Configuration
        self.buffer_size = settings.tick_buffer_size
        
        # Statistics
        self.total_ticks_processed = 0
        
        self.logger.info("TickStreamService initialized")
    
    def subscribe(
        self,
        symbol: str,
        timeframes: List[str],
        callback_id: str,
        callback: callable
    ) -> None:
        """
        Subscribe to tick updates for a symbol and timeframes.
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes to subscribe to
            callback_id: Unique identifier for this subscription
            callback: Async callback function(symbol, timeframe, candle)
        
        Example:
            >>> async def my_callback(symbol, timeframe, candle):
            ...     print(f"New candle: {symbol} {timeframe}")
            >>> 
            >>> service.subscribe("NIFTY", ["1m", "5m"], "client1", my_callback)
        """
        symbol = symbol.upper()
        
        # Store callback
        self.callbacks[callback_id] = callback
        
        # Subscribe to each timeframe
        for timeframe in timeframes:
            normalized_tf = normalize_timeframe(timeframe)
            
            # Create aggregator if doesn't exist
            if normalized_tf not in self.aggregators[symbol]:
                self.aggregators[symbol][normalized_tf] = CandleAggregator(
                    symbol, normalized_tf, self.buffer_size
                )
                self.logger.info(f"Created aggregator for {symbol} {normalized_tf}")
            
            # Add subscriber
            self.subscribers[symbol][normalized_tf].add(callback_id)
            
            self.logger.info(
                f"Subscribed {callback_id} to {symbol} {normalized_tf}"
            )
    
    def unsubscribe(
        self,
        symbol: str,
        timeframes: List[str],
        callback_id: str
    ) -> None:
        """
        Unsubscribe from tick updates.
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes to unsubscribe from
            callback_id: Subscription identifier
        """
        symbol = symbol.upper()
        
        for timeframe in timeframes:
            normalized_tf = normalize_timeframe(timeframe)
            
            if symbol in self.subscribers and normalized_tf in self.subscribers[symbol]:
                self.subscribers[symbol][normalized_tf].discard(callback_id)
                
                self.logger.info(
                    f"Unsubscribed {callback_id} from {symbol} {normalized_tf}"
                )
                
                # Clean up if no more subscribers
                if not self.subscribers[symbol][normalized_tf]:
                    del self.subscribers[symbol][normalized_tf]
                    if normalized_tf in self.aggregators[symbol]:
                        del self.aggregators[symbol][normalized_tf]
                        self.logger.info(
                            f"Removed aggregator for {symbol} {normalized_tf}"
                        )
    
    def unsubscribe_all(self, callback_id: str) -> None:
        """
        Unsubscribe from all symbols and timeframes.
        
        Args:
            callback_id: Subscription identifier
        """
        # Find all subscriptions for this callback
        to_remove = []
        
        for symbol in self.subscribers:
            for timeframe in self.subscribers[symbol]:
                if callback_id in self.subscribers[symbol][timeframe]:
                    to_remove.append((symbol, timeframe))
        
        # Remove subscriptions
        for symbol, timeframe in to_remove:
            self.subscribers[symbol][timeframe].discard(callback_id)
            
            # Clean up if no more subscribers
            if not self.subscribers[symbol][timeframe]:
                del self.subscribers[symbol][timeframe]
                if timeframe in self.aggregators[symbol]:
                    del self.aggregators[symbol][timeframe]
        
        # Remove callback
        if callback_id in self.callbacks:
            del self.callbacks[callback_id]
        
        self.logger.info(f"Unsubscribed {callback_id} from all streams")
    
    async def process_tick(
        self,
        symbol: str,
        price: float,
        volume: float,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Process a new tick and update all relevant candles.
        
        Args:
            symbol: Trading symbol
            price: Tick price
            volume: Tick volume
            timestamp: Tick timestamp (defaults to now)
        
        Example:
            >>> await service.process_tick("NIFTY", 21530.50, 100)
        """
        symbol = symbol.upper()
        timestamp = timestamp or datetime.now()
        
        # Create tick
        tick = TickData(symbol, price, volume, timestamp)
        
        self.total_ticks_processed += 1
        
        # Process tick for all aggregators of this symbol
        if symbol in self.aggregators:
            for timeframe, aggregator in self.aggregators[symbol].items():
                # Update candle
                partial_candle = aggregator.add_tick(tick)
                
                # Notify subscribers
                if partial_candle and symbol in self.subscribers:
                    if timeframe in self.subscribers[symbol]:
                        await self._notify_subscribers(
                            symbol, timeframe, partial_candle
                        )
    
    async def _notify_subscribers(
        self,
        symbol: str,
        timeframe: str,
        candle: PartialCandle
    ) -> None:
        """Notify all subscribers of a candle update."""
        if symbol not in self.subscribers or timeframe not in self.subscribers[symbol]:
            return
        
        # Get all callback IDs for this symbol/timeframe
        callback_ids = list(self.subscribers[symbol][timeframe])
        
        # Call each callback
        for callback_id in callback_ids:
            if callback_id in self.callbacks:
                try:
                    await self.callbacks[callback_id](symbol, timeframe, candle)
                except Exception as e:
                    self.logger.error(
                        f"Error in callback {callback_id}: {e}",
                        exc_info=True
                    )
    
    def get_current_candle(
        self,
        symbol: str,
        timeframe: str
    ) -> Optional[PartialCandle]:
        """
        Get current forming candle for a symbol and timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
        
        Returns:
            Optional[PartialCandle]: Current candle if available
        """
        symbol = symbol.upper()
        normalized_tf = normalize_timeframe(timeframe)
        
        if symbol in self.aggregators and normalized_tf in self.aggregators[symbol]:
            return self.aggregators[symbol][normalized_tf].get_current_candle()
        
        return None
    
    def get_stats(self) -> Dict:
        """Get service statistics."""
        stats = {
            'total_ticks_processed': self.total_ticks_processed,
            'active_symbols': len(self.aggregators),
            'total_aggregators': sum(len(aggs) for aggs in self.aggregators.values()),
            'total_subscribers': sum(
                len(subs) 
                for symbol_subs in self.subscribers.values() 
                for subs in symbol_subs.values()
            ),
            'symbols': {}
        }
        
        # Per-symbol stats
        for symbol, aggregators in self.aggregators.items():
            stats['symbols'][symbol] = {
                'timeframes': {},
                'subscribers': {}
            }
            
            for timeframe, aggregator in aggregators.items():
                stats['symbols'][symbol]['timeframes'][timeframe] = aggregator.get_stats()
                
                if symbol in self.subscribers and timeframe in self.subscribers[symbol]:
                    stats['symbols'][symbol]['subscribers'][timeframe] = len(
                        self.subscribers[symbol][timeframe]
                    )
        
        return stats


# Singleton instance
_tick_stream_service: Optional[TickStreamService] = None


def get_tick_stream_service() -> TickStreamService:
    """
    Get TickStreamService singleton instance.
    
    Returns:
        TickStreamService: Service instance
    """
    global _tick_stream_service
    if _tick_stream_service is None:
        _tick_stream_service = TickStreamService()
    return _tick_stream_service
