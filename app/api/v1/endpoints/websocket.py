"""
WebSocket endpoints for real-time data streaming.
"""

try:
    from fastapi import APIRouter, WebSocket, WebSocketDisconnect
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None
    WebSocket = None
    WebSocketDisconnect = Exception

from app.core.logging import get_logger
from app.services.websocket_manager import get_websocket_manager
from app.services.tick_stream import get_tick_stream_service

logger = get_logger(__name__)

# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/ws", tags=["websocket"])
else:
    router = None


if FASTAPI_AVAILABLE:
    @router.websocket("/stream")
    async def websocket_stream(websocket: WebSocket):
        """
        WebSocket endpoint for real-time data streaming.
        
        Supports:
        - Real-time candle updates
        - Multi-symbol subscriptions
        - Multi-timeframe subscriptions
        - Indicator updates (optional)
        
        Message Format (Client -> Server):
        {
            "type": "subscription",
            "data": {
                "action": "subscribe" | "unsubscribe",
                "symbols": ["NIFTY", "BANKNIFTY"],
                "timeframes": ["1m", "5m"],
                "indicators": ["RSI", "MACD"]  // optional
            }
        }
        
        Message Format (Server -> Client):
        {
            "type": "candle" | "indicator" | "error" | "ack",
            "data": {...},
            "timestamp": "2024-01-15T15:25:00"
        }
        
        Example Usage (JavaScript):
            const ws = new WebSocket('ws://localhost:8000/api/v1/ws/stream');
            
            ws.onopen = () => {
                ws.send(JSON.stringify({
                    type: 'subscription',
                    data: {
                        action: 'subscribe',
                        symbols: ['NIFTY'],
                        timeframes: ['1m', '5m']
                    }
                }));
            };
            
            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                console.log('Received:', message);
            };
        """
        manager = get_websocket_manager()
        connection_id = None
        
        try:
            # Accept connection
            connection_id = await manager.connect(websocket)
            logger.info(f"WebSocket connected: {connection_id}")
            
            # Handle messages
            while True:
                # Receive message from client
                message = await websocket.receive_text()
                
                # Handle message
                await manager.handle_message(connection_id, message)
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket error for {connection_id}: {e}", exc_info=True)
        finally:
            # Cleanup
            if connection_id:
                await manager.disconnect(connection_id)


    @router.websocket("/ticks")
    async def websocket_ticks(websocket: WebSocket):
        """
        WebSocket endpoint for tick-by-tick data streaming.
        
        This endpoint provides raw tick data without aggregation.
        Useful for custom candle building or high-frequency analysis.
        
        Message Format (Client -> Server):
        {
            "type": "subscription",
            "data": {
                "action": "subscribe" | "unsubscribe",
                "symbols": ["NIFTY", "BANKNIFTY"]
            }
        }
        
        Message Format (Server -> Client):
        {
            "type": "tick",
            "data": {
                "symbol": "NIFTY",
                "price": 21530.50,
                "volume": 100.0,
                "timestamp": "2024-01-15T15:25:30.123"
            }
        }
        
        Example Usage (JavaScript):
            const ws = new WebSocket('ws://localhost:8000/api/v1/ws/ticks');
            
            ws.onopen = () => {
                ws.send(JSON.stringify({
                    type: 'subscription',
                    data: {
                        action: 'subscribe',
                        symbols: ['NIFTY']
                    }
                }));
            };
            
            ws.onmessage = (event) => {
                const tick = JSON.parse(event.data);
                console.log('Tick:', tick);
            };
        """
        manager = get_websocket_manager()
        connection_id = None
        
        try:
            # Accept connection
            connection_id = await manager.connect(websocket)
            logger.info(f"Tick WebSocket connected: {connection_id}")
            
            # Handle messages
            while True:
                # Receive message from client
                message = await websocket.receive_text()
                
                # Handle message (simplified for tick streaming)
                await manager.handle_message(connection_id, message)
        
        except WebSocketDisconnect:
            logger.info(f"Tick WebSocket disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"Tick WebSocket error for {connection_id}: {e}", exc_info=True)
        finally:
            # Cleanup
            if connection_id:
                await manager.disconnect(connection_id)


    @router.get("/stats")
    async def get_websocket_stats():
        """
        Get WebSocket connection statistics.
        
        Returns:
            Dict: Connection statistics including active connections,
                  total connections, messages sent, etc.
        
        Example:
            GET /api/v1/ws/stats
        """
        try:
            manager = get_websocket_manager()
            tick_service = get_tick_stream_service()
            
            ws_stats = manager.get_stats()
            tick_stats = tick_service.get_stats()
            
            return {
                "websocket": ws_stats,
                "tick_stream": tick_stats
            }
        
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {
                "error": str(e)
            }


    @router.get("/health")
    async def websocket_health():
        """
        Health check endpoint for WebSocket service.
        
        Returns:
            Dict: Health status
        
        Example:
            GET /api/v1/ws/health
        """
        try:
            manager = get_websocket_manager()
            connection_count = manager.get_connection_count()
            
            return {
                "status": "healthy",
                "active_connections": connection_count,
                "max_connections": manager.max_connections,
                "capacity_used_pct": (connection_count / manager.max_connections) * 100
            }
        
        except Exception as e:
            logger.error(f"Health check error: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e)
            }
