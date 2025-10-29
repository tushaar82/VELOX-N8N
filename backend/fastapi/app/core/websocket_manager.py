"""
VELOX-N8N WebSocket Manager
Real-time data streaming for indicators and market data
"""

from typing import Dict, List, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging
from datetime import datetime
import weakref

from app.core.config import ws_settings
from app.core.logging import log_api_request, log_error

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager for real-time data streaming
    """
    
    def __init__(self):
        # Active connections by symbol
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        
        # Subscription management
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
        
        # Message queues
        self.message_queues: Dict[str, asyncio.Queue] = {}
        
        # Heartbeat management
        self.last_heartbeat: Dict[WebSocket, datetime] = {}
        
        # Connection limits
        self.max_connections = ws_settings.MAX_CONNECTIONS
        self.heartbeat_interval = ws_settings.HEARTBEAT_INTERVAL
        
        # Performance tracking
        self.connection_count = 0
        self.message_count = 0
        self.error_count = 0
    
    async def connect(self, websocket: WebSocket, symbol: str):
        """
        Accept and register a new WebSocket connection
        """
        try:
            # Check connection limits
            if self.connection_count >= self.max_connections:
                logger.warning(f"Connection limit reached for {symbol}")
                await websocket.close(code=1008, reason="Connection limit reached")
                return False
            
            # Add connection to active connections
            if symbol not in self.active_connections:
                self.active_connections[symbol] = set()
            
            self.active_connections[symbol].add(websocket)
            
            # Initialize connection metadata
            self.connection_metadata[websocket] = {
                "symbol": symbol,
                "connected_at": datetime.utcnow(),
                "ip_address": websocket.client.host if websocket.client else None,
                "user_agent": websocket.headers.get("user-agent"),
                "subscriptions": set()
            }
            
            # Initialize subscriptions
            self.subscriptions[websocket] = set()
            
            # Update connection count
            self.connection_count += 1
            
            # Initialize message queue for this symbol
            if symbol not in self.message_queues:
                self.message_queues[symbol] = asyncio.Queue(maxsize=ws_settings.MESSAGE_QUEUE_SIZE)
            
            # Set last heartbeat
            self.last_heartbeat[websocket] = datetime.utcnow()
            
            logger.info(f"WebSocket connected for {symbol}: {websocket.client.host if websocket.client else 'unknown'}")
            
            # Send welcome message
            await self.send_personal_message(websocket, {
                "type": "connection",
                "status": "connected",
                "symbol": symbol,
                "timestamp": datetime.utcnow().isoformat(),
                "connection_id": id(websocket)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket for {symbol}: {e}")
            await websocket.close(code=1011, reason="Internal server error")
            return False
    
    async def disconnect(self, websocket: WebSocket, symbol: str):
        """
        Disconnect and unregister a WebSocket connection
        """
        try:
            # Remove from active connections
            if symbol in self.active_connections:
                self.active_connections[symbol].discard(websocket)
                
                # Clean up empty symbol sets
                if not self.active_connections[symbol]:
                    del self.active_connections[symbol]
            
            # Clean up metadata
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
            
            # Clean up subscriptions
            if websocket in self.subscriptions:
                del self.subscriptions[websocket]
            
            # Update connection count
            self.connection_count = max(0, self.connection_count - 1)
            
            logger.info(f"WebSocket disconnected for {symbol}: {websocket.client.host if websocket.client else 'unknown'}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket for {symbol}: {e}")
            return False
    
    async def subscribe(self, websocket: WebSocket, symbol: str, subscription_type: str):
        """
        Subscribe a connection to a specific data type
        """
        try:
            if websocket not in self.subscriptions:
                self.subscriptions[websocket] = set()
            
            subscription_key = f"{symbol}:{subscription_type}"
            self.subscriptions[websocket].add(subscription_key)
            
            # Update connection metadata
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["subscriptions"].add(subscription_key)
            
            logger.info(f"WebSocket subscribed to {subscription_type} for {symbol}")
            
            # Send confirmation
            await self.send_personal_message(websocket, {
                "type": "subscription",
                "status": "subscribed",
                "symbol": symbol,
                "subscription_type": subscription_type,
                "timestamp": datetime.utcnow().isoformat()
                "connection_id": id(websocket)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing WebSocket to {subscription_type} for {symbol}: {e}")
            return False
    
    async def unsubscribe(self, websocket: WebSocket, symbol: str, subscription_type: str):
        """
        Unsubscribe a connection from a specific data type
        """
        try:
            if websocket not in self.subscriptions:
                return False
            
            subscription_key = f"{symbol}:{subscription_type}"
            self.subscriptions[websocket].discard(subscription_key)
            
            # Update connection metadata
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["subscriptions"].discard(subscription_key)
            
            logger.info(f"WebSocket unsubscribed from {subscription_type} for {symbol}")
            
            # Send confirmation
            await self.send_personal_message(websocket, {
                "type": "subscription",
                "status": "unsubscribed",
                "symbol": symbol,
                "subscription_type": subscription_type,
                "timestamp": datetime.utcnow().isoformat(),
                "connection_id": id(websocket)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing WebSocket from {subscription_type} for {symbol}: {e}")
            return False
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """
        Send a message to a specific WebSocket connection
        """
        try:
            await websocket.send_text(json.dumps(message))
            self.message_count += 1
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.error_count += 1
    
    async def broadcast_to_symbol(self, symbol: str, message: dict):
        """
        Broadcast a message to all connections for a specific symbol
        """
        try:
            if symbol not in self.active_connections:
                return
            
            disconnected = set()
            for connection in self.active_connections[symbol].copy():
                try:
                    await connection.send_text(json.dumps(message))
                    self.message_count += 1
                except Exception as e:
                    logger.error(f"Error broadcasting to {symbol}: {e}")
                    disconnected.add(connection)
                    self.error_count += 1
            
            # Remove disconnected connections
            self.active_connections[symbol] -= disconnected
            
        except Exception as e:
            logger.error(f"Error broadcasting to {symbol}: {e}")
            self.error_count += 1
    
    async def broadcast_to_all(self, message: dict):
        """
        Broadcast a message to all active connections
        """
        try:
            for symbol, connections in self.active_connections.items():
                for connection in connections.copy():
                    try:
                        await connection.send_text(json.dumps({
                            **message,
                            "symbol": symbol
                        }))
                        self.message_count += 1
                    except Exception as e:
                        logger.error(f"Error broadcasting to {symbol}: {e}")
                        self.error_count += 1
        except Exception as e:
            logger.error(f"Error broadcasting to all: {e}")
            self.error_count += 1
    
    async def send_market_data(self, symbol: str, data: dict):
        """
        Send market data to subscribed connections
        """
        message = {
            "type": "market_data",
            "symbol": symbol,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_symbol(symbol, message)
    
    async def send_indicator_data(self, symbol: str, indicators: dict):
        """
        Send indicator data to subscribed connections
        """
        message = {
            "type": "indicator_data",
            "symbol": symbol,
            "indicators": indicators,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_symbol(symbol, message)
    
    async def send_trade_update(self, symbol: str, trade_data: dict):
        """
        Send trade update to subscribed connections
        """
        message = {
            "type": "trade_update",
            "symbol": symbol,
            "trade": trade_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_symbol(symbol, message)
    
    async def send_strategy_signal(self, symbol: str, signal_data: dict):
        """
        Send strategy signal to subscribed connections
        """
        message = {
            "type": "strategy_signal",
            "symbol": symbol,
            "signal": signal_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_symbol(symbol, message)
    
    async def send_alert(self, symbol: str, alert_data: dict):
        """
        Send alert to subscribed connections
        """
        message = {
            "type": "alert",
            "symbol": symbol,
            "alert": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_symbol(symbol, message)
    
    async def send_heartbeat(self, websocket: WebSocket):
        """
        Send heartbeat to a specific connection
        """
        try:
            message = {
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_text(json.dumps(message))
            self.last_heartbeat[websocket] = datetime.utcnow()
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            self.error_count += 1
    
    async def check_heartbeats(self):
        """
        Check all connections for heartbeat timeouts
        """
        try:
            current_time = datetime.utcnow()
            timeout_threshold = datetime.utcnow() - timedelta(seconds=self.heartbeat_interval * 2)
            
            disconnected = set()
            for websocket, last_heartbeat in self.last_heartbeat.items():
                if last_heartbeat < timeout_threshold:
                    logger.warning(f"Heartbeat timeout for connection: {websocket.client.host if websocket.client else 'unknown'}")
                    disconnected.add(websocket)
            
            # Remove timed out connections
            for websocket in disconnected:
                await self.disconnect(websocket, self.connection_metadata.get(websocket, {}).get("symbol", "unknown"))
            
        except Exception as e:
            logger.error(f"Error checking heartbeats: {e}")
            self.error_count += 1
    
    async def get_connection_stats(self) -> dict:
        """
        Get connection statistics
        """
        try:
            stats = {
                "total_connections": self.connection_count,
                "connections_by_symbol": {
                    symbol: len(connections) for symbol, connections in self.active_connections.items()
                },
                "total_messages_sent": self.message_count,
                "total_errors": self.error_count,
                "message_queues": {
                    symbol: queue.qsize() for symbol, queue in self.message_queues.items()
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting connection stats: {e}")
            return {
                "total_connections": self.connection_count,
                "connections_by_symbol": {},
                "total_messages_sent": self.message_count,
                "total_errors": self.error_count,
                "message_queues": {},
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def get_symbol_connections(self, symbol: str) -> List[Dict]:
        """
        Get all connections for a specific symbol
        """
        try:
            connections = []
            if symbol in self.active_connections:
                for websocket in self.active_connections[symbol]:
                    metadata = self.connection_metadata.get(websocket, {})
                    connections.append({
                        "connection_id": id(websocket),
                        "ip_address": metadata.get("ip_address"),
                        "user_agent": metadata.get("user_agent"),
                        "connected_at": metadata.get("connected_at"),
                        "subscriptions": list(metadata.get("subscriptions", set()))
                    })
            
            return connections
            
        except Exception as e:
            logger.error(f"Error getting connections for {symbol}: {e}")
            return []
    
    def is_healthy(self) -> bool:
        """
        Check if the WebSocket manager is healthy
        """
        # Basic health check - can be enhanced
        return self.error_count < self.connection_count * 0.1  # Less than 10% error rate
    
    async def startup(self):
        """
        Initialize WebSocket manager on startup
        """
        try:
            # Start heartbeat task
            asyncio.create_task(self._heartbeat_loop())
            
            logger.info("WebSocket manager started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting WebSocket manager: {e}")
            return False
    
    async def shutdown(self):
        """
        Shutdown WebSocket manager
        """
        try:
            # Close all active connections
            for symbol, connections in self.active_connections.items():
                for websocket in connections.copy():
                    try:
                        await websocket.close(code=1001, reason="Server shutdown")
                    except Exception as e:
                        logger.error(f"Error closing connection: {e}")
            
            # Clear all data structures
            self.active_connections.clear()
            self.connection_metadata.clear()
            self.subscriptions.clear()
            self.message_queues.clear()
            self.last_heartbeat.clear()
            
            logger.info("WebSocket manager shutdown successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down WebSocket manager: {e}")
            return False
    
    async def _heartbeat_loop(self):
        """
        Background task to check heartbeats
        """
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            await self.check_heartbeats()


# Global WebSocket manager instance
manager = ConnectionManager()