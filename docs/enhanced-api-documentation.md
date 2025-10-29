# Enhanced VELOX-N8N API Documentation

## Overview

Complete API documentation for VELOX-N8N algorithmic trading system with additional endpoints for analysis, funds management, and historical data replay.

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

## Account & Funds Management APIs

### 1. Get Account Balance
```http
GET /account/balance
```

**Parameters:**
- `user_id` (query): User ID - default: current user

**Response:**
```json
{
  "user_id": 1,
  "account_balance": {
    "total_balance": 100000.00,
    "available_balance": 85000.00,
    "used_margin": 15000.00,
    "margin_available": 85000.00,
    "currency": "INR"
  },
  "breakdown": {
    "cash": 50000.00,
    "collateral": 50000.00,
    "unrealized_pnl": 0.00,
    "realized_pnl": 2500.00
  },
  "last_updated": "2024-01-15T09:15:30Z"
}
```

### 2. Get Fund Details
```http
GET /account/funds
```

**Response:**
```json
{
  "funds": {
    "equity": 102500.00,
    "cash": 85000.00,
    "margin_used": 15000.00,
    "margin_available": 85000.00,
    "open_pnl": 2500.00,
    "closed_pnl": 2500.00,
    "total_pnl": 5000.00,
    "withdrawable": 85000.00
  },
  "limits": {
    "max_position_size": 100000.00,
    "max_margin": 50000.00,
    "risk_limit": 10000.00
  }
}
```

### 3. Get Transaction History
```http
GET /account/transactions
```

**Parameters:**
- `user_id` (query): User ID - default: current user
- `type` (query): Transaction type (deposit, withdrawal, trade, adjustment) - optional
- `start_date` (query): Start date (ISO format) - optional
- `end_date` (query): End date (ISO format) - optional
- `limit` (query): Number of transactions - default: 100
- `offset` (query): Offset for pagination - default: 0

**Response:**
```json
{
  "transactions": [
    {
      "transaction_id": "TXN_20240115_001",
      "type": "deposit",
      "amount": 100000.00,
      "balance_before": 0.00,
      "balance_after": 100000.00,
      "status": "completed",
      "description": "Initial deposit",
      "timestamp": "2024-01-15T09:00:00Z"
    },
    {
      "transaction_id": "TXN_20240115_002",
      "type": "trade",
      "amount": -15000.00,
      "balance_before": 100000.00,
      "balance_after": 85000.00,
      "status": "completed",
      "description": "Margin used for NIFTY 50 position",
      "timestamp": "2024-01-15T09:15:30Z"
    }
  ],
  "total_count": 2,
  "has_more": false
}
```

### 4. Add Funds
```http
POST /account/add-funds
```

**Request Body:**
```json
{
  "amount": 50000.00,
  "payment_method": "bank_transfer",
  "reference": "DEPOSIT_20240115",
  "notes": "Additional trading capital"
}
```

**Response:**
```json
{
  "transaction_id": "TXN_20240115_003",
  "amount": 50000.00,
  "status": "pending",
  "new_balance": 150000.00,
  "timestamp": "2024-01-15T09:20:00Z"
}
```

### 5. Withdraw Funds
```http
POST /account/withdraw-funds
```

**Request Body:**
```json
{
  "amount": 10000.00,
  "withdrawal_method": "bank_transfer",
  "bank_details": {
    "account_number": "1234567890",
    "ifsc": "HDFC0001234",
    "account_name": "John Doe"
  },
  "notes": "Profit withdrawal"
}
```

## Enhanced P&L APIs

### 1. Get Overall P&L
```http
GET /pnl/overall
```

**Parameters:**
- `user_id` (query): User ID - default: current user
- `period` (query): Period (today, week, month, quarter, year, all) - default: "today"
- `start_date` (query): Custom start date (ISO format) - optional
- `end_date` (query): Custom end date (ISO format) - optional

**Response:**
```json
{
  "user_id": 1,
  "period": "today",
  "overall_pnl": {
    "total_pnl": 2500.00,
    "realized_pnl": 2000.00,
    "unrealized_pnl": 500.00,
    "total_trades": 15,
    "winning_trades": 10,
    "losing_trades": 5,
    "win_rate": 66.67,
    "profit_factor": 2.5,
    "max_drawdown": -500.00,
    "sharpe_ratio": 1.25
  },
  "breakdown": {
    "by_symbol": [
      {
        "symbol": "NIFTY 50",
        "pnl": 1500.00,
        "trades": 8,
        "win_rate": 75.0,
        "contribution_percent": 60.0
      },
      {
        "symbol": "BANKNIFTY",
        "pnl": 1000.00,
        "trades": 7,
        "win_rate": 57.14,
        "contribution_percent": 40.0
      }
    ],
    "by_strategy": [
      {
        "strategy_id": 1,
        "strategy_name": "Trend Following",
        "pnl": 1800.00,
        "trades": 10,
        "win_rate": 70.0
      },
      {
        "strategy_id": 2,
        "strategy_name": "Mean Reversion",
        "pnl": 700.00,
        "trades": 5,
        "win_rate": 60.0
      }
    ]
  },
  "timestamp": "2024-01-15T09:15:30Z"
}
```

### 2. Get Stock-wise P&L
```http
GET /pnl/stocks
```

**Parameters:**
- `user_id` (query): User ID - default: current user
- `symbols` (query): Comma-separated symbols - optional
- `period` (query): Period - default: "today"
- `start_date` (query): Custom start date - optional
- `end_date` (query): Custom end date - optional

**Response:**
```json
{
  "user_id": 1,
  "period": "today",
  "stock_pnl": [
    {
      "symbol": "NIFTY 50",
      "exchange": "NSE",
      "current_position": {
        "quantity": 50,
        "average_price": 19845.50,
        "current_price": 19850.25,
        "side": "LONG",
        "pnl": 237.50,
        "pnl_percent": 0.24,
        "value": 992512.50
      },
      "trades_today": [
        {
          "trade_id": "TRD_20240115_001",
          "side": "BUY",
          "quantity": 50,
          "entry_price": 19840.00,
          "exit_price": 19860.00,
          "pnl": 1000.00,
          "timestamp": "2024-01-15T09:30:00Z"
        }
      ],
      "daily_pnl": 1237.50,
      "total_trades": 8,
      "winning_trades": 6,
      "losing_trades": 2,
      "win_rate": 75.0,
      "volume_traded": 400000,
      "commission_paid": 200.00
    },
    {
      "symbol": "BANKNIFTY",
      "exchange": "NSE",
      "current_position": {
        "quantity": 0,
        "average_price": 0,
        "current_price": 44550.75,
        "side": "FLAT",
        "pnl": 0.00,
        "pnl_percent": 0.00,
        "value": 0
      },
      "trades_today": [
        {
          "trade_id": "TRD_20240115_002",
          "side": "SELL",
          "quantity": 30,
          "entry_price": 44580.00,
          "exit_price": 44550.00,
          "pnl": 900.00,
          "timestamp": "2024-01-15T10:15:00Z"
        }
      ],
      "daily_pnl": 900.00,
      "total_trades": 7,
      "winning_trades": 4,
      "losing_trades": 3,
      "win_rate": 57.14,
      "volume_traded": 267450,
      "commission_paid": 150.00
    }
  ],
  "total_stocks": 2,
  "total_pnl": 2137.50,
  "timestamp": "2024-01-15T09:15:30Z"
}
```

### 3. Get P&L History
```http
GET /pnl/history
```

**Parameters:**
- `user_id` (query): User ID - default: current user
- `period` (query): Period - default: "month"
- `start_date` (query): Custom start date - optional
- `end_date` (query): Custom end date - optional
- `granularity` (query): Data granularity (daily, weekly, monthly) - default: "daily"
- `limit` (query): Number of records - default: 100

**Response:**
```json
{
  "pnl_history": [
    {
      "date": "2024-01-15",
      "daily_pnl": 2137.50,
      "realized_pnl": 1800.00,
      "unrealized_pnl": 337.50,
      "total_trades": 15,
      "win_rate": 66.67,
      "top_contributor": "NIFTY 50",
      "bottom_contributor": "RELIANCE"
    },
    {
      "date": "2024-01-14",
      "daily_pnl": -500.00,
      "realized_pnl": -300.00,
      "unrealized_pnl": -200.00,
      "total_trades": 8,
      "win_rate": 37.5,
      "top_contributor": "TCS",
      "bottom_contributor": "INFY"
    }
  ],
  "summary": {
    "period_pnl": 1637.50,
    "best_day": 2137.50,
    "worst_day": -800.00,
    "avg_daily_pnl": 163.75,
    "volatility": 45.2
  }
}
```

## Enhanced Historical Data Replay APIs

### 1. Start Historical Replay
```http
POST /backtesting/start-replay
```

**Request Body:**
```json
{
  "symbol": "NIFTY 50",
  "timeframe": "5m",
  "start_date": "2023-01-01T09:15:00Z",
  "end_date": "2023-12-31T15:30:00Z",
  "replay_speed": 1.0,
  "include_weekends": false,
  "include_holidays": false,
  "tick_data": true,
  "strategy_config": {
    "strategy_id": 1,
    "parameters": {
      "ema_periods": [20, 50],
      "adx_threshold": 25
    }
  }
}
```

**Response:**
```json
{
  "replay_id": "REPLAY_20240115_001",
  "status": "STARTED",
  "symbol": "NIFTY 50",
  "timeframe": "5m",
  "total_ticks": 98750,
  "total_bars": 13100,
  "estimated_duration": "6 hours 15 minutes",
  "started_at": "2024-01-15T09:15:30Z",
  "current_progress": 0.0,
  "websocket_url": "ws://localhost:8000/api/v1/backtesting/ws/REPLAY_20240115_001"
}
```

### 2. Control Replay
```http
POST /backtesting/control-replay/{replay_id}
```

**Request Body:**
```json
{
  "action": "pause", // pause, resume, stop, seek
  "timestamp": "2023-06-15T10:30:00Z", // for seek action
  "speed": 2.0 // for speed adjustment
}
```

**Response:**
```json
{
  "replay_id": "REPLAY_20240115_001",
  "status": "PAUSED",
  "current_timestamp": "2023-06-15T10:30:00Z",
  "progress_percent": 45.2,
  "message": "Replay paused at requested timestamp"
}
```

### 3. Get Replay Status
```http
GET /backtesting/replay-status/{replay_id}
```

**Response:**
```json
{
  "replay_id": "REPLAY_20240115_001",
  "status": "RUNNING",
  "progress": {
    "current_timestamp": "2023-06-15T10:30:00Z",
    "progress_percent": 45.2,
    "ticks_processed": 44625,
    "total_ticks": 98750,
    "elapsed_time": "2h 45m 30s",
    "estimated_remaining": "3h 29m 30s"
  },
  "performance": {
    "cpu_usage": 15.2,
    "memory_usage": 45.8,
    "processing_speed": 1250 // ticks per second
  },
  "current_data": {
    "timestamp": "2023-06-15T10:30:00Z",
    "price": 19850.25,
    "volume": 1500,
    "indicators": {
      "ema_20": 19845.50,
      "ema_50": 19820.75,
      "rsi": 58.3
    }
  }
}
```

### 4. Replay WebSocket
```http
WS /backtesting/ws/{replay_id}
```

**Message Format:**
```json
{
  "type": "tick_update",
  "replay_id": "REPLAY_20240115_001",
  "timestamp": "2023-06-15T10:30:00Z",
  "data": {
    "price": 19850.25,
    "volume": 1500,
    "bid": 19849.75,
    "ask": 19850.50,
    "indicators": {
      "ema_20": 19845.50,
      "ema_50": 19820.75,
      "rsi": 58.3,
      "macd": 15.25
    },
    "current_bar": {
      "open": 19840,
      "high": 19855,
      "low": 19835,
      "close": 19850.25,
      "volume": 15000
    }
  }
}
```

### 5. Get Replay Data Snapshot
```http
GET /backtesting/replay-snapshot/{replay_id}
```

**Parameters:**
- `timestamp` (query): Specific timestamp for snapshot (ISO format)
- `bars_before` (query): Number of bars before timestamp - default: 50
- `bars_after` (query): Number of bars after timestamp - default: 50

**Response:**
```json
{
  "replay_id": "REPLAY_20240115_001",
  "snapshot_timestamp": "2023-06-15T10:30:00Z",
  "data": {
    "bars_before": [
      {
        "timestamp": "2023-06-15T09:25:00Z",
        "open": 19835,
        "high": 19845,
        "low": 19830,
        "close": 19840,
        "volume": 12000
      }
    ],
    "current_bar": {
      "timestamp": "2023-06-15T10:30:00Z",
      "open": 19840,
      "high": 19855,
      "low": 19835,
      "close": 19850.25,
      "volume": 15000
    },
    "bars_after": [
      {
        "timestamp": "2023-06-15T10:35:00Z",
        "open": 19850.25,
        "high": 19860,
        "low": 19845,
        "close": 19855,
        "volume": 16000
      }
    ],
    "indicators_at_timestamp": {
      "ema_20": 19845.50,
      "ema_50": 19820.75,
      "rsi": 58.3,
      "macd": 15.25,
      "bb_upper": 19900.00,
      "bb_lower": 19800.00
    }
  }
}
```

## Enhanced Analysis APIs

### 1. Get Market Analysis
```http
GET /analysis/market/{symbol}
```

**Parameters:**
- `symbol` (path): Trading symbol
- `timeframe` (query): Timeframe - default: "1h"
- `period` (query): Analysis period - default: 30
- `indicators` (query): Comma-separated indicators - default: "volume,volatility,trend"

**Response:**
```json
{
  "symbol": "NIFTY 50",
  "timeframe": "1h",
  "analysis_period": "30 days",
  "market_analysis": {
    "price_action": {
      "current_trend": "BULLISH",
      "trend_strength": 0.75,
      "support_levels": [19800, 19750, 19700],
      "resistance_levels": [19900, 19950, 20000],
      "pivot_point": 19850,
      "pivot_type": "standard"
    },
    "volume_analysis": {
      "avg_volume": 1500000,
      "volume_trend": "INCREASING",
      "volume_spike_detected": true,
      "volume_spike_factor": 2.5,
      "buy_volume": 2400000,
      "sell_volume": 1200000,
      "volume_ratio": 2.0
    },
    "volatility_analysis": {
      "current_volatility": 25.5,
      "volatility_trend": "DECREASING",
      "volatility_percentile": 75,
      "atr": 25.50,
      "beta": 1.15,
      "implied_volatility": 28.5
    },
    "pattern_recognition": {
      "detected_patterns": [
        {
          "pattern": "BULLISH_ENGULFING",
          "confidence": 0.85,
          "timeframe": "4h",
          "start_time": "2024-01-15T06:00:00Z",
          "end_time": "2024-01-15T10:00:00Z"
        }
      ],
      "reliability": 0.78
    }
  },
  "timestamp": "2024-01-15T09:15:30Z"
}
```

### 2. Get Strategy Analysis
```http
GET /analysis/strategy/{strategy_id}
```

**Parameters:**
- `strategy_id` (path): Strategy ID
- `period` (query): Analysis period - default: "month"
- `include_benchmark` (query): Include benchmark comparison - default: true

**Response:**
```json
{
  "strategy_id": 1,
  "strategy_name": "Trend Following Strategy",
  "analysis_period": "30 days",
  "strategy_analysis": {
    "performance_metrics": {
      "total_return": 5.2,
      "annualized_return": 62.4,
      "max_drawdown": -8.5,
      "sharpe_ratio": 1.85,
      "sortino_ratio": 2.45,
      "calmar_ratio": 7.35,
      "win_rate": 68.5,
      "profit_factor": 3.2,
      "avg_win": 450.00,
      "avg_loss": -125.00,
      "largest_win": 2500.00,
      "largest_loss": -800.00
    },
    "risk_analysis": {
      "var_95": 2.5,
      "cvar_95": -150.00,
      "max_consecutive_losses": 3,
      "max_consecutive_wins": 8,
      "recovery_time": 5.2, // days
      "risk_adjusted_return": 4.8
    },
    "benchmark_comparison": {
      "benchmark": "NIFTY 50",
      "benchmark_return": 3.8,
      "alpha": 1.4,
      "beta": 0.85,
      "information_ratio": 0.65,
      "tracking_error": 0.45
    },
    "regime_analysis": {
      "bull_market_performance": 8.5,
      "bear_market_performance": -2.3,
      "sideways_market_performance": 1.2,
      "high_volatility_performance": 6.8,
      "low_volatility_performance": 3.5
    }
  },
  "recommendations": [
    {
      "type": "OPTIMIZATION",
      "description": "Consider reducing position size during high volatility periods",
      "priority": "HIGH"
    },
    {
      "type": "RISK_MANAGEMENT",
      "description": "Implement tighter stop-losses for better risk-adjusted returns",
      "priority": "MEDIUM"
    }
  ]
}
```

### 3. Get Correlation Analysis
```http
GET /analysis/correlation
```

**Parameters:**
- `symbols` (query): Comma-separated symbols
- `period` (query): Analysis period - default: "90"
- `method` (query): Correlation method (pearson, spearman) - default: "pearson"

**Response:**
```json
{
  "symbols": ["NIFTY 50", "BANKNIFTY", "FINNIFTY"],
  "period": "90 days",
  "correlation_matrix": [
    {
      "symbol1": "NIFTY 50",
      "symbol2": "BANKNIFTY",
      "correlation": 0.75,
      "p_value": 0.001,
      "significance": "HIGH"
    },
    {
      "symbol1": "NIFTY 50",
      "symbol2": "FINNIFTY",
      "correlation": 0.65,
      "p_value": 0.005,
      "significance": "MEDIUM"
    },
    {
      "symbol1": "BANKNIFTY",
      "symbol2": "FINNIFTY",
      "correlation": 0.82,
      "p_value": 0.0001,
      "significance": "HIGH"
    }
  ],
  "analysis": {
    "highest_correlation": {
      "pair": ["BANKNIFTY", "FINNIFTY"],
      "value": 0.82
    },
    "lowest_correlation": {
      "pair": ["NIFTY 50", "FINNIFTY"],
      "value": 0.65
    },
    "avg_correlation": 0.74,
    "diversification_benefit": 0.18
  }
}
```

## Enhanced N8N Integration Endpoints

### 1. Trigger Strategy Execution
```http
POST /n8n/trigger-strategy
```

**Request Body:**
```json
{
  "strategy_id": 1,
  "trigger_type": "indicator_alert", // indicator_alert, time_based, manual
  "symbol": "NIFTY 50",
  "timeframe": "5m",
  "parameters": {
    "indicator": "rsi",
    "condition": "cross_above",
    "threshold": 70,
    "confirmation_required": true
  },
  "execution_mode": "paper", // paper, live
  "n8n_workflow_id": "wf_12345"
}
```

**Response:**
```json
{
  "trigger_id": "TRG_20240115_001",
  "strategy_id": 1,
  "status": "TRIGGERED",
  "triggered_at": "2024-01-15T09:15:30Z",
  "n8n_execution_id": "EXEC_20240115_001",
  "message": "Strategy triggered successfully in N8N"
}
```

### 2. Get N8N Workflow Status
```http
GET /n8n/workflow-status/{workflow_id}
```

**Response:**
```json
{
  "workflow_id": "wf_12345",
  "strategy_id": 1,
  "status": "RUNNING",
  "started_at": "2024-01-15T09:15:30Z",
  "current_step": "Calculate Position Size",
  "steps_completed": 3,
  "total_steps": 8,
  "progress_percent": 37.5,
  "execution_time": "2m 15s",
  "data_flow": [
    {
      "step": "Get Market Data",
      "status": "COMPLETED",
      "duration": "1.2s",
      "output_size": "2.5KB"
    },
    {
      "step": "Calculate Indicators",
      "status": "COMPLETED",
      "duration": "3.5s",
      "output_size": "1.8KB"
    }
  ]
}
```

### 3. N8N Webhook Receiver
```http
POST /n8n/webhook-receiver
```

**Request Body:**
```json
{
  "webhook_type": "strategy_result",
  "workflow_id": "wf_12345",
  "strategy_id": 1,
  "execution_id": "EXEC_20240115_001",
  "result": {
    "action": "PLACE_ORDER",
    "order_details": {
      "symbol": "NIFTY 50",
      "side": "BUY",
      "quantity": 50,
      "price": 19850.25,
      "order_type": "MARKET"
    },
    "status": "SUCCESS",
    "executed_at": "2024-01-15T09:18:45Z"
  },
  "metadata": {
    "execution_time": "3m 15s",
    "nodes_executed": 8,
    "data_processed": "15.2KB"
  }
}
```

## Error Codes and Handling

### Enhanced Error Responses

```json
{
  "error": {
    "code": "INSUFFICIENT_FUNDS",
    "message": "Insufficient funds for requested trade",
    "details": {
      "required": 15000.00,
      "available": 85000.00,
      "shortfall": 5000.00,
      "suggestions": [
        "Reduce position size",
        "Add more funds to account",
        "Use margin if available"
      ]
    },
    "recovery_actions": [
      {
        "action": "REDUCE_QUANTITY",
        "description": "Reduce order quantity to available balance",
        "auto_fix": true
      }
    ]
  },
  "timestamp": "2024-01-15T09:15:30Z",
  "request_id": "REQ_20240115_001"
}
```

### Rate Limiting with Tiers

```json
{
  "rate_limit": {
    "current_tier": "STANDARD",
    "limits": {
      "market_data": {"requests_per_minute": 100, "requests_per_hour": 5000},
      "indicators": {"requests_per_minute": 200, "requests_per_hour": 10000},
      "trading": {"requests_per_minute": 50, "requests_per_hour": 2000},
      "backtesting": {"requests_per_minute": 30, "requests_per_hour": 1000}
    },
    "usage": {
      "current_minute": {"requests_used": 45, "requests_remaining": 55},
      "current_hour": {"requests_used": 1200, "requests_remaining": 3800},
      "reset_time": "2024-01-15T10:00:00Z"
    },
    "upgrade_options": [
      {
        "tier": "PROFESSIONAL",
        "multiplier": 2.0,
        "features": ["higher_limits", "priority_support", "advanced_analytics"]
      }
    ]
  }
}
```

This enhanced API documentation provides comprehensive endpoints for account management, detailed P&L analysis, historical data replay, and advanced N8N integration capabilities.