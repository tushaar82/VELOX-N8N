"""
Tests for input validators.
"""

import pytest
from app.utils.validators import (
    validate_symbol,
    sanitize_symbol,
    validate_exchange,
    validate_date_string,
    validate_date_range,
    validate_strike_price,
    validate_timeframe_input,
    validate_positive_integer,
    validate_percentage,
    is_index_symbol,
    get_supported_exchanges
)


class TestSymbolValidation:
    """Tests for symbol validation."""
    
    def test_valid_symbols(self, sample_symbols):
        """Test validation of valid symbols."""
        for symbol in sample_symbols:
            is_valid, error = validate_symbol(symbol)
            assert is_valid is True
            assert error is None
    
    def test_invalid_symbols(self):
        """Test validation of invalid symbols."""
        invalid_symbols = ['', '123', 'ABC-DEF!', 'a' * 21]
        
        for symbol in invalid_symbols:
            is_valid, error = validate_symbol(symbol)
            assert is_valid is False
            assert error is not None
    
    def test_symbol_sanitization(self):
        """Test symbol sanitization."""
        assert sanitize_symbol('nifty') == 'NIFTY'
        assert sanitize_symbol('  NIFTY  ') == 'NIFTY'
        assert sanitize_symbol('Nifty') == 'NIFTY'


class TestExchangeValidation:
    """Tests for exchange validation."""
    
    def test_valid_exchanges(self, sample_exchanges):
        """Test validation of valid exchanges."""
        for exchange in sample_exchanges:
            is_valid, error = validate_exchange(exchange)
            assert is_valid is True
            assert error is None
    
    def test_invalid_exchange(self):
        """Test validation of invalid exchange."""
        is_valid, error = validate_exchange('INVALID')
        assert is_valid is False
        assert error is not None
    
    def test_get_supported_exchanges(self):
        """Test getting supported exchanges."""
        exchanges = get_supported_exchanges()
        assert isinstance(exchanges, list)
        assert len(exchanges) > 0
        assert 'NSE' in exchanges


class TestDateValidation:
    """Tests for date validation."""
    
    def test_valid_date_string(self):
        """Test validation of valid date strings."""
        valid_dates = ['2024-01-01', '2024-12-31', '2023-06-15']
        
        for date_str in valid_dates:
            is_valid, error = validate_date_string(date_str)
            assert is_valid is True
            assert error is None
    
    def test_invalid_date_string(self):
        """Test validation of invalid date strings."""
        invalid_dates = ['2024-13-01', '2024-01-32', 'invalid', '01-01-2024']
        
        for date_str in invalid_dates:
            is_valid, error = validate_date_string(date_str)
            assert is_valid is False
            assert error is not None
    
    def test_valid_date_range(self):
        """Test validation of valid date ranges."""
        is_valid, error = validate_date_range('2024-01-01', '2024-01-31')
        assert is_valid is True
        assert error is None
    
    def test_invalid_date_range(self):
        """Test validation of invalid date ranges (end before start)."""
        is_valid, error = validate_date_range('2024-01-31', '2024-01-01')
        assert is_valid is False
        assert error is not None


class TestStrikePriceValidation:
    """Tests for strike price validation."""
    
    def test_valid_strike_prices(self):
        """Test validation of valid strike prices."""
        valid_strikes = [100.0, 21500.0, 50000.0]
        
        for strike in valid_strikes:
            is_valid, error = validate_strike_price(strike)
            assert is_valid is True
            assert error is None
    
    def test_invalid_strike_prices(self):
        """Test validation of invalid strike prices."""
        invalid_strikes = [-100.0, 0.0, 1000000.0]
        
        for strike in invalid_strikes:
            is_valid, error = validate_strike_price(strike)
            assert is_valid is False
            assert error is not None


class TestTimeframeValidation:
    """Tests for timeframe validation."""
    
    def test_valid_timeframes(self, sample_timeframes):
        """Test validation of valid timeframes."""
        for tf in sample_timeframes:
            is_valid, error = validate_timeframe_input(tf)
            assert is_valid is True
            assert error is None
    
    def test_invalid_timeframes(self):
        """Test validation of invalid timeframes."""
        invalid_tfs = ['invalid', '0m', '1000d', 'abc']
        
        for tf in invalid_tfs:
            is_valid, error = validate_timeframe_input(tf)
            assert is_valid is False
            assert error is not None


class TestIntegerValidation:
    """Tests for positive integer validation."""
    
    def test_valid_positive_integers(self):
        """Test validation of valid positive integers."""
        is_valid, error = validate_positive_integer(10, "test", max_value=100)
        assert is_valid is True
        assert error is None
    
    def test_invalid_positive_integers(self):
        """Test validation of invalid positive integers."""
        # Negative
        is_valid, error = validate_positive_integer(-10, "test")
        assert is_valid is False
        
        # Zero
        is_valid, error = validate_positive_integer(0, "test")
        assert is_valid is False
        
        # Exceeds max
        is_valid, error = validate_positive_integer(150, "test", max_value=100)
        assert is_valid is False


class TestPercentageValidation:
    """Tests for percentage validation."""
    
    def test_valid_percentages(self):
        """Test validation of valid percentages."""
        valid_pcts = [0.0, 50.0, 100.0]
        
        for pct in valid_pcts:
            is_valid, error = validate_percentage(pct, "test")
            assert is_valid is True
            assert error is None
    
    def test_invalid_percentages(self):
        """Test validation of invalid percentages."""
        invalid_pcts = [-10.0, 150.0]
        
        for pct in invalid_pcts:
            is_valid, error = validate_percentage(pct, "test")
            assert is_valid is False
            assert error is not None


class TestIndexSymbolCheck:
    """Tests for index symbol checking."""
    
    def test_index_symbols(self):
        """Test identification of index symbols."""
        index_symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'NIFTY50']
        
        for symbol in index_symbols:
            assert is_index_symbol(symbol) is True
    
    def test_non_index_symbols(self):
        """Test identification of non-index symbols."""
        non_index_symbols = ['RELIANCE', 'TCS', 'INFY']
        
        for symbol in non_index_symbols:
            assert is_index_symbol(symbol) is False
