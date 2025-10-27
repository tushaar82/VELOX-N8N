# VELOX Technical Indicators - Complete List

## Overview
VELOX API provides **77 technical indicators** across 5 categories, all accessible via REST API endpoints.

## API Endpoints

### 1. Get Available Indicators
```
GET /api/v1/indicators/available
```
Returns metadata for all 77 indicators including parameters, categories, and descriptions.

### 2. Calculate Indicators
```
POST /api/v1/indicators/calculate
```
Calculate specific indicators for historical data.

### 3. Multi-Timeframe Analysis
```
POST /api/v1/indicators/multi-timeframe
```
Calculate indicators across multiple timeframes simultaneously.

### 4. Latest Indicator Values
```
GET /api/v1/indicators/latest/{symbol}
```
Get the most recent indicator values for a symbol.

---

## Complete Indicator List (77 Total)

### Volume Indicators (9)

| Indicator | Name | Description | Default Parameters |
|-----------|------|-------------|-------------------|
| **MFI** | Money Flow Index | Measures buying and selling pressure | window: 14 |
| **ADI** | Accumulation/Distribution Index | Volume flow indicator | - |
| **OBV** | On-Balance Volume | Cumulative volume indicator | - |
| **CMF** | Chaikin Money Flow | Volume-weighted average of accumulation/distribution | window: 20 |
| **ForceIndex** | Force Index | Price and volume momentum | window: 13 |
| **EaseOfMovement** | Ease of Movement | Volume-based momentum | window: 14 |
| **VPT** | Volume Price Trend | Cumulative volume based on price changes | - |
| **NVI** | Negative Volume Index | Tracks price changes on down volume days | - |
| **VWAP** | Volume Weighted Average Price | Average price weighted by volume | window: 14 |

---

### Volatility Indicators (13)

| Indicator | Name | Description | Default Parameters |
|-----------|------|-------------|-------------------|
| **ATR** | Average True Range | Measures market volatility | window: 14 |
| **BB_High** | Bollinger Bands Upper | Upper band of Bollinger Bands | window: 20, dev: 2 |
| **BB_Mid** | Bollinger Bands Middle | Middle band (SMA) | window: 20 |
| **BB_Low** | Bollinger Bands Lower | Lower band of Bollinger Bands | window: 20, dev: 2 |
| **BB_Width** | Bollinger Bands Width | Distance between upper and lower bands | window: 20 |
| **BB_Percent** | Bollinger Bands %B | Position within the bands | window: 20 |
| **KC_High** | Keltner Channel Upper | Upper band of Keltner Channel | window: 20 |
| **KC_Mid** | Keltner Channel Middle | Middle band (EMA) | window: 20 |
| **KC_Low** | Keltner Channel Lower | Lower band of Keltner Channel | window: 20 |
| **DC_High** | Donchian Channel Upper | Highest high over period | window: 20 |
| **DC_Mid** | Donchian Channel Middle | Midpoint of channel | window: 20 |
| **DC_Low** | Donchian Channel Lower | Lowest low over period | window: 20 |
| **UlcerIndex** | Ulcer Index | Downside volatility measure | window: 14 |

---

### Trend Indicators (34)

| Indicator | Name | Description | Default Parameters |
|-----------|------|-------------|-------------------|
| **SMA_10** | Simple Moving Average (10) | 10-period simple moving average | window: 10 |
| **SMA_20** | Simple Moving Average (20) | 20-period simple moving average | window: 20 |
| **SMA_50** | Simple Moving Average (50) | 50-period simple moving average | window: 50 |
| **SMA_200** | Simple Moving Average (200) | 200-period simple moving average | window: 200 |
| **EMA_12** | Exponential Moving Average (12) | 12-period exponential moving average | window: 12 |
| **EMA_20** | Exponential Moving Average (20) | 20-period exponential moving average | window: 20 |
| **EMA_26** | Exponential Moving Average (26) | 26-period exponential moving average | window: 26 |
| **EMA_50** | Exponential Moving Average (50) | 50-period exponential moving average | window: 50 |
| **WMA** | Weighted Moving Average | Weighted moving average | window: 20 |
| **MACD** | MACD Line | Moving Average Convergence Divergence | fast: 12, slow: 26, signal: 9 |
| **MACD_Signal** | MACD Signal Line | Signal line for MACD | fast: 12, slow: 26, signal: 9 |
| **MACD_Diff** | MACD Histogram | Difference between MACD and signal | fast: 12, slow: 26, signal: 9 |
| **ADX** | Average Directional Index | Trend strength indicator | window: 14 |
| **ADX_Pos** | ADX Positive Directional | Positive directional movement | window: 14 |
| **ADX_Neg** | ADX Negative Directional | Negative directional movement | window: 14 |
| **VI_Pos** | Vortex Indicator Positive | Positive vortex movement | window: 14 |
| **VI_Neg** | Vortex Indicator Negative | Negative vortex movement | window: 14 |
| **TRIX** | Triple Exponential Average | Rate of change of triple EMA | window: 15 |
| **MassIndex** | Mass Index | Reversal indicator based on range | fast: 9, slow: 25 |
| **CCI** | Commodity Channel Index | Cyclical trend indicator | window: 20 |
| **DPO** | Detrended Price Oscillator | Removes trend from price | window: 20 |
| **KST** | Know Sure Thing | Momentum oscillator | - |
| **KST_Signal** | KST Signal Line | Signal line for KST | - |
| **Ichimoku_A** | Ichimoku Leading Span A | Ichimoku cloud component | - |
| **Ichimoku_B** | Ichimoku Leading Span B | Ichimoku cloud component | - |
| **Ichimoku_Base** | Ichimoku Base Line | Ichimoku base line | - |
| **Ichimoku_Conversion** | Ichimoku Conversion Line | Ichimoku conversion line | - |
| **PSAR** | Parabolic SAR | Stop and reverse indicator | step: 0.02, max: 0.2 |
| **PSAR_Up** | Parabolic SAR Uptrend | SAR values during uptrend | step: 0.02, max: 0.2 |
| **PSAR_Down** | Parabolic SAR Downtrend | SAR values during downtrend | step: 0.02, max: 0.2 |
| **STC** | Schaff Trend Cycle | Cyclical oscillator | fast: 23, slow: 50 |
| **Aroon_Up** | Aroon Up | Time since highest high | window: 25 |
| **Aroon_Down** | Aroon Down | Time since lowest low | window: 25 |
| **Aroon_Indicator** | Aroon Oscillator | Difference between Aroon Up and Down | window: 25 |

---

### Momentum Indicators (18)

| Indicator | Name | Description | Default Parameters |
|-----------|------|-------------|-------------------|
| **RSI** | Relative Strength Index | Momentum oscillator (0-100) | window: 14 |
| **StochRSI** | Stochastic RSI | Stochastic of RSI | window: 14, smooth1: 3, smooth2: 3 |
| **StochRSI_K** | Stochastic RSI %K | Fast stochastic RSI | window: 14, smooth1: 3, smooth2: 3 |
| **StochRSI_D** | Stochastic RSI %D | Slow stochastic RSI | window: 14, smooth1: 3, smooth2: 3 |
| **TSI** | True Strength Index | Double-smoothed momentum | fast: 13, slow: 25 |
| **UltimateOscillator** | Ultimate Oscillator | Multi-timeframe momentum | w1: 7, w2: 14, w3: 28 |
| **Stoch_K** | Stochastic %K | Fast stochastic oscillator | window: 14, smooth: 3 |
| **Stoch_D** | Stochastic %D | Slow stochastic oscillator | window: 14, smooth: 3 |
| **WilliamsR** | Williams %R | Momentum indicator (-100 to 0) | period: 14 |
| **AwesomeOscillator** | Awesome Oscillator | Momentum histogram | - |
| **KAMA** | Kaufman Adaptive MA | Adaptive moving average | window: 10, pow1: 2, pow2: 30 |
| **ROC** | Rate of Change | Price rate of change | window: 12 |
| **PPO** | Percentage Price Oscillator | MACD in percentage | fast: 12, slow: 26, signal: 9 |
| **PPO_Signal** | PPO Signal Line | Signal line for PPO | fast: 12, slow: 26, signal: 9 |
| **PPO_Hist** | PPO Histogram | PPO histogram | fast: 12, slow: 26, signal: 9 |
| **PVO** | Percentage Volume Oscillator | Volume-based PPO | fast: 12, slow: 26, signal: 9 |
| **PVO_Signal** | PVO Signal Line | Signal line for PVO | fast: 12, slow: 26, signal: 9 |
| **PVO_Hist** | PVO Histogram | PVO histogram | fast: 12, slow: 26, signal: 9 |

---

### Other Indicators (3)

| Indicator | Name | Description | Default Parameters |
|-----------|------|-------------|-------------------|
| **DailyReturn** | Daily Return | Daily percentage return | - |
| **DailyLogReturn** | Daily Log Return | Logarithmic daily return | - |
| **CumulativeReturn** | Cumulative Return | Cumulative percentage return | - |

---

## Usage Examples

### Example 1: Calculate Specific Indicators
```bash
curl -X POST "http://localhost:8000/api/v1/indicators/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "5m",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "indicators": ["RSI", "MACD", "BB_High", "BB_Mid", "BB_Low", "EMA_20"]
  }'
```

### Example 2: Calculate All Indicators
```bash
curl -X POST "http://localhost:8000/api/v1/indicators/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "15m",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }'
```

### Example 3: Multi-Timeframe Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/indicators/multi-timeframe?symbol=NIFTY&exchange=NSE&timeframes=1m&timeframes=5m&timeframes=15m&indicators=RSI&indicators=MACD"
```

### Example 4: Get Latest Values
```bash
curl "http://localhost:8000/api/v1/indicators/latest/NIFTY?exchange=NSE&interval=5m&indicators=RSI&indicators=MACD&indicators=ATR"
```

### Example 5: Get All Available Indicators
```bash
curl "http://localhost:8000/api/v1/indicators/available"
```

---

## Response Format

### Calculate Indicators Response
```json
{
  "symbol": "NIFTY",
  "timeframe": "5m",
  "indicators": {
    "RSI": [45.2, 46.8, 48.1, ...],
    "MACD": [12.5, 13.2, 14.1, ...],
    "MACD_Signal": [11.8, 12.3, 13.0, ...],
    "EMA_20": [19500.5, 19505.2, 19510.8, ...]
  },
  "timestamps": ["2024-01-01T09:15:00", "2024-01-01T09:20:00", ...],
  "metadata": {
    "exchange": "NSE",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "candle_count": 1000,
    "indicator_count": 4
  }
}
```

### Latest Indicators Response
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "timeframe": "5m",
  "timestamp": "2024-01-31T15:25:00",
  "indicators": {
    "RSI": 52.3,
    "MACD": 15.7,
    "ATR": 45.2
  },
  "metadata": {
    "candles_used": 100
  }
}
```

---

## Categories Summary

- **Volume (9)**: Track buying/selling pressure and volume patterns
- **Volatility (13)**: Measure market volatility and price ranges
- **Trend (34)**: Identify trend direction and strength
- **Momentum (18)**: Measure speed and magnitude of price changes
- **Others (3)**: Return calculations and statistics

---

## Notes

1. All indicators are calculated using the `ta` (Technical Analysis Library) Python package
2. Indicators automatically handle NaN values for insufficient data periods
3. Custom parameters can be passed via the `indicator_params` field in requests
4. Multi-timeframe analysis runs calculations in parallel for optimal performance
5. WebSocket streaming is available for real-time indicator updates

---

## Support

For issues or questions:
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
