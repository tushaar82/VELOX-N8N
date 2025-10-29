"""
VELOX-N8N Strategy Model
Database model for trading strategy configuration and management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import json

from app.core.database import Base


class Strategy(Base):
    """
    Strategy model for trading strategy configuration
    """
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    strategy_type = Column(String(50), nullable=False, index=True)  # trend_following, mean_reversion, momentum, etc.
    
    # Strategy configuration
    config = Column(JSON, nullable=False)  # Strategy-specific configuration
    parameters = Column(JSON, nullable=True)  # Strategy parameters
    
    # Status and execution
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    is_enabled = Column(Boolean, default=True, nullable=False)
    status = Column(String(20), default='draft', nullable=False, index=True)  # draft, testing, active, paused, archived
    
    # Risk management
    risk_settings = Column(JSON, nullable=True)  # Risk management settings
    max_position_size = Column(Float, nullable=True)
    risk_per_trade = Column(Float, nullable=True)
    max_daily_loss = Column(Float, nullable=True)
    
    # Performance tracking
    total_trades = Column(Integer, default=0, nullable=False)
    winning_trades = Column(Integer, default=0, nullable=False)
    losing_trades = Column(Integer, default=0, nullable=False)
    total_pnl = Column(Float, default=0.0, nullable=False)
    max_drawdown = Column(Float, default=0.0, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    
    # Execution settings
    symbols = Column(JSON, nullable=False)  # List of symbols to trade
    timeframes = Column(JSON, nullable=False)  # List of timeframes
    execution_mode = Column(String(20), default='paper', nullable=False)  # paper, live
    
    # N8N integration
    n8n_workflow_id = Column(String(100), nullable=True, unique=True)
    n8n_workflow_config = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    last_executed = Column(TIMESTAMP(timezone=True), nullable=True)
    last_backtested = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Foreign keys
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="strategy", cascade="all, delete-orphan")
    performance_records = relationship("StrategyPerformance", back_populates="strategy", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name='{self.name}', type='{self.strategy_type}', status='{self.status}')>"
    
    @property
    def is_running(self) -> bool:
        """Check if strategy is currently running"""
        return self.is_active and self.is_enabled and self.status == 'active'
    
    @property
    def display_status(self) -> str:
        """Get display status name"""
        status_map = {
            'draft': 'Draft',
            'testing': 'Testing',
            'active': 'Active',
            'paused': 'Paused',
            'archived': 'Archived'
        }
        return status_map.get(self.status, self.status.capitalize())
    
    @property
    def display_type(self) -> str:
        """Get display strategy type name"""
        type_map = {
            'trend_following': 'Trend Following',
            'mean_reversion': 'Mean Reversion',
            'momentum': 'Momentum',
            'arbitrage': 'Arbitrage',
            'scalping': 'Scalping',
            'swing': 'Swing Trading',
            'position': 'Position Trading'
        }
        return type_map.get(self.strategy_type, self.strategy_type.replace('_', ' ').title())
    
    def calculate_win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100
    
    def calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        # This would need more detailed trade data
        # For now, return a placeholder
        return 1.0
    
    def update_performance(self, trade_pnl: float, is_win: bool):
        """Update strategy performance metrics"""
        self.total_trades += 1
        self.total_pnl += trade_pnl
        
        if is_win:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        self.win_rate = self.calculate_win_rate()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_performance: bool = True) -> dict:
        """Convert strategy to dictionary"""
        data = {
            'id': self.id,
            'uuid': str(self.uuid),
            'name': self.name,
            'description': self.description,
            'strategy_type': self.strategy_type,
            'display_type': self.display_type,
            'config': self.config,
            'parameters': self.parameters,
            'is_active': self.is_active,
            'is_enabled': self.is_enabled,
            'status': self.status,
            'display_status': self.display_status,
            'risk_settings': self.risk_settings,
            'max_position_size': self.max_position_size,
            'risk_per_trade': self.risk_per_trade,
            'max_daily_loss': self.max_daily_loss,
            'symbols': self.symbols,
            'timeframes': self.timeframes,
            'execution_mode': self.execution_mode,
            'n8n_workflow_id': self.n8n_workflow_id,
            'n8n_workflow_config': self.n8n_workflow_config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_executed': self.last_executed.isoformat() if self.last_executed else None,
            'last_backtested': self.last_backtested.isoformat() if self.last_backtested else None,
            'created_by': self.created_by,
            'is_running': self.is_running
        }
        
        if include_performance:
            data.update({
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'total_pnl': self.total_pnl,
                'max_drawdown': self.max_drawdown,
                'sharpe_ratio': self.sharpe_ratio,
                'win_rate': self.win_rate,
                'profit_factor': self.calculate_profit_factor()
            })
        
        return data
    
    def validate_config(self) -> tuple[bool, list]:
        """Validate strategy configuration"""
        errors = []
        
        # Check required fields
        if not self.name:
            errors.append("Strategy name is required")
        
        if not self.strategy_type:
            errors.append("Strategy type is required")
        
        if not self.config:
            errors.append("Strategy configuration is required")
        
        # Check symbols
        if not self.symbols or not isinstance(self.symbols, list):
            errors.append("At least one symbol is required")
        
        # Check timeframes
        if not self.timeframes or not isinstance(self.timeframes, list):
            errors.append("At least one timeframe is required")
        
        # Strategy-specific validation
        if self.strategy_type == 'trend_following':
            required_params = ['fast_period', 'slow_period', 'signal_period']
            for param in required_params:
                if not self.parameters or param not in self.parameters:
                    errors.append(f"Required parameter '{param}' missing for trend following strategy")
        
        elif self.strategy_type == 'mean_reversion':
            required_params = ['period', 'std_dev']
            for param in required_params:
                if not self.parameters or param not in self.parameters:
                    errors.append(f"Required parameter '{param}' missing for mean reversion strategy")
        
        elif self.strategy_type == 'momentum':
            required_params = ['rsi_period', 'rsi_overbought', 'rsi_oversold']
            for param in required_params:
                if not self.parameters or param not in self.parameters:
                    errors.append(f"Required parameter '{param}' missing for momentum strategy")
        
        return len(errors) == 0, errors
    
    def get_n8n_workflow_url(self) -> str:
        """Get N8N workflow URL"""
        if not self.n8n_workflow_id:
            return None
        
        return f"http://localhost:5678/workflow/{self.n8n_workflow_id}"
    
    def clone(self, new_name: str, created_by: int) -> 'Strategy':
        """Create a clone of this strategy"""
        cloned_strategy = Strategy(
            name=new_name,
            description=f"Clone of {self.name}",
            strategy_type=self.strategy_type,
            config=self.config.copy() if self.config else {},
            parameters=self.parameters.copy() if self.parameters else {},
            risk_settings=self.risk_settings.copy() if self.risk_settings else {},
            max_position_size=self.max_position_size,
            risk_per_trade=self.risk_per_trade,
            max_daily_loss=self.max_daily_loss,
            symbols=self.symbols.copy() if self.symbols else [],
            timeframes=self.timeframes.copy() if self.timeframes else [],
            execution_mode='paper',  # Always start cloned strategies in paper mode
            created_by=created_by
        )
        
        return cloned_strategy


class StrategyPerformance(Base):
    """
    Strategy performance tracking model
    """
    __tablename__ = "strategy_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    
    # Performance metrics
    date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    daily_pnl = Column(Float, default=0.0, nullable=False)
    cumulative_pnl = Column(Float, default=0.0, nullable=False)
    daily_trades = Column(Integer, default=0, nullable=False)
    cumulative_trades = Column(Integer, default=0, nullable=False)
    daily_wins = Column(Integer, default=0, nullable=False)
    cumulative_wins = Column(Integer, default=0, nullable=False)
    daily_losses = Column(Integer, default=0, nullable=False)
    cumulative_losses = Column(Integer, default=0, nullable=False)
    win_rate = Column(Float, default=0.0, nullable=False)
    max_drawdown = Column(Float, default=0.0, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    
    # Additional metrics
    equity_curve = Column(JSON, nullable=True)  # Daily equity values
    volatility = Column(Float, nullable=True)
    var_95 = Column(Float, nullable=True)  # Value at Risk 95%
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="performance_records")
    
    def __repr__(self):
        return f"<StrategyPerformance(id={self.id}, strategy_id={self.strategy_id}, date={self.date}, pnl={self.daily_pnl})>"
    
    def to_dict(self) -> dict:
        """Convert performance record to dictionary"""
        return {
            'id': self.id,
            'strategy_id': self.strategy_id,
            'date': self.date.isoformat() if self.date else None,
            'daily_pnl': self.daily_pnl,
            'cumulative_pnl': self.cumulative_pnl,
            'daily_trades': self.daily_trades,
            'cumulative_trades': self.cumulative_trades,
            'daily_wins': self.daily_wins,
            'cumulative_wins': self.cumulative_wins,
            'daily_losses': self.daily_losses,
            'cumulative_losses': self.cumulative_losses,
            'win_rate': self.win_rate,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'profit_factor': self.profit_factor,
            'equity_curve': self.equity_curve,
            'volatility': self.volatility,
            'var_95': self.var_95,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }