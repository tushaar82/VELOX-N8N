# Phase 4: Market Data & Indicator Services

## Overview
Implement core business logic for market data fetching and technical indicator calculations.

## Goals
- Integrate with OpenAlgo for historical data
- Implement all 43+ technical indicators using ta library
- Create support/resistance calculation service
- Build robust error handling for data services

## Dependencies
- Phase 3 must be completed

## File Changes

### app/services/market_data.py (NEW)
**References:** app/core/config.py, app/schemas/candles.py

Create MarketDataService class to wrap OpenAlgo client:
- Initialize with settings from app/core/config.py
- Import openalgo.orders.api
- Create async method fetch_historical_candles(symbol, exchange, interval, start_date, end_date) that calls OpenAlgo history API and returns pandas DataFrame
- Create async method fetch_current_quote(symbol, exchange) for latest price
- Add error handling for API failures
- Add method to convert OpenAlgo DataFrame to list of Candle models from app/schemas/candles.py
- Add method to validate and normalize timeframe strings (1m, 5m, 15m, 1h, 1d, etc.)
- Cache client instance as singleton

### app/services/indicators.py (NEW)
Create IndicatorService class for technical indicator calculations:
- Import ta library (all indicator classes)
- Create method calculate_all_indicators(df: pd.DataFrame) that:
  - Takes DataFrame with OHLCV columns
  - Calculates all 43+ indicators from ta library organized by category
  - Returns dict with indicator names as keys and Series/values as values
- Create method calculate_specific_indicators(df, indicator_list, params) for selective calculation
- Implement indicator categories:
  - Volume: MFI, ADI, OBV, CMF, ForceIndex, EaseOfMovement, VPT, NVI, VWAP
  - Volatility: ATR, BollingerBands, KeltnerChannel, DonchianChannel, UlcerIndex
  - Trend: SMA, EMA, WMA, MACD, ADX, VortexIndicator, TRIX, MassIndex, CCI, DPO, KST, Ichimoku, PSAR, STC, Aroon
  - Momentum: RSI, StochRSI, TSI, UltimateOscillator, StochasticOscillator, WilliamsR, AwesomeOscillator, KAMA, ROC, PPO, PVO
  - Others: DailyReturn, DailyLogReturn, CumulativeReturn
- Add error handling for insufficient data (NaN handling)
- Create method to format indicators for JSON response
- Add method calculate_indicators_realtime(candles, previous_indicators) for incremental updates

### app/services/support_resistance.py (NEW)
**References:** app/schemas/indicators.py

Create SupportResistanceService class (based on web search algorithm):
- Import scipy.signal.find_peaks, numpy, pandas
- Create method calculate_atr(df, period=14) for Average True Range
- Create method find_swing_extrema(df, window=3, prominence_mult=0.5) that:
  - Uses find_peaks on High prices for resistance candidates
  - Uses find_peaks on inverted Low prices for support candidates
  - Uses ATR-based dynamic prominence
  - Returns DataFrame with price, timestamp, type (S/R), volume
- Create method cluster_levels(points_df, df, half_life_bars=200, atr_mult=1.0) that:
  - Calculates tolerance based on ATR
  - Applies recency weighting (exponential decay)
  - Applies volume weighting
  - Clusters nearby levels using 1D streaming merge
  - Returns separate DataFrames for support and resistance levels
- Create main method compute_support_resistance(df, params) that:
  - Calls find_swing_extrema
  - Calls cluster_levels
  - Returns SupportResistanceResponse model from app/schemas/indicators.py
  - Includes level strength, touch count, last touch timestamp
- Add method to calculate classic pivot points as alternative
- Add method to filter top-N levels by strength

## Completion Criteria
- [ ] MarketDataService successfully fetches data from OpenAlgo
- [ ] All 43+ indicators calculate correctly
- [ ] Support/resistance levels are identified accurately
- [ ] Error handling works for edge cases
- [ ] Services can be instantiated and used independently

## Next Phase
Phase 5: Option Chain Service
