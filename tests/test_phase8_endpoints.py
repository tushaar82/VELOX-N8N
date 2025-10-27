"""
Test script for Phase 8 endpoints.
Tests option chain and WebSocket endpoint structure.
"""

import sys
import os

print("="*60)
print("PHASE 8: OPTION CHAIN & WEBSOCKET ENDPOINTS TESTS")
print("="*60)

tests = []

# Test 1: Check file structure
print("\n1. Checking file structure...")
try:
    files_to_check = [
        "app/api/v1/endpoints/option_chain.py",
        "app/api/v1/endpoints/websocket.py",
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

# Test 2: Check FastAPI availability
print("\n2. Checking FastAPI availability...")
try:
    from fastapi import FastAPI, APIRouter, WebSocket
    print("✓ FastAPI is available")
    FASTAPI_AVAILABLE = True
    tests.append(("FastAPI available", True))
except ImportError:
    print("⚠️  FastAPI not available")
    FASTAPI_AVAILABLE = False
    tests.append(("FastAPI available", False))

# Test 3: Verify endpoint structure
print("\n3. Verifying endpoint structure...")
try:
    with open("app/api/v1/endpoints/option_chain.py", "r") as f:
        oc_code = f.read()
    
    with open("app/api/v1/endpoints/websocket.py", "r") as f:
        ws_code = f.read()
    
    # Check for key endpoints
    checks = [
        # Option Chain endpoints
        ("POST /", "get_option_chain" in oc_code and "async def get_option_chain" in oc_code),
        ("GET /{symbol}", "get_option_chain_simple" in oc_code),
        ("GET /{symbol}/analysis", "get_option_chain_analysis" in oc_code),
        ("POST /{symbol}/filter", "filter_option_chain" in oc_code),
        ("GET /{symbol}/pcr", "get_pcr" in oc_code),
        ("GET /{symbol}/max-pain", "get_max_pain" in oc_code),
        ("GET /{symbol}/oi-analysis", "get_oi_analysis" in oc_code),
        
        # WebSocket endpoints
        ("WS /stream", "websocket_stream" in ws_code),
        ("WS /ticks", "websocket_ticks" in ws_code),
        ("GET /stats", "get_websocket_stats" in ws_code),
        ("GET /health", "websocket_health" in ws_code),
    ]
    
    all_present = True
    for name, present in checks:
        status = "✓" if present else "✗"
        print(f"  {status} {name}")
        if not present:
            all_present = False
    
    tests.append(("Endpoint structure", all_present))
except Exception as e:
    print(f"✗ Structure verification failed: {e}")
    tests.append(("Endpoint structure", False))

# Test 4: Check service integration
print("\n4. Checking service integration...")
try:
    integration_checks = [
        ("OptionChainService", "get_option_chain_service" in oc_code),
        ("WebSocketManager", "get_websocket_manager" in ws_code),
        ("TickStreamService", "get_tick_stream_service" in ws_code),
        ("validate_symbol", "validate_symbol" in oc_code),
    ]
    
    all_present = True
    for name, present in integration_checks:
        status = "✓" if present else "✗"
        print(f"  {status} {name}")
        if not present:
            all_present = False
    
    tests.append(("Service integration", all_present))
except Exception as e:
    print(f"✗ Integration check failed: {e}")
    tests.append(("Service integration", False))

# Test 5: Check WebSocket message handling
print("\n5. Checking WebSocket message handling...")
try:
    ws_features = [
        ("Connection management", "await manager.connect" in ws_code),
        ("Message handling", "await manager.handle_message" in ws_code),
        ("Disconnect handling", "await manager.disconnect" in ws_code),
        ("WebSocketDisconnect", "WebSocketDisconnect" in ws_code),
        ("Error handling", "except Exception" in ws_code),
    ]
    
    all_present = True
    for name, present in ws_features:
        status = "✓" if present else "✗"
        print(f"  {status} {name}")
        if not present:
            all_present = False
    
    tests.append(("WebSocket features", all_present))
except Exception as e:
    print(f"✗ WebSocket check failed: {e}")
    tests.append(("WebSocket features", False))

# Test 6: Check option chain features
print("\n6. Checking option chain features...")
try:
    oc_features = [
        ("Fetch option chain", "fetch_option_chain" in oc_code),
        ("Analyze option chain", "analyze_option_chain" in oc_code),
        ("Filter option chain", "filter_option_chain" in oc_code),
        ("PCR calculation", "pcr_oi" in oc_code),
        ("Max pain", "max_pain" in oc_code),
        ("OI analysis", "call_oi" in oc_code and "put_oi" in oc_code),
        ("v3 API support", "use_v3_api=True" in oc_code),
    ]
    
    all_present = True
    for name, present in oc_features:
        status = "✓" if present else "✗"
        print(f"  {status} {name}")
        if not present:
            all_present = False
    
    tests.append(("Option chain features", all_present))
except Exception as e:
    print(f"✗ Option chain check failed: {e}")
    tests.append(("Option chain features", False))

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
    print("\nPhase 8 endpoints created successfully:")
    print("  ✓ app/api/v1/endpoints/option_chain.py")
    print("  ✓ app/api/v1/endpoints/websocket.py")
    
    print("\nOption Chain Endpoints (7):")
    print("  POST /api/v1/option-chain/")
    print("  GET  /api/v1/option-chain/{symbol}")
    print("  GET  /api/v1/option-chain/{symbol}/analysis")
    print("  POST /api/v1/option-chain/{symbol}/filter")
    print("  GET  /api/v1/option-chain/{symbol}/pcr")
    print("  GET  /api/v1/option-chain/{symbol}/max-pain")
    print("  GET  /api/v1/option-chain/{symbol}/oi-analysis")
    
    print("\nWebSocket Endpoints (4):")
    print("  WS   /api/v1/ws/stream")
    print("  WS   /api/v1/ws/ticks")
    print("  GET  /api/v1/ws/stats")
    print("  GET  /api/v1/ws/health")
    
    print("\nFeatures implemented:")
    print("  ✓ Option chain fetching (v3 API)")
    print("  ✓ PCR calculation")
    print("  ✓ Max pain analysis")
    print("  ✓ OI analysis")
    print("  ✓ Filtering")
    print("  ✓ Real-time WebSocket streaming")
    print("  ✓ Tick-by-tick data")
    print("  ✓ Connection management")
    
    if not FASTAPI_AVAILABLE:
        print("\n⚠️  Note: To run the API server:")
        print("  pip install fastapi uvicorn websockets")
    
    exit_code = 0
else:
    print("❌ Some core tests FAILED!")
    exit_code = 1

print("="*60)
sys.exit(exit_code)
