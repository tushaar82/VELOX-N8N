"""
VELOX-N8N FastAPI Main Application
Algorithmic Trading System with Real-time Indicators and N8N Integration
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import time
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import setup_logging
from app.api import auth, trading, strategies, indicators, market_data, risk, webhooks
from app.core.websocket_manager import manager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting VELOX-N8N FastAPI application...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize WebSocket manager
    await manager.startup()
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down VELOX-N8N FastAPI application...")
    await manager.shutdown()
    logger.info("Application shutdown completed")

# Create FastAPI application
app = FastAPI(
    title="VELOX-N8N Trading API",
    description="Algorithmic Trading System with Real-time Indicators and N8N Integration",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to responses"""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# Rate limiting middleware (basic implementation)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Basic rate limiting implementation"""
    # This is a simplified version - in production, use Redis-based rate limiting
    client_ip = request.client.host
    logger.debug(f"Request from {client_ip} to {request.url.path}")
    
    response = await call_next(request)
    return response

# Include API routers
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["authentication"]
)

app.include_router(
    trading.router,
    prefix="/api/v1/trading",
    tags=["trading"]
)

app.include_router(
    strategies.router,
    prefix="/api/v1/strategies",
    tags=["strategies"]
)

app.include_router(
    indicators.router,
    prefix="/api/v1/indicators",
    tags=["indicators"]
)

app.include_router(
    market_data.router,
    prefix="/api/v1/market-data",
    tags=["market-data"]
)

app.include_router(
    risk.router,
    prefix="/api/v1/risk",
    tags=["risk"]
)

app.include_router(
    webhooks.router,
    prefix="/api/v1/webhooks",
    tags=["webhooks"]
)

# WebSocket endpoint
@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket, symbol: str):
    """WebSocket endpoint for real-time data streaming"""
    await manager.connect(websocket, symbol)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
    finally:
        await manager.disconnect(websocket, symbol)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/api/health")
async def detailed_health_check():
    """Detailed health check with system status"""
    try:
        # Check database connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check Redis connection (if configured)
    redis_status = "healthy"  # TODO: Implement Redis health check
    
    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "services": {
            "database": db_status,
            "redis": redis_status,
            "websocket_manager": "healthy" if manager.is_healthy() else "unhealthy"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "VELOX-N8N Trading API",
        "version": "1.0.0",
        "description": "Algorithmic Trading System with Real-time Indicators and N8N Integration",
        "docs_url": "/docs" if settings.ENVIRONMENT == "development" else None,
        "health_url": "/health",
        "environment": settings.ENVIRONMENT
    }

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global HTTP exception handler"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )

# Static files (for development)
if settings.ENVIRONMENT == "development":
    app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.HOT_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        use_colors=True
    )