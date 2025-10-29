"""
VELOX-N8N Trading Schemas
Pydantic models for trading API validation and serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.trade import OrderType, OrderSide, TradeStatus, PositionType


class OrderCreate(BaseModel):
    """Order creation schema"""
    symbol: str = Field(..., description="Trading symbol")
    exchange: str = Field(..., description="Exchange name")
    instrument_type: str = Field(..., description="Instrument type")
    order_type: OrderType = Field(..., description="Order type")
    order_side: OrderSide = Field(..., description="Order side")
    quantity: float = Field(..., gt=0, description="Order quantity")
    price: Optional[float] = Field(None, gt=0, description="Order price (for limit orders)")
    trigger_price: Optional[float] = Field(None, gt=0, description="Trigger price (for stop orders)")
    
    # Risk management
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")
    take_profit: Optional[float] = Field(None, gt=0, description="Take profit price")
    trailing_stop: Optional[float] = Field(None, gt=0, description="Trailing stop distance")
    
    # Order metadata
    strategy_id: Optional[int] = Field(None, description="Strategy ID")
    tags: Optional[List[str]] = Field(None, description="Order tags")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")
    
    @validator('price')
    def validate_price(cls, v, values):
        """Validate price based on order type"""
        order_type = values.get('order_type')
        if order_type == OrderType.MARKET and v is not None:
            raise ValueError('Market orders cannot have a price')
        elif order_type in [OrderType.LIMIT, OrderType.TAKE_PROFIT] and v is None:
            raise ValueError('Limit orders must have a price')
        return v
    
    @validator('trigger_price')
    def validate_trigger_price(cls, v, values):
        """Validate trigger price for stop orders"""
        order_type = values.get('order_type')
        if order_type in [OrderType.STOP_LOSS, OrderType.STOP_MARKET] and v is None:
            raise ValueError('Stop orders must have a trigger price')
        elif order_type not in [OrderType.STOP_LOSS, OrderType.STOP_MARKET] and v is not None:
            raise ValueError('Only stop orders can have a trigger price')
        return v
    
    @validator('stop_loss', 'take_profit')
    def validate_risk_prices(cls, v, values):
        """Validate stop loss and take profit prices"""
        order_side = values.get('order_side')
        price = values.get('price')
        
        if v is None:
            return v
        
        if order_side == OrderSide.BUY:
            # For buy orders, stop loss should be below price
            if price and v >= price:
                raise ValueError('Stop loss must be below order price for buy orders')
            # Take profit should be above price
            if price and v <= price:
                raise ValueError('Take profit must be above order price for buy orders')
        elif order_side == OrderSide.SELL:
            # For sell orders, stop loss should be above price
            if price and v <= price:
                raise ValueError('Stop loss must be above order price for sell orders')
            # Take profit should be below price
            if price and v >= price:
                raise ValueError('Take profit must be below order price for sell orders')
        
        return v


class OrderUpdate(BaseModel):
    """Order update schema"""
    order_id: str = Field(..., description="Order ID")
    price: Optional[float] = Field(None, gt=0, description="New price")
    quantity: Optional[float] = Field(None, gt=0, description="New quantity")
    stop_loss: Optional[float] = Field(None, gt=0, description="New stop loss")
    take_profit: Optional[float] = Field(None, gt=0, description="New take profit")
    trailing_stop: Optional[float] = Field(None, gt=0, description="New trailing stop")
    notes: Optional[str] = Field(None, max_length=500, description="Update notes")


class OrderCancel(BaseModel):
    """Order cancellation schema"""
    order_id: str = Field(..., description="Order ID")
    reason: Optional[str] = Field(None, max_length=200, description="Cancellation reason")


class OrderResponse(BaseModel):
    """Order response schema"""
    id: int
    uuid: str
    order_id: str
    broker_order_id: Optional[str]
    parent_order_id: Optional[str]
    symbol: str
    exchange: str
    instrument_type: str
    order_type: str
    display_type: str
    order_side: str
    display_side: str
    quantity: float
    price: Optional[float]
    trigger_price: Optional[float]
    status: str
    display_status: str
    filled_quantity: float
    average_price: Optional[float]
    execution_price: Optional[float]
    order_value: Optional[float]
    executed_value: Optional[float]
    brokerage: float
    taxes: float
    charges: float
    total_charges: float
    net_value: Optional[float]
    realized_pnl: Optional[float]
    unrealized_pnl: Optional[float]
    total_pnl: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    trailing_stop: Optional[float]
    strategy_id: Optional[int]
    user_id: int
    tags: Optional[List[str]]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    placed_at: Optional[datetime]
    executed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    is_buy: bool
    is_sell: bool
    is_market_order: bool
    is_limit_order: bool
    is_stop_order: bool
    is_executed: bool
    is_pending: bool
    is_cancelled: bool
    fill_percentage: float
    remaining_quantity: float
    
    class Config:
        from_attributes = True


class PositionResponse(BaseModel):
    """Position response schema"""
    id: int
    uuid: str
    symbol: str
    exchange: str
    instrument_type: str
    quantity: float
    available_quantity: float
    blocked_quantity: float
    position_type: str
    display_type: str
    status: str
    average_buy_price: Optional[float]
    average_sell_price: Optional[float]
    current_price: Optional[float]
    last_price: Optional[float]
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    pnl_percentage: float
    investment_value: float
    current_value: float
    max_profit: Optional[float]
    max_loss: Optional[float]
    max_drawdown: float
    risk_reward_ratio: Optional[float]
    strategy_id: Optional[int]
    user_id: int
    tags: Optional[List[str]]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    opened_at: Optional[datetime]
    closed_at: Optional[datetime]
    last_updated_at: Optional[datetime]
    is_long: bool
    is_short: bool
    is_flat: bool
    is_open: bool
    is_closed: bool
    days_open: int
    
    class Config:
        from_attributes = True


class TradeHistoryRequest(BaseModel):
    """Trade history request schema"""
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    exchange: Optional[str] = Field(None, description="Filter by exchange")
    order_type: Optional[OrderType] = Field(None, description="Filter by order type")
    order_side: Optional[OrderSide] = Field(None, description="Filter by order side")
    status: Optional[TradeStatus] = Field(None, description="Filter by status")
    strategy_id: Optional[int] = Field(None, description="Filter by strategy ID")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class PositionHistoryRequest(BaseModel):
    """Position history request schema"""
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    exchange: Optional[str] = Field(None, description="Filter by exchange")
    position_type: Optional[PositionType] = Field(None, description="Filter by position type")
    status: Optional[str] = Field(None, description="Filter by status")
    strategy_id: Optional[int] = Field(None, description="Filter by strategy ID")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class PortfolioSummary(BaseModel):
    """Portfolio summary schema"""
    total_value: float = Field(..., description="Total portfolio value")
    total_exposure: float = Field(..., description="Total exposure")
    net_exposure: float = Field(..., description="Net exposure")
    available_cash: float = Field(..., description="Available cash")
    used_margin: float = Field(..., description="Used margin")
    available_margin: float = Field(..., description="Available margin")
    margin_call_level: float = Field(..., description="Margin call level")
    total_pnl: float = Field(..., description="Total P&L")
    daily_pnl: float = Field(..., description="Daily P&L")
    unrealized_pnl: float = Field(..., description="Unrealized P&L")
    realized_pnl: float = Field(..., description="Realized P&L")
    total_positions: int = Field(..., description="Total number of positions")
    active_positions: int = Field(..., description="Number of active positions")
    long_positions: int = Field(..., description="Number of long positions")
    short_positions: int = Field(..., description="Number of short positions")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    leverage_ratio: float = Field(..., description="Leverage ratio")
    
    class Config:
        from_attributes = True


class OrderBookRequest(BaseModel):
    """Order book request schema"""
    symbol: str = Field(..., description="Trading symbol")
    exchange: str = Field(..., description="Exchange name")
    depth: int = Field(5, ge=1, le=20, description="Order book depth")
    
    @validator('depth')
    def validate_depth(cls, v):
        """Validate depth is reasonable"""
        if v < 1 or v > 20:
            raise ValueError('Depth must be between 1 and 20')
        return v


class OrderBookLevel(BaseModel):
    """Order book level schema"""
    price: float = Field(..., description="Price level")
    quantity: float = Field(..., description="Quantity at this level")
    orders: int = Field(..., description="Number of orders at this level")


class OrderBookResponse(BaseModel):
    """Order book response schema"""
    symbol: str
    exchange: str
    timestamp: datetime
    bid_levels: List[OrderBookLevel]
    ask_levels: List[OrderBookLevel]
    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    mid_price: Optional[float]
    total_bid_quantity: float
    total_ask_quantity: float
    
    class Config:
        from_attributes = True


class MarketStats(BaseModel):
    """Market statistics schema"""
    symbol: str
    exchange: str
    last_price: float
    bid_price: Optional[float]
    ask_price: Optional[float]
    last_quantity: Optional[float]
    total_volume: float
    total_buy_volume: float
    total_sell_volume: float
    trade_count: int
    price_change: Optional[float]
    price_change_percent: Optional[float]
    high_price: Optional[float]
    low_price: Optional[float]
    open_price: Optional[float]
    vwap: Optional[float]
    open_interest: Optional[float]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class TradingSession(BaseModel):
    """Trading session schema"""
    session_id: str
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    total_orders: int
    executed_orders: int
    cancelled_orders: int
    total_volume: float
    total_value: float
    total_pnl: float
    max_drawdown: float
    positions_opened: int
    positions_closed: int
    
    class Config:
        from_attributes = True


class RiskMetrics(BaseModel):
    """Risk metrics schema"""
    portfolio_value: float
    total_exposure: float
    net_exposure: float
    leverage_ratio: float
    var_1day: Optional[float]
    var_5day: Optional[float]
    var_30day: Optional[float]
    current_drawdown: float
    max_drawdown: float
    drawdown_duration: int
    volatility_10day: Optional[float]
    volatility_30day: Optional[float]
    volatility_90day: Optional[float]
    avg_correlation: Optional[float]
    max_correlation: Optional[float]
    correlation_risk_score: Optional[float]
    sector_concentration: Optional[Dict[str, float]]
    symbol_concentration: Optional[Dict[str, float]]
    concentration_risk_score: Optional[float]
    daily_pnl: float
    weekly_pnl: Optional[float]
    monthly_pnl: Optional[float]
    ytd_pnl: Optional[float]
    overall_risk_score: float
    risk_level: str
    display_risk_level: str
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class TradingAnalytics(BaseModel):
    """Trading analytics schema"""
    period_start: datetime
    period_end: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    average_trade_duration: float
    sharpe_ratio: Optional[float]
    sortino_ratio: Optional[float]
    max_drawdown: float
    max_drawdown_duration: int
    total_commission: float
    net_pnl: float
    return_on_investment: float
    
    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    """Alert creation schema"""
    alert_type: str = Field(..., description="Alert type")
    symbol: Optional[str] = Field(None, description="Symbol (optional)")
    condition: str = Field(..., description="Alert condition")
    threshold: float = Field(..., description="Alert threshold")
    is_active: bool = Field(True, description="Alert active status")
    notification_channels: List[str] = Field(..., description="Notification channels")
    expires_at: Optional[datetime] = Field(None, description="Alert expiration")


class AlertResponse(BaseModel):
    """Alert response schema"""
    id: int
    uuid: str
    alert_type: str
    display_type: str
    severity: str
    display_severity: str
    title: str
    message: str
    user_id: int
    symbol: Optional[str]
    current_value: Optional[float]
    threshold_value: Optional[float]
    threshold_percentage: Optional[float]
    status: str
    display_status: str
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[int]
    resolved_at: Optional[datetime]
    resolved_by: Optional[int]
    resolution_notes: Optional[str]
    email_sent: bool
    sms_sent: bool
    push_sent: bool
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_acknowledged: bool
    is_resolved: bool
    is_critical: bool
    is_high: bool
    severity_score: float
    
    class Config:
        from_attributes = True