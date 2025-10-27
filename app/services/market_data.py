"""
Market data service for fetching historical and current market data.
Integrates with OpenAlgo API for OHLCV data.
"""

from datetime import datetime
from typing import List, Optional

import pandas as pd
from openalgo import api

from app.core.config import get_settings
from app.core.logging import LoggerMixin
from app.schemas.candles import Candle
from app.utils.timeframes import normalize_timeframe, validate_timeframe


class MarketDataService(LoggerMixin):
    """
    Service for fetching market data from OpenAlgo.
    
    Provides methods to fetch historical candles and current quotes.
    """
    
    _instance = None
    _client = None
    
    def __new__(cls):
        """Singleton pattern to reuse OpenAlgo client."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the market data service."""
        if self._client is None:
            settings = get_settings()
            self._initialize_client(settings)
    
    def _initialize_client(self, settings):
        """
        Initialize OpenAlgo API client.
        
        Args:
            settings: Application settings
        """
        try:
            # Initialize OpenAlgo client
            self._client = api(
                api_key=settings.openalgo_api_key,
                host=settings.openalgo_host
            )
            self.logger.info(f"OpenAlgo client initialized: {settings.openalgo_host}")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAlgo client: {e}")
            raise
    
    async def fetch_historical_candles(
        self,
        symbol: str,
        exchange: str,
        interval: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV candles from OpenAlgo.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code (NSE, BSE, etc.)
            interval: Timeframe (1m, 5m, 1h, 1d, etc.)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
        
        Raises:
            ValueError: If timeframe is invalid
            Exception: If API call fails
        
        Example:
            >>> service = MarketDataService()
            >>> df = await service.fetch_historical_candles(
            ...     "NIFTY", "NSE", "5m", "2024-01-01", "2024-01-31"
            ... )
        """
        # Validate and normalize timeframe
        if not validate_timeframe(interval):
            raise ValueError(f"Invalid timeframe: {interval}")
        
        normalized_interval = normalize_timeframe(interval)
        
        self.logger.info(
            f"Fetching historical data: {symbol} {exchange} {normalized_interval} "
            f"from {start_date} to {end_date}"
        )
        
        try:
            # Call OpenAlgo history API
            # Note: Actual OpenAlgo API method may vary - adjust as needed
            response = self._client.history(
                symbol=symbol,
                exchange=exchange,
                interval=normalized_interval,
                start_date=start_date,
                end_date=end_date
            )
            
            # Convert to DataFrame
            if isinstance(response, pd.DataFrame):
                df = response
            elif isinstance(response, dict) and 'data' in response:
                df = pd.DataFrame(response['data'])
            else:
                df = pd.DataFrame(response)
            
            # Ensure required columns exist
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                # Try alternative column names
                column_mapping = {
                    'datetime': 'timestamp',
                    'date': 'timestamp',
                    'time': 'timestamp',
                    'o': 'open',
                    'h': 'high',
                    'l': 'low',
                    'c': 'close',
                    'v': 'volume',
                    'vol': 'volume'
                }
                
                df = df.rename(columns=column_mapping)
                
                # Check again
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert timestamp to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            self.logger.info(f"Fetched {len(df)} candles")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}", exc_info=True)
            raise
    
    async def fetch_current_quote(
        self,
        symbol: str,
        exchange: str
    ) -> dict:
        """
        Fetch current quote/price for a symbol.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
        
        Returns:
            dict: Current quote data with LTP, volume, etc.
        
        Example:
            >>> service = MarketDataService()
            >>> quote = await service.fetch_current_quote("NIFTY", "NSE")
        """
        self.logger.info(f"Fetching current quote: {symbol} {exchange}")
        
        try:
            # Call OpenAlgo quote API
            response = self._client.quotes(
                symbol=symbol,
                exchange=exchange
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error fetching current quote: {e}", exc_info=True)
            raise
    
    def dataframe_to_candles(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str
    ) -> List[Candle]:
        """
        Convert DataFrame to list of Candle models.
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            timeframe: Timeframe string
        
        Returns:
            List[Candle]: List of Candle objects
        
        Example:
            >>> df = pd.DataFrame(...)
            >>> candles = service.dataframe_to_candles(df, "NIFTY", "5m")
        """
        candles = []
        
        for _, row in df.iterrows():
            try:
                candle = Candle(
                    symbol=symbol,
                    timestamp=row['timestamp'],
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=float(row['volume']),
                    timeframe=timeframe
                )
                candles.append(candle)
            except Exception as e:
                self.logger.warning(f"Skipping invalid candle: {e}")
                continue
        
        return candles
    
    async def fetch_candles_with_current(
        self,
        symbol: str,
        exchange: str,
        interval: str,
        start_date: str,
        end_date: str,
        include_current: bool = True
    ) -> tuple[pd.DataFrame, Optional[dict]]:
        """
        Fetch historical candles and optionally current forming candle.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange code
            interval: Timeframe
            start_date: Start date
            end_date: End date
            include_current: Whether to fetch current candle
        
        Returns:
            tuple: (historical_df, current_candle_dict)
        
        Example:
            >>> df, current = await service.fetch_candles_with_current(
            ...     "NIFTY", "NSE", "5m", "2024-01-01", "2024-01-31"
            ... )
        """
        # Fetch historical data
        df = await self.fetch_historical_candles(
            symbol, exchange, interval, start_date, end_date
        )
        
        current_candle = None
        
        if include_current:
            try:
                # Fetch current quote
                quote = await self.fetch_current_quote(symbol, exchange)
                
                # Create current candle from quote
                # Note: This is a simplified version - adjust based on actual API response
                current_candle = {
                    'timestamp': datetime.now(),
                    'open': quote.get('open', quote.get('ltp')),
                    'high': quote.get('high', quote.get('ltp')),
                    'low': quote.get('low', quote.get('ltp')),
                    'close': quote.get('ltp'),
                    'volume': quote.get('volume', 0)
                }
            except Exception as e:
                self.logger.warning(f"Could not fetch current candle: {e}")
        
        return df, current_candle
    
    def validate_and_normalize_timeframe(self, interval: str) -> str:
        """
        Validate and normalize timeframe string.
        
        Args:
            interval: Timeframe string
        
        Returns:
            str: Normalized timeframe
        
        Raises:
            ValueError: If timeframe is invalid
        """
        if not validate_timeframe(interval):
            raise ValueError(f"Invalid timeframe: {interval}")
        
        return normalize_timeframe(interval)
    
    def get_client(self):
        """
        Get the OpenAlgo client instance.
        
        Returns:
            OpenAlgo client
        """
        return self._client


# Convenience function to get service instance
def get_market_data_service() -> MarketDataService:
    """
    Get MarketDataService singleton instance.
    
    Returns:
        MarketDataService: Service instance
    
    Example:
        >>> from app.services.market_data import get_market_data_service
        >>> service = get_market_data_service()
    """
    return MarketDataService()
