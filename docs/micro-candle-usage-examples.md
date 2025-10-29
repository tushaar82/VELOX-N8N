# Micro-Candle Usage Examples and Documentation

## Overview

This document provides comprehensive usage examples for the micro-candle generation system, including API calls, N8N workflows, and frontend integration examples.

## 1. API Usage Examples

### 1.1 Basic Micro-Candle Generation

```bash
# Generate micro-candles for NIFTY 50 for a single day
curl -X POST "http://localhost:8000/api/v1/micro-candle/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NIFTY 50",
    "start_date": "2023-01-01T09:15:00Z",
    "end_date": "2023-01-01T15:30:00Z",
    "config": {
      "micro_candles_per_minute": 10,
      "noise_factor": 0.1,
      "enable_trend_following": true,
      "enable_mean_reversion": true
    }
  }'
```

### 1.2 Advanced Configuration

```bash
# Generate micro-candles with custom configuration
curl -X POST "http://localhost:8000/api/v1/micro-candle/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BANKNIFTY",
    "start_date": "2023-01-01T09:15:00Z",
    "end_date": "2023-01-07T15:30:00Z",
    "config": {
      "micro_candles_per_minute": 20,
      "noise_factor": 0.15,
      "volatility_smoothing": 0.7,
      "enable_trend_following": true,
      "enable_mean_reversion": true,
      "enable_volatility_expansion": true,
      "max_price_deviation": 0.08,
      "min_volume_per_micro": 0.02
    }
  }'
```

### 1.3 Response Format

```json
{
  "symbol": "NIFTY 50",
  "start_date": "2023-01-01T09:15:00Z",
  "end_date": "2023-01-01T15:30:00Z",
  "original_candles": 375,
  "micro_candles_generated": 3750,
  "micro_candles": [
    {
      "timestamp": "2023-01-01T09:15:00Z",
      "open": 17850.25,
      "high": 17852.10,
      "low": 17849.80,
      "close": 17851.45,
      "volume": 1250
    },
    {
      "timestamp": "2023-01-01T09:15:06Z",
      "open": 17851.45,
      "high": 17853.20,
      "low": 17850.90,
      "close": 17852.75,
      "volume": 1180
    }
  ]
}
```

### 1.4 Configuration Management

```bash
# Get current configuration
curl -X GET "http://localhost:8000/api/v1/micro-candle/config"

# Update configuration
curl -X POST "http://localhost:8000/api/v1/micro-candle/config" \
  -H "Content-Type: application/json" \
  -d '{
    "micro_candles_per_minute": 15,
    "noise_factor": 0.12,
    "enable_volatility_expansion": false
  }'
```

## 2. Enhanced Historical Replay Examples

### 2.1 Start Micro-Candle Replay Session

```bash
# Start replay with micro-candles
curl -X POST "http://localhost:8000/api/v1/backtesting/start-enhanced-replay" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NIFTY 50",
    "timeframe": "1m",
    "start_date": "2023-01-01T09:15:00Z",
    "end_date": "2023-01-01T15:30:00Z",
    "replay_speed": 2.0,
    "enable_micro_candles": true,
    "micro_candle_config": {
      "micro_candles_per_minute": 10,
      "noise_factor": 0.1
    },
    "strategy_config": {
      "type": "trend_following",
      "indicators": [
        {
          "name": "ema_20_50",
          "type": "moving_average",
          "parameters": {
            "ema_periods": [20, 50]
          }
        },
        {
          "name": "rsi",
          "type": "oscillator",
          "parameters": {
            "rsi_period": 14
          }
        }
      ],
      "risk_management": {
        "account_size": 100000,
        "risk_percent": 2.0
      }
    }
  }'
```

### 2.2 WebSocket Connection for Real-time Updates

```javascript
// Connect to enhanced replay WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/backtesting/ws/REPLAY_20230101_091500');

ws.onopen = function(event) {
    console.log('Connected to enhanced replay');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'micro_candle_update') {
        console.log('Micro-candle update:', data.data);
        
        // Update chart with micro-candle data
        updateChartWithMicroCandle(data.data.micro_candle);
        
        // Update indicators
        updateIndicators(data.data.indicators);
        
        // Check for signals
        if (data.data.signals) {
            processSignals(data.data.signals);
        }
    } else if (data.type === 'enhanced_session_update') {
        console.log('Session update:', data);
        updateProgress(data.progress);
        updateStatus(data.status);
    }
};

function updateChartWithMicroCandle(microCandle) {
    // Add micro-candle to chart
    chart.update({
        time: microCandle.timestamp,
        open: microCandle.open,
        high: microCandle.high,
        low: microCandle.low,
        close: microCandle.close,
        volume: microCandle.volume
    });
}
```

## 3. N8N Workflow Examples

### 3.1 Complete Micro-Candle Backtesting Workflow

```json
{
  "name": "Complete Micro-Candle Backtesting",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "micro-backtest-start",
        "responseMode": "responseNode"
      },
      "position": [240, 300]
    },
    {
      "name": "Parse Request",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "jsCode": "// Parse backtest request\nconst requestBody = $json.body;\nconst symbol = requestBody.symbol || 'NIFTY 50';\nconst startDate = requestBody.start_date || '2023-01-01T09:15:00Z';\nconst endDate = requestBody.end_date || '2023-01-01T15:30:00Z';\nconst strategyType = requestBody.strategy_type || 'trend_following';\nconst microConfig = requestBody.micro_candle_config || {\n  micro_candles_per_minute: 10,\n  noise_factor: 0.1\n};\n\nreturn [{\n  json: {\n    symbol: symbol,\n    start_date: startDate,\n    end_date: endDate,\n    strategy_type: strategyType,\n    micro_candle_config: microConfig,\n    backtest_id: `BT_${Date.now()}`\n  }\n}];"
      },
      "position": [460, 300]
    },
    {
      "name": "Generate Micro-Candles",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/api/v1/micro-candle/generate",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {"name": "symbol", "value": "={{$json.symbol}}"},
            {"name": "start_date", "value": "={{$json.start_date}}"},
            {"name": "end_date", "value": "={{$json.end_date}}"},
            {"name": "config", "value": "={{$json.micro_candle_config}}"}
          ]
        }
      },
      "position": [680, 300]
    },
    {
      "name": "Process Micro-Candles",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "jsCode": "// Process micro-candles for strategy execution\nconst response = items[0].json;\nconst microCandles = response.micro_candles || [];\nconst symbol = response.symbol;\nconst backtestId = items[1].json.backtest_id;\nconst strategyType = items[1].json.strategy_type;\n\n// Group micro-candles into 1-minute bars\nconst bars = [];\nlet currentBar = null;\n\nfor (const micro of microCandles) {\n  const microTime = new Date(micro.timestamp);\n  const barTime = getBarStartTime(microTime, '1m');\n  \n  if (!currentBar || currentBar.timestamp !== barTime) {\n    if (currentBar) {\n      bars.push(currentBar);\n    }\n    currentBar = {\n      timestamp: barTime,\n      open: micro.open,\n      high: micro.high,\n      low: micro.low,\n      close: micro.close,\n      volume: micro.volume,\n      micro_candles: [micro]\n    };\n  } else {\n    currentBar.high = Math.max(currentBar.high, micro.high);\n    currentBar.low = Math.min(currentBar.low, micro.low);\n    currentBar.close = micro.close;\n    currentBar.volume += micro.volume;\n    currentBar.micro_candles.push(micro);\n  }\n}\n\nif (currentBar) {\n  bars.push(currentBar);\n}\n\nfunction getBarStartTime(time, timeframe) {\n  const minutes = { '1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60 }[timeframe] || 1;\n  const totalMinutes = time.getHours() * 60 + time.getMinutes();\n  const barStartMinutes = Math.floor(totalMinutes / minutes) * minutes;\n  \n  const barStart = new Date(time);\n  barStart.setHours(Math.floor(barStartMinutes / 60));\n  barStart.setMinutes(barStartMinutes % 60);\n  barStart.setSeconds(0);\n  barStart.setMilliseconds(0);\n  \n  return barStart;\n}\n\nreturn bars.map(bar => ({\n  json: {\n    backtest_id: backtestId,\n    symbol: symbol,\n    strategy_type: strategyType,\n    timestamp: bar.timestamp.toISOString(),\n    open: bar.open,\n    high: bar.high,\n    low: bar.low,\n    close: bar.close,\n    volume: bar.volume,\n    micro_candles: bar.micro_candles,\n    micro_candle_count: bar.micro_candles.length\n  }\n}));"
      },
      "position": [900, 300]
    },
    {
      "name": "Execute Strategy on Micro-Candles",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "jsCode": "// Execute strategy on micro-candle data\nconst bar = items[0].json;\nconst microCandles = bar.micro_candles || [];\nconst strategyType = bar.strategy_type;\nconst backtestId = bar.backtestId;\n\nconst signals = [];\nlet position = null;\nlet trades = [];\nlet pnl = 0;\n\n// Process each micro-candle\nfor (let i = 0; i < microCandles.length; i++) {\n  const micro = microCandles[i];\n  \n  // Calculate micro-indicators\n  const indicators = calculateMicroIndicators(microCandles.slice(0, i + 1));\n  \n  // Generate signal\n  const signal = generateSignal(micro, indicators, strategyType);\n  \n  if (signal && signal.action !== 'HOLD') {\n    // Execute trade\n    const trade = executeTrade(signal, micro, position);\n    \n    if (trade) {\n      trades.push(trade);\n      \n      // Update position\n      if (signal.action === 'BUY') {\n        position = { type: 'LONG', entry: micro.close, quantity: trade.quantity, stop_loss: trade.stop_loss };\n      } else if (signal.action === 'SELL' && position) {\n        // Close position\n        const tradePnl = (micro.close - position.entry) * position.quantity;\n        pnl += tradePnl;\n        position = null;\n      }\n      \n      signals.push({\n        timestamp: micro.timestamp,\n        signal: signal.action,\n        confidence: signal.confidence,\n        reason: signal.reason,\n        price: micro.close,\n        indicators: indicators,\n        trade: trade\n      });\n    }\n  }\n}\n\nfunction calculateMicroIndicators(micros) {\n  const prices = micros.map(m => m.close);\n  const volumes = micros.map(m => m.volume);\n  \n  // Simple EMA calculation\n  const ema5 = calculateEMA(prices, 5);\n  const ema10 = calculateEMA(prices, 10);\n  \n  // RSI calculation\n  const rsi = calculateRSI(prices, 14);\n  \n  return {\n    ema_5: ema5[ema5.length - 1] || prices[0],\n    ema_10: ema10[ema10.length - 1] || prices[0],\n    rsi: rsi[rsi.length - 1] || 50,\n    volume_avg: volumes.reduce((a, b) => a + b, 0) / volumes.length,\n    price_momentum: prices.length > 1 ? (prices[prices.length - 1] - prices[0]) / prices[0] : 0\n  };\n}\n\nfunction generateSignal(micro, indicators, strategyType) {\n  if (strategyType === 'trend_following') {\n    const emaCross = indicators.ema_5 > indicators.ema_10;\n    const momentum = indicators.price_momentum;\n    \n    if (emaCross && momentum > 0.001) {\n      return {\n        action: 'BUY',\n        confidence: 'HIGH',\n        reason: `Micro EMA crossover with momentum ${(momentum * 100).toFixed(3)}%`\n      };\n    } else if (!emaCross && momentum < -0.001) {\n      return {\n        action: 'SELL',\n        confidence: 'HIGH',\n        reason: `Micro EMA crossunder with momentum ${(momentum * 100).toFixed(3)}%`\n      };\n    }\n  } else if (strategyType === 'mean_reversion') {\n    const rsi = indicators.rsi;\n    \n    if (rsi < 30) {\n      return {\n        action: 'BUY',\n        confidence: 'MEDIUM',\n        reason: `Micro oversold: RSI ${rsi.toFixed(1)}`\n      };\n    } else if (rsi > 70) {\n      return {\n        action: 'SELL',\n        confidence: 'MEDIUM',\n        reason: `Micro overbought: RSI ${rsi.toFixed(1)}`\n      };\n    }\n  }\n  \n  return { action: 'HOLD', confidence: 'LOW', reason: 'No signal' };\n}\n\nfunction executeTrade(signal, micro, position) {\n  const quantity = 100; // Fixed quantity for example\n  const atr = 50; // Example ATR value\n  \n  return {\n    timestamp: micro.timestamp,\n    action: signal.action,\n    symbol: bar.symbol,\n    price: micro.close,\n    quantity: quantity,\n    stop_loss: signal.action === 'BUY' ? micro.close - (atr * 2) : micro.close + (atr * 2),\n    take_profit: signal.action === 'BUY' ? micro.close + (atr * 3) : micro.close - (atr * 3)\n  };\n}\n\n// Helper functions\nfunction calculateEMA(prices, period) {\n  const ema = [];\n  const multiplier = 2 / (period + 1);\n  \n  for (let i = 0; i < prices.length; i++) {\n    if (i === 0) {\n      ema[i] = prices[i];\n    } else {\n      ema[i] = (prices[i] - ema[i - 1]) * multiplier + ema[i - 1];\n    }\n  }\n  \n  return ema;\n}\n\nfunction calculateRSI(prices, period) {\n  const rsi = [];\n  \n  for (let i = period; i < prices.length; i++) {\n    const gains = [];\n    const losses = [];\n    \n    for (let j = i - period + 1; j <= i; j++) {\n      const change = prices[j] - prices[j - 1];\n      if (change > 0) {\n        gains.push(change);\n        losses.push(0);\n      } else {\n        gains.push(0);\n        losses.push(Math.abs(change));\n      }\n    }\n    \n    const avgGain = gains.reduce((a, b) => a + b, 0) / period;\n    const avgLoss = losses.reduce((a, b) => a + b, 0) / period;\n    \n    const rs = avgGain / avgLoss;\n    rsi.push(100 - (100 / (1 + rs)));\n  }\n  \n  return rsi;\n}\n\nreturn [{\n  json: {\n    backtest_id: backtestId,\n    symbol: bar.symbol,\n    timestamp: bar.timestamp,\n    bar_data: {\n      open: bar.open,\n      high: bar.high,\n      low: bar.low,\n      close: bar.close,\n      volume: bar.volume\n    },\n    micro_candles_processed: bar.micro_candle_count,\n    signals_generated: signals.length,\n    signals: signals,\n    trades: trades,\n    pnl: pnl,\n    final_position: position\n  }\n}];"
      },
      "position": [1120, 300]
    },
    {
      "name": "Store Results",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/api/v1/backtesting/store-results",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {"name": "results", "value": "={{$json}}"}
          ]
        }
      },
      "position": [1340, 300]
    },
    {
      "name": "Return Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{{\"backtest_id\": $json.backtest_id, \"status\": \"completed\", \"signals_generated\": $json.signals_generated, \"total_pnl\": $json.pnl}}}"
      },
      "position": [1560, 300]
    }
  ]
}
```

## 4. Frontend Integration Examples

### 4.1 React Component for Micro-Candle Chart

```typescript
// frontend/src/components/MicroCandleChart.tsx
import React, { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi } from 'lightweight-charts';

interface MicroCandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface MicroCandleChartProps {
  symbol: string;
  onDataUpdate: (data: MicroCandleData) => void;
}

const MicroCandleChart: React.FC<MicroCandleChartProps> = ({ symbol, onDataUpdate }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  
  const [isConnected, setIsConnected] = useState(false);
  const [showMicroCandles, setShowMicroCandles] = useState(true);
  const [replaySpeed, setReplaySpeed] = useState(1);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 600,
      layout: {
        background: { color: '#1e1e1e' },
        textColor: '#d1d5db',
      },
      grid: {
        vertLines: { color: '#374151' },
        horzLines: { color: '#374151' },
      },
      timeScale: {
        borderColor: '#4b5563',
        timeVisible: true,
        secondsVisible: true,
      },
      rightPriceScale: {
        borderColor: '#4b5563',
      },
    });

    // Add candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#3b82f6',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: 'volume',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  useEffect(() => {
    // Connect to WebSocket for real-time micro-candle data
    const ws = new WebSocket(`ws://localhost:8000/api/v1/micro-candle/ws/${symbol}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('Connected to micro-candle stream');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'micro_candle_update' && showMicroCandles) {
        const microCandle = data.data.micro_candle;
        
        // Update chart
        if (candleSeriesRef.current) {
          candleSeriesRef.current.update({
            time: microCandle.timestamp,
            open: microCandle.open,
            high: microCandle.high,
            low: microCandle.low,
            close: microCandle.close,
          });
        }
        
        // Update volume
        if (volumeSeriesRef.current) {
          volumeSeriesRef.current.update({
            time: microCandle.timestamp,
            value: microCandle.volume,
            color: microCandle.close >= microCandle.open ? '#10b981' : '#ef4444',
          });
        }
        
        // Notify parent component
        onDataUpdate(microCandle);
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from micro-candle stream');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return () => {
      ws.close();
    };
  }, [symbol, showMicroCandles, onDataUpdate]);

  const startReplay = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/backtesting/start-enhanced-replay', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol,
          timeframe: '1m',
          start_date: '2023-01-01T09:15:00Z',
          end_date: '2023-01-01T15:30:00Z',
          replay_speed: replaySpeed,
          enable_micro_candles: true,
        }),
      });
      
      const result = await response.json();
      console.log('Replay started:', result);
    } catch (error) {
      console.error('Failed to start replay:', error);
    }
  };

  return (
    <div className="micro-candle-chart">
      <div className="chart-controls">
        <h3>Micro-Candle Chart: {symbol}</h3>
        
        <div className="control-group">
          <button 
            onClick={startReplay}
            disabled={!isConnected}
            className="start-btn"
          >
            Start Replay
          </button>
          
          <label>
            <input
              type="checkbox"
              checked={showMicroCandles}
              onChange={(e) => setShowMicroCandles(e.target.checked)}
            />
            Show Micro-Candles
          </label>
          
          <div className="speed-control">
            <label>Speed: </label>
            <select 
              value={replaySpeed} 
              onChange={(e) => setReplaySpeed(Number(e.target.value))}
            >
              <option value={0.5}>0.5x</option>
              <option value={1}>1x</option>
              <option value={2}>2x</option>
              <option value={5}>5x</option>
            </select>
          </div>
        </div>
        
        <div className="connection-status">
          Status: {isConnected ? 
            <span className="connected">Connected</span> : 
            <span className="disconnected">Disconnected</span>
          }
        </div>
      </div>
      
      <div ref={chartContainerRef} className="chart-container" />
    </div>
  );
};

export default MicroCandleChart;
```

### 4.2 Strategy Performance Dashboard

```typescript
// frontend/src/components/StrategyPerformanceDashboard.tsx
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PerformanceData {
  timestamp: string;
  pnl: number;
  equity: number;
  drawdown: number;
  trades: number;
  win_rate: number;
}

interface StrategyPerformanceDashboardProps {
  backtestId: string;
}

const StrategyPerformanceDashboard: React.FC<StrategyPerformanceDashboardProps> = ({ backtestId }) => {
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [summary, setSummary] = useState({
    total_pnl: 0,
    total_trades: 0,
    win_rate: 0,
    max_drawdown: 0,
    sharpe_ratio: 0
  });

  useEffect(() => {
    // Fetch performance data
    const fetchPerformanceData = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/backtesting/performance/${backtestId}`);
        const data = await response.json();
        
        setPerformanceData(data.equity_curve);
        setSummary(data.summary);
      } catch (error) {
        console.error('Failed to fetch performance data:', error);
      }
    };

    fetchPerformanceData();
    
    // Set up real-time updates
    const ws = new WebSocket(`ws://localhost:8000/api/v1/backtesting/performance-ws/${backtestId}`);
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      
      if (update.type === 'performance_update') {
        setPerformanceData(prev => [...prev, update.data]);
        
        // Update summary
        setSummary(prev => ({
          ...prev,
          total_pnl: update.data.equity,
          total_trades: update.data.trades,
          win_rate: update.data.win_rate
        }));
      }
    };
    
    return () => {
      ws.close();
    };
  }, [backtestId]);

  return (
    <div className="strategy-performance-dashboard">
      <h2>Strategy Performance Dashboard</h2>
      
      <div className="summary-cards">
        <div className="card">
          <h3>Total P&L</h3>
          <p className={summary.total_pnl >= 0 ? 'positive' : 'negative'}>
            ₹{summary.total_pnl.toFixed(2)}
          </p>
        </div>
        
        <div className="card">
          <h3>Total Trades</h3>
          <p>{summary.total_trades}</p>
        </div>
        
        <div className="card">
          <h3>Win Rate</h3>
          <p>{(summary.win_rate * 100).toFixed(1)}%</p>
        </div>
        
        <div className="card">
          <h3>Max Drawdown</h3>
          <p className="negative">{(summary.max_drawdown * 100).toFixed(2)}%</p>
        </div>
        
        <div className="card">
          <h3>Sharpe Ratio</h3>
          <p>{summary.sharpe_ratio.toFixed(2)}</p>
        </div>
      </div>
      
      <div className="charts">
        <div className="chart-container">
          <h3>Equity Curve</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="equity" 
                stroke="#8884d8" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="chart-container">
          <h3>Drawdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="drawdown" 
                stroke="#82ca9d" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default StrategyPerformanceDashboard;
```

## 5. Performance Optimization Examples

### 5.1 Batch Processing for Large Datasets

```python
# backend/fastapi/app/services/batch_micro_candle_processor.py
import asyncio
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from .micro_candle_generator import MicroCandleGenerator
from .historical_data_fetcher import Candle

class BatchMicroCandleProcessor:
    def __init__(self, batch_size: int = 1000, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.generator = MicroCandleGenerator()
    
    async def process_large_dataset(
        self, 
        candles: List[Candle], 
        progress_callback=None
    ) -> List[Dict]:
        """Process large dataset in batches"""
        total_candles = len(candles)
        all_micro_candles = []
        
        # Create batches
        batches = [
            candles[i:i + self.batch_size] 
            for i in range(0, total_candles, self.batch_size)
        ]
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            loop = asyncio.get_event_loop()
            
            # Submit all batches for processing
            tasks = []
            for i, batch in enumerate(batches):
                task = loop.run_in_executor(
                    executor, 
                    self._process_batch, 
                    batch, 
                    i
                )
                tasks.append(task)
            
            # Wait for all batches to complete
            batch_results = await asyncio.gather(*tasks)
            
            # Combine results
            for i, result in enumerate(batch_results):
                all_micro_candles.extend(result)
                
                # Report progress
                if progress_callback:
                    progress = ((i + 1) / len(batches)) * 100
                    progress_callback(progress)
        
        return all_micro_candles
    
    def _process_batch(self, batch: List[Candle], batch_index: int) -> List[Dict]:
        """Process a single batch of candles"""
        micro_candles = []
        
        for i in range(len(batch) - 1):
            current = batch[i]
            next_candle = batch[i + 1]
            
            batch_micros = self.generator.generate_micro_candles(current, next_candle)
            micro_candles.extend([mc.__dict__ for mc in batch_micros])
        
        return micro_candles
```

### 5.2 Caching Strategy

```python
# backend/fastapi/app/services/micro_candle_cache.py
import redis
import json
import pickle
from typing import List, Optional
from datetime import datetime, timedelta
from .historical_data_fetcher import Candle

class MicroCandleCache:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.cache_ttl = 3600  # 1 hour
    
    def _get_cache_key(self, symbol: str, start_date: datetime, end_date: datetime, config_hash: str) -> str:
        """Generate cache key for micro-candles"""
        return f"micro_candles:{symbol}:{start_date.strftime('%Y%m%d')}:{end_date.strftime('%Y%m%d')}:{config_hash}"
    
    async def get_cached_micro_candles(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime, 
        config_hash: str
    ) -> Optional[List[Dict]]:
        """Get cached micro-candles"""
        cache_key = self._get_cache_key(symbol, start_date, end_date, config_hash)
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return pickle.loads(cached_data)
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    async def cache_micro_candles(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime, 
        config_hash: str, 
        micro_candles: List[Dict]
    ):
        """Cache micro-candles"""
        cache_key = self._get_cache_key(symbol, start_date, end_date, config_hash)
        
        try:
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                pickle.dumps(micro_candles)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def invalidate_cache(self, symbol: str):
        """Invalidate cache for a symbol"""
        pattern = f"micro_candles:{symbol}:*"
        keys = self.redis_client.keys(pattern)
        
        if keys:
            self.redis_client.delete(*keys)
```

These usage examples provide comprehensive guidance for implementing and using the micro-candle generation system across different components of your trading infrastructure.