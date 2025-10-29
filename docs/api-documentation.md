# VELOX-N8N API Documentation

## Overview

Complete API documentation for the VELOX-N8N algorithmic trading system. All endpoints are designed to work seamlessly with N8N HTTP Request and Webhook nodes.

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

## Authentication

### JWT Bearer Token
```http
Authorization: Bearer your-jwt-token-here
```

### API Key Authentication (for N8N)
```http
X-API-Key: your-api-key-here
```

## Market Data APIs

### 1. Get Current Market Data
```http
GET /market-data/current/{symbol}
```

**Parameters:**
- `symbol` (path): Trading symbol (e.g., "NIFTY 50", "BANKNIFTY")
- `exchange` (query): Exchange name (NSE, BSE) - default: "NSE"

**Response:**
```json
{
  "symbol": "NIFTY 50",
  "exchange": "NSE",
  "current_price": 19850.25,
  "bid": 19849.75,
  "ask": 19850.50,
  "volume": 1500000,
  "timestamp": "2024-01-15T09:15:30Z",
  "change": 50.25,
  "change_percent": 0.25
}
```

### 2. Get Historical Data
```http
GET /market-data/historical/{symbol}
```

**Parameters:**
- `symbol` (path): Trading symbol
- `timeframe` (query): Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d) - default: "1m"
- `periods` (query): Number of periods - default: 100
- `start_date` (query): Start date (ISO format)
- `end_date` (query): End date (ISO format)
- `include_ticks` (query): Include tick data (true/false) - default: false

**Response:**
```json
{
  "symbol": "NIFTY 50",
  "timeframe": "5m",
  "bars": [
    {
      "timestamp": "2024-01-15T09:15:00Z",
      "open": 19800.00,
      "high": 19855.00,
      "low": 19795.00,
      "close": 19850.25,
      "volume": 1500000
    }
  ],
  "ticks": [
    {
      "timestamp": "2024-01-15T09:15:30Z",
      "price": 19850.25,
      "volume": 1000
    }
  ]
}
```

### 3. Market Scanner
```http
POST /market-data/scan
```

**Request Body:**
```json
{
  "criteria": {
    "price_above": 19000,
    "price_below": 20000,
    "volume_min": 1000000,
    "change_percent_min": 1.0
  },
  "universe": ["NIFTY 50", "BANKNIFTY", "FINNIFTY"],
  "exchange": "NSE"
}
```

**Response:**
```json
{
  "results": [
    {
      "symbol": "NIFTY 50",
      "current_price": 19850.25,
      "volume": 1500000,
      "change_percent": 0.25,
      "matches_criteria": true
    }
  ],
  "total_matches": 1
}
```

### 4. Get Watchlist
```http
GET /market-data/watchlist
```

**Parameters:**
- `user_id` (query): User ID - default: current user

**Response:**
```json
{
  "watchlist": [
    {
      "symbol": "NIFTY 50",
      "exchange": "NSE",
      "current_price": 19850.25,
      "change": 50.25,
      "change_percent": 0.25,
      "last_updated": "2024-01-15T09:15:30Z"
    }
  ]
}
```

## Real-Time Indicator APIs

### 1. Calculate Indicators
```http
POST /indicators/calculate
```

**Request Body:**
```json
{
  "symbol": "NIFTY 50",
  "data": [
    {"timestamp": "2024-01-15T09:15:00Z", "open": 19800, "high": 19855, "low": 19795, "close": 19850, "volume": 1500000}
  ],
  "indicators": [
    {
      "name": "moving_averages",
      "type": "moving_average",
      "parameters": {
        "ema_periods": [20, 50],
        "sma_periods": [20, 50]
      },
      "source": "close"
    },
    {
      "name": "oscillators",
      "type": "oscillator",
      "parameters": {
        "rsi_period": 14,
        "stoch_k": 14,
        "stoch_d": 3
      }
    }
  ]
}
```

**Response:**
```json
{
  "symbol": "NIFTY 50",
  "timestamp": "2024-01-15T09:15:30Z",
  "indicators": {
    "moving_averages": {
      "ema_20": 19845.50,
      "ema_50": 19820.75,
      "sma_20": 19843.25,
      "sma_50": 19818.50
    },
    "oscillators": {
      "rsi": 58.3,
      "stoch_k": 65.2,
      "stoch_d": 62.1
    }
  }
}
```

### 2. Get Real-Time Indicators
```http
GET /indicators/realtime/{symbol}
```

**Parameters:**
- `symbol` (path): Trading symbol
- `indicators` (query): Comma-separated indicator names
- `timeframe` (query): Timeframe - default: "1m"

**Response:**
```json
{
  "symbol": "NIFTY 50",
  "timeframe": "5m",
  "timestamp": "2024-01-15T09:15:30Z",
  "current_price": 19850.25,
  "indicators": {
    "ema_20": 19845.50,
    "ema_50": 19820.75,
    "rsi": 58.3,
    "macd": 15.25,
    "bb_upper": 19900.00,
    "bb_lower": 19800.00,
    "atr": 25.50
  },
  "candle": {
    "current": {
      "open": 19840,
      "high": 19855,
      "low": 19835,
      "close": 19850.25,
      "volume": 1500000
    },
    "previous": {
      "open": 19830,
      "high": 19845,
      "low": 19825,
      "close": 19840,
      "volume": 1200000
    }
  }
}
```

### 3. Get Indicator History
```http
GET /indicators/history/{symbol}
```

**Parameters:**
- `symbol` (path): Trading symbol
- `indicator` (query): Indicator name
- `periods` (query): Number of periods - default: 100
- `timeframe` (query): Timeframe - default: "1m"

**Response:**
```json
{
  "symbol": "NIFTY 50",
  "indicator": "ema_20",
  "timeframe": "5m",
  "history": [
    {
      "timestamp": "2024-01-15T09:15:00Z",
      "price": 19850.25,
      "indicator": 19845.50
    }
  ]
}
```

### 4. Get Indicator Signals
```http
GET /indicators/signals/{symbol}
```

**Parameters:**
- `symbol` (path): Trading symbol
- `strategy` (query): Strategy type (trend_following, mean_reversion, momentum)
- `timeframe` (query): Timeframe - default: "1m"

**Response:**
```json
{
  "symbol": "NIFTY 50",
  "strategy": "trend_following",
  "timestamp": "2024-01-15T09:15:30Z",
  "signals": {
    "primary": "BUY",
    "confidence": "HIGH",
    "reason": "Bullish EMA crossover with ADX 32.1",
    "indicators": {
      "ema_20": 19845.50,
      "ema_50": 19820.75,
      "adx": 32.1
    }
  }
}
```

### 5. Get Available Indicators
```http
GET /indicators/available-indicators
```

**Response:**
```json
{
  "moving_averages": {
    "sma": {"period": "int", "description": "Simple Moving Average period"},
    "ema": {"period": "int", "description": "Exponential Moving Average period"},
    "wma": {"period": "int", "description": "Weighted Moving Average period"},
    "hma": {"period": "int", "description": "Hull Moving Average period"}
  },
  "oscillators": {
    "rsi": {"period": "int", "description": "RSI period (default: 14)"},
    "stochastic": {"k": "int", "d": "int", "description": "Stochastic K and D periods"},
    "macd": {"fast": "int", "slow": "int", "signal": "int", "description": "MACD parameters"}
  },
  "volatility": {
    "bollinger_bands": {"period": "int", "std": "float", "description": "Bollinger Bands parameters"},
    "atr": {"period": "int", "description": "Average True Range period"}
  }
}
```

## Trading APIs

### 1. Place Order
```http
POST /trading/orders
```

**Request Body:**
```json
{
  "symbol": "NIFTY 50",
  "exchange": "NSE",
  "side": "BUY",
  "quantity": 50,
  "order_type": "MARKET",
  "price": 19850.25,
  "stop_loss": 19800.00,
  "take_profit": 19950.00,
  "validity": "DAY",
  "strategy_id": 1
}
```

**Response:**
```json
{
  "order_id": "ORD_20240115_001",
  "symbol": "NIFTY 50",
  "exchange": "NSE",
  "side": "BUY",
  "quantity": 50,
  "order_type": "MARKET",
  "price": 19850.25,
  "status": "PENDING",
  "timestamp": "2024-01-15T09:15:30Z",
  "broker_order_id": "BROKER_12345"
}
```

### 2. Get Order Details
```http
GET /trading/orders/{order_id}
```

**Response:**
```json
{
  "order_id": "ORD_20240115_001",
  "symbol": "NIFTY 50",
  "exchange": "NSE",
  "side": "BUY",
  "quantity": 50,
  "order_type": "MARKET",
  "price": 19850.25,
  "status": "EXECUTED",
  "executed_price": 19850.25,
  "executed_quantity": 50,
  "timestamp": "2024-01-15T09:15:30Z",
  "broker_order_id": "BROKER_12345"
}
```

### 3. Modify Order
```http
PUT /trading/orders/{order_id}
```

**Request Body:**
```json
{
  "price": 19855.00,
  "quantity": 45,
  "stop_loss": 19805.00,
  "take_profit": 19955.00
}
```

### 4. Cancel Order
```http
DELETE /trading/orders/{order_id}
```

### 5. Get Current Positions
```http
GET /trading/positions
```

**Parameters:**
- `user_id` (query): User ID - default: current user
- `symbol` (query): Filter by symbol (optional)

**Response:**
```json
{
  "positions": [
    {
      "symbol": "NIFTY 50",
      "exchange": "NSE",
      "quantity": 50,
      "average_price": 19845.50,
      "current_price": 19850.25,
      "pnl": 237.50,
      "pnl_percent": 0.24,
      "side": "LONG",
      "timestamp": "2024-01-15T09:15:30Z"
    }
  ]
}
```

### 6. Get Trade History
```http
GET /trading/trades
```

**Parameters:**
- `user_id` (query): User ID - default: current user
- `symbol` (query): Filter by symbol (optional)
- `limit` (query): Number of trades - default: 100
- `offset` (query): Offset for pagination - default: 0

**Response:**
```json
{
  "trades": [
    {
      "trade_id": "TRD_20240115_001",
      "symbol": "NIFTY 50",
      "exchange": "NSE",
      "side": "BUY",
      "quantity": 50,
      "price": 19845.50,
      "status": "EXECUTED",
      "timestamp": "2024-01-15T09:15:30Z",
      "strategy_id": 1
    }
  ],
  "total_count": 1,
  "has_more": false
}
```

## Risk Management APIs

### 1. Risk Check
```http
POST /risk/check
```

**Request Body:**
```json
{
  "symbol": "NIFTY 50",
  "side": "BUY",
  "quantity": 50,
  "price": 19850.25,
  "user_id": 1,
  "strategy_id": 1
}
```

**Response:**
```json
{
  "risk_check": {
    "passed": true,
    "risk_score": 2.5,
    "max_risk_allowed": 5.0,
    "warnings": [],
    "blocked": false
  },
  "position_size": {
    "recommended": 50,
    "max_allowed": 100,
    "risk_amount": 2500.00,
    "account_risk_percent": 2.5
  }
}
```

### 2. Calculate Position Size
```http
POST /risk/position-size
```

**Request Body:**
```json
{
  "account_size": 100000,
  "risk_percent": 2.0,
  "symbol": "NIFTY 50",
  "method": "volatility_based",
  "atr": 25.50,
  "stop_loss_points": 51.00
}
```

**Response:**
```json
{
  "position_size": 78,
  "risk_amount": 2000.00,
  "stop_loss_distance": 51.00,
  "method": "volatility_based",
  "calculation": {
    "max_risk": 2000.00,
    "risk_per_share": 25.50,
    "recommended_shares": 78
  }
}
```

### 3. Calculate Stop Loss
```http
POST /risk/stop-loss
```

**Request Body:**
```json
{
  "symbol": "NIFTY 50",
  "entry_price": 19850.25,
  "side": "BUY",
  "method": "atr_based",
  "atr": 25.50,
  "multiplier": 2.0
}
```

**Response:**
```json
{
  "stop_loss": 19799.25,
  "method": "atr_based",
  "distance": 51.00,
  "risk_percent": 0.26,
  "calculation": {
    "atr": 25.50,
    "multiplier": 2.0,
    "stop_distance": 51.00
  }
}
```

### 4. Calculate Take Profit
```http
POST /risk/take-profit
```

**Request Body:**
```json
{
  "symbol": "NIFTY 50",
  "entry_price": 19850.25,
  "side": "BUY",
  "method": "fixed_risk_reward",
  "risk_reward_ratio": 2.0,
  "stop_loss": 19799.25
}
```

**Response:**
```json
{
  "take_profit": 19952.25,
  "method": "fixed_risk_reward",
  "risk_reward_ratio": 2.0,
  "profit_distance": 102.00,
  "calculation": {
    "risk_distance": 51.00,
    "ratio": 2.0,
    "profit_distance": 102.00
  }
}
```

### 5. Get Portfolio Risk
```http
GET /risk/portfolio-risk/{user_id}
```

**Response:**
```json
{
  "user_id": 1,
  "portfolio_risk": {
    "total_exposure": 500000.00,
    "total_risk": 5000.00,
    "risk_percent": 5.0,
    "max_allowed_risk": 10000.00,
    "utilization": 50.0
  },
  "positions": [
    {
      "symbol": "NIFTY 50",
      "exposure": 100000.00,
      "risk": 1000.00,
      "risk_percent": 1.0
    }
  ]
}
```

## Strategy Management APIs

### 1. Create Strategy
```http
POST /strategies/
```

**Request Body:**
```json
{
  "name": "Trend Following Strategy",
  "description": "EMA crossover with ADX confirmation",
  "type": "trend_following",
  "config": {
    "ema_periods": [20, 50],
    "adx_period": 14,
    "adx_threshold": 25,
    "risk_percent": 2.0
  },
  "is_paper_trading": true,
  "n8n_workflow_id": "wf_12345"
}
```

**Response:**
```json
{
  "strategy_id": 1,
  "name": "Trend Following Strategy",
  "description": "EMA crossover with ADX confirmation",
  "type": "trend_following",
  "config": {
    "ema_periods": [20, 50],
    "adx_period": 14,
    "adx_threshold": 25,
    "risk_percent": 2.0
  },
  "is_active": false,
  "is_paper_trading": true,
  "created_by": 1,
  "created_at": "2024-01-15T09:15:30Z"
}
```

### 2. List Strategies
```http
GET /strategies/
```

**Parameters:**
- `user_id` (query): User ID - default: current user
- `type` (query): Strategy type filter (optional)
- `is_active` (query): Active status filter (optional)

**Response:**
```json
{
  "strategies": [
    {
      "strategy_id": 1,
      "name": "Trend Following Strategy",
      "type": "trend_following",
      "is_active": true,
      "is_paper_trading": true,
      "performance": {
        "total_trades": 25,
        "win_rate": 68.0,
        "total_pnl": 2500.00,
        "sharpe_ratio": 1.25
      }
    }
  ]
}
```

### 3. Start Strategy
```http
POST /strategies/{strategy_id}/start
```

**Response:**
```json
{
  "strategy_id": 1,
  "status": "STARTED",
  "started_at": "2024-01-15T09:15:30Z",
  "mode": "paper_trading",
  "message": "Strategy started successfully"
}
```

### 4. Stop Strategy
```http
POST /strategies/{strategy_id}/stop
```

**Response:**
```json
{
  "strategy_id": 1,
  "status": "STOPPED",
  "stopped_at": "2024-01-15T15:30:30Z",
  "message": "Strategy stopped successfully"
}
```

### 5. Get Strategy Performance
```http
GET /strategies/{strategy_id}/performance
```

**Response:**
```json
{
  "strategy_id": 1,
  "performance": {
    "total_trades": 25,
    "winning_trades": 17,
    "losing_trades": 8,
    "win_rate": 68.0,
    "total_pnl": 2500.00,
    "max_drawdown": -500.00,
    "sharpe_ratio": 1.25,
    "sortino_ratio": 1.85,
    "calmar_ratio": 2.50,
    "daily_returns": [0.5, -0.2, 0.8, 0.3],
    "equity_curve": [
      {"date": "2024-01-01", "equity": 100000},
      {"date": "2024-01-02", "equity": 100500}
    ]
  }
}
```

### 6. Backtest Strategy
```http
POST /strategies/{strategy_id}/backtest
```

**Request Body:**
```json
{
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 100000,
  "commission": 0.1,
  "slippage": 0.05
}
```

**Response:**
```json
{
  "backtest_id": "BT_20240115_001",
  "strategy_id": 1,
  "period": "2023-01-01 to 2024-01-01",
  "results": {
    "total_trades": 245,
    "win_rate": 65.3,
    "total_pnl": 15000.00,
    "max_drawdown": -2000.00,
    "sharpe_ratio": 1.45,
    "annual_return": 15.0,
    "equity_curve": [
      {"date": "2023-01-01", "equity": 100000},
      {"date": "2023-01-02", "equity": 100500}
    ]
  }
}
```

## Backtesting APIs

### 1. Run Backtest
```http
POST /backtesting/run
```

**Request Body:**
```json
{
  "strategy_config": {
    "type": "trend_following",
    "parameters": {
      "ema_periods": [20, 50],
      "adx_threshold": 25
    }
  },
  "symbol": "NIFTY 50",
  "timeframe": "5m",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 100000,
  "commission": 0.1,
  "slippage": 0.05
}
```

**Response:**
```json
{
  "backtest_id": "BT_20240115_001",
  "status": "RUNNING",
  "started_at": "2024-01-15T09:15:30Z",
  "estimated_completion": "2024-01-15T09:20:30Z"
}
```

### 2. Record Backtest Trade
```http
POST /backtesting/record-trade
```

**Request Body:**
```json
{
  "backtest_id": "BT_20240115_001",
  "trade": {
    "symbol": "NIFTY 50",
    "side": "BUY",
    "quantity": 50,
    "entry_price": 19845.50,
    "exit_price": 19900.00,
    "entry_time": "2023-06-15T09:15:30Z",
    "exit_time": "2023-06-15T10:30:30Z",
    "pnl": 2725.00,
    "commission": 19.85,
    "slippage": 2.50
  }
}
```

### 3. Get Backtest Results
```http
GET /backtesting/results/{backtest_id}
```

**Response:**
```json
{
  "backtest_id": "BT_20240115_001",
  "status": "COMPLETED",
  "completed_at": "2024-01-15T09:20:30Z",
  "results": {
    "total_trades": 245,
    "winning_trades": 160,
    "losing_trades": 85,
    "win_rate": 65.3,
    "total_pnl": 15000.00,
    "max_drawdown": -2000.00,
    "sharpe_ratio": 1.45,
    "annual_return": 15.0,
    "profit_factor": 1.85,
    "recovery_factor": 7.5
  }
}
```

### 4. Get Equity Curve
```http
GET /backtesting/equity-curve/{backtest_id}
```

**Response:**
```json
{
  "backtest_id": "BT_20240115_001",
  "equity_curve": [
    {"date": "2023-01-01", "equity": 100000, "drawdown": 0},
    {"date": "2023-01-02", "equity": 100500, "drawdown": 0},
    {"date": "2023-01-03", "equity": 100200, "drawdown": -300}
  ]
}
```

## WebSocket APIs

### 1. Real-time Data Stream
```http
WS /realtime/ws/{symbol}
```

**Connection Parameters:**
- `symbol`: Trading symbol to subscribe to
- `indicators`: Comma-separated indicator names (optional)
- `timeframe`: Timeframe for indicators (optional)

**Message Format:**
```json
{
  "type": "tick_update",
  "symbol": "NIFTY 50",
  "timestamp": "2024-01-15T09:15:30Z",
  "data": {
    "price": 19850.25,
    "volume": 1000,
    "indicators": {
      "ema_20": 19845.50,
      "ema_50": 19820.75,
      "rsi": 58.3
    }
  }
}
```

### 2. Strategy Updates
```http
WS /strategies/ws/{strategy_id}
```

**Message Format:**
```json
{
  "type": "strategy_update",
  "strategy_id": 1,
  "timestamp": "2024-01-15T09:15:30Z",
  "data": {
    "status": "RUNNING",
    "current_signal": "BUY",
    "active_positions": 1,
    "daily_pnl": 250.00
  }
}
```

## Webhook APIs

### 1. Indicator Alert Webhook
```http
POST /webhooks/indicator-alert
```

**Request Body:**
```json
{
  "symbol": "NIFTY 50",
  "indicator": "rsi",
  "current_value": 75.5,
  "threshold": 70,
  "timestamp": "2024-01-15T09:15:30Z",
  "action": "trigger_strategy"
}
```

### 2. Trade Execution Webhook
```http
POST /webhooks/trade-executed
```

**Request Body:**
```json
{
  "trade_id": "TRD_20240115_001",
  "symbol": "NIFTY 50",
  "side": "BUY",
  "quantity": 50,
  "price": 19850.25,
  "status": "EXECUTED",
  "timestamp": "2024-01-15T09:15:30Z"
}
```

## Error Responses

All APIs return consistent error format:

```json
{
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "Symbol 'INVALID' not found",
    "details": {
      "symbol": "INVALID",
      "valid_symbols": ["NIFTY 50", "BANKNIFTY", "FINNIFTY"]
    }
  },
  "timestamp": "2024-01-15T09:15:30Z"
}
```

## Rate Limits

- **Market Data APIs**: 100 requests/minute
- **Indicator APIs**: 200 requests/minute
- **Trading APIs**: 50 requests/minute
- **Risk Management APIs**: 100 requests/minute
- **Strategy APIs**: 50 requests/minute

## Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error

## SDK Examples

### Python
```python
import requests

# Get real-time indicators
response = requests.get(
    "http://localhost:8000/api/v1/indicators/realtime/NIFTY 50",
    params={
        "indicators": "ema_20,ema_50,rsi",
        "timeframe": "5m"
    },
    headers={"Authorization": "Bearer your-jwt-token"}
)

data = response.json()
print(f"EMA 20: {data['indicators']['ema_20']}")
```

### JavaScript (N8N HTTP Request Node)
```javascript
// N8N Function Node
const symbol = 'NIFTY 50';
const indicators = 'ema_20,ema_50,rsi,adx';

const response = await fetch(`http://localhost:8000/api/v1/indicators/realtime/${symbol}?indicators=${indicators}`, {
  headers: {
    'Authorization': 'Bearer your-jwt-token',
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
return [{
  json: {
    symbol: data.symbol,
    price: data.current_price,
    indicators: data.indicators
  }
}];
```

This comprehensive API documentation provides all endpoints needed for N8N workflow integration and real-time trading system development.