# Phase 9: Main Application & Router Integration

## Overview
Integrate all components into the main FastAPI application with proper startup/shutdown handling.

## Goals
- Create main FastAPI application
- Integrate all routers
- Configure CORS and middleware
- Implement startup/shutdown lifecycle
- Add health check endpoints

## Dependencies
- Phases 7 and 8 must be completed

## File Changes

### app/api/v1/router.py (NEW)
**References:** app/api/v1/endpoints/indicators.py, app/api/v1/endpoints/option_chain.py, app/api/v1/endpoints/websocket.py, app/api/v1/endpoints/meta.py

Create main v1 router that aggregates all feature routers:
- Import APIRouter
- Import routers from endpoints: indicators, option_chain, websocket, meta
- Create v1_router = APIRouter()
- Include indicators_router from app/api/v1/endpoints/indicators.py with prefix /indicators, tags=["indicators"]
- Include option_chain_router from app/api/v1/endpoints/option_chain.py with prefix /option-chain, tags=["option-chain"]
- Include websocket_router from app/api/v1/endpoints/websocket.py with prefix /ws, tags=["websocket"]
- Include meta_router from app/api/v1/endpoints/meta.py with prefix /meta, tags=["metadata"]

### app/main.py (NEW)
**References:** app/core/config.py, app/api/v1/router.py

Create FastAPI application instance with:
- Import FastAPI, CORSMiddleware
- Initialize FastAPI app with title, description, version
- Configure CORS middleware using settings from app/core/config.py
- Include routers from app/api/v1/router.py with /api/v1 prefix
- Add startup event handler to initialize OpenAlgo client, start background tick aggregation tasks
- Add shutdown event handler to cleanup resources (close WebSocket connections, stop background tasks)
- Add root endpoint (/) returning API info and health status
- Add health check endpoint (/health) returning service status

## Completion Criteria
- [ ] Application starts without errors
- [ ] All routers are accessible
- [ ] CORS is configured correctly
- [ ] Startup tasks initialize properly
- [ ] Shutdown cleanup works correctly
- [ ] Health check endpoint responds
- [ ] API documentation is available at /docs

## Next Phase
Phase 10: Testing Infrastructure
