"""
Test script for Option Chain Service (Phase 5).
Tests import, instantiation, and parsing logic.
"""

import sys
import asyncio
from datetime import datetime

print("="*60)
print("PHASE 5: OPTION CHAIN SERVICE TESTS")
print("="*60)

# Test 1: Import test
print("\n1. Testing imports...")
try:
    from app.services.option_chain import OptionChainService, get_option_chain_service
    from app.schemas.option_chain import OptionChainResponse, OptionData
    print("✓ Imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Check Playwright availability
print("\n2. Checking Playwright availability...")
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
    print("✓ Playwright is installed")
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not installed")
    print("   Install with: pip install playwright")
    print("   Then run: playwright install chromium")

# Test 3: Service instantiation
print("\n3. Testing service instantiation...")
try:
    service = OptionChainService()
    print("✓ OptionChainService instantiated")
except Exception as e:
    print(f"✗ Instantiation failed: {e}")
    sys.exit(1)

# Test 4: Test parsing with mock data
print("\n4. Testing parse_option_chain_data() with mock data...")
try:
    # Create mock NSE API response
    mock_data = {
        "records": {
            "expiryDates": ["25-Jan-2024", "01-Feb-2024"],
            "underlyingValue": 21530.50,
            "data": [
                {
                    "strikePrice": 21500,
                    "CE": {
                        "openInterest": 1500000,
                        "totalTradedVolume": 50000,
                        "lastPrice": 125.50,
                        "impliedVolatility": 18.5,
                        "changeinOpenInterest": 25000,
                        "bidprice": 125.00,
                        "askPrice": 126.00
                    },
                    "PE": {
                        "openInterest": 2000000,
                        "totalTradedVolume": 75000,
                        "lastPrice": 110.25,
                        "impliedVolatility": 19.2,
                        "changeinOpenInterest": 30000,
                        "bidprice": 110.00,
                        "askPrice": 110.50
                    }
                },
                {
                    "strikePrice": 21550,
                    "CE": {
                        "openInterest": 1200000,
                        "totalTradedVolume": 40000,
                        "lastPrice": 95.75,
                        "impliedVolatility": 17.8,
                        "changeinOpenInterest": 20000,
                        "bidprice": 95.50,
                        "askPrice": 96.00
                    },
                    "PE": {
                        "openInterest": 1800000,
                        "totalTradedVolume": 60000,
                        "lastPrice": 135.50,
                        "impliedVolatility": 20.1,
                        "changeinOpenInterest": 25000,
                        "bidprice": 135.00,
                        "askPrice": 136.00
                    }
                }
            ]
        }
    }
    
    # Parse the mock data
    response = service.parse_option_chain_data(mock_data, "NIFTY")
    
    print(f"✓ Parsing successful")
    print(f"  Symbol: {response.symbol}")
    print(f"  Underlying: {response.underlying_value}")
    print(f"  Expiry dates: {len(response.expiry_dates)}")
    print(f"  Options: {len(response.options)}")
    
    # Validate response
    assert response.symbol == "NIFTY"
    assert response.underlying_value == 21530.50
    assert len(response.options) == 2
    assert response.options[0].strike_price == 21500
    assert response.options[0].call_oi == 1500000
    assert response.options[0].put_oi == 2000000
    
    # Check PCR calculation
    if response.options[0].pcr_oi:
        print(f"  PCR (OI) for 21500: {response.options[0].pcr_oi:.2f}")
        assert response.options[0].pcr_oi > 0
    
    print("✓ All validations passed")
    
except Exception as e:
    print(f"✗ Parsing test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test analysis
print("\n5. Testing analyze_option_chain()...")
try:
    analysis = service.analyze_option_chain(response)
    
    print(f"✓ Analysis successful")
    print(f"  ATM Strike: {analysis.atm_strike}")
    print(f"  Max Pain: {analysis.max_pain}")
    print(f"  PCR (OI): {analysis.pcr_oi:.2f}")
    print(f"  PCR (Volume): {analysis.pcr_volume:.2f}")
    print(f"  Total Call OI: {analysis.total_call_oi:,}")
    print(f"  Total Put OI: {analysis.total_put_oi:,}")
    print(f"  Support Levels: {analysis.support_levels}")
    print(f"  Resistance Levels: {analysis.resistance_levels}")
    
    # Validate
    assert analysis.atm_strike in [21500, 21550]
    assert analysis.total_call_oi > 0
    assert analysis.total_put_oi > 0
    assert len(analysis.support_levels) > 0
    assert len(analysis.resistance_levels) > 0
    
    print("✓ All analysis validations passed")
    
except Exception as e:
    print(f"✗ Analysis test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test filtering
print("\n6. Testing filter_option_chain()...")
try:
    filtered = service.filter_option_chain(
        response,
        min_oi=1000000,
        strike_range=1
    )
    
    print(f"✓ Filtering successful")
    print(f"  Original options: {len(response.options)}")
    print(f"  Filtered options: {len(filtered.options)}")
    print(f"  Metadata: {filtered.metadata}")
    
    assert len(filtered.options) <= len(response.options)
    assert filtered.metadata.get('filtered') == True
    
    print("✓ Filtering validations passed")
    
except Exception as e:
    print(f"✗ Filtering test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Test max pain calculation
print("\n7. Testing _calculate_max_pain()...")
try:
    max_pain = service._calculate_max_pain(response.options, response.underlying_value)
    
    print(f"✓ Max pain calculation successful")
    print(f"  Max Pain Strike: {max_pain}")
    
    assert max_pain is not None
    assert max_pain in [opt.strike_price for opt in response.options]
    
    print("✓ Max pain validations passed")
    
except Exception as e:
    print(f"✗ Max pain test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Test support/resistance finding
print("\n8. Testing support/resistance level finding...")
try:
    support = service._find_support_levels(response.options, top_n=2)
    resistance = service._find_resistance_levels(response.options, top_n=2)
    
    print(f"✓ S/R level finding successful")
    print(f"  Support levels: {support}")
    print(f"  Resistance levels: {resistance}")
    
    assert len(support) <= 2
    assert len(resistance) <= 2
    
    print("✓ S/R validations passed")
    
except Exception as e:
    print(f"✗ S/R test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 9: Live fetch test (only if Playwright is available)
if PLAYWRIGHT_AVAILABLE:
    print("\n9. Testing live fetch (OPTIONAL - may fail due to NSE restrictions)...")
    print("   This test attempts to fetch real data from NSE...")
    print("   Note: NSE may block requests, this is expected behavior")
    
    async def test_live_fetch():
        try:
            # Try to fetch NIFTY option chain
            live_response = await service.fetch_option_chain("NIFTY", is_index=True, max_retries=1)
            
            print(f"✓ Live fetch successful!")
            print(f"  Symbol: {live_response.symbol}")
            print(f"  Underlying: {live_response.underlying_value}")
            print(f"  Total strikes: {len(live_response.options)}")
            print(f"  Expiry dates: {len(live_response.expiry_dates)}")
            
            if live_response.options:
                print(f"  Sample strike: {live_response.options[0].strike_price}")
                print(f"  Sample call OI: {live_response.options[0].call_oi}")
                print(f"  Sample put OI: {live_response.options[0].put_oi}")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Live fetch failed (this is expected): {e}")
            print("   NSE often blocks automated requests")
            print("   The parsing logic is still validated with mock data")
            return False
    
    # Run async test
    try:
        live_success = asyncio.run(test_live_fetch())
    except Exception as e:
        print(f"⚠️  Could not run live test: {e}")
        live_success = False
else:
    print("\n9. Skipping live fetch test (Playwright not installed)")
    live_success = None

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

tests = [
    ("Import test", True),
    ("Service instantiation", True),
    ("Parse mock data", True),
    ("Analyze option chain", True),
    ("Filter option chain", True),
    ("Max pain calculation", True),
    ("Support/Resistance finding", True),
]

# Add optional tests
optional_tests = [
    ("Playwright available", PLAYWRIGHT_AVAILABLE),
]

if live_success is not None:
    optional_tests.append(("Live fetch", live_success))

# Print core tests
for name, passed in tests:
    status = "✓ PASSED" if passed else "✗ FAILED"
    print(f"{name:35s}: {status}")

# Print optional tests
print("\nOptional Tests:")
for name, passed in optional_tests:
    if passed:
        status = "✓ AVAILABLE"
    elif passed is False:
        status = "⚠️  NOT AVAILABLE"
    else:
        status = "⚠️  SKIPPED"
    print(f"{name:35s}: {status}")

# Count results
core_passed = all(result[1] for result in tests)

print("\n" + "="*60)
if core_passed:
    print("🎉 All core tests PASSED!")
    print("\nThe option chain service is working correctly.")
    print("Mock data parsing, analysis, and filtering all work.")
    if not PLAYWRIGHT_AVAILABLE:
        print("\nTo enable live fetching:")
        print("  1. pip install playwright")
        print("  2. playwright install chromium")
    elif live_success is False:
        print("\nNote: Live fetching may fail due to NSE restrictions.")
        print("This is normal - NSE blocks many automated requests.")
    exit_code = 0
else:
    print("❌ Some core tests FAILED!")
    exit_code = 1

print("="*60)
sys.exit(exit_code)
