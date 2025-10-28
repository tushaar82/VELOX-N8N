# 📡 VELOX Enhanced API Endpoints Reference

Complete reference for all VELOX Real-Time Technical Analysis API endpoints including new categorized indicators and technical analysis features.

**Base URL:** `http://localhost:8000/api/v1`

---

## 🔍 Table of Contents

1. [Root Endpoints](#root-endpoints)
2. [Indicators - Categorized](#indicators---categorized)
3. [Technical Analysis](#technical-analysis)
4. [Original Indicators](#original-indicators)
5. [Support & Resistance](#support--resistance)
6. [Candles](#candles-endpoints)
7. [Option Chain](#option-chain-endpoints)
8. [WebSocket](#websocket-endpoints)

---

## Root Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "websocket_connections": 0,
  "max_connections": 100
}
```

### Application Info
```http
GET /info
```

**Response:**
```json
{
  "application": {
    "name": "VELOX Real-Time Technical Analysis API",
    "version": "1.0.0",
    "environment": "INFO"
  },
  "configuration": {
    "openalgo_host": "http://localhost:5000",
    "max_websocket_connections": 100,
    "tick_buffer_size": 1000,
    "default_timeframes": ["1m", "5m", "15m", "1h", "1d"]
  },
  "statistics": {
    "tick_stream": {...},
    "websocket": {...}
  }
}
```

---

## Indicators - Categorized

### Get Indicators by Category

#### Volume Indicators
```http
GET /api/v1/indicators/volume
```

**Response:**
```json
[
  {
    "name": "MFI",
    "category": "volume",
    "description": "Money Flow Index",
    "parameters": {"window": {"default": 14, "min": 2, "max": 100}},
    "min_periods": 14
  },
  ...
]
```

#### Volatility Indicators
```http
GET /api/v1/indicators/volatility
```

#### Trend Indicators
```http
GET /api/v1/indicators/trend
```

#### Momentum Indicators
```http
GET /api/v1/indicators/momentum
```

#### Statistical Indicators (NEW)
```http
GET /api/v1/indicators/statistical
```

**Available Statistical Indicators:**
- `StdDev` - Standard Deviation
- `ZScore` - Z-Score
- `PriceROC` - Price Rate of Change
- `ATRP` - Average True Range Percentage
- `BBWPercent` - Bollinger Band Width Percentage
- `PricePosition` - Price Position within Bollinger Bands

#### Pattern Indicators (NEW)
```http
GET /api/v1/indicators/patterns
```

**Available Pattern Indicators:**
- `Doji` - Doji Candlestick Pattern
- `Hammer` - Hammer Candlestick Pattern
- `BullishEngulfing` - Bullish Engulfing Pattern
- `BearishEngulfing` - Bearish Engulfing Pattern
- `InsideBar` - Inside Bar Pattern
- `OutsideBar` - Outside Bar Pattern

#### Other Indicators
```http
GET /api/v1/indicators/others
```

### Calculate Single Indicator by Category

#### Volume Indicator
```http
POST /api/v1/indicators/volume/{indicator}
```

**Query Parameters:**
- `symbol` (required): Trading symbol
- `exchange` (required): Exchange code
- `interval` (required): Timeframe
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Request Body:**
```json
{
  "window": 14
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/indicators/volume/MFI \
  -H "Content-Type: application/json" \
  -d '{"window": 14}' \
  -G -d "symbol=NIFTY&exchange=NSE&interval=5m"
```

#### Volatility Indicator
```http
POST /api/v1/indicators/volatility/{indicator}
```

#### Trend Indicator
```http
POST /api/v1/indicators/trend/{indicator}
```

#### Momentum Indicator
```http
POST /api/v1/indicators/momentum/{indicator}
```

#### Statistical Indicator (NEW)
```http
POST /api/v1/indicators/statistical/{indicator}
```

#### Pattern Indicator (NEW)
```http
POST /api/v1/indicators/patterns/{indicator}
```

---

## Technical Analysis (NEW)

### Pivot Points
```http
POST /api/v1/analysis/pivot-points
```

**Query Parameters:**
- `symbol` (required): Trading symbol
- `exchange` (required): Exchange code
- `interval` (required): Timeframe
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `pivot_type` (optional): `standard`, `fibonacci`, `woodie`, `camarilla` (default: standard)
- `lookback` (optional): Number of periods (default: 20)

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "timeframe": "1d",
  "pivot_type": "standard",
  "lookback": 20,
  "current_price": 21530.0,
  "pivots": {
    "pivot": 21500.0,
    "support_1": 21450.0,
    "support_2": 21400.0,
    "resistance_1": 21550.0,
    "resistance_2": 21600.0
  },
  "timestamp": "2024-01-15T15:30:00",
  "metadata": {
    "candles_used": 20,
    "calculation_method": "standard"
  }
}
```

### Fibonacci Retracements
```http
POST /api/v1/analysis/fibonacci
```

**Query Parameters:**
- `symbol` (required): Trading symbol
- `exchange` (required): Exchange code
- `interval` (required): Timeframe
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `swing_high` (optional): Manual swing high (auto-detect if None)
- `swing_low` (optional): Manual swing low (auto-detect if None)
- `trend` (optional): `up`, `down` (default: up)

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "timeframe": "1d",
  "trend": "up",
  "swing_high": 22000.0,
  "swing_low": 21000.0,
  "current_price": 21530.0,
  "retracement_levels": {
    "0.0%": 22000.0,
    "23.6%": 21764.0,
    "38.2%": 21618.0,
    "50.0%": 21500.0,
    "61.8%": 21382.0,
    "78.6%": 21236.0,
    "100.0%": 21000.0
  },
  "extension_levels": {
    "127.2%": 22272.0,
    "161.8%": 22618.0,
    "200.0%": 23000.0,
    "261.8%": 23518.0
  },
  "timestamp": "2024-01-15T15:30:00",
  "metadata": {
    "candles_used": 50,
    "auto_detect": true
  }
}
```

### Price Pattern Recognition
```http
POST /api/v1/analysis/price-patterns
```

**Query Parameters:**
- `symbol` (required): Trading symbol
- `exchange` (required): Exchange code
- `interval` (required): Timeframe
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `pattern_types` (optional): List of pattern types to detect
- `lookback` (optional): Number of candles to analyze (default: 100)

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "timeframe": "1d",
  "patterns_detected": [
    {
      "type": "higher_highs_higher_lows",
      "direction": "bullish",
      "strength": "strong",
      "start_index": 10,
      "end_index": 15,
      "confidence": 0.8
    },
    {
      "type": "double_top",
      "direction": "bearish",
      "strength": "medium",
      "start_index": 20,
      "end_index": 25,
      "resistance_level": 21800.0,
      "confidence": 0.7
    }
  ],
  "current_price": 21530.0,
  "timestamp": "2024-01-15T15:30:00",
  "metadata": {
    "candles_analyzed": 100,
    "pattern_types": ["all"]
  }
}
```

### Market Sentiment Analysis
```http
POST /api/v1/analysis/market-sentiment
```

**Query Parameters:**
- `symbol` (required): Trading symbol
- `exchange` (required): Exchange code
- `interval` (required): Timeframe
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `lookback` (optional): Number of periods (default: 50)

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "timeframe": "1d",
  "sentiment": "bullish",
  "score": 1.5,
  "factors": [
    "Moderate uptrend (above SMA20)",
    "High volume confirmation",
    "Strong 5-day momentum"
  ],
  "indicators_used": ["SMA20", "SMA50", "Volume", "PriceMomentum"],
  "technical_summary": {
    "trend": "uptrend",
    "volume_status": "high",
    "momentum_5d": "+2.50%",
    "momentum_10d": "+3.20%"
  },
  "current_price": 21530.0,
  "timestamp": "2024-01-15T15:30:00",
  "metadata": {
    "periods_analyzed": 50
  }
}
```

---

## Original Indicators

### Get Available Indicators
```http
GET /api/v1/indicators/available
```

**Response:**
```json
{
  "total_indicators": 77,
  "categories": {
    "volume": ["MFI", "ADI", "OBV", "CMF", "ForceIndex", ...],
    "volatility": ["ATR", "BB_High", "BB_Mid", "BB_Low", ...],
    "trend": ["SMA_10", "SMA_20", "EMA_12", "MACD", ...],
    "momentum": ["RSI", "StochRSI", "TSI", "WilliamsR", ...],
    "statistical": ["StdDev", "ZScore", "PriceROC", ...],
    "pattern": ["Doji", "Hammer", "BullishEngulfing", ...],
    "others": ["DailyReturn", "DailyLogReturn", "CumulativeReturn"]
  },
  "all_indicators": ["RSI", "MACD", "SMA", ...]
}
```

### Calculate Indicators
```http
POST /api/v1/indicators/calculate
```

### Multi-Timeframe Indicators
```http
POST /api/v1/indicators/multi-timeframe
```

### Get Latest Indicators
```http
GET /api/v1/indicators/latest/{symbol}
```

---

## Support & Resistance

### Get Support/Resistance Levels
```http
GET /api/v1/support-resistance/{symbol}
```

### Get Pivot Points
```http
GET /api/v1/support-resistance/{symbol}/pivots
```

### Get Nearest Levels
```http
GET /api/v1/support-resistance/{symbol}/nearest
```

---

## Candles Endpoints

### Get Historical Candles
```http
POST /api/v1/candles/
```

### Get Latest Candle
```http
GET /api/v1/candles/{symbol}/latest
```

### Multi-Timeframe Candles
```http
POST /api/v1/candles/multi-timeframe
```

---

## Option Chain Endpoints

### Get Option Chain
```http
POST /api/v1/option-chain/
```

### Get Option Chain Analysis
```http
GET /api/v1/option-chain/{symbol}/analysis
```

### Get Put-Call Ratio
```http
GET /api/v1/option-chain/{symbol}/pcr
```

### Get Max Pain
```http
GET /api/v1/option-chain/{symbol}/max-pain
```

---

## WebSocket Endpoints

### Real-time Stream
```
WS /api/v1/ws/stream
```

### Tick Stream
```
WS /api/v1/ws/ticks
```

---

## 📊 Total Indicators Summary

| Category | Count | Examples |
|-----------|--------|----------|
| Volume | 9 | MFI, OBV, VWAP |
| Volatility | 14 | ATR, Bollinger Bands, Keltner Channel |
| Trend | 30+ | SMA, EMA, MACD, ADX, Ichimoku |
| Momentum | 20+ | RSI, Stochastic, Williams %R |
| Statistical | 6 | Standard Deviation, Z-Score, Price ROC |
| Pattern | 6 | Doji, Hammer, Engulfing Patterns |
| Others | 3 | Daily Return, Cumulative Return |
| **Total** | **88+** | |

---

## 🔧 Usage Examples

### Calculate Statistical Indicators
```python
import requests

# Calculate Z-Score
response = requests.post(
    'http://localhost:8000/api/v1/indicators/statistical/ZScore',
    params={
        'symbol': 'NIFTY',
        'exchange': 'NSE',
        'interval': '5m'
    },
    json={'window': 20}
)

data = response.json()
print(f"Z-Score values: {data['indicators']['ZScore']}")
```

### Get Pivot Points
```python
import requests

# Calculate Fibonacci pivots
response = requests.post(
    'http://localhost:8000/api/v1/analysis/pivot-points',
    params={
        'symbol': 'NIFTY',
        'exchange': 'NSE',
        'interval': '1d',
        'pivot_type': 'fibonacci'
    }
)

data = response.json()
print(f"Pivot points: {data['pivots']}")
```

### Detect Price Patterns
```python
import requests

# Detect patterns
response = requests.post(
    'http://localhost:8000/api/v1/analysis/price-patterns',
    params={
        'symbol': 'NIFTY',
        'exchange': 'NSE',
        'interval': '1d',
        'lookback': 100
    }
)

data = response.json()
for pattern in data['patterns_detected']:
    print(f"Pattern: {pattern['type']}, Confidence: {pattern['confidence']}")
```

---

## 🚀 New Features Summary

1. **Categorized Indicators**: 88+ indicators organized into 7 categories
2. **Individual Indicator Endpoints**: Calculate single indicators by category
3. **Statistical Indicators**: 6 new statistical analysis indicators
4. **Pattern Recognition**: 6 candlestick and chart pattern indicators
5. **Pivot Points**: 4 types (Standard, Fibonacci, Woodie, Camarilla)
6. **Fibonacci Analysis**: Automatic swing detection with retracements/extensions
7. **Pattern Detection**: Chart pattern recognition with confidence scores
8. **Market Sentiment**: Multi-factor sentiment analysis

---

**Total Endpoints:** 35+ (including all categorized indicators)

**API Version:** 1.0.0

**Last Updated:** 2025-10-28