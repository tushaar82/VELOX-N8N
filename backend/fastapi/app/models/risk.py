"""
VELOX-N8N Risk Management Model
Database model for risk management and settings
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class RiskLevel(str, enum.Enum):
    """Risk level enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(str, enum.Enum):
    """Alert type enumeration"""
    POSITION_SIZE = "POSITION_SIZE"
    DAILY_LOSS = "DAILY_LOSS"
    DRAWDOWN = "DRAWDOWN"
    CORRELATION = "CORRELATION"
    VOLATILITY = "VOLATILITY"
    MARGIN = "MARGIN"
    LIQUIDITY = "LIQUIDITY"
    CONCENTRATION = "CONCENTRATION"
    LEVERAGE = "LEVERAGE"


class RiskSettings(Base):
    """
    Risk settings model for user-specific risk management
    """
    __tablename__ = "risk_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Position sizing limits
    max_position_size = Column(Float, nullable=False, default=100000.0)  # Maximum position size in currency
    max_position_percentage = Column(Float, nullable=False, default=10.0)  # Maximum position size as % of portfolio
    max_positions_per_symbol = Column(Integer, nullable=False, default=1)  # Max positions per symbol
    max_total_positions = Column(Integer, nullable=False, default=10)  # Max total positions
    
    # Risk per trade
    risk_per_trade = Column(Float, nullable=False, default=2.0)  # Risk per trade in percentage
    max_risk_per_trade = Column(Float, nullable=False, default=2000.0)  # Max risk per trade in currency
    risk_per_trade_percentage = Column(Float, nullable=False, default=1.0)  # Risk per trade as % of portfolio
    
    # Daily and overall limits
    max_daily_loss = Column(Float, nullable=False, default=10000.0)  # Maximum daily loss
    max_daily_loss_percentage = Column(Float, nullable=False, default=5.0)  # Max daily loss as % of portfolio
    max_monthly_loss = Column(Float, nullable=False, default=20000.0)  # Maximum monthly loss
    max_overall_loss = Column(Float, nullable=False, default=50000.0)  # Maximum overall loss
    
    # Drawdown limits
    max_drawdown = Column(Float, nullable=False, default=20.0)  # Maximum drawdown in percentage
    max_drawdown_amount = Column(Float, nullable=False, default=20000.0)  # Maximum drawdown in currency
    
    # Correlation and concentration
    max_correlation = Column(Float, nullable=False, default=0.7)  # Maximum correlation between positions
    max_sector_concentration = Column(Float, nullable=False, default=30.0)  # Max concentration in one sector
    max_symbol_concentration = Column(Float, nullable=False, default=20.0)  # Max concentration in one symbol
    
    # Leverage and margin
    max_leverage = Column(Float, nullable=False, default=2.0)  # Maximum leverage ratio
    margin_call_threshold = Column(Float, nullable=False, default=80.0)  # Margin call threshold in percentage
    stop_out_threshold = Column(Float, nullable=False, default=90.0)  # Stop out threshold in percentage
    
    # Volatility limits
    max_volatility = Column(Float, nullable=False, default=50.0)  # Maximum volatility in percentage
    volatility_lookback_days = Column(Integer, nullable=False, default=30)  # Volatility calculation period
    
    # Stop loss and take profit
    default_stop_loss = Column(Float, nullable=False, default=2.0)  # Default stop loss in percentage
    default_take_profit = Column(Float, nullable=False, default=4.0)  # Default take profit in percentage
    trailing_stop_enabled = Column(Boolean, default=False, nullable=False)
    trailing_stop_distance = Column(Float, nullable=False, default=1.0)  # Trailing stop distance in percentage
    
    # Risk management settings
    auto_reduce_positions = Column(Boolean, default=True, nullable=False)
    auto_close_positions = Column(Boolean, default=False, nullable=False)
    risk_reduction_threshold = Column(Float, nullable=False, default=80.0)  # Risk reduction threshold in percentage
    
    # Alert settings
    email_alerts = Column(Boolean, default=True, nullable=False)
    sms_alerts = Column(Boolean, default=False, nullable=False)
    push_alerts = Column(Boolean, default=True, nullable=False)
    alert_threshold = Column(Float, nullable=False, default=70.0)  # Alert threshold in percentage
    
    # Metadata
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    last_reviewed = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="risk_settings")
    risk_alerts = relationship("RiskAlert", back_populates="risk_settings", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RiskSettings(id={self.id}, user_id={self.user_id}, max_position_size={self.max_position_size})>"
    
    @property
    def is_conservative(self) -> bool:
        """Check if risk settings are conservative"""
        return (
            self.risk_per_trade <= 1.0 and
            self.max_drawdown <= 15.0 and
            self.max_leverage <= 1.5
        )
    
    @property
    def is_aggressive(self) -> bool:
        """Check if risk settings are aggressive"""
        return (
            self.risk_per_trade >= 3.0 or
            self.max_leverage >= 3.0 or
            self.max_drawdown >= 30.0
        )
    
    def calculate_position_size(self, portfolio_value: float, risk_amount: float = None) -> float:
        """Calculate recommended position size"""
        if risk_amount is None:
            risk_amount = portfolio_value * (self.risk_per_trade / 100)
        
        # Calculate position size based on risk
        position_size = risk_amount / (self.default_stop_loss / 100)
        
        # Apply maximum position size limits
        max_size_by_percentage = portfolio_value * (self.max_position_percentage / 100)
        max_size = min(self.max_position_size, max_size_by_percentage)
        
        return min(position_size, max_size)
    
    def validate_risk_settings(self) -> tuple[bool, list]:
        """Validate risk settings"""
        errors = []
        
        # Check logical consistency
        if self.max_daily_loss_percentage > 100:
            errors.append("Daily loss percentage cannot exceed 100%")
        
        if self.max_drawdown > 100:
            errors.append("Maximum drawdown cannot exceed 100%")
        
        if self.risk_per_trade > self.max_daily_loss_percentage:
            errors.append("Risk per trade cannot exceed maximum daily loss percentage")
        
        if self.max_leverage < 1:
            errors.append("Maximum leverage must be at least 1")
        
        if self.margin_call_threshold >= self.stop_out_threshold:
            errors.append("Margin call threshold must be less than stop out threshold")
        
        if self.default_take_profit <= self.default_stop_loss:
            errors.append("Take profit must be greater than stop loss")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> dict:
        """Convert risk settings to dictionary"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'user_id': self.user_id,
            'max_position_size': self.max_position_size,
            'max_position_percentage': self.max_position_percentage,
            'max_positions_per_symbol': self.max_positions_per_symbol,
            'max_total_positions': self.max_total_positions,
            'risk_per_trade': self.risk_per_trade,
            'max_risk_per_trade': self.max_risk_per_trade,
            'risk_per_trade_percentage': self.risk_per_trade_percentage,
            'max_daily_loss': self.max_daily_loss,
            'max_daily_loss_percentage': self.max_daily_loss_percentage,
            'max_monthly_loss': self.max_monthly_loss,
            'max_overall_loss': self.max_overall_loss,
            'max_drawdown': self.max_drawdown,
            'max_drawdown_amount': self.max_drawdown_amount,
            'max_correlation': self.max_correlation,
            'max_sector_concentration': self.max_sector_concentration,
            'max_symbol_concentration': self.max_symbol_concentration,
            'max_leverage': self.max_leverage,
            'margin_call_threshold': self.margin_call_threshold,
            'stop_out_threshold': self.stop_out_threshold,
            'max_volatility': self.max_volatility,
            'volatility_lookback_days': self.volatility_lookback_days,
            'default_stop_loss': self.default_stop_loss,
            'default_take_profit': self.default_take_profit,
            'trailing_stop_enabled': self.trailing_stop_enabled,
            'trailing_stop_distance': self.trailing_stop_distance,
            'auto_reduce_positions': self.auto_reduce_positions,
            'auto_close_positions': self.auto_close_positions,
            'risk_reduction_threshold': self.risk_reduction_threshold,
            'email_alerts': self.email_alerts,
            'sms_alerts': self.sms_alerts,
            'push_alerts': self.push_alerts,
            'alert_threshold': self.alert_threshold,
            'notes': self.notes,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None,
            'is_conservative': self.is_conservative,
            'is_aggressive': self.is_aggressive
        }


class RiskAlert(Base):
    """
    Risk alert model for risk monitoring and notifications
    """
    __tablename__ = "risk_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    
    # Alert information
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # User and context
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    risk_settings_id = Column(Integer, ForeignKey("risk_settings.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    position_id = Column(Integer, nullable=True)  # Reference to position if applicable
    
    # Alert details
    current_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    threshold_percentage = Column(Float, nullable=True)
    
    # Alert data
    alert_data = Column(JSON, nullable=True)  # Detailed alert information
    recommendations = Column(JSON, nullable=True)  # Recommended actions
    
    # Status and resolution
    status = Column(String(20), default='ACTIVE', nullable=False, index=True)  # ACTIVE, ACKNOWLEDGED, RESOLVED
    acknowledged_at = Column(TIMESTAMP(timezone=True), nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(TIMESTAMP(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Notification settings
    email_sent = Column(Boolean, default=False, nullable=False)
    sms_sent = Column(Boolean, default=False, nullable=False)
    push_sent = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    tags = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    risk_settings = relationship("RiskSettings", back_populates="risk_alerts")
    strategy = relationship("Strategy")
    position = relationship("Position")
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f"<RiskAlert(id={self.id}, type='{self.alert_type}', severity='{self.severity}', user_id={self.user_id})>"
    
    @property
    def is_active(self) -> bool:
        """Check if alert is active"""
        return self.status == 'ACTIVE'
    
    @property
    def is_acknowledged(self) -> bool:
        """Check if alert is acknowledged"""
        return self.status in ['ACKNOWLEDGED', 'RESOLVED']
    
    @property
    def is_resolved(self) -> bool:
        """Check if alert is resolved"""
        return self.status == 'RESOLVED'
    
    @property
    def is_critical(self) -> bool:
        """Check if alert is critical"""
        return self.severity == RiskLevel.CRITICAL.value
    
    @property
    def is_high(self) -> bool:
        """Check if alert is high severity"""
        return self.severity == RiskLevel.HIGH.value
    
    @property
    def display_severity(self) -> str:
        """Get display severity name"""
        severity_map = {
            'LOW': 'Low',
            'MEDIUM': 'Medium',
            'HIGH': 'High',
            'CRITICAL': 'Critical'
        }
        return severity_map.get(self.severity, self.severity)
    
    @property
    def display_status(self) -> str:
        """Get display status name"""
        status_map = {
            'ACTIVE': 'Active',
            'ACKNOWLEDGED': 'Acknowledged',
            'RESOLVED': 'Resolved'
        }
        return status_map.get(self.status, self.status)
    
    @property
    def display_type(self) -> str:
        """Get display alert type name"""
        type_map = {
            'POSITION_SIZE': 'Position Size',
            'DAILY_LOSS': 'Daily Loss',
            'DRAWDOWN': 'Drawdown',
            'CORRELATION': 'Correlation',
            'VOLATILITY': 'Volatility',
            'MARGIN': 'Margin',
            'LIQUIDITY': 'Liquidity',
            'CONCENTRATION': 'Concentration',
            'LEVERAGE': 'Leverage'
        }
        return type_map.get(self.alert_type, self.alert_type.replace('_', ' ').title())
    
    def acknowledge(self, user_id: int):
        """Acknowledge alert"""
        self.status = 'ACKNOWLEDGED'
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = user_id
        self.updated_at = datetime.utcnow()
    
    def resolve(self, user_id: int, notes: str = None):
        """Resolve alert"""
        self.status = 'RESOLVED'
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        self.resolution_notes = notes
        self.updated_at = datetime.utcnow()
    
    def calculate_severity_score(self) -> float:
        """Calculate severity score (0-100)"""
        base_scores = {
            'LOW': 25,
            'MEDIUM': 50,
            'HIGH': 75,
            'CRITICAL': 100
        }
        
        base_score = base_scores.get(self.severity, 50)
        
        # Adjust based on threshold breach
        if self.threshold_percentage and self.threshold_percentage > 100:
            excess = self.threshold_percentage - 100
            base_score = min(100, base_score + (excess * 0.5))
        
        return base_score
    
    def to_dict(self, include_details: bool = True) -> dict:
        """Convert risk alert to dictionary"""
        data = {
            'id': self.id,
            'uuid': str(self.uuid),
            'alert_type': self.alert_type,
            'display_type': self.display_type,
            'severity': self.severity,
            'display_severity': self.display_severity,
            'title': self.title,
            'message': self.message,
            'user_id': self.user_id,
            'risk_settings_id': self.risk_settings_id,
            'strategy_id': self.strategy_id,
            'position_id': self.position_id,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'threshold_percentage': self.threshold_percentage,
            'status': self.status,
            'display_status': self.display_status,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'acknowledged_by': self.acknowledged_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'resolution_notes': self.resolution_notes,
            'email_sent': self.email_sent,
            'sms_sent': self.sms_sent,
            'push_sent': self.push_sent,
            'tags': self.tags,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'is_acknowledged': self.is_acknowledged,
            'is_resolved': self.is_resolved,
            'is_critical': self.is_critical,
            'is_high': self.is_high,
            'severity_score': self.calculate_severity_score()
        }
        
        if include_details:
            data.update({
                'alert_data': self.alert_data,
                'recommendations': self.recommendations
            })
        
        return data


class RiskMetrics(Base):
    """
    Risk metrics model for tracking portfolio risk metrics
    """
    __tablename__ = "risk_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    
    # User and context
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    
    # Portfolio metrics
    portfolio_value = Column(Float, nullable=False)
    total_exposure = Column(Float, nullable=False)
    net_exposure = Column(Float, nullable=False)
    leverage_ratio = Column(Float, nullable=False)
    
    # Risk metrics
    var_1day = Column(Float, nullable=True)  # Value at Risk 1 day
    var_5day = Column(Float, nullable=True)  # Value at Risk 5 days
    var_30day = Column(Float, nullable=True)  # Value at Risk 30 days
    expected_shortfall = Column(Float, nullable=True)
    
    # Drawdown metrics
    current_drawdown = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    drawdown_duration = Column(Integer, nullable=False)  # Days in current drawdown
    
    # Volatility metrics
    volatility_10day = Column(Float, nullable=True)
    volatility_30day = Column(Float, nullable=True)
    volatility_90day = Column(Float, nullable=True)
    
    # Correlation metrics
    avg_correlation = Column(Float, nullable=True)
    max_correlation = Column(Float, nullable=True)
    correlation_risk_score = Column(Float, nullable=True)
    
    # Concentration metrics
    sector_concentration = Column(JSON, nullable=True)
    symbol_concentration = Column(JSON, nullable=True)
    concentration_risk_score = Column(Float, nullable=True)
    
    # Performance metrics
    daily_pnl = Column(Float, nullable=False)
    weekly_pnl = Column(Float, nullable=True)
    monthly_pnl = Column(Float, nullable=True)
    ytd_pnl = Column(Float, nullable=True)
    
    # Risk scores
    overall_risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False, index=True)
    
    # Metadata
    metrics_data = Column(JSON, nullable=True)  # Additional metrics
    calculation_method = Column(String(50), nullable=True)
    
    # Timestamps
    calculated_at = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    strategy = relationship("Strategy")
    
    def __repr__(self):
        return f"<RiskMetrics(id={self.id}, user_id={self.user_id}, risk_score={self.overall_risk_score}, calculated_at={self.calculated_at})>"
    
    @property
    def is_high_risk(self) -> bool:
        """Check if risk level is high"""
        return self.risk_level in [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value]
    
    @property
    def is_low_risk(self) -> bool:
        """Check if risk level is low"""
        return self.risk_level == RiskLevel.LOW.value
    
    @property
    def display_risk_level(self) -> str:
        """Get display risk level name"""
        level_map = {
            'LOW': 'Low',
            'MEDIUM': 'Medium',
            'HIGH': 'High',
            'CRITICAL': 'Critical'
        }
        return level_map.get(self.risk_level, self.risk_level)
    
    def calculate_risk_level(self) -> str:
        """Calculate risk level based on risk score"""
        if self.overall_risk_score >= 80:
            return RiskLevel.CRITICAL.value
        elif self.overall_risk_score >= 60:
            return RiskLevel.HIGH.value
        elif self.overall_risk_score >= 40:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value
    
    def calculate_overall_risk_score(self) -> float:
        """Calculate overall risk score"""
        # Weight different risk factors
        weights = {
            'drawdown': 0.25,
            'leverage': 0.20,
            'volatility': 0.15,
            'correlation': 0.15,
            'concentration': 0.15,
            'var': 0.10
        }
        
        # Normalize individual scores (0-100)
        drawdown_score = min(100, abs(self.current_drawdown) * 5) if self.current_drawdown else 0
        leverage_score = min(100, (self.leverage_ratio - 1) * 50) if self.leverage_ratio > 1 else 0
        volatility_score = min(100, (self.volatility_30day or 0) * 2)
        correlation_score = min(100, (self.avg_correlation or 0) * 100)
        concentration_score = min(100, (self.concentration_risk_score or 0))
        var_score = min(100, abs(self.var_1day or 0) / (self.portfolio_value or 1) * 100)
        
        # Calculate weighted average
        overall_score = (
            drawdown_score * weights['drawdown'] +
            leverage_score * weights['leverage'] +
            volatility_score * weights['volatility'] +
            correlation_score * weights['correlation'] +
            concentration_score * weights['concentration'] +
            var_score * weights['var']
        )
        
        return min(100, overall_score)
    
    def to_dict(self) -> dict:
        """Convert risk metrics to dictionary"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'user_id': self.user_id,
            'strategy_id': self.strategy_id,
            'portfolio_value': self.portfolio_value,
            'total_exposure': self.total_exposure,
            'net_exposure': self.net_exposure,
            'leverage_ratio': self.leverage_ratio,
            'var_1day': self.var_1day,
            'var_5day': self.var_5day,
            'var_30day': self.var_30day,
            'expected_shortfall': self.expected_shortfall,
            'current_drawdown': self.current_drawdown,
            'max_drawdown': self.max_drawdown,
            'drawdown_duration': self.drawdown_duration,
            'volatility_10day': self.volatility_10day,
            'volatility_30day': self.volatility_30day,
            'volatility_90day': self.volatility_90day,
            'avg_correlation': self.avg_correlation,
            'max_correlation': self.max_correlation,
            'correlation_risk_score': self.correlation_risk_score,
            'sector_concentration': self.sector_concentration,
            'symbol_concentration': self.symbol_concentration,
            'concentration_risk_score': self.concentration_risk_score,
            'daily_pnl': self.daily_pnl,
            'weekly_pnl': self.weekly_pnl,
            'monthly_pnl': self.monthly_pnl,
            'ytd_pnl': self.ytd_pnl,
            'overall_risk_score': self.overall_risk_score,
            'risk_level': self.risk_level,
            'display_risk_level': self.display_risk_level,
            'metrics_data': self.metrics_data,
            'calculation_method': self.calculation_method,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_high_risk': self.is_high_risk,
            'is_low_risk': self.is_low_risk
        }