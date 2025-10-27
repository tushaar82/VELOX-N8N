# Phase 8: API Endpoints - Option Chain & WebSocket

## Overview
Create REST API endpoints for option chain data and WebSocket streaming endpoints.

## Goals
- Implement option chain fetching endpoints
- Create WebSocket streaming endpoint
- Handle real-time subscriptions
- Implement metadata endpoints

## Dependencies
- Phase 5 and Phase 6 must be completed

## File Changes

### app/api/v1/endpoints/option_chain.py (NEW)
**References:** app/schemas/option_chain.py, app/services/option_chain.py

Create option chain router with endpoints:

1. POST /fetch - Fetch option chain data:
   - Accept OptionChainRequest from app/schemas/option_chain.py
   - Use OptionChainService from app/services/option_chain.py to scrape NSE data
   - Return OptionChainResponse with strikes, OI, volume, LTP, IV
   - Handle both index (NIFTY, BANKNIFTY) and equity symbols

2. POST /fetch-index - Convenience endpoint for index option chains:
   - Hardcoded is_index=True
   - Accept symbol parameter
   - Return option chain data

3. POST /fetch-stock - Convenience endpoint for stock option chains:
   - Hardcoded is_index=False
   - Accept symbol parameter
   - Return option chain data

4. GET /supported-symbols - List supported index symbols:
   - Return list of common indices (NIFTY, BANKNIFTY, FINNIFTY, etc.)

Add rate limiting consideration (NSE may block excessive requests)
Add caching for option chain data (short TTL, e.g., 30 seconds)
Add proper error handling for Playwright failures and NSE API errors

### app/api/v1/endpoints/websocket.py (NEW)
**References:** app/services/websocket_manager.py, app/schemas/indicators.py, app/services/tick_stream.py

Create WebSocket router with endpoint:

1. WebSocket /stream - Real-time tick and indicator updates:
   - Accept WebSocket connection
   - Use WebSocketManager from app/services/websocket_manager.py
   - Handle connection lifecycle (connect, disconnect)
   - Accept subscription messages in JSON format:
     - {"action": "subscribe", "symbols": ["AAPL", "MSFT"], "timeframes": ["1m", "5m"], "indicators": ["RSI", "MACD"]}
     - {"action": "unsubscribe", "symbols": ["AAPL"]}
   - Validate subscription requests using WebSocketSubscription from app/schemas/indicators.py
   - Register client with TickStreamManager from app/services/tick_stream.py
   - Broadcast real-time updates:
     - Partial candle updates (tick by tick)
     - Completed candle updates
     - Indicator value updates
   - Send acknowledgment messages for subscriptions
   - Handle client disconnection gracefully
   - Implement error handling for invalid messages
   - Add connection limit enforcement

Message format for broadcasts:
- {"type": "candle", "symbol": "AAPL", "timeframe": "1m", "data": {...}}
- {"type": "indicator", "symbol": "AAPL", "timeframe": "1m", "indicators": {...}}
- {"type": "error", "message": "..."}
- {"type": "ack", "action": "subscribed", "symbols": [...]}

Note: Actual tick data ingestion mechanism needs to be implemented separately

### app/api/v1/endpoints/meta.py (NEW)
Create metadata router with endpoints:

1. GET /indicators - List all available indicators:
   - Return comprehensive list of 43+ indicators from ta library
   - Organize by category (Volume, Volatility, Trend, Momentum, Others)
   - Include indicator names, descriptions, required parameters

2. GET /timeframes - List supported timeframes:
   - Return list of supported interval strings
   - Include OpenAlgo-compatible formats (1m, 5m, 15m, 30m, 1h, 1d, etc.)

3. GET /exchanges - List supported exchanges:
   - Return list of exchanges supported by OpenAlgo (NSE, BSE, NFO, etc.)

4. GET /active-subscriptions - Get current WebSocket subscriptions:
   - Return count of active WebSocket connections
   - Return list of actively subscribed symbols and timeframes
   - Useful for monitoring and debugging

5. GET /system-status - System health and statistics:
   - Return service status
   - Return OpenAlgo connection status
   - Return active WebSocket connection count
   - Return memory usage statistics
   - Return tick processing statistics

All endpoints return JSON responses with appropriate status codes

## Completion Criteria
- [ ] Option chain endpoints fetch data successfully
- [ ] WebSocket connections work properly
- [ ] Subscriptions are handled correctly
- [ ] Real-time updates are broadcast to clients
- [ ] Metadata endpoints return accurate information
- [ ] Error handling is comprehensive

## Next Phase
Phase 9: Main Application & Router Integration
