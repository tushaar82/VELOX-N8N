"""
Simple import test for WebSocket Infrastructure (Phase 6).
Tests that modules can be imported and basic structure is correct.
"""

import sys

print("="*60)
print("PHASE 6: WEBSOCKET INFRASTRUCTURE IMPORT TESTS")
print("="*60)

tests = []

# Test 1: Check if pandas is available
print("\n1. Checking dependencies...")
try:
    import pandas as pd
    print("✓ pandas is available")
    PANDAS_AVAILABLE = True
except ImportError:
    print("⚠️  pandas not available (required for full functionality)")
    PANDAS_AVAILABLE = False

# Test 2: Import core modules (without pandas-dependent code)
print("\n2. Testing core imports...")
try:
    from app.core.config import get_settings
    from app.core.logging import get_logger
    from app.utils.timeframes import normalize_timeframe
    print("✓ Core modules imported")
    tests.append(("Core modules", True))
except Exception as e:
    print(f"✗ Core import failed: {e}")
    tests.append(("Core modules", False))

# Test 3: Import schemas
print("\n3. Testing schema imports...")
try:
    from app.schemas.candles import PartialCandle
    from app.schemas.indicators import WebSocketMessage, WebSocketSubscription
    print("✓ Schema modules imported")
    tests.append(("Schema modules", True))
except Exception as e:
    print(f"✗ Schema import failed: {e}")
    tests.append(("Schema modules", False))

# Test 4: Try importing services (may fail without pandas)
print("\n4. Testing service imports...")
if PANDAS_AVAILABLE:
    try:
        from app.services.tick_stream import TickStreamService
        from app.services.websocket_manager import WebSocketManager
        print("✓ Service modules imported")
        tests.append(("Service modules", True))
    except Exception as e:
        print(f"✗ Service import failed: {e}")
        tests.append(("Service modules", False))
else:
    print("⚠️  Skipping service imports (pandas required)")
    tests.append(("Service modules (skipped)", None))

# Test 5: Check file structure
print("\n5. Checking file structure...")
try:
    import os
    files_to_check = [
        "app/services/tick_stream.py",
        "app/services/websocket_manager.py",
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✓ {file_path} ({size} bytes)")
        else:
            print(f"  ✗ {file_path} NOT FOUND")
            all_exist = False
    
    tests.append(("File structure", all_exist))
except Exception as e:
    print(f"✗ File check failed: {e}")
    tests.append(("File structure", False))

# Test 6: Verify code structure (without executing)
print("\n6. Verifying code structure...")
try:
    with open("app/services/tick_stream.py", "r") as f:
        tick_stream_code = f.read()
    
    with open("app/services/websocket_manager.py", "r") as f:
        websocket_code = f.read()
    
    # Check for key classes
    checks = [
        ("TickData class", "class TickData" in tick_stream_code),
        ("CandleAggregator class", "class CandleAggregator" in tick_stream_code),
        ("TickStreamService class", "class TickStreamService" in tick_stream_code),
        ("WebSocketConnection class", "class WebSocketConnection" in websocket_code),
        ("WebSocketManager class", "class WebSocketManager" in websocket_code),
        ("get_tick_stream_service", "def get_tick_stream_service" in tick_stream_code),
        ("get_websocket_manager", "def get_websocket_manager" in websocket_code),
    ]
    
    all_present = True
    for name, present in checks:
        status = "✓" if present else "✗"
        print(f"  {status} {name}")
        if not present:
            all_present = False
    
    tests.append(("Code structure", all_present))
except Exception as e:
    print(f"✗ Code verification failed: {e}")
    tests.append(("Code structure", False))

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

for name, passed in tests:
    if passed is True:
        status = "✓ PASSED"
    elif passed is False:
        status = "✗ FAILED"
    else:
        status = "⚠️  SKIPPED"
    print(f"{name:35s}: {status}")

# Count results
core_tests = [t for t in tests if t[1] is not None]
core_passed = all(result[1] for result in core_tests if result[1] is not None)

print("\n" + "="*60)
if core_passed:
    print("🎉 All core tests PASSED!")
    print("\nWebSocket infrastructure files created successfully:")
    print("  ✓ app/services/tick_stream.py")
    print("  ✓ app/services/websocket_manager.py")
    print("\nKey classes implemented:")
    print("  ✓ TickData - Individual tick representation")
    print("  ✓ CandleAggregator - Tick-to-candle aggregation")
    print("  ✓ TickStreamService - Multi-symbol/timeframe management")
    print("  ✓ WebSocketConnection - Individual connection handler")
    print("  ✓ WebSocketManager - Connection pool management")
    
    if not PANDAS_AVAILABLE:
        print("\n⚠️  Note: Full functional tests require dependencies:")
        print("  pip install pandas numpy scipy")
        print("  Then run: python3 test_websocket_infra.py")
    
    exit_code = 0
else:
    print("❌ Some core tests FAILED!")
    exit_code = 1

print("="*60)
sys.exit(exit_code)
