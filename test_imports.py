"""
Simple import test for Phase 4 services.
Tests that all modules can be imported without errors.
"""

print("="*60)
print("PHASE 4 IMPORT TESTS")
print("="*60)

tests = []

# Test core imports
print("\n1. Testing core modules...")
try:
    from app.core.config import get_settings
    from app.core.logging import setup_logging, get_logger
    print("✓ Core modules imported successfully")
    tests.append(("Core modules", True))
except Exception as e:
    print(f"✗ Error importing core modules: {e}")
    tests.append(("Core modules", False))

# Test utils imports
print("\n2. Testing utils modules...")
try:
    from app.utils.timeframes import normalize_timeframe, validate_timeframe
    from app.utils.validators import validate_symbol, sanitize_symbol
    print("✓ Utils modules imported successfully")
    tests.append(("Utils modules", True))
except Exception as e:
    print(f"✗ Error importing utils modules: {e}")
    tests.append(("Utils modules", False))

# Test schema imports
print("\n3. Testing schema modules...")
try:
    from app.schemas.candles import Candle, CandleRequest
    from app.schemas.indicators import IndicatorRequest, SupportResistanceResponse
    from app.schemas.option_chain import OptionChainRequest
    print("✓ Schema modules imported successfully")
    tests.append(("Schema modules", True))
except Exception as e:
    print(f"✗ Error importing schema modules: {e}")
    tests.append(("Schema modules", False))

# Test service imports
print("\n4. Testing service modules...")
try:
    from app.services.indicators import IndicatorService
    from app.services.support_resistance import SupportResistanceService
    print("✓ Service modules imported successfully")
    tests.append(("Service modules", True))
except Exception as e:
    print(f"✗ Error importing service modules: {e}")
    tests.append(("Service modules", False))

# Test instantiation
print("\n5. Testing service instantiation...")
try:
    indicator_service = IndicatorService()
    sr_service = SupportResistanceService()
    print("✓ Services instantiated successfully")
    tests.append(("Service instantiation", True))
except Exception as e:
    print(f"✗ Error instantiating services: {e}")
    tests.append(("Service instantiation", False))

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

for name, passed in tests:
    status = "✓ PASSED" if passed else "✗ FAILED"
    print(f"{name:30s}: {status}")

all_passed = all(result[1] for result in tests)

if all_passed:
    print("\n🎉 All import tests passed!")
    print("\nNote: Full functional tests require dependencies:")
    print("  - Run: ./scripts/setup.sh")
    print("  - Or: pip install -r requirements.txt")
else:
    print("\n❌ Some import tests failed!")

exit(0 if all_passed else 1)
