"""
Verify test structure and count test cases.
"""

import os
import sys

print("="*60)
print("PHASE 10: TEST VERIFICATION")
print("="*60)

tests = []

# Test 1: Check test directory structure
print("\n1. Checking test directory structure...")
try:
    test_files = [
        "tests/conftest.py",
        "tests/test_config.py",
        "tests/test_validators.py",
        "tests/test_timeframes.py",
        "pytest.ini",
        "run_tests.py"
    ]
    
    all_exist = True
    for file_path in test_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✓ {file_path} ({size} bytes)")
        else:
            print(f"  ✗ {file_path} NOT FOUND")
            all_exist = False
    
    tests.append(("Test file structure", all_exist))
except Exception as e:
    print(f"✗ File check failed: {e}")
    tests.append(("Test file structure", False))

# Test 2: Count test functions
print("\n2. Counting test functions...")
try:
    test_count = 0
    test_files_to_scan = [
        "tests/test_config.py",
        "tests/test_validators.py",
        "tests/test_timeframes.py"
    ]
    
    for file_path in test_files_to_scan:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                # Count functions starting with 'test_'
                count = content.count('def test_')
                test_count += count
                print(f"  {file_path}: {count} tests")
    
    print(f"\n  Total test functions: {test_count}")
    tests.append(("Test count", test_count > 0))
except Exception as e:
    print(f"✗ Test counting failed: {e}")
    tests.append(("Test count", False))

# Test 3: Check pytest configuration
print("\n3. Checking pytest configuration...")
try:
    with open("pytest.ini", 'r') as f:
        config = f.read()
    
    checks = [
        ("testpaths defined", "testpaths" in config),
        ("markers defined", "markers" in config),
        ("verbose output", "-v" in config),
    ]
    
    all_present = True
    for name, present in checks:
        status = "✓" if present else "✗"
        print(f"  {status} {name}")
        if not present:
            all_present = False
    
    tests.append(("Pytest configuration", all_present))
except Exception as e:
    print(f"✗ Config check failed: {e}")
    tests.append(("Pytest configuration", False))

# Test 4: Check fixtures
print("\n4. Checking test fixtures...")
try:
    with open("tests/conftest.py", 'r') as f:
        conftest = f.read()
    
    fixtures = [
        "sample_ohlcv_data",
        "sample_candle_dict",
        "sample_option_data",
        "mock_settings",
        "sample_symbols",
        "sample_timeframes",
        "sample_exchanges"
    ]
    
    all_present = True
    for fixture in fixtures:
        if f"def {fixture}" in conftest:
            print(f"  ✓ {fixture}")
        else:
            print(f"  ✗ {fixture} missing")
            all_present = False
    
    tests.append(("Test fixtures", all_present))
except Exception as e:
    print(f"✗ Fixture check failed: {e}")
    tests.append(("Test fixtures", False))

# Test 5: Check test classes
print("\n5. Checking test classes...")
try:
    test_classes = []
    
    for file_path in test_files_to_scan:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                # Count classes starting with 'Test'
                import re
                classes = re.findall(r'class (Test\w+)', content)
                test_classes.extend(classes)
    
    print(f"  Found {len(test_classes)} test classes:")
    for cls in test_classes[:10]:  # Show first 10
        print(f"    - {cls}")
    
    if len(test_classes) > 10:
        print(f"    ... and {len(test_classes) - 10} more")
    
    tests.append(("Test classes", len(test_classes) > 0))
except Exception as e:
    print(f"✗ Class check failed: {e}")
    tests.append(("Test classes", False))

# Test 6: Check if pytest is available
print("\n6. Checking pytest availability...")
try:
    import pytest
    print(f"  ✓ pytest {pytest.__version__} is installed")
    tests.append(("Pytest available (optional)", True))
except ImportError:
    print("  ⚠️  pytest not installed (optional)")
    print("     Install with: pip install pytest pytest-asyncio")
    tests.append(("Pytest available (optional)", None))

# Summary
print("\n" + "="*60)
print("TEST VERIFICATION SUMMARY")
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
    print("🎉 All verification checks PASSED!")
    print("\nTest suite is ready:")
    print(f"  ✓ {test_count} test functions")
    print(f"  ✓ {len(test_classes)} test classes")
    print("  ✓ Fixtures configured")
    print("  ✓ Pytest configuration ready")
    
    print("\nTo run tests:")
    print("  python run_tests.py")
    print("  or")
    print("  pytest tests/ -v")
    
    exit_code = 0
else:
    print("❌ Some verification checks FAILED!")
    exit_code = 1

print("="*60)
sys.exit(exit_code)
