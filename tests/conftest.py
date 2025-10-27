"""
Pytest configuration and fixtures for testing.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture
def sample_ohlcv_data():
    """
    Generate sample OHLCV data for testing.
    
    Returns 100 candles with realistic price movement.
    """
    num_candles = 100
    base_price = 21500
    
    data = []
    current_time = datetime(2024, 1, 1, 9, 15)
    
    for i in range(num_candles):
        # Generate price with some randomness
        price_change = (i % 10 - 5) * 10  # Oscillating pattern
        close = base_price + price_change + (i * 2)  # Slight uptrend
        
        open_price = close - 5
        high = close + 10
        low = close - 10
        volume = 1000000 + (i * 1000)
        
        data.append({
            'timestamp': current_time + timedelta(minutes=i*5),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_candle_dict():
    """Sample candle as dictionary."""
    return {
        'symbol': 'NIFTY',
        'timestamp': datetime(2024, 1, 15, 15, 25),
        'open': 21500.0,
        'high': 21550.0,
        'low': 21480.0,
        'close': 21530.0,
        'volume': 1500000.0,
        'timeframe': '5m'
    }


@pytest.fixture
def sample_option_data():
    """Sample option chain data."""
    return {
        'strike_price': 21500.0,
        'call_oi': 1500000,
        'call_volume': 50000,
        'call_ltp': 125.50,
        'call_iv': 18.5,
        'put_oi': 2000000,
        'put_volume': 75000,
        'put_ltp': 110.25,
        'put_iv': 19.2
    }


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    class MockSettings:
        openalgo_api_key = "test_key"
        openalgo_host = "http://localhost:5000"
        openalgo_version = "v1"
        cors_origins = "http://localhost:3000"
        log_level = "INFO"
        max_websocket_connections = 100
        tick_buffer_size = 1000
        default_timeframes = "1m,5m,15m,1h,1d"
        app_host = "0.0.0.0"
        app_port = 8000
        app_workers = 4
        
        def get_cors_origins(self):
            return self.cors_origins.split(",")
        
        def get_default_timeframes(self):
            return self.default_timeframes.split(",")
    
    return MockSettings()


@pytest.fixture
def sample_symbols():
    """Sample trading symbols."""
    return ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'RELIANCE', 'TCS']


@pytest.fixture
def sample_timeframes():
    """Sample timeframes."""
    return ['1m', '5m', '15m', '1h', '1d']


@pytest.fixture
def sample_exchanges():
    """Sample exchanges."""
    return ['NSE', 'BSE', 'NFO', 'BFO']
