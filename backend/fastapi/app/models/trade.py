"""
VELOX-N8N Trade Model
Database model for trade execution and tracking
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey, Enum
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class OrderType(str, enum.Enum):
    """Order type enumeration"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_MARKET = "STOP_MARKET"
    TAKE_PROFIT = "TAKE_PROFIT"


class OrderSide(str, enum.Enum):
    """Order side enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    PENDING = "PENDING"
    PLACED = "PLACED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TradeStatus(str, enum.Enum):
    """Trade status enumeration"""
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    PARTIALLY_EXECUTED = "PARTIALLY_EXECUTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class PositionType(str, enum.Enum):
    """Position type enumeration"""
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


class Trade(Base):
    """
    Trade model for order execution tracking
    """
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    
    # Order information
    order_id = Column(String(100), unique=True, nullable=False, index=True)
    broker_order_id = Column(String(100), nullable=True, index=True)
    parent_order_id = Column(String(100), nullable=True)  # For bracket orders
    
    # Trade details
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), nullable=False)
    instrument_type = Column(String(20), nullable=False)  # EQUITY, FUTURES, OPTIONS, etc.
    
    # Order parameters
    order_type = Column(Enum(OrderType), nullable=False)
    order_side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=True)  # None for market orders
    trigger_price = Column(Float, nullable=True)  # For stop orders
    
    # Execution details
    status = Column(Enum(TradeStatus), nullable=False, index=True)
    filled_quantity = Column(Float, default=0.0, nullable=False)
    average_price = Column(Float, nullable=True)
    execution_price = Column(Float, nullable=True)  # Last execution price
    
    # Financial details
    order_value = Column(Float, nullable=True)  # quantity * price
    executed_value = Column(Float, nullable=True)  # filled_quantity * average_price
    brokerage = Column(Float, default=0.0, nullable=False)
    taxes = Column(Float, default=0.0, nullable=False)
    charges = Column(Float, default=0.0, nullable=False)
    total_charges = Column(Float, default=0.0, nullable=False)
    
    # P&L tracking
    realized_pnl = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, nullable=True)
    total_pnl = Column(Float, nullable=True)
    
    # Risk management
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    trailing_stop = Column(Float, nullable=True)
    
    # Strategy and user context
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # Trade tags and labels
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional trade metadata
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    placed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    executed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    cancelled_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")
    position = relationship("Position", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade(id={self.id}, order_id='{self.order_id}', symbol='{self.symbol}', side='{self.order_side}', status='{self.status}')>"
    
    @property
    def is_buy(self) -> bool:
        """Check if trade is a buy order"""
        return self.order_side == OrderSide.BUY
    
    @property
    def is_sell(self) -> bool:
        """Check if trade is a sell order"""
        return self.order_side == OrderSide.SELL
    
    @property
    def is_market_order(self) -> bool:
        """Check if trade is a market order"""
        return self.order_type == OrderType.MARKET
    
    @property
    def is_limit_order(self) -> bool:
        """Check if trade is a limit order"""
        return self.order_type == OrderType.LIMIT
    
    @property
    def is_stop_order(self) -> bool:
        """Check if trade is a stop order"""
        return self.order_type in [OrderType.STOP_LOSS, OrderType.STOP_MARKET]
    
    @property
    def is_executed(self) -> bool:
        """Check if trade is executed"""
        return self.status == TradeStatus.EXECUTED
    
    @property
    def is_pending(self) -> bool:
        """Check if trade is pending"""
        return self.status in [TradeStatus.PENDING, TradeStatus.PLACED, TradeStatus.PARTIALLY_EXECUTED]
    
    @property
    def is_cancelled(self) -> bool:
        """Check if trade is cancelled"""
        return self.status == TradeStatus.CANCELLED
    
    @property
    def fill_percentage(self) -> float:
        """Calculate fill percentage"""
        if self.quantity == 0:
            return 0.0
        return (self.filled_quantity / self.quantity) * 100
    
    @property
    def remaining_quantity(self) -> float:
        """Calculate remaining quantity to be filled"""
        return max(0, self.quantity - self.filled_quantity)
    
    @property
    def display_status(self) -> str:
        """Get display status name"""
        status_map = {
            'PENDING': 'Pending',
            'PLACED': 'Placed',
            'PARTIALLY_FILLED': 'Partially Filled',
            'FILLED': 'Filled',
            'CANCELLED': 'Cancelled',
            'REJECTED': 'Rejected',
            'EXPIRED': 'Expired'
        }
        return status_map.get(self.status.value, self.status.value)
    
    @property
    def display_side(self) -> str:
        """Get display side name"""
        return self.order_side.value
    
    @property
    def display_type(self) -> str:
        """Get display order type name"""
        type_map = {
            'MARKET': 'Market',
            'LIMIT': 'Limit',
            'STOP_LOSS': 'Stop Loss',
            'STOP_MARKET': 'Stop Market',
            'TAKE_PROFIT': 'Take Profit'
        }
        return type_map.get(self.order_type.value, self.order_type.value)
    
    def calculate_charges(self) -> float:
        """Calculate total charges"""
        return self.brokerage + self.taxes + self.charges
    
    def calculate_net_value(self) -> float:
        """Calculate net trade value after charges"""
        if not self.executed_value:
            return 0.0
        return self.executed_value - self.calculate_charges()
    
    def update_execution(self, filled_qty: float, avg_price: float, execution_price: float = None):
        """Update trade execution details"""
        self.filled_quantity = filled_qty
        self.average_price = avg_price
        self.execution_price = execution_price or avg_price
        self.executed_value = filled_qty * avg_price
        self.executed_at = datetime.utcnow()
        
        # Update status based on fill
        if filled_qty >= self.quantity:
            self.status = TradeStatus.EXECUTED
        elif filled_qty > 0:
            self.status = TradeStatus.PARTIALLY_EXECUTED
        
        self.updated_at = datetime.utcnow()
    
    def cancel(self, reason: str = None):
        """Cancel the trade"""
        self.status = TradeStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
        if reason:
            if not self.notes:
                self.notes = ""
            self.notes += f"\nCancelled: {reason}"
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_details: bool = True) -> dict:
        """Convert trade to dictionary"""
        data = {
            'id': self.id,
            'uuid': str(self.uuid),
            'order_id': self.order_id,
            'broker_order_id': self.broker_order_id,
            'parent_order_id': self.parent_order_id,
            'symbol': self.symbol,
            'exchange': self.exchange,
            'instrument_type': self.instrument_type,
            'order_type': self.order_type.value,
            'display_type': self.display_type,
            'order_side': self.order_side.value,
            'display_side': self.display_side,
            'quantity': self.quantity,
            'price': self.price,
            'trigger_price': self.trigger_price,
            'status': self.status.value,
            'display_status': self.display_status,
            'filled_quantity': self.filled_quantity,
            'average_price': self.average_price,
            'execution_price': self.execution_price,
            'order_value': self.order_value,
            'executed_value': self.executed_value,
            'brokerage': self.brokerage,
            'taxes': self.taxes,
            'charges': self.charges,
            'total_charges': self.calculate_charges(),
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'total_pnl': self.total_pnl,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'trailing_stop': self.trailing_stop,
            'strategy_id': self.strategy_id,
            'user_id': self.user_id,
            'tags': self.tags,
            'notes': self.notes,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'placed_at': self.placed_at.isoformat() if self.placed_at else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'is_buy': self.is_buy,
            'is_sell': self.is_sell,
            'is_market_order': self.is_market_order,
            'is_limit_order': self.is_limit_order,
            'is_stop_order': self.is_stop_order,
            'is_executed': self.is_executed,
            'is_pending': self.is_pending,
            'is_cancelled': self.is_cancelled,
            'fill_percentage': self.fill_percentage,
            'remaining_quantity': self.remaining_quantity
        }
        
        if include_details:
            data.update({
                'net_value': self.calculate_net_value()
            })
        
        return data


class Position(Base):
    """
    Position model for tracking open positions
    """
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    
    # Position details
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), nullable=False)
    instrument_type = Column(String(20), nullable=False)
    
    # Position quantities
    quantity = Column(Float, default=0.0, nullable=False)
    available_quantity = Column(Float, default=0.0, nullable=False)
    blocked_quantity = Column(Float, default=0.0, nullable=False)
    
    # Position type and status
    position_type = Column(Enum(PositionType), nullable=False, index=True)
    status = Column(String(20), default='OPEN', nullable=False, index=True)
    
    # Price information
    average_buy_price = Column(Float, nullable=True)
    average_sell_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    last_price = Column(Float, nullable=True)
    
    # P&L information
    unrealized_pnl = Column(Float, default=0.0, nullable=False)
    realized_pnl = Column(Float, default=0.0, nullable=False)
    total_pnl = Column(Float, default=0.0, nullable=False)
    pnl_percentage = Column(Float, default=0.0, nullable=False)
    
    # Position value
    investment_value = Column(Float, default=0.0, nullable=False)
    current_value = Column(Float, default=0.0, nullable=False)
    
    # Risk metrics
    max_profit = Column(Float, nullable=True)
    max_loss = Column(Float, nullable=True)
    max_drawdown = Column(Float, default=0.0, nullable=False)
    risk_reward_ratio = Column(Float, nullable=True)
    
    # Strategy and user context
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    tags = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    opened_at = Column(TIMESTAMP(timezone=True), nullable=False)
    closed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    last_updated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="positions")
    strategy = relationship("Strategy", back_populates="positions")
    trades = relationship("Trade", back_populates="position")
    
    def __repr__(self):
        return f"<Position(id={self.id}, symbol='{self.symbol}', type='{self.position_type}', quantity={self.quantity})>"
    
    @property
    def is_long(self) -> bool:
        """Check if position is long"""
        return self.position_type == PositionType.LONG
    
    @property
    def is_short(self) -> bool:
        """Check if position is short"""
        return self.position_type == PositionType.SHORT
    
    @property
    def is_flat(self) -> bool:
        """Check if position is flat"""
        return self.position_type == PositionType.FLAT or self.quantity == 0
    
    @property
    def is_open(self) -> bool:
        """Check if position is open"""
        return self.status == 'OPEN' and self.quantity != 0
    
    @property
    def is_closed(self) -> bool:
        """Check if position is closed"""
        return self.status == 'CLOSED' or self.quantity == 0
    
    @property
    def display_type(self) -> str:
        """Get display position type name"""
        type_map = {
            'LONG': 'Long',
            'SHORT': 'Short',
            'FLAT': 'Flat'
        }
        return type_map.get(self.position_type.value, self.position_type.value)
    
    @property
    def days_open(self) -> int:
        """Calculate days position has been open"""
        if not self.opened_at:
            return 0
        
        end_date = self.closed_at or datetime.utcnow()
        return (end_date - self.opened_at).days
    
    def calculate_pnl_percentage(self) -> float:
        """Calculate P&L percentage"""
        if self.investment_value == 0:
            return 0.0
        return (self.total_pnl / self.investment_value) * 100
    
    def update_current_price(self, price: float):
        """Update current price and recalculate P&L"""
        self.last_price = self.current_price
        self.current_price = price
        self.current_value = abs(self.quantity) * price
        self.last_updated_at = datetime.utcnow()
        
        # Recalculate unrealized P&L
        if self.is_long:
            self.unrealized_pnl = (price - self.average_buy_price) * self.quantity
        elif self.is_short:
            self.unrealized_pnl = (self.average_sell_price - price) * abs(self.quantity)
        
        self.total_pnl = self.realized_pnl + self.unrealized_pnl
        self.pnl_percentage = self.calculate_pnl_percentage()
        
        self.updated_at = datetime.utcnow()
    
    def add_trade(self, trade: Trade):
        """Add trade to position"""
        if trade.is_buy:
            if self.is_short:
                # Closing short position
                self.quantity += trade.filled_quantity
                self.realized_pnl += (self.average_sell_price - trade.average_price) * trade.filled_quantity
            else:
                # Adding to long position
                if self.quantity == 0:
                    self.average_buy_price = trade.average_price
                else:
                    total_cost = (self.average_buy_price * self.quantity) + (trade.average_price * trade.filled_quantity)
                    self.quantity += trade.filled_quantity
                    self.average_buy_price = total_cost / self.quantity
                    return
                
                self.quantity += trade.filled_quantity
        
        elif trade.is_sell:
            if self.is_long:
                # Closing long position
                self.quantity -= trade.filled_quantity
                self.realized_pnl += (trade.average_price - self.average_buy_price) * trade.filled_quantity
            else:
                # Adding to short position
                if self.quantity == 0:
                    self.average_sell_price = trade.average_price
                else:
                    total_revenue = (self.average_sell_price * abs(self.quantity)) + (trade.average_price * trade.filled_quantity)
                    self.quantity -= trade.filled_quantity
                    self.average_sell_price = total_revenue / abs(self.quantity)
                    return
                
                self.quantity -= trade.filled_quantity
        
        # Update position type
        if self.quantity > 0:
            self.position_type = PositionType.LONG
        elif self.quantity < 0:
            self.position_type = PositionType.SHORT
        else:
            self.position_type = PositionType.FLAT
            self.status = 'CLOSED'
            self.closed_at = datetime.utcnow()
        
        # Update investment value
        self.investment_value = abs(self.quantity) * (self.average_buy_price or self.average_sell_price or 0)
        self.available_quantity = self.quantity
        self.total_pnl = self.realized_pnl + self.unrealized_pnl
        self.pnl_percentage = self.calculate_pnl_percentage()
        
        self.updated_at = datetime.utcnow()
    
    def close_position(self, closing_price: float):
        """Close the position"""
        if self.is_long:
            self.realized_pnl += (closing_price - self.average_buy_price) * self.quantity
        elif self.is_short:
            self.realized_pnl += (self.average_sell_price - closing_price) * abs(self.quantity)
        
        self.quantity = 0
        self.available_quantity = 0
        self.position_type = PositionType.FLAT
        self.status = 'CLOSED'
        self.closed_at = datetime.utcnow()
        self.current_price = closing_price
        self.current_value = 0
        self.unrealized_pnl = 0
        self.total_pnl = self.realized_pnl
        self.pnl_percentage = self.calculate_pnl_percentage()
        
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_details: bool = True) -> dict:
        """Convert position to dictionary"""
        data = {
            'id': self.id,
            'uuid': str(self.uuid),
            'symbol': self.symbol,
            'exchange': self.exchange,
            'instrument_type': self.instrument_type,
            'quantity': self.quantity,
            'available_quantity': self.available_quantity,
            'blocked_quantity': self.blocked_quantity,
            'position_type': self.position_type.value,
            'display_type': self.display_type,
            'status': self.status,
            'average_buy_price': self.average_buy_price,
            'average_sell_price': self.average_sell_price,
            'current_price': self.current_price,
            'last_price': self.last_price,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'total_pnl': self.total_pnl,
            'pnl_percentage': self.pnl_percentage,
            'investment_value': self.investment_value,
            'current_value': self.current_value,
            'max_profit': self.max_profit,
            'max_loss': self.max_loss,
            'max_drawdown': self.max_drawdown,
            'risk_reward_ratio': self.risk_reward_ratio,
            'strategy_id': self.strategy_id,
            'user_id': self.user_id,
            'tags': self.tags,
            'notes': self.notes,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'last_updated_at': self.last_updated_at.isoformat() if self.last_updated_at else None,
            'is_long': self.is_long,
            'is_short': self.is_short,
            'is_flat': self.is_flat,
            'is_open': self.is_open,
            'is_closed': self.is_closed,
            'days_open': self.days_open
        }
        
        return data