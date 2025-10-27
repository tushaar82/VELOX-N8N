"""
Main FastAPI application for VELOX Real-Time Technical Analysis System.

This is the entry point for the application. It integrates all services,
endpoints, and middleware.

To run:
    Development: uvicorn main:app --reload
    Production:  uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
"""

from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    CORSMiddleware = None
    JSONResponse = None

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("="*60)
    logger.info("VELOX Real-Time Technical Analysis System")
    logger.info("="*60)
    logger.info("Starting application...")
    logger.info(f"Environment: {settings.log_level}")
    logger.info(f"OpenAlgo Host: {settings.openalgo_host}")
    logger.info(f"Max WebSocket Connections: {settings.max_websocket_connections}")
    
    # Initialize services
    try:
        from app.services.tick_stream import get_tick_stream_service
        from app.services.websocket_manager import get_websocket_manager
        
        tick_service = get_tick_stream_service()
        ws_manager = get_websocket_manager()
        
        logger.info("✓ Services initialized")
    except Exception as e:
        logger.warning(f"Could not initialize all services: {e}")
    
    logger.info("Application started successfully!")
    logger.info("="*60)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    logger.info("Application stopped")


# Create FastAPI app
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="VELOX Real-Time Technical Analysis API",
        description="""
        Real-time technical analysis system for Indian stock market.
        
        Features:
        - 70+ technical indicators
        - Support/Resistance analysis
        - NSE option chain data
        - Real-time WebSocket streaming
        - Multi-timeframe analysis
        
        Powered by OpenAlgo, FastAPI, and ta library.
        """,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    try:
        from app.api.v1.router import api_router
        app.include_router(api_router, prefix="/api/v1")
        logger.info("✓ API v1 router included")
    except Exception as e:
        logger.error(f"Could not include API router: {e}")
    
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """
        Root endpoint with API information.
        """
        return {
            "name": "VELOX Real-Time Technical Analysis API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "redoc": "/redoc",
            "endpoints": {
                "indicators": "/api/v1/indicators",
                "support_resistance": "/api/v1/support-resistance",
                "candles": "/api/v1/candles",
                "option_chain": "/api/v1/option-chain",
                "websocket": "/api/v1/ws"
            }
        }
    
    
    @app.get("/health", tags=["health"])
    async def health_check():
        """
        Health check endpoint.
        """
        try:
            from app.services.websocket_manager import get_websocket_manager
            ws_manager = get_websocket_manager()
            connection_count = ws_manager.get_connection_count()
            
            return {
                "status": "healthy",
                "websocket_connections": connection_count,
                "max_connections": settings.max_websocket_connections
            }
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e)
            }
    
    
    @app.get("/info", tags=["info"])
    async def app_info():
        """
        Application information and statistics.
        """
        try:
            from app.services.tick_stream import get_tick_stream_service
            from app.services.websocket_manager import get_websocket_manager
            
            tick_service = get_tick_stream_service()
            ws_manager = get_websocket_manager()
            
            tick_stats = tick_service.get_stats()
            ws_stats = ws_manager.get_stats()
            
            return {
                "application": {
                    "name": "VELOX Real-Time Technical Analysis API",
                    "version": "1.0.0",
                    "environment": settings.log_level
                },
                "configuration": {
                    "openalgo_host": settings.openalgo_host,
                    "max_websocket_connections": settings.max_websocket_connections,
                    "tick_buffer_size": settings.tick_buffer_size,
                    "default_timeframes": settings.get_default_timeframes()
                },
                "statistics": {
                    "tick_stream": tick_stats,
                    "websocket": ws_stats
                }
            }
        except Exception as e:
            logger.error(f"Error getting app info: {e}")
            return {
                "application": {
                    "name": "VELOX Real-Time Technical Analysis API",
                    "version": "1.0.0"
                },
                "error": str(e)
            }
    
    
    # Exception handlers
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        """Handle 404 errors."""
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": "The requested resource was not found",
                "path": str(request.url)
            }
        )
    
    
    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )
    
    
    logger.info("FastAPI application created")

else:
    # Fallback if FastAPI not available
    app = None
    logger.warning("FastAPI not available - application not created")


# For running with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server with uvicorn...")
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
