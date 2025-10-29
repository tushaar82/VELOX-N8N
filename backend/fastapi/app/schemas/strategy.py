"""
VELOX-N8N Strategy Schemas
Pydantic models for strategy API validation and serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.strategy import Strategy


class StrategyType(str, Enum):
    """Strategy type enumeration"""
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    ARBITRAGE = "arbitrage"
    SCALPING = "scalping"
    SWING = "swing"
    POSITION = "position"


class StrategyStatus(str, Enum):
    """Strategy status enumeration"""
    DRAFT = "draft"
    TESTING = "testing"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionMode(str, Enum):
    """Execution mode enumeration"""
    PAPER = "paper"
    LIVE = "live"


class StrategyCreate(BaseModel):
    """Strategy creation schema"""
    name: str = Field(..., min_length=3, max_length=100, description="Strategy name")
    description: Optional[str] = Field(None, max_length=500, description="Strategy description")
    strategy_type: StrategyType = Field(..., description="Strategy type")
    
    # Strategy configuration
    config: Dict[str, Any] = Field(..., description="Strategy configuration")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Strategy parameters")
    
    # Risk management
    risk_settings: Optional[Dict[str, Any]] = Field(None, description="Risk management settings")
    max_position_size: Optional[float] = Field(None, gt=0, description="Maximum position size")
    risk_per_trade: Optional[float] = Field(None, gt=0, le=10, description="Risk per trade in percentage")
    max_daily_loss: Optional[float] = Field(None, gt=0, description="Maximum daily loss")
    
    # Execution settings
    symbols: List[str] = Field(..., min_items=1, description="Trading symbols")
    timeframes: List[str] = Field(..., min_items=1, description="Trading timeframes")
    execution_mode: ExecutionMode = Field(ExecutionMode.PAPER, description="Execution mode")
    
    # N8N integration
    n8n_workflow_id: Optional[str] = Field(None, max_length=100, description="N8N workflow ID")
    n8n_workflow_config: Optional[Dict[str, Any]] = Field(None, description="N8N workflow configuration")
    
    @validator('symbols')
    def validate_symbols(cls, v):
        """Validate symbols list"""
        if not v or len(v) == 0:
            raise ValueError('At least one symbol is required')
        return v
    
    @validator('timeframes')
    def validate_timeframes(cls, v):
        """Validate timeframes list"""
        if not v or len(v) == 0:
            raise ValueError('At least one timeframe is required')
        return v
    
    @validator('config')
    def validate_config(cls, v, values):
        """Validate strategy configuration based on type"""
        strategy_type = values.get('strategy_type')
        
        if strategy_type == StrategyType.TREND_FOLLOWING:
            required_params = ['fast_period', 'slow_period', 'signal_period']
            for param in required_params:
                if param not in v:
                    raise ValueError(f'Required parameter "{param}" missing for trend following strategy')
        
        elif strategy_type == StrategyType.MEAN_REVERSION:
            required_params = ['period', 'std_dev']
            for param in required_params:
                if param not in v:
                    raise ValueError(f'Required parameter "{param}" missing for mean reversion strategy')
        
        elif strategy_type == StrategyType.MOMENTUM:
            required_params = ['rsi_period', 'rsi_overbought', 'rsi_oversold']
            for param in required_params:
                if param not in v:
                    raise ValueError(f'Required parameter "{param}" missing for momentum strategy')
        
        return v


class StrategyUpdate(BaseModel):
    """Strategy update schema"""
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Strategy name")
    description: Optional[str] = Field(None, max_length=500, description="Strategy description")
    config: Optional[Dict[str, Any]] = Field(None, description="Strategy configuration")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Strategy parameters")
    risk_settings: Optional[Dict[str, Any]] = Field(None, description="Risk management settings")
    max_position_size: Optional[float] = Field(None, gt=0, description="Maximum position size")
    risk_per_trade: Optional[float] = Field(None, gt=0, le=10, description="Risk per trade in percentage")
    max_daily_loss: Optional[float] = Field(None, gt=0, description="Maximum daily loss")
    symbols: Optional[List[str]] = Field(None, min_items=1, description="Trading symbols")
    timeframes: Optional[List[str]] = Field(None, min_items=1, description="Trading timeframes")
    execution_mode: Optional[ExecutionMode] = Field(None, description="Execution mode")
    n8n_workflow_id: Optional[str] = Field(None, max_length=100, description="N8N workflow ID")
    n8n_workflow_config: Optional[Dict[str, Any]] = Field(None, description="N8N workflow configuration")


class StrategyResponse(BaseModel):
    """Strategy response schema"""
    id: int
    uuid: str
    name: str
    description: Optional[str]
    strategy_type: str
    display_type: str
    config: Dict[str, Any]
    parameters: Optional[Dict[str, Any]]
    is_active: bool
    is_enabled: bool
    status: str
    display_status: str
    risk_settings: Optional[Dict[str, Any]]
    max_position_size: Optional[float]
    risk_per_trade: Optional[float]
    max_daily_loss: Optional[float]
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: Optional[float]
    win_rate: Optional[float]
    profit_factor: float
    symbols: List[str]
    timeframes: List[str]
    execution_mode: str
    n8n_workflow_id: Optional[str]
    n8n_workflow_config: Optional[Dict[str, Any]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_executed: Optional[datetime]
    last_backtested: Optional[datetime]
    created_by: int
    is_running: bool
    
    class Config:
        from_attributes = True


class StrategyListRequest(BaseModel):
    """Strategy list request schema"""
    strategy_type: Optional[StrategyType] = Field(None, description="Filter by strategy type")
    status: Optional[StrategyStatus] = Field(None, description="Filter by status")
    execution_mode: Optional[ExecutionMode] = Field(None, description="Filter by execution mode")
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    created_by: Optional[int] = Field(None, description="Filter by creator ID")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class StrategyPerformanceRequest(BaseModel):
    """Strategy performance request schema"""
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class StrategyBacktestRequest(BaseModel):
    """Strategy backtest request schema"""
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    initial_capital: float = Field(..., gt=0, description="Initial capital for backtest")
    commission: float = Field(0.1, ge=0, le=1, description="Commission rate (percentage)")
    slippage: float = Field(0.05, ge=0, le=1, description="Slippage rate (percentage)")
    
    # Backtest settings
    symbols: Optional[List[str]] = Field(None, description="Override symbols for backtest")
    timeframes: Optional[List[str]] = Field(None, description="Override timeframes for backtest")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Override parameters for backtest")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date"""
        start_date = values.get('start_date')
        if start_date and v <= start_date:
            raise ValueError('End date must be after start date')
        return v


class StrategyBacktestResponse(BaseModel):
    """Strategy backtest response schema"""
    backtest_id: str
    strategy_id: int
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    return_percentage: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    max_drawdown: float
    max_drawdown_percentage: float
    sharpe_ratio: Optional[float]
    sortino_ratio: Optional[float]
    calmar_ratio: Optional[float]
    average_trade_duration: float
    best_trade: float
    worst_trade: float
    commission_paid: float
    slippage_cost: float
    net_profit: float
    equity_curve: List[Dict[str, Any]]
    trade_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StrategyCloneRequest(BaseModel):
    """Strategy clone request schema"""
    name: str = Field(..., min_length=3, max_length=100, description="New strategy name")
    description: Optional[str] = Field(None, max_length=500, description="New strategy description")
    execution_mode: Optional[ExecutionMode] = Field(None, description="New execution mode")


class StrategyConfigTemplate(BaseModel):
    """Strategy configuration template schema"""
    strategy_type: StrategyType
    name: str
    description: str
    default_config: Dict[str, Any]
    default_parameters: Dict[str, Any]
    required_config: List[str]
    optional_config: List[str]
    config_schema: Dict[str, Any]
    parameter_schema: Dict[str, Any]


class StrategyOptimizationRequest(BaseModel):
    """Strategy optimization request schema"""
    optimization_target: str = Field(..., description="Optimization target (sharpe, profit_factor, return, etc.)")
    parameter_ranges: Dict[str, Dict[str, float]] = Field(..., description="Parameter ranges to optimize")
    optimization_method: str = Field("grid_search", description="Optimization method")
    max_iterations: int = Field(100, ge=1, le=1000, description="Maximum optimization iterations")
    
    # Backtest settings for optimization
    start_date: datetime = Field(..., description="Optimization start date")
    end_date: datetime = Field(..., description="Optimization end date")
    initial_capital: float = Field(..., gt=0, description="Initial capital for optimization")
    commission: float = Field(0.1, ge=0, le=1, description="Commission rate (percentage)")
    slippage: float = Field(0.05, ge=0, le=1, description="Slippage rate (percentage)")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date"""
        start_date = values.get('start_date')
        if start_date and v <= start_date:
            raise ValueError('End date must be after start date')
        return v


class StrategyOptimizationResult(BaseModel):
    """Strategy optimization result schema"""
    optimization_id: str
    strategy_id: int
    optimization_target: str
    best_parameters: Dict[str, Any]
    best_score: float
    optimization_results: List[Dict[str, Any]]
    parameter_importance: Dict[str, float]
    optimization_progress: float
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StrategyComparisonRequest(BaseModel):
    """Strategy comparison request schema"""
    strategy_ids: List[int] = Field(..., min_items=2, description="Strategy IDs to compare")
    start_date: datetime = Field(..., description="Comparison start date")
    end_date: datetime = Field(..., description="Comparison end date")
    metrics: List[str] = Field(["total_return", "sharpe_ratio", "max_drawdown"], description="Metrics to compare")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date"""
        start_date = values.get('start_date')
        if start_date and v <= start_date:
            raise ValueError('End date must be after start date')
        return v


class StrategyComparisonResult(BaseModel):
    """Strategy comparison result schema"""
    comparison_id: str
    strategies: List[Dict[str, Any]]
    comparison_metrics: Dict[str, List[float]]
    ranking: List[Dict[str, Any]]
    statistical_significance: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StrategyAlert(BaseModel):
    """Strategy alert schema"""
    strategy_id: int
    alert_type: str
    condition: str
    threshold: float
    is_active: bool = Field(True, description="Alert active status")
    notification_channels: List[str] = Field(..., description="Notification channels")
    expires_at: Optional[datetime] = Field(None, description="Alert expiration")


class StrategyStats(BaseModel):
    """Strategy statistics schema"""
    total_strategies: int
    active_strategies: int
    paused_strategies: int
    draft_strategies: int
    archived_strategies: int
    paper_trading_strategies: int
    live_trading_strategies: int
    strategies_by_type: Dict[str, int]
    strategies_by_status: Dict[str, int]
    total_trades: int
    total_pnl: float
    average_return: float
    best_performing_strategy: Optional[Dict[str, Any]]
    worst_performing_strategy: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True