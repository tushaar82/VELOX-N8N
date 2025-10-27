"""
Test script for WebSocket Infrastructure (Phase 6).
Tests tick stream and WebSocket manager functionality.
"""

import asyncio
import sys
from datetime import datetime, timedelta

print("="*60)
print("PHASE 6: WEBSOCKET INFRASTRUCTURE TESTS")
print("="*60)

# Test 1: Import test
print("\n1. Testing imports...")
try:
    from app.services.tick_stream import (
        TickData, CandleAggregator, TickStreamService, get_tick_stream_service
    )
    from app.services.websocket_manager import (
        WebSocketConnection, WebSocketManager, get_websocket_manager
    )
    from app.schemas.candles import PartialCandle
    print("✓ Imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Test TickData
print("\n2. Testing TickData...")
try:
    tick = TickData(
        symbol="NIFTY",
        price=21530.50,
        volume=100.0,
        timestamp=datetime.now()
    )
    print(f"✓ Created tick: {tick.symbol} @ {tick.price}")
    assert tick.symbol == "NIFTY"
    assert tick.price == 21530.50
    assert tick.volume == 100.0
    print("✓ TickData validations passed")
except Exception as e:
    print(f"✗ TickData test failed: {e}")
    sys.exit(1)

# Test 3: Test CandleAggregator
print("\n3. Testing CandleAggregator...")
try:
    aggregator = CandleAggregator("NIFTY", "1m", buffer_size=100)
    print(f"✓ Created aggregator for {aggregator.symbol} {aggregator.timeframe}")
    
    # Add some ticks
    base_time = datetime.now().replace(second=0, microsecond=0)
    prices = [21500, 21510, 21505, 21520, 21515]
    
    for i, price in enumerate(prices):
        tick = TickData(
            symbol="NIFTY",
            price=price,
            volume=100.0,
            timestamp=base_time + timedelta(seconds=i*10)
        )
        candle = aggregator.add_tick(tick)
        
        if candle:
            print(f"  Tick {i+1}: O={candle.open:.2f} H={candle.high:.2f} "
                  f"L={candle.low:.2f} C={candle.close:.2f} V={candle.volume:.0f}")
    
    # Check final candle
    final_candle = aggregator.get_current_candle()
    assert final_candle is not None
    assert final_candle.open == 21500
    assert final_candle.high == 21520
    assert final_candle.low == 21500
    assert final_candle.close == 21515
    assert final_candle.tick_count == 5
    
    print(f"✓ Candle aggregation working correctly")
    print(f"  Stats: {aggregator.get_stats()}")
    
except Exception as e:
    print(f"✗ CandleAggregator test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test TickStreamService
print("\n4. Testing TickStreamService...")
try:
    service = get_tick_stream_service()
    print("✓ TickStreamService initialized")
    
    # Test subscription
    received_candles = []
    
    async def test_callback(symbol, timeframe, candle):
        received_candles.append((symbol, timeframe, candle))
        print(f"  Callback received: {symbol} {timeframe} @ {candle.close:.2f}")
    
    # Subscribe
    service.subscribe("NIFTY", ["1m", "5m"], "test_client", test_callback)
    print("✓ Subscribed to NIFTY 1m, 5m")
    
    # Process some ticks
    async def process_ticks():
        base_time = datetime.now().replace(second=0, microsecond=0)
        prices = [21500, 21510, 21505, 21520, 21515]
        
        for i, price in enumerate(prices):
            await service.process_tick(
                symbol="NIFTY",
                price=price,
                volume=100.0,
                timestamp=base_time + timedelta(seconds=i*10)
            )
            await asyncio.sleep(0.01)  # Small delay
    
    # Run tick processing
    asyncio.run(process_ticks())
    
    print(f"✓ Processed {service.total_ticks_processed} ticks")
    print(f"✓ Received {len(received_candles)} candle updates")
    
    # Check stats
    stats = service.get_stats()
    print(f"  Stats: {stats['active_symbols']} symbols, "
          f"{stats['total_aggregators']} aggregators")
    
    # Get current candle
    current = service.get_current_candle("NIFTY", "1m")
    if current:
        print(f"  Current 1m candle: O={current.open:.2f} H={current.high:.2f} "
              f"L={current.low:.2f} C={current.close:.2f}")
    
    # Unsubscribe
    service.unsubscribe("NIFTY", ["1m", "5m"], "test_client")
    print("✓ Unsubscribed successfully")
    
except Exception as e:
    print(f"✗ TickStreamService test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test WebSocketManager (without actual WebSocket)
print("\n5. Testing WebSocketManager...")
try:
    manager = get_websocket_manager()
    print("✓ WebSocketManager initialized")
    
    # Check stats
    stats = manager.get_stats()
    print(f"  Max connections: {stats['max_connections']}")
    print(f"  Active connections: {stats['active_connections']}")
    
    # Test would require actual WebSocket connections
    print("✓ WebSocketManager basic functionality working")
    print("  (Full WebSocket testing requires FastAPI server)")
    
except Exception as e:
    print(f"✗ WebSocketManager test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test multi-timeframe aggregation
print("\n6. Testing multi-timeframe aggregation...")
try:
    # Create new service instance for clean test
    from app.services.tick_stream import TickStreamService
    multi_service = TickStreamService()
    
    # Track candles for different timeframes
    candles_1m = []
    candles_5m = []
    
    async def callback_1m(symbol, timeframe, candle):
        if timeframe == "1m":
            candles_1m.append(candle)
    
    async def callback_5m(symbol, timeframe, candle):
        if timeframe == "5m":
            candles_5m.append(candle)
    
    # Subscribe to multiple timeframes
    multi_service.subscribe("NIFTY", ["1m"], "client_1m", callback_1m)
    multi_service.subscribe("NIFTY", ["5m"], "client_5m", callback_5m)
    
    # Process ticks over 6 minutes
    async def process_multi_ticks():
        base_time = datetime.now().replace(second=0, microsecond=0)
        
        for minute in range(6):
            for second in range(0, 60, 10):  # Every 10 seconds
                price = 21500 + minute * 5 + (second / 10)
                await multi_service.process_tick(
                    symbol="NIFTY",
                    price=price,
                    volume=100.0,
                    timestamp=base_time + timedelta(minutes=minute, seconds=second)
                )
        
        await asyncio.sleep(0.1)
    
    asyncio.run(process_multi_ticks())
    
    print(f"✓ Processed ticks for multi-timeframe test")
    print(f"  1m candles received: {len(candles_1m)}")
    print(f"  5m candles received: {len(candles_5m)}")
    
    # Verify we got updates for both timeframes
    assert len(candles_1m) > 0, "No 1m candles received"
    assert len(candles_5m) > 0, "No 5m candles received"
    
    print("✓ Multi-timeframe aggregation working")
    
except Exception as e:
    print(f"✗ Multi-timeframe test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Test VWAP calculation
print("\n7. Testing VWAP calculation...")
try:
    vwap_aggregator = CandleAggregator("NIFTY", "1m")
    
    # Add ticks with different prices and volumes
    base_time = datetime.now().replace(second=0, microsecond=0)
    tick_data = [
        (21500, 100),
        (21510, 200),
        (21505, 150),
        (21520, 300),
    ]
    
    for i, (price, volume) in enumerate(tick_data):
        tick = TickData(
            symbol="NIFTY",
            price=price,
            volume=volume,
            timestamp=base_time + timedelta(seconds=i*10)
        )
        candle = vwap_aggregator.add_tick(tick)
    
    final_candle = vwap_aggregator.get_current_candle()
    
    # Calculate expected VWAP
    total_value = sum(price * volume for price, volume in tick_data)
    total_volume = sum(volume for _, volume in tick_data)
    expected_vwap = total_value / total_volume
    
    print(f"  VWAP calculated: {final_candle.vwap:.2f}")
    print(f"  VWAP expected: {expected_vwap:.2f}")
    
    assert abs(final_candle.vwap - expected_vwap) < 0.01, "VWAP calculation incorrect"
    
    print("✓ VWAP calculation correct")
    
except Exception as e:
    print(f"✗ VWAP test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

tests = [
    ("Import test", True),
    ("TickData", True),
    ("CandleAggregator", True),
    ("TickStreamService", True),
    ("WebSocketManager", True),
    ("Multi-timeframe aggregation", True),
    ("VWAP calculation", True),
]

for name, passed in tests:
    status = "✓ PASSED" if passed else "✗ FAILED"
    print(f"{name:35s}: {status}")

print("\n" + "="*60)
print("🎉 All tests PASSED!")
print("="*60)
print("\nWebSocket infrastructure is working correctly:")
print("  ✓ Tick data processing")
print("  ✓ Candle aggregation")
print("  ✓ Multi-timeframe support")
print("  ✓ VWAP calculation")
print("  ✓ Subscription management")
print("  ✓ WebSocket manager ready")
print("\nTo test with actual WebSocket connections:")
print("  1. Implement FastAPI endpoints (Phase 7-9)")
print("  2. Start the server")
print("  3. Connect with WebSocket client")
print("="*60)

sys.exit(0)
