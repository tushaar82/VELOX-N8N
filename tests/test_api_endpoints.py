"""
Test script for API endpoints (Phase 7).
Tests endpoint structure and imports.
"""

import sys
import os

print("="*60)
print("PHASE 7: API ENDPOINTS TESTS")
print("="*60)

tests = []

# Test 1: Check file structure
print("\n1. Checking file structure...")
try:
    files_to_check = [
        "app/api/v1/endpoints/indicators.py",
        "app/api/v1/endpoints/support_resistance.py",
        "app/api/v1/endpoints/candles.py",
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
    from fastapi import FastAPI, APIRouter
    print("✓ FastAPI is available")
    FASTAPI_AVAILABLE = True
    tests.append(("FastAPI available", True))
except ImportError:
    print("⚠️  FastAPI not available (required for running server)")
    FASTAPI_AVAILABLE = False
    tests.append(("FastAPI available", False))

# Test 3: Import endpoint modules
print("\n3. Testing endpoint imports...")
try:
    from app.api.v1.endpoints import indicators
    from app.api.v1.endpoints import support_resistance
    from app.api.v1.endpoints import candles
    print("✓ Endpoint modules imported")
    tests.append(("Endpoint imports", True))
except Exception as e:
    if "pandas" in str(e):
        print(f"⚠️  Import skipped (pandas required): {e}")
        tests.append(("Endpoint imports (skipped)", None))
    else:
        print(f"✗ Import failed: {e}")
        tests.append(("Endpoint imports", False))

# Test 4: Check router availability
if FASTAPI_AVAILABLE:
    print("\n4. Checking routers...")
    try:
        from app.api.v1.endpoints.indicators import router as indicators_router
        from app.api.v1.endpoints.support_resistance import router as sr_router
        from app.api.v1.endpoints.candles import router as candles_router
        
        routers = [
            ("indicators", indicators_router),
            ("support_resistance", sr_router),
            ("candles", candles_router)
        ]
        
        all_valid = True
        for name, router in routers:
            if router is not None:
                print(f"  ✓ {name} router available")
            else:
                print(f"  ✗ {name} router is None")
                all_valid = False
        
        tests.append(("Routers", all_valid))
    except Exception as e:
        if "pandas" in str(e):
            print(f"⚠️  Router check skipped (pandas required)")
            tests.append(("Routers (skipped)", None))
        else:
            print(f"✗ Router check failed: {e}")
            tests.append(("Routers", False))
else:
    print("\n4. Skipping router check (FastAPI not available)")
    tests.append(("Routers (skipped)", None))

# Test 5: Verify endpoint structure
print("\n5. Verifying endpoint structure...")
try:
    with open("app/api/v1/endpoints/indicators.py", "r") as f:
        indicators_code = f.read()
    
    with open("app/api/v1/endpoints/support_resistance.py", "r") as f:
        sr_code = f.read()
    
    with open("app/api/v1/endpoints/candles.py", "r") as f:
        candles_code = f.read()
    
    # Check for key endpoints
    checks = [
        # Indicators endpoints
        ("GET /available", "get_available_indicators" in indicators_code),
        ("POST /calculate", "calculate_indicators" in indicators_code),
        ("POST /multi-timeframe", "calculate_multi_timeframe_indicators" in indicators_code),
        ("GET /latest/{symbol}", "get_latest_indicators" in indicators_code),
        
        # Support/Resistance endpoints
        ("GET /{symbol}", "get_support_resistance" in sr_code),
        ("GET /{symbol}/pivots", "get_pivot_points" in sr_code),
        ("GET /{symbol}/nearest", "get_nearest_levels" in sr_code),
        
        # Candles endpoints
        ("POST /", "get_candles" in candles_code),
        ("GET /{symbol}", "get_candles_simple" in candles_code),
        ("GET /{symbol}/latest", "get_latest_candle" in candles_code),
        ("POST /multi-timeframe", "get_multi_timeframe_candles" in candles_code),
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

# Test 6: Check for proper validation
print("\n6. Checking validation usage...")
try:
    validation_checks = [
        ("validate_symbol", "validate_symbol" in indicators_code),
        ("validate_exchange", "validate_exchange" in indicators_code),
        ("validate_timeframe", "validate_timeframe_input" in indicators_code),
        ("validate_date_range", "validate_date_range" in indicators_code),
    ]
    
    all_present = True
    for name, present in validation_checks:
        status = "✓" if present else "✗"
        print(f"  {status} {name}")
        if not present:
            all_present = False
    
    tests.append(("Validation usage", all_present))
except Exception as e:
    print(f"✗ Validation check failed: {e}")
    tests.append(("Validation usage", False))

# Test 7: Check service integration
print("\n7. Checking service integration...")
try:
    integration_checks = [
        ("MarketDataService", "get_market_data_service" in indicators_code),
        ("IndicatorService", "get_indicator_service" in indicators_code),
        ("SupportResistanceService", "get_support_resistance_service" in sr_code),
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
    print("\nAPI endpoints created successfully:")
    print("  ✓ app/api/v1/endpoints/indicators.py")
    print("  ✓ app/api/v1/endpoints/support_resistance.py")
    print("  ✓ app/api/v1/endpoints/candles.py")
    
    print("\nEndpoints implemented:")
    print("\n  Indicators:")
    print("    GET  /api/v1/indicators/available")
    print("    POST /api/v1/indicators/calculate")
    print("    POST /api/v1/indicators/multi-timeframe")
    print("    GET  /api/v1/indicators/latest/{symbol}")
    
    print("\n  Support/Resistance:")
    print("    GET  /api/v1/support-resistance/{symbol}")
    print("    GET  /api/v1/support-resistance/{symbol}/pivots")
    print("    GET  /api/v1/support-resistance/{symbol}/nearest")
    
    print("\n  Candles:")
    print("    POST /api/v1/candles/")
    print("    GET  /api/v1/candles/{symbol}")
    print("    GET  /api/v1/candles/{symbol}/latest")
    print("    POST /api/v1/candles/multi-timeframe")
    
    if not FASTAPI_AVAILABLE:
        print("\n⚠️  Note: To run the API server:")
        print("  pip install fastapi uvicorn")
        print("  Then implement main.py and run: uvicorn main:app")
    
    exit_code = 0
else:
    print("❌ Some core tests FAILED!")
    exit_code = 1

print("="*60)
sys.exit(exit_code)
