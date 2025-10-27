# 📡 VELOX API Endpoints Reference

Complete reference for all VELOX Real-Time Technical Analysis API endpoints.

**Base URL:** `http://localhost:8000/api/v1`

---

## 🔍 Table of Contents

1. [Root Endpoints](#root-endpoints)
2. [Indicators](#indicators-endpoints)
3. [Support & Resistance](#support--resistance-endpoints)
4. [Candles](#candles-endpoints)
5. [Option Chain](#option-chain-endpoints)
6. [WebSocket](#websocket-endpoints)

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

### Root
```http
GET /
```

**Response:**
```json
{
  "name": "VELOX Real-Time Technical Analysis API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "redoc": "/redoc",
  "endpoints": {
    "indicators": "/api/v1/indicators",
    "support_resistance": "/api/v1/support-resistance",
    "candles": "/api/v1/candles",
    "option_chain": "/api/v1/option-chain",
    "websocket": "/api/v1/ws"
  }
}
```

---

## Indicators Endpoints

### 1. Get Available Indicators
```http
GET /api/v1/indicators/available
```

**Response:**
```json
{
  "total_indicators": 70,
  "categories": {
    "momentum": ["RSI", "STOCH", "STOCHRSI", "WILLIAMS_R", ...],
    "trend": ["SMA", "EMA", "MACD", "ADX", "AROON", ...],
    "volatility": ["BBANDS", "ATR", "KELTNER", ...],
    "volume": ["OBV", "CMF", "MFI", "VWAP", ...]
  },
  "all_indicators": ["RSI", "MACD", "SMA", ...]
}
```

### 2. Calculate Indicators
```http
POST /api/v1/indicators/calculate
```

**Request Body:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "interval": "5m",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "indicators": ["RSI", "MACD", "SMA"],
  "include_current": false
}
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "interval": "5m",
  "candles": [...],
  "indicators": {
    "RSI": [45.2, 48.5, 52.1, ...],
    "MACD": [12.5, 15.2, 18.3, ...],
    "MACD_signal": [10.2, 12.5, 14.8, ...],
    "MACD_histogram": [2.3, 2.7, 3.5, ...],
    "SMA_20": [21500, 21520, 21540, ...]
  },
  "metadata": {
    "total_candles": 100,
    "indicators_calculated": 3,
    "timestamp": "2024-01-15T15:30:00"
  }
}
```

### 3. Multi-Timeframe Indicators
```http
POST /api/v1/indicators/multi-timeframe
```

**Request Body:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "timeframes": ["1m", "5m", "15m"],
  "indicators": ["RSI", "MACD"],
  "start_date": "2024-01-01"
}
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "timeframes": {
    "1m": {
      "candles": [...],
      "indicators": {
        "RSI": [...],
        "MACD": [...]
      }
    },
    "5m": {...},
    "15m": {...}
  },
  "timestamp": "2024-01-15T15:30:00"
}
```

### 4. Get Latest Indicator Values
```http
GET /api/v1/indicators/latest/{symbol}?exchange=NSE&interval=5m&indicators=RSI,MACD
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "interval": "5m",
  "latest_candle": {
    "timestamp": "2024-01-15T15:30:00",
    "open": 21500,
    "high": 21550,
    "low": 21480,
    "close": 21530,
    "volume": 1500000
  },
  "indicators": {
    "RSI": 52.3,
    "MACD": 15.2,
    "MACD_signal": 12.5,
    "MACD_histogram": 2.7
  },
  "timestamp": "2024-01-15T15:30:00"
}
```

---

## Support & Resistance Endpoints

### 1. Get Support/Resistance Levels
```http
GET /api/v1/support-resistance/{symbol}?exchange=NSE&interval=5m&lookback_periods=100
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "interval": "5m",
  "current_price": 21530,
  "support_levels": [
    {"price": 21450, "strength": 3, "touches": 5},
    {"price": 21380, "strength": 2, "touches": 3}
  ],
  "resistance_levels": [
    {"price": 21600, "strength": 4, "touches": 6},
    {"price": 21680, "strength": 2, "touches": 4}
  ],
  "metadata": {
    "total_support": 2,
    "total_resistance": 2,
    "lookback_periods": 100,
    "timestamp": "2024-01-15T15:30:00"
  }
}
```

### 2. Get Pivot Points
```http
GET /api/v1/support-resistance/{symbol}/pivots?exchange=NSE&pivot_type=standard
```

**Query Parameters:**
- `pivot_type`: `standard`, `fibonacci`, `woodie`

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "pivot_type": "standard",
  "current_price": 21530,
  "pivots": {
    "pivot": 21500,
    "r1": 21600,
    "r2": 21700,
    "r3": 21800,
    "s1": 21400,
    "s2": 21300,
    "s3": 21200
  },
  "timestamp": "2024-01-15T15:30:00"
}
```

### 3. Get Nearest Levels
```http
GET /api/v1/support-resistance/{symbol}/nearest?exchange=NSE&interval=5m&count=3
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "current_price": 21530,
  "nearest_support": [
    {"price": 21500, "distance": 30, "strength": 3},
    {"price": 21450, "distance": 80, "strength": 2}
  ],
  "nearest_resistance": [
    {"price": 21550, "distance": 20, "strength": 2},
    {"price": 21600, "distance": 70, "strength": 4}
  ],
  "timestamp": "2024-01-15T15:30:00"
}
```

---

## Candles Endpoints

### 1. Get Historical Candles (POST)
```http
POST /api/v1/candles/
```

**Request Body:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "interval": "5m",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "include_current": false
}
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "interval": "5m",
  "candles": [
    {
      "timestamp": "2024-01-01T09:15:00",
      "open": 21500,
      "high": 21550,
      "low": 21480,
      "close": 21530,
      "volume": 1500000
    },
    ...
  ],
  "metadata": {
    "total_candles": 100,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "timestamp": "2024-01-15T15:30:00"
  }
}
```

### 2. Get Historical Candles (GET)
```http
GET /api/v1/candles/{symbol}?exchange=NSE&interval=5m&start_date=2024-01-01&end_date=2024-01-31
```

**Response:** Same as POST method

### 3. Get Latest Candle
```http
GET /api/v1/candles/{symbol}/latest?exchange=NSE&interval=5m
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "interval": "5m",
  "candle": {
    "timestamp": "2024-01-15T15:30:00",
    "open": 21500,
    "high": 21550,
    "low": 21480,
    "close": 21530,
    "volume": 1500000
  },
  "is_current": true,
  "timestamp": "2024-01-15T15:30:00"
}
```

### 4. Multi-Timeframe Candles
```http
POST /api/v1/candles/multi-timeframe
```

**Request Body:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "timeframes": ["1m", "5m", "15m"],
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "exchange": "NSE",
  "timeframes": {
    "1m": {
      "candles": [...],
      "count": 500
    },
    "5m": {
      "candles": [...],
      "count": 100
    },
    "15m": {
      "candles": [...],
      "count": 33
    }
  },
  "timestamp": "2024-01-15T15:30:00"
}
```

---

## Option Chain Endpoints

### 1. Get Option Chain (POST)
```http
POST /api/v1/option-chain/
```

**Request Body:**
```json
{
  "symbol": "NIFTY",
  "is_index": true
}
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "underlying_value": 21530,
  "expiry_dates": ["30-Jan-2025", "06-Feb-2025", ...],
  "options": [
    {
      "strike_price": 21500,
      "call_oi": 1500000,
      "call_volume": 50000,
      "call_ltp": 125.50,
      "call_change_oi": 25000,
      "call_iv": 18.5,
      "put_oi": 2000000,
      "put_volume": 75000,
      "put_ltp": 110.25,
      "put_change_oi": 30000,
      "put_iv": 19.2
    },
    ...
  ],
  "timestamp": "2024-01-15T15:30:00"
}
```

### 2. Get Option Chain (GET)
```http
GET /api/v1/option-chain/{symbol}?is_index=true&expiry=30-Jan-2025
```

**Response:** Same as POST method

### 3. Get Option Chain Analysis
```http
GET /api/v1/option-chain/{symbol}/analysis?is_index=true
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "underlying_value": 21530,
  "atm_strike": 21500,
  "pcr_oi": 1.33,
  "pcr_volume": 1.50,
  "max_pain": 21500,
  "total_call_oi": 15000000,
  "total_put_oi": 20000000,
  "total_call_volume": 500000,
  "total_put_volume": 750000,
  "support_levels": [21400, 21300],
  "resistance_levels": [21600, 21700],
  "timestamp": "2024-01-15T15:30:00"
}
```

### 4. Filter Option Chain
```http
POST /api/v1/option-chain/{symbol}/filter?min_oi=10000&strike_range=10
```

**Query Parameters:**
- `min_oi`: Minimum open interest
- `min_volume`: Minimum volume
- `strike_range`: Strikes above/below ATM

**Response:** Filtered option chain data

### 5. Get Put-Call Ratio (PCR)
```http
GET /api/v1/option-chain/{symbol}/pcr?is_index=true
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "expiry_dates": ["30-Jan-2025", "06-Feb-2025"],
  "underlying_value": 21530,
  "pcr_oi": 1.33,
  "pcr_volume": 1.50,
  "total_call_oi": 15000000,
  "total_put_oi": 20000000,
  "total_call_volume": 500000,
  "total_put_volume": 750000,
  "timestamp": "2024-01-15T15:30:00"
}
```

### 6. Get Max Pain
```http
GET /api/v1/option-chain/{symbol}/max-pain?is_index=true
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "underlying_value": 21530,
  "max_pain": 21500,
  "atm_strike": 21500,
  "distance_from_max_pain": 30,
  "timestamp": "2024-01-15T15:30:00"
}
```

### 7. Get OI Analysis
```http
GET /api/v1/option-chain/{symbol}/oi-analysis?is_index=true&top_n=5
```

**Response:**
```json
{
  "symbol": "NIFTY",
  "underlying_value": 21530,
  "top_call_oi": [
    {
      "strike": 21500,
      "oi": 2500000,
      "volume": 80000,
      "ltp": 125.50,
      "change_oi": 50000
    },
    ...
  ],
  "top_put_oi": [
    {
      "strike": 21500,
      "oi": 3000000,
      "volume": 100000,
      "ltp": 110.25,
      "change_oi": 60000
    },
    ...
  ],
  "timestamp": "2024-01-15T15:30:00"
}
```

---

## WebSocket Endpoints

### 1. Real-time Stream
```
WS /api/v1/ws/stream
```

**Subscribe Message:**
```json
{
  "type": "subscription",
  "data": {
    "action": "subscribe",
    "symbols": ["NIFTY", "BANKNIFTY"],
    "timeframes": ["1m", "5m"],
    "indicators": ["RSI", "MACD"]
  }
}
```

**Unsubscribe Message:**
```json
{
  "type": "subscription",
  "data": {
    "action": "unsubscribe",
    "symbols": ["NIFTY"],
    "timeframes": ["1m"]
  }
}
```

**Server Response (Candle Update):**
```json
{
  "type": "candle",
  "data": {
    "symbol": "NIFTY",
    "timeframe": "5m",
    "timestamp": "2024-01-15T15:30:00",
    "open": 21500,
    "high": 21550,
    "low": 21480,
    "close": 21530,
    "volume": 1500000
  },
  "timestamp": "2024-01-15T15:30:00"
}
```

**Server Response (Indicator Update):**
```json
{
  "type": "indicator",
  "data": {
    "symbol": "NIFTY",
    "timeframe": "5m",
    "indicators": {
      "RSI": 52.3,
      "MACD": 15.2
    }
  },
  "timestamp": "2024-01-15T15:30:00"
}
```

### 2. Tick Stream
```
WS /api/v1/ws/ticks
```

**Subscribe Message:**
```json
{
  "type": "subscription",
  "data": {
    "action": "subscribe",
    "symbols": ["NIFTY"]
  }
}
```

**Server Response:**
```json
{
  "type": "tick",
  "data": {
    "symbol": "NIFTY",
    "price": 21530.50,
    "volume": 100.0,
    "timestamp": "2024-01-15T15:25:30.123"
  }
}
```

### 3. WebSocket Stats
```http
GET /api/v1/ws/stats
```

**Response:**
```json
{
  "websocket": {
    "active_connections": 5,
    "total_connections": 25,
    "messages_sent": 1500,
    "messages_received": 300
  },
  "tick_stream": {
    "active_subscriptions": 10,
    "ticks_processed": 5000,
    "buffer_size": 1000
  }
}
```

### 4. WebSocket Health
```http
GET /api/v1/ws/health
```

**Response:**
```json
{
  "status": "healthy",
  "active_connections": 5,
  "max_connections": 100,
  "capacity_used_pct": 5.0
}
```

---

## 📝 Common Parameters

### Symbols
- `NIFTY`, `BANKNIFTY`, `FINNIFTY` (Indices)
- `RELIANCE`, `TCS`, `INFY` (Stocks)

### Exchanges
- `NSE` - National Stock Exchange
- `BSE` - Bombay Stock Exchange
- `NFO` - NSE Futures & Options
- `BFO` - BSE Futures & Options

### Timeframes
- `1m`, `3m`, `5m`, `10m`, `15m`, `30m` (Minutes)
- `1h`, `2h`, `4h` (Hours)
- `1d`, `1w`, `1mo` (Days/Weeks/Months)

### Date Format
- ISO 8601: `2024-01-15T15:30:00`
- Simple: `2024-01-15`

---

## 🔐 Authentication

Currently, the API does not require authentication. For production:
- Add API key authentication
- Use JWT tokens
- Implement rate limiting

---

## 📊 Rate Limits

Default limits (configurable):
- 60 requests per minute per IP
- 1000 requests per hour per IP
- 100 concurrent WebSocket connections

---

## 🐛 Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid input",
  "message": "Symbol is required",
  "details": {...}
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "No data found for symbol INVALID",
  "path": "/api/v1/candles/INVALID"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

---

## 📚 Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## 💡 Usage Examples

### cURL
```bash
# Get indicators
curl -X POST http://localhost:8000/api/v1/indicators/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "5m",
    "indicators": ["RSI", "MACD"]
  }'
```

### Python
```python
import requests

# Get option chain
response = requests.get(
    "http://localhost:8000/api/v1/option-chain/NIFTY",
    params={"is_index": True}
)
data = response.json()
```

### JavaScript
```javascript
// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/stream');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscription',
    data: {
      action: 'subscribe',
      symbols: ['NIFTY'],
      timeframes: ['1m', '5m']
    }
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

---

**Total Endpoints:** 22 (18 REST + 4 WebSocket)

**API Version:** 1.0.0

**Last Updated:** 2025-10-27
