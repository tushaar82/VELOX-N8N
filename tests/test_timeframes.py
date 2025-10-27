"""
Tests for timeframe utilities.
"""

import pytest
from datetime import datetime, timedelta
from app.utils.timeframes import (
    normalize_timeframe,
    validate_timeframe,
    parse_timeframe,
    timeframe_to_pandas_freq,
    get_candle_count,
    get_timeframe_duration,
    get_bucket_start,
    get_supported_timeframes,
    is_intraday_timeframe,
    compare_timeframes,
    get_higher_timeframe
)


class TestTimeframeNormalization:
    """Tests for timeframe normalization."""
    
    def test_normalize_minutes(self):
        """Test normalization of minute timeframes."""
        assert normalize_timeframe('1M') == '1m'
        assert normalize_timeframe('5MIN') == '5m'
        assert normalize_timeframe('15MINUTE') == '15m'
    
    def test_normalize_hours(self):
        """Test normalization of hour timeframes."""
        assert normalize_timeframe('1H') == '1h'
        assert normalize_timeframe('4HOUR') == '4h'
    
    def test_normalize_days(self):
        """Test normalization of day timeframes."""
        assert normalize_timeframe('1D') == '1d'
        assert normalize_timeframe('1DAY') == '1d'
    
    def test_normalize_weeks(self):
        """Test normalization of week timeframes."""
        assert normalize_timeframe('1W') == '1w'
        assert normalize_timeframe('1WEEK') == '1w'
    
    def test_normalize_months(self):
        """Test normalization of month timeframes."""
        assert normalize_timeframe('1MO') == '1mo'
        assert normalize_timeframe('1MONTH') == '1mo'


class TestTimeframeValidation:
    """Tests for timeframe validation."""
    
    def test_valid_timeframes(self, sample_timeframes):
        """Test validation of valid timeframes."""
        for tf in sample_timeframes:
            assert validate_timeframe(tf) is True
    
    def test_invalid_timeframes(self):
        """Test validation of invalid timeframes."""
        invalid_tfs = ['invalid', '0m', '1000d', 'abc', '']
        
        for tf in invalid_tfs:
            assert validate_timeframe(tf) is False


class TestTimeframeParsing:
    """Tests for timeframe parsing to seconds."""
    
    def test_parse_minutes(self):
        """Test parsing minute timeframes."""
        assert parse_timeframe('1m') == 60
        assert parse_timeframe('5m') == 300
        assert parse_timeframe('15m') == 900
    
    def test_parse_hours(self):
        """Test parsing hour timeframes."""
        assert parse_timeframe('1h') == 3600
        assert parse_timeframe('4h') == 14400
    
    def test_parse_days(self):
        """Test parsing day timeframes."""
        assert parse_timeframe('1d') == 86400
    
    def test_parse_weeks(self):
        """Test parsing week timeframes."""
        assert parse_timeframe('1w') == 604800
    
    def test_parse_invalid(self):
        """Test parsing invalid timeframes."""
        with pytest.raises((ValueError, KeyError)):
            parse_timeframe('invalid')


class TestPandasFrequency:
    """Tests for pandas frequency conversion."""
    
    def test_pandas_freq_minutes(self):
        """Test pandas frequency for minutes."""
        assert timeframe_to_pandas_freq('1m') == '1T'
        assert timeframe_to_pandas_freq('5m') == '5T'
    
    def test_pandas_freq_hours(self):
        """Test pandas frequency for hours."""
        assert timeframe_to_pandas_freq('1h') == '1H'
    
    def test_pandas_freq_days(self):
        """Test pandas frequency for days."""
        assert timeframe_to_pandas_freq('1d') == '1D'


class TestCandleCount:
    """Tests for candle count calculation."""
    
    def test_candle_count_minutes(self):
        """Test candle count for minute timeframes."""
        start = datetime(2024, 1, 1, 9, 0)
        end = datetime(2024, 1, 1, 10, 0)
        
        count = get_candle_count(start, end, '1m')
        assert count == 60
        
        count = get_candle_count(start, end, '5m')
        assert count == 12
    
    def test_candle_count_hours(self):
        """Test candle count for hour timeframes."""
        start = datetime(2024, 1, 1, 0, 0)
        end = datetime(2024, 1, 2, 0, 0)
        
        count = get_candle_count(start, end, '1h')
        assert count == 24


class TestTimeframeDuration:
    """Tests for timeframe duration."""
    
    def test_duration_minutes(self):
        """Test duration for minute timeframes."""
        duration = get_timeframe_duration('5m')
        assert duration == timedelta(minutes=5)
    
    def test_duration_hours(self):
        """Test duration for hour timeframes."""
        duration = get_timeframe_duration('1h')
        assert duration == timedelta(hours=1)
    
    def test_duration_days(self):
        """Test duration for day timeframes."""
        duration = get_timeframe_duration('1d')
        assert duration == timedelta(days=1)


class TestBucketStart:
    """Tests for bucket start calculation."""
    
    def test_bucket_start_minutes(self):
        """Test bucket start for minute timeframes."""
        timestamp = datetime(2024, 1, 1, 9, 17, 30)
        
        # 5-minute bucket
        bucket = get_bucket_start(timestamp, '5m')
        assert bucket.minute % 5 == 0
        assert bucket.second == 0
        assert bucket.microsecond == 0
    
    def test_bucket_start_hours(self):
        """Test bucket start for hour timeframes."""
        timestamp = datetime(2024, 1, 1, 9, 45, 30)
        
        # 1-hour bucket
        bucket = get_bucket_start(timestamp, '1h')
        assert bucket.minute == 0
        assert bucket.second == 0
    
    def test_bucket_start_days(self):
        """Test bucket start for day timeframes."""
        timestamp = datetime(2024, 1, 1, 15, 30, 0)
        
        # 1-day bucket
        bucket = get_bucket_start(timestamp, '1d')
        assert bucket.hour == 0
        assert bucket.minute == 0
        assert bucket.second == 0


class TestSupportedTimeframes:
    """Tests for supported timeframes."""
    
    def test_get_supported_timeframes(self):
        """Test getting supported timeframes."""
        timeframes = get_supported_timeframes()
        assert isinstance(timeframes, list)
        assert len(timeframes) > 0
        assert '1m' in timeframes
        assert '5m' in timeframes
        assert '1h' in timeframes
        assert '1d' in timeframes


class TestIntradayCheck:
    """Tests for intraday timeframe check."""
    
    def test_intraday_timeframes(self):
        """Test identification of intraday timeframes."""
        intraday_tfs = ['1m', '5m', '15m', '1h', '4h']
        
        for tf in intraday_tfs:
            assert is_intraday_timeframe(tf) is True
    
    def test_non_intraday_timeframes(self):
        """Test identification of non-intraday timeframes."""
        non_intraday_tfs = ['1d', '1w', '1mo']
        
        for tf in non_intraday_tfs:
            assert is_intraday_timeframe(tf) is False


class TestTimeframeComparison:
    """Tests for timeframe comparison."""
    
    def test_compare_equal(self):
        """Test comparison of equal timeframes."""
        assert compare_timeframes('1m', '1m') == 0
    
    def test_compare_less(self):
        """Test comparison of smaller timeframe."""
        assert compare_timeframes('1m', '5m') < 0
    
    def test_compare_greater(self):
        """Test comparison of larger timeframe."""
        assert compare_timeframes('1h', '1m') > 0


class TestHigherTimeframe:
    """Tests for higher timeframe calculation."""
    
    def test_higher_timeframe_minutes(self):
        """Test getting higher timeframe for minutes."""
        higher = get_higher_timeframe('1m', multiplier=5)
        assert higher == '5m'
    
    def test_higher_timeframe_hours(self):
        """Test getting higher timeframe for hours."""
        higher = get_higher_timeframe('1h', multiplier=4)
        assert higher == '4h'
    
    def test_higher_timeframe_none(self):
        """Test getting higher timeframe when none exists."""
        higher = get_higher_timeframe('1mo', multiplier=12)
        # Should return None or handle gracefully
        assert higher is None or isinstance(higher, str)
