# VELOX-N8N Algorithmic Trading System

## Overview

A comprehensive algorithmic trading system that combines real-time tick-by-tick indicators with visual strategy development using N8N workflows, specifically designed for Indian markets (NSE/BSE) with multi-broker support through OpenAlgo.

## Features

- **Real-Time Tick-by-Tick Indicators**: TradingView-like experience with 50+ technical indicators
- **Visual Strategy Development**: No-code strategy design using N8N workflows
- **Multi-Broker Support**: Integration with Indian markets through OpenAlgo
- **Micro-Candle Generation**: 10 micro-candles per minute for granular backtesting
- **Advanced Risk Management**: Multiple position sizing methods and portfolio controls
- **Comprehensive Frontend**: React-based dashboard with real-time charts
- **Backtesting Framework**: Historical replay with strategy optimization

## Technology Stack

### Backend
- **FastAPI**: High-performance async API framework
- **PostgreSQL**: Primary database for trades, strategies, users
- **Redis**: Real-time caching and session management
- **TA-Lib**: Technical analysis library
- **WebSockets**: Real-time data streaming

### Frontend
- **React 18**: Modern UI framework with TypeScript
- **Material-UI**: Professional component library
- **Redux Toolkit**: State management
- **Chart.js**: Interactive charts and visualization

### Infrastructure
- **Docker**: Containerized deployment
- **N8N**: Visual workflow automation
- **Nginx**: Reverse proxy and load balancing
- **Grafana**: System monitoring and analytics
- **OpenAlgo**: Multi-broker trading gateway

## Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+
- Python 3.9+
- Git 2.30+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/VELOX-N8N.git
cd VELOX-N8N
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the development environment**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

4. **Initialize the database**
```bash
docker-compose exec fastapi alembic upgrade head
```

5. **Access the applications**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- N8N: http://localhost:5678
- Grafana: http://localhost:3001

## Documentation

- [Implementation Plan](complete-implementation-plan.md)
- [Detailed Task Breakdown](detailed-task-breakdown.md)
- [Project Roadmap](project-roadmap.md)
- [Implementation Checklist](implementation-checklist.md)
- [Architecture Plan](architecture-plan.md)
- [API Documentation](api-documentation.md)

## Project Structure

```
VELOX-N8N/
├── backend/
│   ├── fastapi/                 # FastAPI backend application
│   │   ├── app/
│   │   │   ├── api/            # API endpoints
│   │   │   ├── core/           # Core configuration
│   │   │   ├── models/          # Database models
│   │   │   ├── services/        # Business logic
│   │   │   └── utils/           # Utility functions
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── n8n/                    # N8N workflows and custom nodes
│       ├── custom-nodes/
│       └── workflows/
├── frontend/                     # React frontend application
│   ├── public/
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   ├── store/              # Redux store
│   │   └── utils/              # Utility functions
│   ├── package.json
│   └── Dockerfile
├── infrastructure/               # Infrastructure configuration
│   ├── nginx/
│   ├── grafana/
│   ├── postgres/
│   └── redis/
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
├── tests/                       # Test files
├── docker-compose.yml            # Production compose file
├── docker-compose.dev.yml       # Development compose file
└── .env.example                 # Environment variables template
```

## Development

### Backend Development
```bash
cd backend/fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Running Tests
```bash
# Backend tests
cd backend/fastapi
pytest

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.