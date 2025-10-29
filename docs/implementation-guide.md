# Algorithmic Trading System Implementation Guide

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Infrastructure Configuration](#infrastructure-configuration)
3. [Core Services Implementation](#core-services-implementation)
4. [N8N Strategy Development](#n8n-strategy-development)
5. [Frontend Development](#frontend-development)
6. [Testing and Deployment](#testing-and-deployment)

## Development Environment Setup

### Prerequisites
```bash
# System Requirements
- Ubuntu 20.04+ / CentOS 8+ / Windows 10+
- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+
- Python 3.9+
- Git 2.30+

# Development Tools
- VS Code / PyCharm
- Postman / Insomnia
- DBeaver / pgAdmin
- Redis Desktop Manager
```

### Project Structure Creation
```bash
# Create main project directory
mkdir VELOX-N8N
cd VELOX-N8N

# Create subdirectories
mkdir -p backend/fastapi/app/{api,core,models,services,utils}
mkdir -p backend/n8n/{custom-nodes,workflows}
mkdir -p frontend/src/{components,pages,services,store,utils}
mkdir -p infrastructure/{nginx,grafana,postgres,redis}
mkdir -p docs
mkdir -p scripts
mkdir -p tests

# Initialize git repository
git init
echo "# VELOX-N8N Algorithmic Trading System" > README.md
```

### Environment Configuration
```bash
# Create environment files
touch .env
touch .env.example
touch docker-compose.yml
touch docker-compose.dev.yml
```

## Infrastructure Configuration

### Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: velo_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./infrastructure/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - fastapi
      - frontend
    networks:
      - velo_network

  # FastAPI Backend
  fastapi:
    build:
      context: ./backend/fastapi
      dockerfile: Dockerfile
    container_name: velo_fastapi
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/velo_trading
      - REDIS_URL=redis://redis:6379
      - OPENALGO_URL=http://openalgo:3000
    depends_on:
      - postgres
      - redis
      - openalgo
    volumes:
      - ./backend/fastapi:/app
    networks:
      - velo_network

  # N8N Workflow Engine
  n8n:
    image: n8nio/n8n:latest
    container_name: velo_n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=password
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=postgres
      - DB_POSTGRESDB_PASSWORD=password
    depends_on:
      - postgres
    volumes:
      - ./backend/n8n/custom-nodes:/home/node/.n8n/custom
      - ./backend/n8n/workflows:/home/node/.n8n/workflows
    networks:
      - velo_network

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: velo_frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_WS_URL=ws://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - velo_network

  # PostgreSQL Database
  postgres:
    image: postgres:14
    container_name: velo_postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=velo_trading
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - velo_network

  # Redis Cache
  redis:
    image: redis:6-alpine
    container_name: velo_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - velo_network

  # Grafana Monitoring
  grafana:
    image: grafana/grafana:latest
    container_name: velo_grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./infrastructure/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./infrastructure/grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - postgres
    networks:
      - velo_network

  # OpenAlgo Gateway
  openalgo:
    image: openalgo/openalgo:latest
    container_name: velo_openalgo
    ports:
      - "3000:3000"
    environment:
      - OPENALGO_ENV=production
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/openalgo
    depends_on:
      - postgres
    volumes:
      - openalgo_data:/app/data
    networks:
      - velo_network

volumes:
  postgres_data:
  redis_data:
  grafana_data:
  openalgo_data:

networks:
  velo_network:
    driver: bridge
```

### Environment Variables
```bash
# .env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/velo_trading
REDIS_URL=redis://localhost:6379

# API Configuration
FASTAPI_SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAlgo Configuration
OPENALGO_URL=http://localhost:3000
OPENALGO_API_KEY=your-openalgo-api-key

# Broker Configuration
BROKER_NAME=your-broker-name
BROKER_API_KEY=your-broker-api-key
BROKER_API_SECRET=your-broker-secret

# Market Data Configuration
MARKET_DATA_API_KEY=your-market-data-api-key
MARKET_DATA_URL=https://api.market-data.com

# Email Configuration (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/app/logs/velo-trading.log
```

## Core Services Implementation

### FastAPI Backend Setup

#### Requirements and Dependencies
```python
# backend/fastapi/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
websockets==12.0
pandas==2.1.3
numpy==1.25.2
ta-lib==0.4.28
requests==2.31.0
aiohttp==3.9.1
celery==5.3.4
pytest==7.4.3
pytest-asyncio==0.21.1
```

#### FastAPI Application Structure
```python
# backend/fastapi/app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, trading, strategies, indicators
from app.core.config import settings
from app.core.database import engine
from app.models import user, strategy, trade
import uvicorn

app = FastAPI(
    title="VELOX-N8N Trading API",
    description="Algorithmic Trading System API",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["trading"])
app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["strategies"])
app.include_router(indicators.router, prefix="/api/v1/indicators", tags=["indicators"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Database Models
```python
# backend/fastapi/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="investor")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    strategies = relationship("Strategy", back_populates="creator")
    trades = relationship("Trade", back_populates="user")

# backend/fastapi/app/models/strategy.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    type = Column(String(50), nullable=False)  # trend, mean_reversion, momentum
    config = Column(JSON, nullable=False)
    n8n_workflow_id = Column(String(100))
    is_active = Column(Boolean, default=False)
    is_paper_trading = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")

# backend/fastapi/app/models/trade.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(10), nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    order_id = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="trades")
    user = relationship("User", back_populates="trades")
```

#### API Endpoints
```python
# backend/fastapi/app/api/trading.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.trade import Trade
from app.schemas.trading import TradeCreate, TradeResponse
from app.services.trading_service import TradingService
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/orders", response_model=TradeResponse)
async def place_order(
    order: TradeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Place a new trading order"""
    trading_service = TradingService(db)
    return await trading_service.place_order(order, current_user.id)

@router.get("/positions")
async def get_positions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current positions"""
    trading_service = TradingService(db)
    return await trading_service.get_positions(current_user.id)

@router.get("/trades")
async def get_trades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get trade history"""
    trading_service = TradingService(db)
    return await trading_service.get_trades(current_user.id, skip, limit)
```

## N8N Strategy Development

### Custom Trading Nodes Development

#### Market Data Node
```javascript
// backend/n8n/custom-nodes/MarketData/MarketData.node.ts
import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
} from 'n8n-workflow';

export class MarketData implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'Market Data',
		name: 'marketData',
		group: ['transform'],
		version: 1,
		description: 'Fetch real-time market data for trading symbols',
		defaults: {
			name: 'Market Data',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'marketDataApi',
				required: true,
			},
		],
		properties: [
			{
				displayName: 'Symbol',
				name: 'symbol',
				type: 'string',
				default: 'NIFTY 50',
				required: true,
				description: 'Trading symbol',
			},
			{
				displayName: 'Exchange',
				name: 'exchange',
				type: 'options',
				options: [
					{
						name: 'NSE',
						value: 'NSE',
					},
					{
						name: 'BSE',
						value: 'BSE',
					},
				],
				default: 'NSE',
				required: true,
			},
			{
				displayName: 'Data Type',
				name: 'dataType',
				type: 'options',
				options: [
					{
						name: 'Quote',
						value: 'quote',
					},
					{
						name: 'OHLC',
						value: 'ohlc',
					},
					{
						name: 'Depth',
						value: 'depth',
					},
				],
				default: 'quote',
				required: true,
			},
		],
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];
		const credentials = await this.getCredentials('marketDataApi');
		
		for (let i = 0; i < items.length; i++) {
			const symbol = this.getNodeParameter('symbol', i) as string;
			const exchange = this.getNodeParameter('exchange', i) as string;
			const dataType = this.getNodeParameter('dataType', i) as string;
			
			// Fetch market data from API
			const marketData = await fetchMarketData(
				symbol,
				exchange,
				dataType,
				credentials
			);
			
			returnData.push({
				json: marketData,
			});
		}
		
		return [returnData];
	}
}

async function fetchMarketData(
	symbol: string,
	exchange: string,
	dataType: string,
	credentials: any
): Promise<any> {
	// Implementation to fetch market data from your data provider
	// This would integrate with your FastAPI market data endpoint
	
	const response = await fetch(`${credentials.apiUrl}/market-data/${symbol}`, {
		headers: {
			'Authorization': `Bearer ${credentials.apiKey}`,
			'Content-Type': 'application/json',
		},
	});
	
	const data = await response.json();
	return data;
}
```

#### Technical Indicator Node
```javascript
// backend/n8n/custom-nodes/Indicators/TechnicalIndicator.node.ts
import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
} from 'n8n-workflow';

export class TechnicalIndicator implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'Technical Indicator',
		name: 'technicalIndicator',
		group: ['transform'],
		version: 1,
		description: 'Calculate technical indicators for market data',
		defaults: {
			name: 'Technical Indicator',
		},
		inputs: ['main'],
		outputs: ['main'],
		properties: [
			{
				displayName: 'Indicator Type',
				name: 'indicatorType',
				type: 'options',
				options: [
					{
						name: 'SMA',
						value: 'sma',
					},
					{
						name: 'EMA',
						value: 'ema',
					},
					{
						name: 'RSI',
						value: 'rsi',
					},
					{
						name: 'MACD',
						value: 'macd',
					},
					{
						name: 'Bollinger Bands',
						value: 'bollinger',
					},
				],
				default: 'sma',
				required: true,
			},
			{
				displayName: 'Period',
				name: 'period',
				type: 'number',
				default: 14,
				required: true,
				description: 'Period for indicator calculation',
			},
			{
				displayName: 'Source Data',
				name: 'sourceData',
				type: 'string',
				default: 'close',
				required: true,
				description: 'JSON path to price data (e.g., $.data.close)',
			},
		],
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];
		
		for (let i = 0; i < items.length; i++) {
			const indicatorType = this.getNodeParameter('indicatorType', i) as string;
			const period = this.getNodeParameter('period', i) as number;
			const sourceData = this.getNodeParameter('sourceData', i) as string;
			
			// Extract price data from input
			const priceData = this.evaluateExpression(sourceData, items[i]) as number[];
			
			// Calculate indicator
			const indicatorValue = await calculateIndicator(
				indicatorType,
				period,
				priceData
			);
			
			returnData.push({
				json: {
					indicator: indicatorType,
					period: period,
					value: indicatorValue,
					timestamp: new Date().toISOString(),
				},
			});
		}
		
		return [returnData];
	}
}

async function calculateIndicator(
	type: string,
	period: number,
	data: number[]
): Promise<number> {
	// Implementation would call your FastAPI indicator service
	const response = await fetch(`http://fastapi:8000/api/v1/indicators/calculate`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			type: type,
			period: period,
			data: data,
		}),
	});
	
	const result = await response.json();
	return result.value;
}
```

### Strategy Workflow Templates

#### Trend Following Strategy Workflow
```json
{
  "name": "Trend Following Strategy",
  "nodes": [
    {
      "parameters": {
        "symbol": "NIFTY 50",
        "exchange": "NSE",
        "dataType": "quote"
      },
      "name": "Get Market Data",
      "type": "n8n-nodes-base.marketData",
      "position": [240, 300]
    },
    {
      "parameters": {
        "indicatorType": "ema",
        "period": 20,
        "sourceData": "$.data.close"
      },
      "name": "EMA 20",
      "type": "n8n-nodes-base.technicalIndicator",
      "position": [460, 200]
    },
    {
      "parameters": {
        "indicatorType": "ema",
        "period": 50,
        "sourceData": "$.data.close"
      },
      "name": "EMA 50",
      "type": "n8n-nodes-base.technicalIndicator",
      "position": [460, 400]
    },
    {
      "parameters": {
        "series1": "$.EMA_20.value",
        "series2": "$.EMA_50.value",
        "direction": "up"
      },
      "name": "Check Crossover",
      "type": "n8n-nodes-base.crossover",
      "position": [680, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "id": "crossover_condition",
              "leftValue": "={{$json.crossover}}",
              "rightValue": true,
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            }
          ],
          "combinator": "and"
        },
        "options": {}
      },
      "name": "Signal Filter",
      "type": "n8n-nodes-base.if",
      "position": [900, 300]
    },
    {
      "parameters": {
        "method": "volatility_based",
        "riskPercent": 2,
        "accountSize": 100000
      },
      "name": "Position Sizing",
      "type": "n8n-nodes-base.positionSizer",
      "position": [1120, 200]
    },
    {
      "parameters": {
        "method": "atr_based",
        "multiplier": 2
      },
      "name": "Stop Loss",
      "type": "n8n-nodes-base.stopLoss",
      "position": [1120, 400]
    },
    {
      "parameters": {
        "symbol": "={{$node['Get Market Data'].json['symbol']}}",
        "side": "BUY",
        "quantity": "={{$node['Position Sizing'].json['quantity']}}",
        "orderType": "MARKET"
      },
      "name": "Place Order",
      "type": "n8n-nodes-base.placeOrder",
      "position": [1340, 300]
    }
  ],
  "connections": {
    "Get Market Data": {
      "main": [
        [
          {
            "node": "EMA 20",
            "type": "main",
            "index": 0
          },
          {
            "node": "EMA 50",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "EMA 20": {
      "main": [
        [
          {
            "node": "Check Crossover",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "EMA 50": {
      "main": [
        [
          {
            "node": "Check Crossover",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check Crossover": {
      "main": [
        [
          {
            "node": "Signal Filter",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Signal Filter": {
      "main": [
        [
          {
            "node": "Position Sizing",
            "type": "main",
            "index": 0
          },
          {
            "node": "Stop Loss",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Position Sizing": {
      "main": [
        [
          {
            "node": "Place Order",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Stop Loss": {
      "main": [
        [
          {
            "node": "Place Order",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## Frontend Development

### React Application Structure
```typescript
// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { store } from './store';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Strategies from './pages/Strategies';
import Trading from './pages/Trading';
import Portfolio from './pages/Portfolio';
import ProtectedRoute from './components/ProtectedRoute';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route index element={<Dashboard />} />
                    <Route path="strategies" element={<Strategies />} />
                    <Route path="trading" element={<Trading />} />
                    <Route path="portfolio" element={<Portfolio />} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            } />
          </Routes>
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
```

### Trading Dashboard Component
```typescript
// frontend/src/pages/Trading.tsx
import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchPositions, fetchTrades, placeOrder } from '../store/slices/tradingSlice';
import OrderForm from '../components/OrderForm';
import PositionChart from '../components/PositionChart';

const Trading: React.FC = () => {
  const dispatch = useDispatch();
  const { positions, trades, loading } = useSelector((state: any) => state.trading);
  const [showOrderForm, setShowOrderForm] = useState(false);

  useEffect(() => {
    dispatch(fetchPositions());
    dispatch(fetchTrades());
  }, [dispatch]);

  const handlePlaceOrder = async (orderData: any) => {
    try {
      await dispatch(placeOrder(orderData));
      setShowOrderForm(false);
      // Refresh data
      dispatch(fetchPositions());
      dispatch(fetchTrades());
    } catch (error) {
      console.error('Failed to place order:', error);
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Trading Dashboard
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => setShowOrderForm(true)}
            >
              Place Order
            </Button>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Positions
            </Typography>
            <PositionChart positions={positions} />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Quick Stats
            </Typography>
            <Typography variant="body1">
              Total P&L: ₹{positions.reduce((sum, pos) => sum + pos.pnl, 0).toFixed(2)}
            </Typography>
            <Typography variant="body1">
              Active Positions: {positions.length}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Trades
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Symbol</TableCell>
                    <TableCell>Side</TableCell>
                    <TableCell>Quantity</TableCell>
                    <TableCell>Price</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Timestamp</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {trades.slice(0, 10).map((trade) => (
                    <TableRow key={trade.id}>
                      <TableCell>{trade.symbol}</TableCell>
                      <TableCell>{trade.side}</TableCell>
                      <TableCell>{trade.quantity}</TableCell>
                      <TableCell>₹{trade.price}</TableCell>
                      <TableCell>{trade.status}</TableCell>
                      <TableCell>{new Date(trade.timestamp).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>

      {showOrderForm && (
        <OrderForm
          open={showOrderForm}
          onClose={() => setShowOrderForm(false)}
          onSubmit={handlePlaceOrder}
        />
      )}
    </Grid>
  );
};

export default Trading;
```

## Testing and Deployment

### Testing Strategy
```bash
# Backend Testing
cd backend/fastapi
pytest tests/ -v --cov=app

# Frontend Testing
cd frontend
npm test -- --coverage --watchAll=false

# Integration Testing
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Deployment Scripts
```bash
#!/bin/bash
# scripts/deploy.sh

echo "Deploying VELOX-N8N Trading System..."

# Build and start services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
sleep 30

# Run database migrations
docker-compose exec fastapi alembic upgrade head

# Initialize N8N custom nodes
docker-compose exec n8n npm install /home/node/.n8n/custom

# Setup Grafana dashboards
docker-compose exec grafana grafana-cli import-dashboard /etc/grafana/provisioning/dashboards/trading-dashboard.json

echo "Deployment completed successfully!"
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:8000"
echo "N8N: http://localhost:5678"
echo "Grafana: http://localhost:3001"
```

This implementation guide provides a comprehensive roadmap for building your algorithmic trading system with N8N-based strategy design. The modular architecture allows for incremental development and easy scaling as your requirements evolve.