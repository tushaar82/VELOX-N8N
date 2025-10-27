# VELOX Real-Time Technical Analysis System

A comprehensive FastAPI application for real-time technical analysis and market data with OpenAlgo integration, 43+ technical indicators, NSE option chain scraping, and WebSocket streaming.

## 🚀 Features

- **43+ Technical Indicators**: Complete suite from the `ta` library including RSI, MACD, Bollinger Bands, and more
- **Real-time WebSocket Streaming**: Tick-by-tick updates with multi-timeframe candle aggregation
- **Support/Resistance Levels**: Advanced algorithms using swing highs/lows with ATR clustering
- **NSE Option Chain**: Live option chain data scraping for indices and equities
- **Multi-timeframe Analysis**: Simultaneous analysis across multiple timeframes (1m, 5m, 15m, 1h, 1d)
- **OpenAlgo Integration**: Seamless integration for historical OHLCV data
- **Production-ready**: Async-first design with comprehensive error handling

## 📋 Prerequisites

- Python 3.10 or higher
- OpenAlgo server running (for market data)
- Chromium browser (installed via Playwright)

## 🛠️ Installation

### Option 1: Docker (Recommended) 🐳

**Includes:** VELOX API + n8n + Node-RED + Grafana + PostgreSQL + Redis

```bash
# 1. Configure
cp .env.example .env
nano .env  # Set OPENALGO_API_KEY and passwords

# 2. Start everything
chmod +x docker-start.sh
./docker-start.sh

# 3. Access services
# VELOX API: http://localhost:8000/docs
# n8n:       http://localhost:5678
# Node-RED:  http://localhost:1880
# Grafana:   http://localhost:3001
```

📚 **Full Docker Guide:** [DOCKER-GUIDE.md](DOCKER-GUIDE.md)  
⚡ **Quick Start:** [QUICK-START.md](QUICK-START.md)

### Option 2: Manual Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd VELOX-N8N
```

#### 2. Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Create a virtual environment
- Install all Python dependencies
- Install Playwright browsers
- Create `.env` file from template

#### 3. Configure Environment Variables

Edit the `.env` file and add your OpenAlgo API key:

```bash
OPENALGO_API_KEY=your_actual_api_key_here
OPENALGO_HOST=http://127.0.0.1:5000
```

### 4. (Optional) Clone OpenAlgo Reference

```bash
chmod +x scripts/clone_openalgo.sh
./scripts/clone_openalgo.sh
```

## 🚦 Running the Application

### Development Mode

```bash
chmod +x scripts/run_dev.sh
./scripts/run_dev.sh
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
chmod +x scripts/run_prod.sh
./scripts/run_prod.sh
```

### Using Docker

```bash
docker-compose up -d
```

## 📚 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Indicators

- `POST /api/v1/indicators/calculate` - Calculate specific indicators
- `POST /api/v1/indicators/calculate-all` - Calculate all 43+ indicators
- `GET /api/v1/indicators/available` - List available indicators
- `POST /api/v1/indicators/support-resistance` - Calculate S/R levels
- `POST /api/v1/indicators/multi-timeframe` - Multi-timeframe analysis

### Option Chain

- `POST /api/v1/option-chain/fetch` - Fetch option chain data
- `POST /api/v1/option-chain/fetch-index` - Fetch index option chain
- `POST /api/v1/option-chain/fetch-stock` - Fetch stock option chain
- `GET /api/v1/option-chain/supported-symbols` - List supported symbols

### WebSocket

- `WS /api/v1/ws/stream` - Real-time tick and indicator updates

### Metadata

- `GET /api/v1/meta/indicators` - List all indicators with details
- `GET /api/v1/meta/timeframes` - List supported timeframes
- `GET /api/v1/meta/exchanges` - List supported exchanges
- `GET /api/v1/meta/active-subscriptions` - Current WebSocket subscriptions
- `GET /api/v1/meta/system-status` - System health and statistics

## 📊 Available Technical Indicators

### Volume Indicators
MFI, ADI, OBV, CMF, ForceIndex, EaseOfMovement, VPT, NVI, VWAP

### Volatility Indicators
ATR, BollingerBands, KeltnerChannel, DonchianChannel, UlcerIndex

### Trend Indicators
SMA, EMA, WMA, MACD, ADX, VortexIndicator, TRIX, MassIndex, CCI, DPO, KST, Ichimoku, PSAR, STC, Aroon

### Momentum Indicators
RSI, StochRSI, TSI, UltimateOscillator, StochasticOscillator, WilliamsR, AwesomeOscillator, KAMA, ROC, PPO, PVO

### Others
DailyReturn, DailyLogReturn, CumulativeReturn

## 🌐 WebSocket Usage

### Connect to WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/stream');

ws.onopen = () => {
  // Subscribe to symbols and timeframes
  ws.send(JSON.stringify({
    action: 'subscribe',
    symbols: ['NIFTY', 'BANKNIFTY'],
    timeframes: ['1m', '5m'],
    indicators: ['RSI', 'MACD', 'EMA']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Message Types

- **Candle Update**: `{"type": "candle", "symbol": "NIFTY", "timeframe": "1m", "data": {...}}`
- **Indicator Update**: `{"type": "indicator", "symbol": "NIFTY", "timeframe": "1m", "indicators": {...}}`
- **Acknowledgment**: `{"type": "ack", "action": "subscribed", "symbols": [...]}`
- **Error**: `{"type": "error", "message": "..."}`

## 🔧 Supported Timeframes

- `1m`, `3m`, `5m`, `10m`, `15m`, `30m` - Minutes
- `1h`, `2h`, `4h` - Hours
- `1d`, `1w`, `1M` - Days, Weeks, Months

## 📖 Example Usage

### Calculate RSI and MACD

```python
import requests

response = requests.post('http://localhost:8000/api/v1/indicators/calculate', json={
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "5m",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "indicators": ["RSI", "MACD"]
})

data = response.json()
print(data['indicators'])
```

### Fetch Option Chain

```python
import requests

response = requests.post('http://localhost:8000/api/v1/option-chain/fetch', json={
    "symbol": "NIFTY",
    "is_index": True
})

option_chain = response.json()
print(option_chain['options'])
```

### Calculate Support/Resistance

```python
import requests

response = requests.post('http://localhost:8000/api/v1/indicators/support-resistance', json={
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "1d",
    "lookback_days": 90
})

levels = response.json()
print('Support:', levels['support_levels'])
print('Resistance:', levels['resistance_levels'])
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v --cov=app
```

## 📁 Project Structure

```
VELOX-N8N/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── indicators.py
│   │       │   ├── option_chain.py
│   │       │   ├── websocket.py
│   │       │   └── meta.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── schemas/
│   │   ├── candles.py
│   │   ├── indicators.py
│   │   └── option_chain.py
│   ├── services/
│   │   ├── market_data.py
│   │   ├── indicators.py
│   │   ├── support_resistance.py
│   │   ├── option_chain.py
│   │   ├── tick_stream.py
│   │   └── websocket_manager.py
│   ├── utils/
│   │   ├── timeframes.py
│   │   └── validators.py
│   └── main.py
├── tests/
├── scripts/
├── docs/
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

## 🐳 Docker Deployment

Build and run with Docker:

```bash
docker build -t velox-analysis .
docker run -p 8000:8000 --env-file .env velox-analysis
```

Or use docker-compose:

```bash
docker-compose up -d
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENALGO_API_KEY` | OpenAlgo API key | Required |
| `OPENALGO_HOST` | OpenAlgo server URL | http://127.0.0.1:5000 |
| `OPENALGO_VERSION` | API version | v1 |
| `CORS_ORIGINS` | Allowed CORS origins | localhost:3000 |
| `LOG_LEVEL` | Logging level | INFO |
| `MAX_WEBSOCKET_CONNECTIONS` | Max WebSocket connections | 100 |
| `TICK_BUFFER_SIZE` | Tick buffer size per symbol | 1000 |
| `DEFAULT_TIMEFRAMES` | Default timeframes | 1m,5m,15m,1h,1d |

## 🔐 Security Considerations

- Never commit `.env` file to version control
- Use environment variables for sensitive data
- Implement rate limiting for production
- Use HTTPS in production
- Validate all user inputs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

[Your License Here]

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review API documentation at `/docs` endpoint

## 🙏 Acknowledgments

- **OpenAlgo** - Market data integration
- **ta library** - Technical indicators
- **FastAPI** - Web framework
- **Playwright** - Web scraping

## 📚 Additional Documentation

- [API Documentation](docs/API.md)
- [Indicators Guide](docs/INDICATORS.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

---

**Built with ❤️ for traders and developers**
