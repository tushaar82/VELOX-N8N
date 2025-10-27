# 🚀 VELOX Quick Start Guide

Get up and running in 5 minutes!

---

## ⚡ Quick Start

### 1. Configure (2 minutes)

```bash
# Copy environment file
cp .env.example .env

# Edit with your API key
nano .env
```

**Required:** Set `OPENALGO_API_KEY=your_key_here`

### 2. Start (1 minute)

```bash
# Make scripts executable
chmod +x docker-start.sh docker-stop.sh

# Start everything
./docker-start.sh
```

### 3. Access (2 minutes)

| Service | URL | Credentials |
|---------|-----|-------------|
| **VELOX API** | http://localhost:8000/docs | - |
| **n8n** | http://localhost:5678 | admin / changeme123 |
| **Node-RED** | http://localhost:1880 | - |
| **Grafana** | http://localhost:3001 | admin / changeme123 |

---

## 📝 Common Commands

```bash
# Start services
./docker-start.sh

# Stop services
./docker-stop.sh

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Status
docker-compose ps
```

---

## 🧪 Test API

```bash
# Health check
curl http://localhost:8000/health

# Get available indicators
curl http://localhost:8000/api/v1/indicators/available

# Calculate RSI
curl -X POST http://localhost:8000/api/v1/indicators/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NIFTY",
    "exchange": "NSE",
    "interval": "5m",
    "indicators": ["RSI"]
  }'
```

---

## 🔌 Integration Examples

### n8n Workflow

1. Open http://localhost:5678
2. Create new workflow
3. Add HTTP Request node:
   - URL: `http://velox-api:8000/api/v1/indicators/calculate`
   - Method: POST
   - Body: See test example above

### Node-RED Flow

1. Open http://localhost:1880
2. Drag HTTP Request node
3. Configure:
   - URL: `http://velox-api:8000/api/v1/candles/NIFTY?exchange=NSE&interval=5m`
   - Method: GET

### Grafana Dashboard

1. Open http://localhost:3001
2. Login with admin/changeme123
3. Add datasource:
   - Type: JSON API
   - URL: `http://velox-api:8000`
4. Create dashboard

---

## 🛑 Stop Everything

```bash
./docker-stop.sh

# Or remove all data
docker-compose down -v
```

---

## 📚 Full Documentation

See [DOCKER-GUIDE.md](DOCKER-GUIDE.md) for complete documentation.

---

**That's it! You're ready to go! 🎉**
