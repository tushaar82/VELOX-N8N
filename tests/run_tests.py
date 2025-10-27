"""
Test runner script for VELOX project.
Runs all tests and generates coverage report.
"""

import sys
import subprocess

print("="*60)
print("VELOX TEST SUITE")
print("="*60)

# Check if pytest is available
try:
    import pytest
    print("\n✓ pytest is available")
except ImportError:
    print("\n✗ pytest not found")
    print("Install with: pip install pytest pytest-asyncio pytest-cov")
    sys.exit(1)

# Run tests
print("\nRunning tests...")
print("-"*60)

# Run pytest with coverage if available
try:
    import pytest_cov
    # Run with coverage
    result = pytest.main([
        'tests/',
        '-v',
        '--tb=short',
        '--cov=app',
        '--cov-report=term-missing',
        '--cov-report=html'
    ])
except ImportError:
    # Run without coverage
    print("Note: pytest-cov not installed, running without coverage")
    result = pytest.main([
        'tests/',
        '-v',
        '--tb=short'
    ])

print("-"*60)

# Summary
if result == 0:
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nTest coverage report generated in htmlcov/index.html")
    sys.exit(0)
else:
    print("\n" + "="*60)
    print("❌ SOME TESTS FAILED")
    print("="*60)
    sys.exit(1)
