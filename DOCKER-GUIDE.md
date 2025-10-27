# 🐳 VELOX Docker Deployment Guide

Complete guide for deploying VELOX with n8n, Grafana, and Node-RED using Docker.

---

## 📦 What's Included

This Docker setup includes:

1. **VELOX API** - Real-time technical analysis API (Port 8000)
2. **n8n** - Workflow automation platform (Port 5678)
3. **Node-RED** - Flow-based programming tool (Port 1880)
4. **Grafana** - Monitoring and visualization (Port 3001)
5. **PostgreSQL** - Database for n8n (Port 5432)
6. **Redis** - Cache and message broker (Port 6379)

---

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 10GB+ disk space

### 1. Clone and Configure

```bash
# Navigate to project directory
cd VELOX-N8N

# Copy environment file
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

**Important:** Update these values in `.env`:
- `OPENALGO_API_KEY` - Your OpenAlgo API key
- `N8N_PASSWORD` - Change from default
- `GRAFANA_PASSWORD` - Change from default
- `POSTGRES_PASSWORD` - Change from default

### 2. Start Services

```bash
# Make scripts executable
chmod +x docker-start.sh docker-stop.sh

# Start all services
./docker-start.sh
```

Or manually:

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access Services

Once started, access:

- **VELOX API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **n8n:** http://localhost:5678
- **Node-RED:** http://localhost:1880
- **Grafana:** http://localhost:3001

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file to configure:

```bash
# VELOX API
OPENALGO_API_KEY=your_api_key_here
OPENALGO_HOST=http://host.docker.internal:5000
LOG_LEVEL=INFO

# n8n
N8N_USER=admin
N8N_PASSWORD=changeme123

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=changeme123

# Database
POSTGRES_USER=n8n
POSTGRES_PASSWORD=changeme123
POSTGRES_DB=n8n

# Timezone
TIMEZONE=Asia/Kolkata
```

### Port Mapping

Default ports (can be changed in `docker-compose.yml`):

| Service | Internal | External | Description |
|---------|----------|----------|-------------|
| VELOX API | 8000 | 8000 | REST API & WebSocket |
| n8n | 5678 | 5678 | Workflow automation |
| Node-RED | 1880 | 1880 | Flow programming |
| Grafana | 3000 | 3001 | Monitoring dashboard |
| PostgreSQL | 5432 | 5432 | Database |
| Redis | 6379 | 6379 | Cache |

---

## 📊 Service Details

### VELOX API

**Purpose:** Real-time technical analysis API

**Features:**
- 70+ technical indicators
- Support/Resistance analysis
- NSE option chain data
- Real-time WebSocket streaming
- Multi-timeframe analysis

**Health Check:** http://localhost:8000/health

**API Docs:** http://localhost:8000/docs

### n8n

**Purpose:** Workflow automation and integration

**Use Cases:**
- Automate trading workflows
- Connect VELOX API with other services
- Schedule indicator calculations
- Send alerts and notifications
- Data processing pipelines

**Login:** http://localhost:5678
- Username: admin (from .env)
- Password: changeme123 (from .env)

**Documentation:** https://docs.n8n.io

### Node-RED

**Purpose:** Visual flow-based programming

**Use Cases:**
- Create custom dashboards
- Build trading bots
- Real-time data visualization
- WebSocket connections
- IoT integrations

**Access:** http://localhost:1880

**Documentation:** https://nodered.org/docs

### Grafana

**Purpose:** Monitoring and visualization

**Use Cases:**
- Real-time market dashboards
- Performance monitoring
- Alert management
- Custom visualizations
- Time-series analysis

**Login:** http://localhost:3001
- Username: admin (from .env)
- Password: changeme123 (from .env)

**Pre-configured:**
- VELOX API datasource
- Dashboard provisioning

**Documentation:** https://grafana.com/docs

---

## 🔌 Integration Examples

### n8n Workflow Example

Connect to VELOX API from n8n:

1. Add HTTP Request node
2. Configure:
   - Method: POST
   - URL: `http://velox-api:8000/api/v1/indicators/calculate`
   - Headers: `Content-Type: application/json`
   - Body:
   ```json
   {
     "symbol": "NIFTY",
     "exchange": "NSE",
     "interval": "5m",
     "indicators": ["RSI", "MACD"]
   }
   ```

### Node-RED Flow Example

WebSocket connection to VELOX:

```javascript
// WebSocket node configuration
ws://velox-api:8000/api/v1/ws/stream

// Subscribe message
{
  "type": "subscription",
  "data": {
    "action": "subscribe",
    "symbols": ["NIFTY"],
    "timeframes": ["1m", "5m"]
  }
}
```

### Grafana Dashboard

Add VELOX API as datasource:

1. Go to Configuration > Data Sources
2. Add "JSON API" datasource
3. URL: `http://velox-api:8000`
4. Create dashboard with API queries

---

## 🛠️ Management Commands

### Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d velox-api

# Start with logs
docker-compose up
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f velox-api
docker-compose logs -f n8n
docker-compose logs -f node-red
docker-compose logs -f grafana

# Last 100 lines
docker-compose logs --tail=100 velox-api
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart velox-api
```

### Check Status

```bash
# Service status
docker-compose ps

# Resource usage
docker stats
```

### Update Services

```bash
# Pull latest images
docker-compose pull

# Rebuild VELOX API
docker-compose build velox-api

# Restart with new images
docker-compose up -d
```

---

## 🗂️ Data Persistence

Data is persisted in Docker volumes:

- `n8n_data` - n8n workflows and settings
- `node_red_data` - Node-RED flows
- `grafana_data` - Grafana dashboards and config
- `postgres_data` - PostgreSQL database
- `redis_data` - Redis cache

### Backup Data

```bash
# Backup n8n data
docker run --rm -v velox-n8n_n8n_data:/data -v $(pwd):/backup alpine tar czf /backup/n8n-backup.tar.gz -C /data .

# Backup Grafana data
docker run --rm -v velox-n8n_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz -C /data .
```

### Restore Data

```bash
# Restore n8n data
docker run --rm -v velox-n8n_n8n_data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/n8n-backup.tar.gz"
```

---

## 🔒 Security

### Production Checklist

- [ ] Change all default passwords in `.env`
- [ ] Use strong passwords (16+ characters)
- [ ] Enable HTTPS (use reverse proxy like Nginx)
- [ ] Configure firewall rules
- [ ] Limit exposed ports
- [ ] Enable authentication on all services
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity
- [ ] Keep Docker images updated

### Recommended: Reverse Proxy

Use Nginx or Traefik for:
- HTTPS/SSL termination
- Domain names
- Load balancing
- Rate limiting

---

## 🐛 Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose logs velox-api

# Check if port is already in use
netstat -tulpn | grep 8000

# Restart service
docker-compose restart velox-api
```

### Cannot connect to VELOX API

```bash
# Check if service is running
docker-compose ps

# Check health
curl http://localhost:8000/health

# Check logs
docker-compose logs velox-api
```

### Out of memory

```bash
# Check resource usage
docker stats

# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory
```

### Database connection issues

```bash
# Check PostgreSQL
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Reset everything

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove all data
rm -rf logs/* n8n-workflows/* node-red-flows/*

# Start fresh
./docker-start.sh
```

---

## 📈 Performance Tuning

### VELOX API

Adjust in `docker-compose.yml`:

```yaml
environment:
  - MAX_WEBSOCKET_CONNECTIONS=200  # Increase for more connections
  - TICK_BUFFER_SIZE=2000          # Increase for more buffering
```

### PostgreSQL

Add to postgres service:

```yaml
command: postgres -c max_connections=200 -c shared_buffers=256MB
```

### Redis

Add to redis service:

```yaml
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

---

## 🔄 Updates

### Update VELOX API

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose build velox-api
docker-compose up -d velox-api
```

### Update Other Services

```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d
```

---

## 📚 Additional Resources

- **VELOX API Docs:** http://localhost:8000/docs
- **n8n Documentation:** https://docs.n8n.io
- **Node-RED Documentation:** https://nodered.org/docs
- **Grafana Documentation:** https://grafana.com/docs
- **Docker Documentation:** https://docs.docker.com

---

## 💡 Tips

1. **Use Docker Desktop** for easy management on Windows/Mac
2. **Monitor logs** regularly for errors
3. **Backup data** before major updates
4. **Use environment variables** for configuration
5. **Test in development** before production deployment
6. **Set up monitoring** with Grafana
7. **Create workflows** in n8n for automation
8. **Use Node-RED** for custom dashboards

---

## 🆘 Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check service documentation
4. Verify `.env` configuration
5. Ensure ports are not in use

---

**Happy Trading! 📈🚀**
