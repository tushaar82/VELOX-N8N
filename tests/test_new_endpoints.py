"""
Comprehensive tests for new endpoints and indicators.
Tests categorized indicators, technical analysis, and connectivity fixes.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import pandas as pd

from app.api.v1.endpoints.indicators_categorized import (
    VOLUME_INDICATORS, VOLATILITY_INDICATORS, TREND_INDICATORS,
    MOMENTUM_INDICATORS, STATISTICAL_INDICATORS, PATTERN_INDICATORS
)
from app.services.indicators import IndicatorService
from app.api.v1.endpoints.technical_analysis import (
    _calculate_pivots, _calculate_fibonacci, _detect_patterns, _analyze_sentiment
)


class TestCategorizedIndicators:
    """Test categorized indicator endpoints."""
    
    def test_volume_indicators_list(self):
        """Test volume indicators list endpoint."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        # Check if all volume indicators are available
        for indicator in VOLUME_INDICATORS:
            assert indicator in AVAILABLE_INDICATORS, f"Volume indicator {indicator} not found"
    
    def test_volatility_indicators_list(self):
        """Test volatility indicators list endpoint."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        # Check if all volatility indicators are available
        for indicator in VOLATILITY_INDICATORS:
            assert indicator in AVAILABLE_INDICATORS, f"Volatility indicator {indicator} not found"
    
    def test_trend_indicators_list(self):
        """Test trend indicators list endpoint."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        # Check if all trend indicators are available
        for indicator in TREND_INDICATORS:
            assert indicator in AVAILABLE_INDICATORS, f"Trend indicator {indicator} not found"
    
    def test_momentum_indicators_list(self):
        """Test momentum indicators list endpoint."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        # Check if all momentum indicators are available
        for indicator in MOMENTUM_INDICATORS:
            assert indicator in AVAILABLE_INDICATORS, f"Momentum indicator {indicator} not found"
    
    def test_statistical_indicators_list(self):
        """Test statistical indicators list endpoint."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        # Check if all statistical indicators are available
        for indicator in STATISTICAL_INDICATORS:
            assert indicator in AVAILABLE_INDICATORS, f"Statistical indicator {indicator} not found"
    
    def test_pattern_indicators_list(self):
        """Test pattern indicators list endpoint."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        # Check if all pattern indicators are available
        for indicator in PATTERN_INDICATORS:
            assert indicator in AVAILABLE_INDICATORS, f"Pattern indicator {indicator} not found"


class TestNewIndicators:
    """Test newly added indicators."""
    
    @pytest.fixture
    def sample_df(self):
        """Create sample OHLCV DataFrame for testing."""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        return pd.DataFrame({
            'timestamp': dates,
            'open': [100 + i * 0.1 for i in range(100)],
            'high': [101 + i * 0.1 for i in range(100)],
            'low': [99 + i * 0.1 for i in range(100)],
            'close': [100.5 + i * 0.1 for i in range(100)],
            'volume': [1000000 + i * 1000 for i in range(100)]
        })
    
    def test_statistical_indicators(self, sample_df):
        """Test statistical indicators calculation."""
        service = IndicatorService()
        
        # Test all statistical indicators
        indicators = service._calculate_statistical_indicators(sample_df, {})
        
        # Check if all statistical indicators are calculated
        expected_indicators = [
            'StdDev', 'ZScore', 'PriceROC', 'ATRP', 'BBWPercent', 'PricePosition'
        ]
        
        for indicator in expected_indicators:
            assert indicator in indicators, f"Statistical indicator {indicator} not calculated"
            assert not indicators[indicator].empty, f"Statistical indicator {indicator} is empty"
    
    def test_pattern_indicators(self, sample_df):
        """Test pattern indicators calculation."""
        service = IndicatorService()
        
        # Test all pattern indicators
        indicators = service._calculate_pattern_indicators(sample_df, {})
        
        # Check if all pattern indicators are calculated
        expected_indicators = [
            'Doji', 'Hammer', 'BullishEngulfing', 'BearishEngulfing',
            'InsideBar', 'OutsideBar'
        ]
        
        for indicator in expected_indicators:
            assert indicator in indicators, f"Pattern indicator {indicator} not calculated"
            assert not indicators[indicator].empty, f"Pattern indicator {indicator} is empty"
    
    def test_indicator_count(self):
        """Test total indicator count is 70+."""
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        
        # Count total indicators
        total_indicators = len(AVAILABLE_INDICATORS)
        
        # Should have at least 70 indicators
        assert total_indicators >= 70, f"Only {total_indicators} indicators, expected 70+"
        
        print(f"Total indicators available: {total_indicators}")


class TestTechnicalAnalysis:
    """Test technical analysis endpoints."""
    
    @pytest.fixture
    def sample_df(self):
        """Create sample OHLCV DataFrame for testing."""
        dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
        # Create some realistic price movements
        import numpy as np
        np.random.seed(42)
        
        base_price = 100
        returns = np.random.normal(0.001, 0.02, 50)
        prices = [base_price]
        
        for ret in returns:
            prices.append(prices[-1] * (1 + ret))
        
        return pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * 1.02 for p in prices],
            'low': [p * 0.98 for p in prices],
            'close': prices,
            'volume': [1000000 + i * 10000 for i in range(50)]
        })
    
    def test_pivot_points_calculation(self, sample_df):
        """Test pivot points calculation."""
        # Test standard pivots
        pivots = _calculate_pivots(sample_df, "standard", 20)
        
        required_keys = ['pivot', 'support_1', 'support_2', 'resistance_1', 'resistance_2']
        for key in required_keys:
            assert key in pivots, f"Pivot key {key} missing"
            assert pivots[key] > 0, f"Pivot {key} should be positive"
        
        # Test Fibonacci pivots
        fib_pivots = _calculate_pivots(sample_df, "fibonacci", 20)
        for key in required_keys:
            assert key in fib_pivots, f"Fibonacci pivot key {key} missing"
        
        # Test Woodie pivots
        woodie_pivots = _calculate_pivots(sample_df, "woodie", 20)
        for key in required_keys:
            assert key in woodie_pivots, f"Woodie pivot key {key} missing"
        
        # Test Camarilla pivots
        camarilla_pivots = _calculate_pivots(sample_df, "camarilla", 20)
        required_camarilla = ['pivot', 'support_1', 'support_2', 'support_3', 
                           'resistance_1', 'resistance_2', 'resistance_3']
        for key in required_camarilla:
            assert key in camarilla_pivots, f"Camarilla pivot key {key} missing"
    
    def test_fibonacci_retracements(self, sample_df):
        """Test Fibonacci retracement calculation."""
        # Test with auto-detect
        fib = _calculate_fibonacci(sample_df, None, None, "up")
        
        required_keys = ['swing_high', 'swing_low', 'retracements', 'extensions']
        for key in required_keys:
            assert key in fib, f"Fibonacci key {key} missing"
        
        # Check retracement levels
        retracements = fib['retracements']
        expected_levels = ['0.0%', '23.6%', '38.2%', '50.0%', '61.8%', '78.6%', '100.0%']
        for level in expected_levels:
            assert level in retracements, f"Retracement level {level} missing"
        
        # Check extension levels
        extensions = fib['extensions']
        expected_extensions = ['127.2%', '161.8%', '200.0%', '261.8%']
        for ext in expected_extensions:
            assert ext in extensions, f"Extension level {ext} missing"
    
    def test_pattern_detection(self, sample_df):
        """Test chart pattern detection."""
        patterns = _detect_patterns(sample_df, [], 50)
        
        # Should detect some patterns
        assert len(patterns) > 0, "No patterns detected"
        
        # Check pattern structure
        for pattern in patterns:
            required_keys = ['type', 'direction', 'strength', 'start_index', 'end_index', 'confidence']
            for key in required_keys:
                assert key in pattern, f"Pattern missing key {key}"
                assert pattern[key] is not None, f"Pattern key {key} is None"
    
    def test_market_sentiment_analysis(self, sample_df):
        """Test market sentiment analysis."""
        sentiment = _analyze_sentiment(sample_df)
        
        # Check sentiment structure
        required_keys = ['sentiment', 'score', 'factors', 'indicators_used', 'technical_summary']
        for key in required_keys:
            assert key in sentiment, f"Sentiment missing key {key}"
        
        # Check sentiment value
        valid_sentiments = [
            'very_bullish', 'bullish', 'neutral', 'bearish', 'very_bearish'
        ]
        assert sentiment['sentiment'] in valid_sentiments, f"Invalid sentiment value"
        
        # Check technical summary
        tech_summary = sentiment['technical_summary']
        assert 'trend' in tech_summary, "Missing trend in technical summary"
        assert 'volume_status' in tech_summary, "Missing volume status in technical summary"


class TestConnectivityFixes:
    """Test connectivity fixes for OpenAlgo and Playwright."""
    
    def test_openalgo_host_config(self):
        """Test OpenAlgo host configuration fix."""
        # This test would verify the fix-openalgo-host.sh script
        # For now, just check if the script exists and is executable
        import os
        
        script_path = "scripts/fix-openalgo-host.sh"
        assert os.path.exists(script_path), f"Script {script_path} not found"
        
        # Check if script is executable (on Unix systems)
        if os.name != 'nt':  # Not Windows
            assert os.access(script_path, os.X_OK), f"Script {script_path} not executable"
    
    def test_dockerfile_playwright_fix(self):
        """Test Dockerfile Playwright installation fix."""
        import os
        
        dockerfile_path = "Dockerfile"
        assert os.path.exists(dockerfile_path), "Dockerfile not found"
        
        # Read Dockerfile and check for Playwright installation
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Should install Playwright before user switch
        assert "playwright install chromium" in content, "Playwright installation not found in Dockerfile"
        assert "USER velox" in content, "User switch not found in Dockerfile"
        
        # Check order: install before user switch
        install_pos = content.find("playwright install chromium")
        user_pos = content.find("USER velox")
        assert install_pos < user_pos, "Playwright should be installed before user switch"


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.asyncio
    async def test_indicator_calculation_pipeline(self):
        """Test complete indicator calculation pipeline."""
        # Create sample data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        df = pd.DataFrame({
            'timestamp': dates,
            'open': [100 + i * 0.1 for i in range(100)],
            'high': [101 + i * 0.1 for i in range(100)],
            'low': [99 + i * 0.1 for i in range(100)],
            'close': [100.5 + i * 0.1 for i in range(100)],
            'volume': [1000000 + i * 1000 for i in range(100)]
        })
        
        # Test indicator service
        service = IndicatorService()
        
        # Calculate all indicators
        all_indicators = service.calculate_all_indicators(df)
        
        # Should have 70+ indicators
        assert len(all_indicators) >= 70, f"Only {len(all_indicators)} indicators calculated"
        
        # Check each category has indicators
        categories = {
            'volume': 0,
            'volatility': 0,
            'trend': 0,
            'momentum': 0,
            'statistical': 0,
            'pattern': 0,
            'others': 0
        }
        
        from app.api.v1.endpoints.indicators import AVAILABLE_INDICATORS
        for indicator_name in all_indicators.keys():
            if indicator_name in AVAILABLE_INDICATORS:
                category = AVAILABLE_INDICATORS[indicator_name]['category']
                if category in categories:
                    categories[category] += 1
        
        # Each category should have indicators
        for category, count in categories.items():
            assert count > 0, f"No indicators found for category {category}"
        
        print(f"Indicator counts by category: {categories}")
    
    def test_api_endpoint_structure(self):
        """Test if all API endpoints are properly structured."""
        from app.api.v1.router import api_router
        
        # Check if router has routes
        assert api_router is not None, "API router not initialized"
        
        # Get all routes
        routes = api_router.routes
        
        # Should have routes for indicators, analysis, etc.
        route_paths = [route.path for route in routes]
        
        # Check for main endpoint categories
        expected_prefixes = [
            '/indicators',
            '/analysis',
            '/option-chain',
            '/support-resistance',
            '/candles',
            '/ws'
        ]
        
        for prefix in expected_prefixes:
            assert any(prefix in path for path in route_paths), f"Missing routes for {prefix}"


if __name__ == "__main__":
    # Run specific tests
    pytest.main([__file__, "-v", "--tb=short"])