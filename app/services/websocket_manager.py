"""
WebSocket connection manager for real-time data streaming.
Manages WebSocket connections, subscriptions, and message broadcasting.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import uuid4

try:
    from fastapi import WebSocket, WebSocketDisconnect
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    WebSocket = None
    WebSocketDisconnect = Exception

from app.core.config import get_settings
from app.core.logging import LoggerMixin
from app.schemas.candles import PartialCandle
from app.schemas.indicators import WebSocketMessage, WebSocketSubscription
from app.services.tick_stream import get_tick_stream_service


class WebSocketConnection:
    """Represents a single WebSocket connection."""
    
    def __init__(self, websocket: WebSocket, connection_id: str):
        """
        Initialize WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
            connection_id: Unique connection identifier
        """
        self.websocket = websocket
        self.connection_id = connection_id
        self.subscriptions: Dict[str, Set[str]] = {}  # {symbol: {timeframes}}
        self.connected_at = datetime.now()
        self.messages_sent = 0
        self.messages_received = 0
    
    async def send_json(self, data: dict) -> None:
        """Send JSON message to client."""
        await self.websocket.send_json(data)
        self.messages_sent += 1
    
    async def send_message(self, message: WebSocketMessage) -> None:
        """Send WebSocketMessage to client."""
        await self.send_json(message.model_dump())
    
    def add_subscription(self, symbol: str, timeframes: List[str]) -> None:
        """Add subscription for symbol and timeframes."""
        symbol = symbol.upper()
        if symbol not in self.subscriptions:
            self.subscriptions[symbol] = set()
        self.subscriptions[symbol].update(timeframes)
    
    def remove_subscription(self, symbol: str, timeframes: List[str]) -> None:
        """Remove subscription for symbol and timeframes."""
        symbol = symbol.upper()
        if symbol in self.subscriptions:
            for tf in timeframes:
                self.subscriptions[symbol].discard(tf)
            if not self.subscriptions[symbol]:
                del self.subscriptions[symbol]
    
    def get_stats(self) -> Dict:
        """Get connection statistics."""
        return {
            'connection_id': self.connection_id,
            'connected_at': self.connected_at.isoformat(),
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'subscriptions': {
                symbol: list(timeframes)
                for symbol, timeframes in self.subscriptions.items()
            }
        }


class WebSocketManager(LoggerMixin):
    """
    Manages WebSocket connections and message broadcasting.
    
    Features:
    - Connection management
    - Subscription handling
    - Message broadcasting
    - Connection limits
    - Statistics tracking
    """
    
    def __init__(self):
        """Initialize WebSocket manager."""
        settings = get_settings()
        
        # Active connections: {connection_id: WebSocketConnection}
        self.connections: Dict[str, WebSocketConnection] = {}
        
        # Tick stream service
        self.tick_stream = get_tick_stream_service()
        
        # Configuration
        self.max_connections = settings.max_websocket_connections
        
        # Statistics
        self.total_connections = 0
        self.total_messages_sent = 0
        
        self.logger.info("WebSocketManager initialized")
    
    async def connect(self, websocket: WebSocket) -> str:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
        
        Returns:
            str: Connection ID
        
        Raises:
            Exception: If max connections reached
        """
        if len(self.connections) >= self.max_connections:
            raise Exception(
                f"Maximum connections ({self.max_connections}) reached"
            )
        
        # Accept connection
        await websocket.accept()
        
        # Generate connection ID
        connection_id = str(uuid4())
        
        # Create connection object
        connection = WebSocketConnection(websocket, connection_id)
        self.connections[connection_id] = connection
        
        self.total_connections += 1
        
        self.logger.info(
            f"WebSocket connected: {connection_id} "
            f"(total: {len(self.connections)})"
        )
        
        # Send welcome message
        welcome = WebSocketMessage(
            type="ack",
            data={
                "connection_id": connection_id,
                "message": "Connected successfully"
            },
            timestamp=datetime.now()
        )
        await connection.send_message(welcome)
        
        return connection_id
    
    async def disconnect(self, connection_id: str) -> None:
        """
        Disconnect and cleanup a WebSocket connection.
        
        Args:
            connection_id: Connection identifier
        """
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # Unsubscribe from all tick streams
        self.tick_stream.unsubscribe_all(connection_id)
        
        # Remove connection
        del self.connections[connection_id]
        
        self.logger.info(
            f"WebSocket disconnected: {connection_id} "
            f"(remaining: {len(self.connections)})"
        )
    
    async def handle_subscription(
        self,
        connection_id: str,
        subscription: WebSocketSubscription
    ) -> None:
        """
        Handle subscription request from client.
        
        Args:
            connection_id: Connection identifier
            subscription: Subscription request
        """
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        if subscription.action == "subscribe":
            # Subscribe to tick stream
            self.tick_stream.subscribe(
                symbol=subscription.symbols[0] if subscription.symbols else "",
                timeframes=subscription.timeframes,
                callback_id=connection_id,
                callback=self._create_candle_callback(connection_id)
            )
            
            # Update connection subscriptions
            for symbol in subscription.symbols:
                connection.add_subscription(symbol, subscription.timeframes)
            
            # Send acknowledgment
            ack = WebSocketMessage(
                type="ack",
                data={
                    "action": "subscribe",
                    "symbols": subscription.symbols,
                    "timeframes": subscription.timeframes,
                    "status": "success"
                },
                timestamp=datetime.now()
            )
            await connection.send_message(ack)
            
            self.logger.info(
                f"Subscribed {connection_id} to {subscription.symbols} "
                f"{subscription.timeframes}"
            )
        
        elif subscription.action == "unsubscribe":
            # Unsubscribe from tick stream
            for symbol in subscription.symbols:
                self.tick_stream.unsubscribe(
                    symbol=symbol,
                    timeframes=subscription.timeframes,
                    callback_id=connection_id
                )
                
                # Update connection subscriptions
                connection.remove_subscription(symbol, subscription.timeframes)
            
            # Send acknowledgment
            ack = WebSocketMessage(
                type="ack",
                data={
                    "action": "unsubscribe",
                    "symbols": subscription.symbols,
                    "timeframes": subscription.timeframes,
                    "status": "success"
                },
                timestamp=datetime.now()
            )
            await connection.send_message(ack)
            
            self.logger.info(
                f"Unsubscribed {connection_id} from {subscription.symbols} "
                f"{subscription.timeframes}"
            )
    
    def _create_candle_callback(self, connection_id: str):
        """Create callback function for candle updates."""
        async def callback(symbol: str, timeframe: str, candle: PartialCandle):
            """Send candle update to client."""
            if connection_id not in self.connections:
                return
            
            connection = self.connections[connection_id]
            
            # Create message
            message = WebSocketMessage(
                type="candle",
                data={
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "candle": candle.model_dump()
                },
                timestamp=datetime.now()
            )
            
            try:
                await connection.send_message(message)
                self.total_messages_sent += 1
            except Exception as e:
                self.logger.error(
                    f"Error sending to {connection_id}: {e}"
                )
        
        return callback
    
    async def broadcast(
        self,
        message: WebSocketMessage,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None
    ) -> None:
        """
        Broadcast message to all relevant connections.
        
        Args:
            message: Message to broadcast
            symbol: Optional symbol filter
            timeframe: Optional timeframe filter
        """
        for connection in self.connections.values():
            # Filter by subscription if specified
            if symbol and timeframe:
                if symbol not in connection.subscriptions:
                    continue
                if timeframe not in connection.subscriptions[symbol]:
                    continue
            
            try:
                await connection.send_message(message)
                self.total_messages_sent += 1
            except Exception as e:
                self.logger.error(
                    f"Error broadcasting to {connection.connection_id}: {e}"
                )
    
    async def send_error(
        self,
        connection_id: str,
        error_message: str
    ) -> None:
        """
        Send error message to a specific connection.
        
        Args:
            connection_id: Connection identifier
            error_message: Error message
        """
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        error = WebSocketMessage(
            type="error",
            data={"error": error_message},
            timestamp=datetime.now()
        )
        
        try:
            await connection.send_message(error)
        except Exception as e:
            self.logger.error(
                f"Error sending error to {connection_id}: {e}"
            )
    
    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.connections)
    
    def get_stats(self) -> Dict:
        """Get manager statistics."""
        return {
            'active_connections': len(self.connections),
            'total_connections': self.total_connections,
            'total_messages_sent': self.total_messages_sent,
            'max_connections': self.max_connections,
            'connections': [
                conn.get_stats() for conn in self.connections.values()
            ]
        }
    
    async def handle_message(
        self,
        connection_id: str,
        message: str
    ) -> None:
        """
        Handle incoming message from client.
        
        Args:
            connection_id: Connection identifier
            message: JSON message string
        """
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        connection.messages_received += 1
        
        try:
            # Parse message
            data = json.loads(message)
            
            # Handle subscription messages
            if data.get("type") == "subscription":
                subscription = WebSocketSubscription(**data.get("data", {}))
                await self.handle_subscription(connection_id, subscription)
            
            # Handle other message types
            elif data.get("type") == "ping":
                # Respond with pong
                pong = WebSocketMessage(
                    type="pong",
                    data={},
                    timestamp=datetime.now()
                )
                await connection.send_message(pong)
            
            else:
                await self.send_error(
                    connection_id,
                    f"Unknown message type: {data.get('type')}"
                )
        
        except json.JSONDecodeError as e:
            await self.send_error(connection_id, f"Invalid JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error handling message: {e}", exc_info=True)
            await self.send_error(connection_id, f"Error: {str(e)}")


# Singleton instance
_websocket_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """
    Get WebSocketManager singleton instance.
    
    Returns:
        WebSocketManager: Manager instance
    """
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager
