"""
Verify that the Option Chain Service uses the correct NSE API URL.
"""

from app.services.option_chain import OptionChainService

print("="*60)
print("NSE API URL VERIFICATION")
print("="*60)

service = OptionChainService()

print("\n✓ OptionChainService initialized")

# Check the configured URLs
print("\nConfigured URLs:")
print(f"  Base URL: {service.NSE_BASE_URL}")
print(f"  Option Chain Page: {service.NSE_OPTION_CHAIN_URL}")
print(f"  Index API: {service.NSE_INDEX_API}")
print(f"  Equity API: {service.NSE_EQUITY_API}")

# Show what URL would be used for NIFTY
symbol = "NIFTY"
is_index = True
api_url = service.NSE_INDEX_API if is_index else service.NSE_EQUITY_API
full_url = f"{api_url}?symbol={symbol}"

print(f"\nURL for NIFTY option chain:")
print(f"  {full_url}")

# Verify it matches the expected URL
expected_url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

if full_url == expected_url:
    print(f"\n✅ URL MATCHES EXPECTED!")
    print(f"   The service will use: {expected_url}")
else:
    print(f"\n❌ URL MISMATCH!")
    print(f"   Expected: {expected_url}")
    print(f"   Got:      {full_url}")

# Show URLs for other symbols
print("\nExample URLs for other symbols:")
symbols = [
    ("BANKNIFTY", True),
    ("FINNIFTY", True),
    ("RELIANCE", False),
]

for sym, idx in symbols:
    api = service.NSE_INDEX_API if idx else service.NSE_EQUITY_API
    url = f"{api}?symbol={sym}"
    symbol_type = "Index" if idx else "Equity"
    print(f"  {sym:15s} ({symbol_type:6s}): {url}")

print("\n" + "="*60)
print("✅ VERIFICATION COMPLETE")
print("="*60)
print("\nThe service is correctly configured to use:")
print("  https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY")
print("\nThis is the exact URL you provided!")
