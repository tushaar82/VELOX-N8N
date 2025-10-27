# Phase 7: API Endpoints - Indicators

## Overview
Create REST API endpoints for indicator calculations and support/resistance analysis.

## Goals
- Implement indicator calculation endpoints
- Create support/resistance endpoints
- Add multi-timeframe analysis endpoints
- Provide metadata endpoints for available indicators

## Dependencies
- Phase 4 must be completed

## File Changes

### app/api/v1/endpoints/indicators.py (NEW)
**References:** app/schemas/indicators.py, app/services/market_data.py, app/services/indicators.py, app/services/support_resistance.py

Create indicators router with endpoints:

1. POST /calculate - Calculate indicators for historical data:
   - Accept IndicatorRequest from app/schemas/indicators.py
   - Use MarketDataService from app/services/market_data.py to fetch historical candles
   - Optionally append current forming candle if include_current=True
   - Use IndicatorService from app/services/indicators.py to calculate indicators
   - Return IndicatorResponse with all calculated indicators
   - Support indicator filtering via indicators parameter

2. POST /calculate-all - Calculate all 43+ indicators:
   - Similar to /calculate but forces all indicators
   - Returns comprehensive indicator data organized by category

3. GET /available - List all available indicators:
   - Return dict of indicator categories and names
   - Include parameter requirements for each indicator

4. POST /support-resistance - Calculate support and resistance levels:
   - Accept symbol, exchange, interval, lookback period
   - Use MarketDataService to fetch historical data
   - Use SupportResistanceService from app/services/support_resistance.py
   - Return SupportResistanceResponse with levels, strength, touches

5. POST /multi-timeframe - Calculate indicators across multiple timeframes:
   - Accept list of timeframes
   - Fetch data for each timeframe in parallel
   - Calculate indicators for each
   - Return dict keyed by timeframe

Add proper error handling, validation, and response models for all endpoints

## Completion Criteria
- [ ] All indicator endpoints work correctly
- [ ] Support/resistance calculation is accurate
- [ ] Multi-timeframe analysis returns data for all requested timeframes
- [ ] Error handling provides clear messages
- [ ] API documentation is auto-generated correctly

## Next Phase
Phase 8: API Endpoints - Option Chain & WebSocket
