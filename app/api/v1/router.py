"""
API v1 router that combines all endpoint routers.
"""

try:
    from fastapi import APIRouter
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None

from app.core.logging import get_logger

logger = get_logger(__name__)

# Create main API router
if FASTAPI_AVAILABLE:
    api_router = APIRouter()
    
    # Import endpoint routers
    try:
        from app.api.v1.endpoints.indicators import router as indicators_router
        api_router.include_router(indicators_router)
        logger.info("Included indicators router")
    except Exception as e:
        logger.warning(f"Could not include indicators router: {e}")
    
    try:
        from app.api.v1.endpoints.support_resistance import router as sr_router
        api_router.include_router(sr_router)
        logger.info("Included support_resistance router")
    except Exception as e:
        logger.warning(f"Could not include support_resistance router: {e}")
    
    try:
        from app.api.v1.endpoints.candles import router as candles_router
        api_router.include_router(candles_router)
        logger.info("Included candles router")
    except Exception as e:
        logger.warning(f"Could not include candles router: {e}")
    
    try:
        from app.api.v1.endpoints.option_chain import router as option_chain_router
        api_router.include_router(option_chain_router)
        logger.info("Included option_chain router")
    except Exception as e:
        logger.warning(f"Could not include option_chain router: {e}")
    
    try:
        from app.api.v1.endpoints.websocket import router as websocket_router
        api_router.include_router(websocket_router)
        logger.info("Included websocket router")
    except Exception as e:
        logger.warning(f"Could not include websocket router: {e}")
else:
    api_router = None
