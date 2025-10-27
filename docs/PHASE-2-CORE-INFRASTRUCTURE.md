# Phase 2: Core Infrastructure

## Overview
Build the core application infrastructure including configuration management, logging, and utility functions.

## Goals
- Implement configuration management
- Set up logging system
- Create utility functions for timeframes and validation
- Establish foundation for other services

## Dependencies
- Phase 1 must be completed

## File Changes

### app/core/config.py (NEW)
Define Settings class using pydantic-settings BaseSettings:
- openalgo_api_key: str (required)
- openalgo_host: str (default: http://127.0.0.1:5000)
- openalgo_version: str (default: v1)
- cors_origins: list[str] (parse from comma-separated string)
- log_level: str (default: INFO)
- max_websocket_connections: int (default: 100)
- tick_buffer_size: int (default: 1000)
- default_timeframes: list[str] (default: [1m, 5m, 15m, 1h, 1d])
- model_config with env_file=.env, case_sensitive=False

Create cached get_settings() function using lru_cache to return singleton Settings instance

### app/core/logging.py (NEW)
**References:** app/core/config.py

Configure application logging:
- Import logging, sys
- Create setup_logging() function that configures root logger with level from settings
- Set format with timestamp, level, module, message
- Add StreamHandler to stdout
- Create get_logger(name) helper function returning configured logger for module

### app/utils/timeframes.py (NEW)
Create timeframe utility functions:
- parse_timeframe(interval_str) to convert string (1m, 5m, 1h, 1d) to seconds
- validate_timeframe(interval_str) to check if timeframe is supported
- get_candle_count(start_date, end_date, interval) to calculate expected candle count
- normalize_timeframe(interval_str) to standardize format
- timeframe_to_pandas_freq(interval_str) to convert to pandas resample frequency
- Map of common timeframe aliases (1min -> 1m, 1hour -> 1h, etc.)

### app/utils/validators.py (NEW)
Create validation utility functions:
- validate_symbol(symbol) to check symbol format
- validate_exchange(exchange) to verify exchange is supported
- validate_date_range(start_date, end_date) to ensure valid date range
- validate_indicator_params(indicator_name, params) to check indicator-specific parameters
- sanitize_symbol(symbol) to clean and uppercase symbol strings
- validate_strike_price(strike) for option chain validation

## Completion Criteria
- [ ] Configuration loads from .env file correctly
- [ ] Logging outputs with proper format
- [ ] Timeframe utilities handle all supported formats
- [ ] Validators catch invalid inputs
- [ ] All utility functions have proper error handling

## Next Phase
Phase 3: Data Schemas
