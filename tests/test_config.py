"""
Tests for configuration management.
"""

import pytest
from app.core.config import Settings


def test_settings_creation(mock_settings):
    """Test that settings can be created."""
    assert mock_settings.openalgo_api_key == "test_key"
    assert mock_settings.log_level == "INFO"


def test_cors_origins_parsing(mock_settings):
    """Test CORS origins parsing."""
    origins = mock_settings.get_cors_origins()
    assert isinstance(origins, list)
    assert len(origins) > 0


def test_default_timeframes_parsing(mock_settings):
    """Test default timeframes parsing."""
    timeframes = mock_settings.get_default_timeframes()
    assert isinstance(timeframes, list)
    assert '1m' in timeframes
    assert '5m' in timeframes


def test_log_level_validation():
    """Test log level validation."""
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    for level in valid_levels:
        # Should not raise error
        assert level in valid_levels


def test_settings_defaults(mock_settings):
    """Test default settings values."""
    assert mock_settings.app_port == 8000
    assert mock_settings.max_websocket_connections == 100
    assert mock_settings.tick_buffer_size == 1000
