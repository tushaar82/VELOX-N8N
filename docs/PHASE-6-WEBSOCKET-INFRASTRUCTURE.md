# Phase 6: Real-time WebSocket Infrastructure

## Overview
Build the real-time streaming infrastructure for tick-by-tick updates and WebSocket broadcasting.

## Goals
- Implement tick aggregation to candles
- Create WebSocket connection manager
- Build broadcasting system for real-time updates
- Support multi-symbol, multi-timeframe subscriptions

## Dependencies
- Phase 2 and Phase 4 must be completed

## File Changes

### app/services/tick_stream.py (NEW)
**References:** app/services/websocket_manager.py

Create TickStreamService for real-time tick aggregation:
- Define Tick dataclass with: symbol, timestamp, price, size
- Define CandleAggregator class (based on web search pattern) with:
  - __init__(interval_sec, on_candle_callback, on_partial_callback)
  - async on_tick(tick) method that aggregates ticks into OHLCV candles
  - _bucket_start(timestamp) to calculate candle bucket
  - Handle out-of-order ticks with configurable tolerance
  - Maintain per-symbol state dict with current candle data
  - Emit completed candles and partial updates
  - Calculate VWAP alongside OHLCV
- Create TickStreamManager class with:
  - Dict of aggregators per (symbol, timeframe) tuple
  - async subscribe(symbol, timeframes) to create aggregators
  - async unsubscribe(symbol, timeframes)
  - async process_tick(tick) to route to all relevant aggregators
  - Callback registration for candle completion
  - Integration with WebSocket broadcast from app/services/websocket_manager.py

### app/services/websocket_manager.py (NEW)
**References:** app/core/config.py, app/services/tick_stream.py

Create WebSocketManager class for connection management and broadcasting:
- Define ConnectionManager class with:
  - active_connections: Set[WebSocket]
  - subscriptions: Dict[WebSocket, dict] with symbol/timeframe/indicator subscriptions
  - async connect(websocket) to accept and register connection
  - disconnect(websocket) to remove connection and cleanup subscriptions
  - async update_subscription(websocket, subscription_data) to modify client subscriptions
  - async broadcast_to_subscribers(message, symbol, timeframe) to send updates to relevant clients
  - async send_personal_message(websocket, message)
  - Connection limit enforcement based on settings from app/core/config.py
- Create WebSocketBroadcaster class with:
  - Integration with TickStreamManager from app/services/tick_stream.py
  - async broadcast_candle_update(candle, indicators) to send real-time updates
  - async broadcast_indicator_update(symbol, timeframe, indicators)
  - Message formatting using orjson for performance
  - Error handling for disconnected clients
- Add heartbeat/ping mechanism to detect stale connections
- Add message queue per connection to handle backpressure

## Completion Criteria
- [ ] Tick aggregation works for multiple timeframes
- [ ] WebSocket connections can be established
- [ ] Subscriptions are managed correctly
- [ ] Broadcasting works for multiple clients
- [ ] Connection limits are enforced
- [ ] Heartbeat keeps connections alive

## Next Phase
Phase 7: API Endpoints - Indicators
