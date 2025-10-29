"""
VELOX-N8N Database Models
Package initialization for all database models
"""

from app.models.user import User
from app.models.strategy import Strategy, StrategyPerformance
from app.models.trade import Trade, Position, OrderType, OrderSide, TradeStatus, PositionType
from app.models.market_data import (
    Symbol, TickData, OHLCData, QuoteData, MarketDataSubscription,
    DataProvider, Timeframe, MarketDataType
)
from app.models.risk import (
    RiskSettings, RiskAlert, RiskMetrics, RiskLevel, AlertType
)
from app.models.audit import (
    AuditLog, SystemLog, ComplianceReport, AuditEventType, AuditSeverity
)

# Export all models
__all__ = [
    # User models
    "User",
    
    # Strategy models
    "Strategy",
    "StrategyPerformance",
    
    # Trade models
    "Trade",
    "Position",
    "OrderType",
    "OrderSide",
    "TradeStatus",
    "PositionType",
    
    # Market data models
    "Symbol",
    "TickData",
    "OHLCData",
    "QuoteData",
    "MarketDataSubscription",
    "DataProvider",
    "Timeframe",
    "MarketDataType",
    
    # Risk models
    "RiskSettings",
    "RiskAlert",
    "RiskMetrics",
    "RiskLevel",
    "AlertType",
    
    # Audit models
    "AuditLog",
    "SystemLog",
    "ComplianceReport",
    "AuditEventType",
    "AuditSeverity",
]

# Model metadata for Alembic
def get_model_metadata():
    """Get all model metadata for migrations"""
    from app.core.database import Base
    return Base.metadata

# Model registry for dynamic operations
MODEL_REGISTRY = {
    "user": User,
    "strategy": Strategy,
    "strategy_performance": StrategyPerformance,
    "trade": Trade,
    "position": Position,
    "symbol": Symbol,
    "tick_data": TickData,
    "ohlc_data": OHLCData,
    "quote_data": QuoteData,
    "market_data_subscription": MarketDataSubscription,
    "risk_settings": RiskSettings,
    "risk_alert": RiskAlert,
    "risk_metrics": RiskMetrics,
    "audit_log": AuditLog,
    "system_log": SystemLog,
    "compliance_report": ComplianceReport,
}

def get_model(model_name: str):
    """Get model class by name"""
    return MODEL_REGISTRY.get(model_name)

def get_all_models():
    """Get all model classes"""
    return MODEL_REGISTRY.values()

def get_model_names():
    """Get all model names"""
    return list(MODEL_REGISTRY.keys())