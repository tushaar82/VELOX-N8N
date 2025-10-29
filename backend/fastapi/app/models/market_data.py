"""
VELOX-N8N Market Data Model
Database model for market data storage and management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey, Index
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class DataProvider(str, enum.Enum):
    """Data provider enumeration"""
    OPENALGO = "OPENALGO"
    YAHOO = "YAHOO"
    ALPHA_VANTAGE = "ALPHA_VANTAGE"
    IEX = "IEX"
    BINANCE = "BINANCE"
    MANUAL = "MANUAL"


class Timeframe(str, enum.Enum):
    """Timeframe enumeration"""
    TICK = "TICK"
    ONE_MINUTE = "1M"
    FIVE_MINUTES = "5M"
    FIFTEEN_MINUTES = "15M"
    THIRTY_MINUTES = "30M"
    ONE_HOUR = "1H"
    FOUR_HOURS = "4H"
    ONE_DAY = "1D"
    ONE_WEEK = "1W"
    ONE_MONTH = "1M"


class MarketDataType(str, enum.Enum):
    """Market data type enumeration"""
    TICK = "TICK"
    OHLC = "OHLC"
    QUOTE = "QUOTE"
    ORDERBOOK = "ORDERBOOK"
    NEWS = "NEWS"
    FUNDAMENTAL = "FUNDAMENTAL"


class Symbol(Base):
    """
    Symbol model for instrument information
    """
    __tablename__ = "symbols"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    
    # Symbol information
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Exchange and instrument details
    exchange = Column(String(20), nullable=False, index=True)
    instrument_type = Column(String(20), nullable=False, index=True)  # EQUITY, FUTURES, OPTIONS, etc.
    segment = Column(String(20), nullable=True)  # EQUITY, DERIVATIVES, etc.
    category = Column(String(50), nullable=True)  # LARGE_CAP, MID_CAP, etc.
    
    # Trading details
    lot_size = Column(Integer, nullable=True)
    tick_size = Column(Float, nullable=True)
    decimal_places = Column(Integer, nullable=True)
    
    # Trading hours
    trading_session_start = Column(String(10), nullable=True)  # HH:MM format
    trading_session_end = Column(String(10), nullable=True)  # HH:MM format
    is_tradable = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    sector = Column(String(50), nullable=True)
    industry = Column(String(50), nullable=True)
    market_cap = Column(String(20), nullable=True)  # LARGE_CAP, MID_CAP, SMALL_CAP
    isin = Column(String(20), nullable=True, unique=True)
    
    # Data provider settings
    data_provider = Column(Enum(DataProvider), nullable=False, default=DataProvider.OPENALGO)
    provider_symbol = Column(String(50), nullable=True)  # Symbol as per provider
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    last_data_update = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    tick_data = relationship("TickData", back_populates="symbol", cascade="all, delete-orphan")
    ohlc_data = relationship("OHLCData", back_populates="symbol", cascade="all, delete-orphan")
    quote_data = relationship("QuoteData", back_populates="symbol", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Symbol(id={self.id}, symbol='{self.symbol}', exchange='{self.exchange}', type='{self.instrument_type}')>"
    
    @property
    def display_name(self) -> str:
        """Get display name"""
        return f"{self.symbol} - {self.name}"
    
    @property
    def is_equity(self) -> bool:
        """Check if symbol is equity"""
        return self.instrument_type.upper() == 'EQUITY'
    
    @property
    def is_derivative(self) -> bool:
        """Check if symbol is derivative"""
        return self.instrument_type.upper() in ['FUTURES', 'OPTIONS']
    
    def to_dict(self) -> dict:
        """Convert symbol to dictionary"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'symbol': self.symbol,
            'name': self.name,
            'description': self.description,
            'exchange': self.exchange,
            'instrument_type': self.instrument_type,
            'segment': self.segment,
            'category': self.category,
            'lot_size': self.lot_size,
            'tick_size': self.tick_size,
            'decimal_places': self.decimal_places,
            'trading_session_start': self.trading_session_start,
            'trading_session_end': self.trading_session_end,
            'is_tradable': self.is_tradable,
            'sector': self.sector,
            'industry': self.industry,
            'market_cap': self.market_cap,
            'isin': self.isin,
            'data_provider': self.data_provider.value,
            'provider_symbol': self.provider_symbol,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_data_update': self.last_data_update.isoformat() if self.last_data_update else None,
            'display_name': self.display_name,
            'is_equity': self.is_equity,
            'is_derivative': self.is_derivative
        }


class TickData(Base):
    """
    Tick data model for real-time price information
    """
    __tablename__ = "tick_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Symbol and timestamp
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    
    # Price information
    last_price = Column(Float, nullable=False)
    bid_price = Column(Float, nullable=True)
    ask_price = Column(Float, nullable=True)
    
    # Volume information
    last_quantity = Column(Float, nullable=True)
    bid_quantity = Column(Float, nullable=True)
    ask_quantity = Column(Float, nullable=True)
    total_volume = Column(Float, nullable=False, default=0)
    total_buy_volume = Column(Float, nullable=False, default=0)
    total_sell_volume = Column(Float, nullable=False, default=0)
    
    # Trade information
    trade_count = Column(Integer, nullable=False, default=0)
    open_interest = Column(Float, nullable=True)
    
    # Additional data
    oi_change = Column(Float, nullable=True)
    price_change = Column(Float, nullable=True)
    price_change_percent = Column(Float, nullable=True)
    
    # Metadata
    data_provider = Column(Enum(DataProvider), nullable=False, default=DataProvider.OPENALGO)
    raw_data = Column(JSON, nullable=True)  # Raw data from provider
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    symbol = relationship("Symbol", back_populates="tick_data")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_tick_symbol_timestamp', 'symbol_id', 'timestamp'),
        Index('idx_tick_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<TickData(id={self.id}, symbol_id={self.symbol_id}, timestamp={self.timestamp}, price={self.last_price})>"
    
    @property
    def spread(self) -> float:
        """Calculate bid-ask spread"""
        if self.bid_price and self.ask_price:
            return self.ask_price - self.bid_price
        return 0.0
    
    @property
    def mid_price(self) -> float:
        """Calculate mid price"""
        if self.bid_price and self.ask_price:
            return (self.bid_price + self.ask_price) / 2
        return self.last_price
    
    def to_dict(self) -> dict:
        """Convert tick data to dictionary"""
        return {
            'id': self.id,
            'symbol_id': self.symbol_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'last_price': self.last_price,
            'bid_price': self.bid_price,
            'ask_price': self.ask_price,
            'last_quantity': self.last_quantity,
            'bid_quantity': self.bid_quantity,
            'ask_quantity': self.ask_quantity,
            'total_volume': self.total_volume,
            'total_buy_volume': self.total_buy_volume,
            'total_sell_volume': self.total_sell_volume,
            'trade_count': self.trade_count,
            'open_interest': self.open_interest,
            'oi_change': self.oi_change,
            'price_change': self.price_change,
            'price_change_percent': self.price_change_percent,
            'data_provider': self.data_provider.value,
            'raw_data': self.raw_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'spread': self.spread,
            'mid_price': self.mid_price
        }


class OHLCData(Base):
    """
    OHLC data model for candlestick information
    """
    __tablename__ = "ohlc_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Symbol and timestamp
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    timeframe = Column(Enum(Timeframe), nullable=False, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    
    # OHLC values
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    
    # Volume information
    volume = Column(Float, nullable=False, default=0)
    buy_volume = Column(Float, nullable=False, default=0)
    sell_volume = Column(Float, nullable=False, default=0)
    
    # Trade information
    trade_count = Column(Integer, nullable=False, default=0)
    
    # Additional data
    vwap = Column(Float, nullable=True)  # Volume Weighted Average Price
    open_interest = Column(Float, nullable=True)
    
    # Price changes
    price_change = Column(Float, nullable=True)
    price_change_percent = Column(Float, nullable=True)
    
    # Metadata
    data_provider = Column(Enum(DataProvider), nullable=False, default=DataProvider.OPENALGO)
    raw_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    
    # Relationships
    symbol = relationship("Symbol", back_populates="ohlc_data")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_ohlc_symbol_timeframe_timestamp', 'symbol_id', 'timeframe', 'timestamp'),
        Index('idx_ohlc_symbol_timestamp', 'symbol_id', 'timestamp'),
        Index('idx_ohlc_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<OHLCData(id={self.id}, symbol_id={self.symbol_id}, timeframe={self.timeframe}, timestamp={self.timestamp})>"
    
    @property
    def is_green(self) -> bool:
        """Check if candle is green (close > open)"""
        return self.close_price > self.open_price
    
    @property
    def is_red(self) -> bool:
        """Check if candle is red (close < open)"""
        return self.close_price < self.open_price
    
    @property
    def body_size(self) -> float:
        """Calculate candle body size"""
        return abs(self.close_price - self.open_price)
    
    @property
    def upper_shadow(self) -> float:
        """Calculate upper shadow size"""
        return self.high_price - max(self.open_price, self.close_price)
    
    @property
    def lower_shadow(self) -> float:
        """Calculate lower shadow size"""
        return min(self.open_price, self.close_price) - self.low_price
    
    @property
    def range_size(self) -> float:
        """Calculate price range"""
        return self.high_price - self.low_price
    
    def calculate_vwap(self) -> float:
        """Calculate VWAP if not present"""
        if self.vwap is not None:
            return self.vwap
        
        if self.volume == 0:
            return self.close_price
        
        # Simplified VWAP calculation
        # In reality, this would need tick-by-tick data
        typical_price = (self.high_price + self.low_price + self.close_price) / 3
        return typical_price
    
    def to_dict(self) -> dict:
        """Convert OHLC data to dictionary"""
        return {
            'id': self.id,
            'symbol_id': self.symbol_id,
            'timeframe': self.timeframe.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'open_price': self.open_price,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'close_price': self.close_price,
            'volume': self.volume,
            'buy_volume': self.buy_volume,
            'sell_volume': self.sell_volume,
            'trade_count': self.trade_count,
            'vwap': self.vwap or self.calculate_vwap(),
            'open_interest': self.open_interest,
            'price_change': self.price_change,
            'price_change_percent': self.price_change_percent,
            'data_provider': self.data_provider.value,
            'raw_data': self.raw_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_green': self.is_green,
            'is_red': self.is_red,
            'body_size': self.body_size,
            'upper_shadow': self.upper_shadow,
            'lower_shadow': self.lower_shadow,
            'range_size': self.range_size
        }


class QuoteData(Base):
    """
    Quote data model for market quotes
    """
    __tablename__ = "quote_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Symbol and timestamp
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    
    # Bid information
    bid_price = Column(Float, nullable=False)
    bid_quantity = Column(Float, nullable=False)
    bid_orders = Column(Integer, nullable=False, default=0)
    
    # Ask information
    ask_price = Column(Float, nullable=False)
    ask_quantity = Column(Float, nullable=False)
    ask_orders = Column(Integer, nullable=False, default=0)
    
    # Market depth (top 5 levels)
    bid_depth = Column(JSON, nullable=True)  # List of [price, quantity, orders]
    ask_depth = Column(JSON, nullable=True)  # List of [price, quantity, orders]
    
    # Additional information
    last_price = Column(Float, nullable=True)
    last_quantity = Column(Float, nullable=True)
    total_volume = Column(Float, nullable=False, default=0)
    open_interest = Column(Float, nullable=True)
    
    # Metadata
    data_provider = Column(Enum(DataProvider), nullable=False, default=DataProvider.OPENALGO)
    raw_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    symbol = relationship("Symbol", back_populates="quote_data")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_quote_symbol_timestamp', 'symbol_id', 'timestamp'),
        Index('idx_quote_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<QuoteData(id={self.id}, symbol_id={self.symbol_id}, timestamp={self.timestamp}, bid={self.bid_price}, ask={self.ask_price})>"
    
    @property
    def spread(self) -> float:
        """Calculate bid-ask spread"""
        return self.ask_price - self.bid_price
    
    @property
    def spread_percentage(self) -> float:
        """Calculate spread as percentage of mid price"""
        mid_price = self.mid_price
        if mid_price == 0:
            return 0.0
        return (self.spread / mid_price) * 100
    
    @property
    def mid_price(self) -> float:
        """Calculate mid price"""
        return (self.bid_price + self.ask_price) / 2
    
    @property
    def weighted_mid_price(self) -> float:
        """Calculate weighted mid price"""
        total_quantity = self.bid_quantity + self.ask_quantity
        if total_quantity == 0:
            return self.mid_price
        
        return (self.bid_price * self.ask_quantity + self.ask_price * self.bid_quantity) / total_quantity
    
    def to_dict(self) -> dict:
        """Convert quote data to dictionary"""
        return {
            'id': self.id,
            'symbol_id': self.symbol_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'bid_price': self.bid_price,
            'bid_quantity': self.bid_quantity,
            'bid_orders': self.bid_orders,
            'ask_price': self.ask_price,
            'ask_quantity': self.ask_quantity,
            'ask_orders': self.ask_orders,
            'bid_depth': self.bid_depth,
            'ask_depth': self.ask_depth,
            'last_price': self.last_price,
            'last_quantity': self.last_quantity,
            'total_volume': self.total_volume,
            'open_interest': self.open_interest,
            'data_provider': self.data_provider.value,
            'raw_data': self.raw_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'spread': self.spread,
            'spread_percentage': self.spread_percentage,
            'mid_price': self.mid_price,
            'weighted_mid_price': self.weighted_mid_price
        }


class MarketDataSubscription(Base):
    """
    Market data subscription model for tracking user subscriptions
    """
    __tablename__ = "market_data_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Subscription details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    data_type = Column(Enum(MarketDataType), nullable=False)
    timeframe = Column(Enum(Timeframe), nullable=True)  # Only for OHLC data
    
    # Subscription status
    is_active = Column(Boolean, default=True, nullable=False)
    is_realtime = Column(Boolean, default=True, nullable=False)
    
    # Subscription settings
    max_history_days = Column(Integer, nullable=True)
    update_frequency = Column(Integer, nullable=True)  # In seconds
    
    # Metadata
    subscription_config = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    last_data_sent = Column(TIMESTAMP(timezone=True), nullable=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    symbol = relationship("Symbol")
    
    def __repr__(self):
        return f"<MarketDataSubscription(id={self.id}, user_id={self.user_id}, symbol_id={self.symbol_id}, type={self.data_type})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if subscription is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def display_data_type(self) -> str:
        """Get display data type name"""
        type_map = {
            'TICK': 'Tick Data',
            'OHLC': 'OHLC Data',
            'QUOTE': 'Quote Data',
            'ORDERBOOK': 'Order Book',
            'NEWS': 'News',
            'FUNDAMENTAL': 'Fundamental'
        }
        return type_map.get(self.data_type.value, self.data_type.value)
    
    def to_dict(self) -> dict:
        """Convert subscription to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol_id': self.symbol_id,
            'data_type': self.data_type.value,
            'display_data_type': self.display_data_type,
            'timeframe': self.timeframe.value if self.timeframe else None,
            'is_active': self.is_active,
            'is_realtime': self.is_realtime,
            'max_history_days': self.max_history_days,
            'update_frequency': self.update_frequency,
            'subscription_config': self.subscription_config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_data_sent': self.last_data_sent.isoformat() if self.last_data_sent else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired
        }