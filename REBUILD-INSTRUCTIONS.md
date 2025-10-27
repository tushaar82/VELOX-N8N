# VELOX API Rebuild Instructions

## Issue
The API documentation at `http://localhost:8000/docs` only shows option chain endpoints because the Docker container is running an old version of the code.

## Solution
You need to rebuild the Docker container to include the updated code with all 77 indicators.

---

## Option 1: Rebuild Everything (Recommended for first time)

This will stop all services, rebuild the VELOX API, and restart everything:

```bash
./docker-rebuild.sh
```

**What it does:**
- Stops all Docker services (n8n, Node-RED, Grafana, Redis, PostgreSQL, VELOX API)
- Removes the old VELOX API image
- Rebuilds the VELOX API with `--no-cache` flag
- Starts all services
- Shows service status

**Downtime:** ~2-3 minutes

---

## Option 2: Rebuild API Only (Faster)

This only rebuilds the VELOX API while keeping other services running:

```bash
./docker-rebuild-api-only.sh
```

**What it does:**
- Stops only the VELOX API container
- Removes the old container
- Rebuilds the VELOX API with `--no-cache` flag
- Starts the VELOX API
- Shows service status

**Downtime:** ~1 minute (only for VELOX API)

---

## After Rebuild

1. **Check the API is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Open the API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Verify all endpoints are visible:**
   You should now see these endpoint groups:
   - **indicators** (4 endpoints) - ✅ NEW!
   - **support-resistance** (3 endpoints) - ✅ NEW!
   - **candles** (4 endpoints) - ✅ NEW!
   - **option-chain** (7 endpoints)
   - **ws** (4 endpoints) - ✅ NEW!

4. **Test the indicators endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/indicators/available
   ```
   
   This should return metadata for all 77 indicators.

---

## What Changed

### Before (Old Container)
- Only option chain endpoints visible
- 8 indicators in metadata

### After (New Container)
- **All 5 endpoint groups visible**
- **77 indicators** organized in 5 categories:
  - Volume: 9 indicators
  - Volatility: 13 indicators
  - Trend: 34 indicators
  - Momentum: 18 indicators
  - Others: 3 indicators

---

## Troubleshooting

### If rebuild fails:

1. **Check Docker is running:**
   ```bash
   docker ps
   ```

2. **Check for port conflicts:**
   ```bash
   lsof -i :8000 -i :5678 -i :1880 -i :3001 -i :6379
   ```

3. **View logs:**
   ```bash
   docker compose logs -f velox-api
   ```

4. **Force clean rebuild:**
   ```bash
   docker compose down -v
   docker system prune -a
   ./docker-start.sh
   ```

### If docs still show old endpoints:

1. **Clear browser cache** (Ctrl+Shift+R or Cmd+Shift+R)
2. **Try incognito/private mode**
3. **Check the OpenAPI spec directly:**
   ```bash
   curl http://localhost:8000/openapi.json | jq '.paths | keys'
   ```

---

## Quick Reference

| Command | Purpose | Downtime |
|---------|---------|----------|
| `./docker-start.sh` | Start all services | N/A |
| `./docker-stop.sh` | Stop all services | All services |
| `./docker-rebuild.sh` | Rebuild everything | ~2-3 min |
| `./docker-rebuild-api-only.sh` | Rebuild API only | ~1 min |
| `docker compose logs -f velox-api` | View API logs | None |
| `docker compose ps` | Check service status | None |

---

## Next Steps

After rebuilding, you can:

1. **Explore the API docs** at http://localhost:8000/docs
2. **Test indicator calculations** using the examples in `docs/INDICATORS-LIST.md`
3. **Set up n8n workflows** to automate indicator calculations
4. **Create Grafana dashboards** to visualize indicators
5. **Use WebSocket streaming** for real-time indicator updates

---

## Documentation

- **Complete Indicator List:** `docs/INDICATORS-LIST.md`
- **API Documentation:** http://localhost:8000/docs
- **Phase 7 Guide:** `docs/PHASE-7-API-INDICATORS.md`
