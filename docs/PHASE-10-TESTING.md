# Phase 10: Testing Infrastructure

## Overview
Create comprehensive test suite for all components.

## Goals
- Set up pytest infrastructure
- Test all services and endpoints
- Ensure code quality and reliability

## Dependencies
- Phase 9 must be completed

## File Changes

### tests/conftest.py (NEW)
Create pytest fixtures:
- test_app fixture that creates FastAPI TestClient
- mock_openalgo_client fixture for testing without real API calls
- sample_ohlcv_data fixture with test DataFrame
- mock_websocket fixture for WebSocket testing
- Override dependencies using app.dependency_overrides
- Setup and teardown for test isolation

### tests/test_indicators.py (NEW)
Create unit tests for indicator calculations:
- Test calculate_all_indicators with sample data
- Test individual indicator calculations (RSI, MACD, Bollinger Bands, etc.)
- Test error handling for insufficient data
- Test indicator parameter validation
- Test multi-timeframe calculations
- Use pytest parametrize for testing multiple indicators

### tests/test_support_resistance.py (NEW)
Create unit tests for support/resistance calculations:
- Test swing extrema detection
- Test level clustering algorithm
- Test ATR calculation
- Test recency and volume weighting
- Test with various market conditions (trending, ranging, volatile)
- Verify level strength calculations

### tests/test_tick_stream.py (NEW)
Create unit tests for tick aggregation:
- Test candle aggregation from ticks
- Test multi-timeframe aggregation
- Test out-of-order tick handling
- Test partial candle updates
- Test VWAP calculation
- Test bucket boundary handling
- Test gap handling (no ticks for a period)

### tests/test_api.py (NEW)
Create integration tests for API endpoints:
- Test POST /api/v1/indicators/calculate endpoint
- Test POST /api/v1/indicators/support-resistance endpoint
- Test POST /api/v1/option-chain/fetch endpoint (with mocked Playwright)
- Test WebSocket /api/v1/ws/stream connection and subscription
- Test error responses for invalid inputs
- Test rate limiting and validation
- Use TestClient for HTTP endpoints
- Use WebSocket test client for WebSocket endpoint

## Completion Criteria
- [ ] All tests pass
- [ ] Code coverage > 80%
- [ ] Integration tests work end-to-end
- [ ] Mock fixtures work correctly

## Next Phase
Phase 11: Deployment & Documentation
