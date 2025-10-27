"""
Test script for Phase 4 services.
Tests indicators and support/resistance calculations with sample data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import services
from app.services.indicators import IndicatorService
from app.services.support_resistance import SupportResistanceService


def generate_sample_data(num_candles=200):
    """Generate sample OHLCV data for testing."""
    print(f"Generating {num_candles} sample candles...")
    
    # Generate timestamps
    start_time = datetime.now() - timedelta(minutes=num_candles * 5)
    timestamps = [start_time + timedelta(minutes=i * 5) for i in range(num_candles)]
    
    # Generate price data with trend and noise
    base_price = 21500
    trend = np.linspace(0, 200, num_candles)  # Upward trend
    noise = np.random.normal(0, 50, num_candles)
    close_prices = base_price + trend + noise
    
    # Generate OHLC from close
    data = []
    for i, (ts, close) in enumerate(zip(timestamps, close_prices)):
        high = close + abs(np.random.normal(0, 20))
        low = close - abs(np.random.normal(0, 20))
        open_price = close + np.random.normal(0, 10)
        volume = abs(np.random.normal(1000000, 200000))
        
        data.append({
            'timestamp': ts,
            'open': open_price,
            'high': max(high, open_price, close),
            'low': min(low, open_price, close),
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    print(f"✓ Generated {len(df)} candles")
    print(f"  Price range: {df['low'].min():.2f} - {df['high'].max():.2f}")
    print(f"  Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    return df


def test_indicator_service():
    """Test the IndicatorService."""
    print("\n" + "="*60)
    print("Testing IndicatorService")
    print("="*60)
    
    # Generate sample data
    df = generate_sample_data(200)
    
    # Initialize service
    service = IndicatorService()
    print("\n✓ IndicatorService initialized")
    
    # Test calculating all indicators
    print("\n1. Testing calculate_all_indicators()...")
    try:
        indicators = service.calculate_all_indicators(df)
        print(f"✓ Calculated {len(indicators)} indicators")
        
        # Show some sample indicators
        print("\nSample indicator values (last 5):")
        for name in ['RSI', 'MACD', 'EMA_20', 'ATR', 'BB_High']:
            if name in indicators:
                values = indicators[name].tail(5).values
                print(f"  {name:15s}: {values}")
        
    except Exception as e:
        print(f"✗ Error calculating all indicators: {e}")
        return False
    
    # Test calculating specific indicators
    print("\n2. Testing calculate_specific_indicators()...")
    try:
        specific = service.calculate_specific_indicators(
            df,
            ['RSI', 'MACD', 'EMA_20', 'SMA_50']
        )
        print(f"✓ Calculated {len(specific)} specific indicators")
        
        # Verify RSI is in valid range
        rsi_values = specific['RSI'].dropna()
        print(f"  RSI range: {rsi_values.min():.2f} - {rsi_values.max():.2f}")
        assert rsi_values.min() >= 0 and rsi_values.max() <= 100, "RSI out of range!"
        print("  ✓ RSI values are valid (0-100)")
        
    except Exception as e:
        print(f"✗ Error calculating specific indicators: {e}")
        return False
    
    # Test formatting for response
    print("\n3. Testing format_indicators_for_response()...")
    try:
        formatted = service.format_indicators_for_response(specific)
        print(f"✓ Formatted {len(formatted)} indicators")
        print(f"  Type: {type(formatted)}")
        print(f"  RSI has {len(formatted['RSI'])} values")
        
    except Exception as e:
        print(f"✗ Error formatting indicators: {e}")
        return False
    
    print("\n✓ All IndicatorService tests passed!")
    return True


def test_support_resistance_service():
    """Test the SupportResistanceService."""
    print("\n" + "="*60)
    print("Testing SupportResistanceService")
    print("="*60)
    
    # Generate sample data
    df = generate_sample_data(200)
    
    # Initialize service
    service = SupportResistanceService()
    print("\n✓ SupportResistanceService initialized")
    
    # Test ATR calculation
    print("\n1. Testing calculate_atr()...")
    try:
        atr = service.calculate_atr(df, period=14)
        print(f"✓ Calculated ATR")
        print(f"  ATR mean: {atr.mean():.2f}")
        print(f"  ATR last: {atr.iloc[-1]:.2f}")
        
    except Exception as e:
        print(f"✗ Error calculating ATR: {e}")
        return False
    
    # Test finding swing extrema
    print("\n2. Testing find_swing_extrema()...")
    try:
        extrema = service.find_swing_extrema(df, window=3, prominence_mult=0.5)
        print(f"✓ Found {len(extrema)} swing extrema")
        support_count = len(extrema[extrema['type'] == 'support'])
        resistance_count = len(extrema[extrema['type'] == 'resistance'])
        print(f"  Support points: {support_count}")
        print(f"  Resistance points: {resistance_count}")
        
    except Exception as e:
        print(f"✗ Error finding swing extrema: {e}")
        return False
    
    # Test computing support/resistance levels
    print("\n3. Testing compute_support_resistance()...")
    try:
        response = service.compute_support_resistance(
            df,
            params={
                'symbol': 'TEST',
                'timeframe': '5m',
                'window': 3,
                'prominence_mult': 0.5,
                'max_levels': 5
            }
        )
        print(f"✓ Computed support/resistance levels")
        print(f"  Support levels: {len(response.support_levels)}")
        print(f"  Resistance levels: {len(response.resistance_levels)}")
        print(f"  Current price: {response.current_price:.2f}")
        print(f"  Tolerance: {response.tolerance:.2f}")
        
        # Show top levels
        if response.support_levels:
            print("\n  Top Support Levels:")
            for level in response.support_levels[:3]:
                print(f"    {level.price:.2f} (strength: {level.strength:.2f}, touches: {level.touches})")
        
        if response.resistance_levels:
            print("\n  Top Resistance Levels:")
            for level in response.resistance_levels[:3]:
                print(f"    {level.price:.2f} (strength: {level.strength:.2f}, touches: {level.touches})")
        
    except Exception as e:
        print(f"✗ Error computing S/R levels: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test pivot points
    print("\n4. Testing calculate_pivot_points()...")
    try:
        pivots = service.calculate_pivot_points(df, method='standard')
        print(f"✓ Calculated pivot points")
        print(f"  PP:  {pivots['PP']:.2f}")
        print(f"  R1:  {pivots['R1']:.2f}")
        print(f"  R2:  {pivots['R2']:.2f}")
        print(f"  R3:  {pivots['R3']:.2f}")
        print(f"  S1:  {pivots['S1']:.2f}")
        print(f"  S2:  {pivots['S2']:.2f}")
        print(f"  S3:  {pivots['S3']:.2f}")
        
    except Exception as e:
        print(f"✗ Error calculating pivot points: {e}")
        return False
    
    print("\n✓ All SupportResistanceService tests passed!")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("PHASE 4 SERVICE TESTS")
    print("="*60)
    
    results = []
    
    # Test IndicatorService
    results.append(("IndicatorService", test_indicator_service()))
    
    # Test SupportResistanceService
    results.append(("SupportResistanceService", test_support_resistance_service()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:30s}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())
