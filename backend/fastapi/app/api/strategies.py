"""
VELOX-N8N Strategy API
REST API endpoints for strategy management and execution
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user_from_token
from app.models.user import User
from app.models.strategy import Strategy, StrategyPerformance
from app.services.strategy_service import StrategyService
from app.schemas.strategy import (
    StrategyCreate, StrategyUpdate, StrategyResponse, StrategyListRequest,
    StrategyPerformanceRequest, StrategyBacktestRequest, StrategyBacktestResponse,
    StrategyCloneRequest, StrategyConfigTemplate, StrategyOptimizationRequest,
    StrategyOptimizationResult, StrategyComparisonRequest, StrategyComparisonResult,
    StrategyAlert, StrategyStats, StrategyType, StrategyStatus, ExecutionMode
)
from app.core.logging import log_api_request, log_security_event

router = APIRouter(prefix="/strategies", tags=["strategies"])


def get_strategy_service(db: Session = Depends(get_db)) -> StrategyService:
    """Get strategy service instance"""
    return StrategyService(db)


@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Create a new trading strategy"""
    try:
        # Validate user permissions
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        # Create strategy
        strategy = await strategy_service.create_strategy(strategy_data, current_user.id)
        
        log_security_event(
            "strategy_created",
            user_id=current_user.id,
            ip_address=None,  # Will be set by middleware
            details={
                "strategy_id": strategy.id,
                "name": strategy.name,
                "type": strategy.strategy_type,
                "symbols": strategy.symbols
            }
        )
        
        return StrategyResponse.from_orm(strategy)
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "strategy_creation_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create strategy"
        )


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: int,
    strategy_update: StrategyUpdate,
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Update an existing strategy"""
    try:
        # Update strategy
        strategy = await strategy_service.update_strategy(strategy_id, strategy_update, current_user.id)
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found or not updatable"
            )
        
        log_security_event(
            "strategy_updated",
            user_id=current_user.id,
            ip_address=None,
            details={
                "strategy_id": strategy_id,
                "updates": strategy_update.dict(exclude_unset=True)
            }
        )
        
        return StrategyResponse.from_orm(strategy)
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "strategy_update_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update strategy"
        )


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Delete a strategy"""
    try:
        # Delete strategy
        success = await strategy_service.delete_strategy(strategy_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found or not deletable"
            )
        
        log_security_event(
            "strategy_deleted",
            user_id=current_user.id,
            ip_address=None,
            details={"strategy_id": strategy_id}
        )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "strategy_deletion_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete strategy"
        )


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Get strategy by ID"""
    try:
        strategy = await strategy_service.get_strategy(strategy_id, current_user.id)
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )
        
        return StrategyResponse.from_orm(strategy)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get strategy"
        )


@router.get("/", response_model=dict)
async def get_strategies(
    strategy_type: Optional[StrategyType] = Query(None, description="Filter by strategy type"),
    status: Optional[StrategyStatus] = Query(None, description="Filter by status"),
    execution_mode: Optional[ExecutionMode] = Query(None, description="Filter by execution mode"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    created_by: Optional[int] = Query(None, description="Filter by creator ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Get user strategies with pagination"""
    try:
        request = StrategyListRequest(
            strategy_type=strategy_type,
            status=status,
            execution_mode=execution_mode,
            symbol=symbol,
            created_by=created_by,
            page=page,
            per_page=per_page
        )
        
        strategies, total = await strategy_service.get_strategies(current_user.id, request)
        
        return {
            "strategies": [StrategyResponse.from_orm(strategy) for strategy in strategies],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get strategies"
        )


@router.post("/{strategy_id}/start", response_model=StrategyResponse)
async def start_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Start a strategy"""
    try:
        # Start strategy
        strategy = await strategy_service.start_strategy(strategy_id, current_user.id)
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found or not startable"
            )
        
        log_security_event(
            "strategy_started",
            user_id=current_user.id,
            ip_address=None,
            details={
                "strategy_id": strategy_id,
                "name": strategy.name,
                "execution_mode": strategy.execution_mode
            }
        )
        
        return StrategyResponse.from_orm(strategy)
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "strategy_start_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start strategy"
        )


@router.post("/{strategy_id}/stop", response_model=StrategyResponse)
async def stop_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Stop a strategy"""
    try:
        # Stop strategy
        strategy = await strategy_service.stop_strategy(strategy_id, current_user.id)
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found or not stoppable"
            )
        
        log_security_event(
            "strategy_stopped",
            user_id=current_user.id,
            ip_address=None,
            details={
                "strategy_id": strategy_id,
                "name": strategy.name
            }
        )
        
        return StrategyResponse.from_orm(strategy)
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "strategy_stop_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop strategy"
        )


@router.post("/{strategy_id}/clone", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def clone_strategy(
    strategy_id: int,
    clone_request: StrategyCloneRequest,
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Clone a strategy"""
    try:
        # Clone strategy
        cloned_strategy = await strategy_service.clone_strategy(strategy_id, clone_request, current_user.id)
        
        if not cloned_strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found or not clonable"
            )
        
        log_security_event(
            "strategy_cloned",
            user_id=current_user.id,
            ip_address=None,
            details={
                "original_strategy_id": strategy_id,
                "cloned_strategy_id": cloned_strategy.id,
                "original_name": cloned_strategy.name,
                "cloned_name": clone_request.name
            }
        )
        
        return StrategyResponse.from_orm(cloned_strategy)
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "strategy_clone_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clone strategy"
        )


@router.post("/{strategy_id}/backtest", response_model=StrategyBacktestResponse, status_code=status.HTTP_201_CREATED)
async def backtest_strategy(
    strategy_id: int,
    backtest_request: StrategyBacktestRequest,
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Backtest a strategy"""
    try:
        # Backtest strategy
        backtest_result = await strategy_service.backtest_strategy(strategy_id, backtest_request, current_user.id)
        
        if not backtest_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found or not backtestable"
            )
        
        log_security_event(
            "strategy_backtested",
            user_id=current_user.id,
            ip_address=None,
            details={
                "strategy_id": strategy_id,
                "backtest_id": backtest_result.backtest_id,
                "return_percentage": backtest_result.return_percentage,
                "sharpe_ratio": backtest_result.sharpe_ratio
            }
        )
        
        return backtest_result
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "strategy_backtest_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to backtest strategy"
        )


@router.get("/{strategy_id}/performance", response_model=dict)
async def get_strategy_performance(
    strategy_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Get strategy performance with pagination"""
    try:
        request = StrategyPerformanceRequest(
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )
        
        performance_records, total = await strategy_service.get_strategy_performance(strategy_id, request, current_user.id)
        
        return {
            "performance": [record.to_dict() for record in performance_records],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get strategy performance"
        )


@router.get("/templates", response_model=List[StrategyConfigTemplate])
async def get_strategy_templates(
    strategy_type: Optional[StrategyType] = Query(None, description="Filter by strategy type"),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Get strategy configuration templates"""
    try:
        # This would typically come from a template service
        # For now, return mock templates
        templates = [
            StrategyConfigTemplate(
                strategy_type=StrategyType.TREND_FOLLOWING,
                name="Simple Moving Average Crossover",
                description="A basic trend following strategy using moving average crossovers",
                default_config={
                    "fast_period": 10,
                    "slow_period": 20,
                    "signal_period": 5
                },
                default_parameters={
                    "risk_per_trade": 2.0,
                    "stop_loss_atr_multiplier": 2.0,
                    "take_profit_risk_reward_ratio": 2.0
                },
                required_config=["fast_period", "slow_period", "signal_period"],
                optional_config=["volume_filter", "timeframe"],
                config_schema={
                    "fast_period": {"type": "integer", "min": 5, "max": 50},
                    "slow_period": {"type": "integer", "min": 10, "max": 100},
                    "signal_period": {"type": "integer", "min": 1, "max": 20}
                },
                parameter_schema={
                    "risk_per_trade": {"type": "float", "min": 0.1, "max": 10.0},
                    "stop_loss_atr_multiplier": {"type": "float", "min": 1.0, "max": 5.0},
                    "take_profit_risk_reward_ratio": {"type": "float", "min": 1.0, "max": 5.0}
                }
            ),
            StrategyConfigTemplate(
                strategy_type=StrategyType.MEAN_REVERSION,
                name="Bollinger Bands Mean Reversion",
                description="A mean reversion strategy using Bollinger Bands",
                default_config={
                    "period": 20,
                    "std_dev": 2.0
                },
                default_parameters={
                    "risk_per_trade": 2.0,
                    "stop_loss_atr_multiplier": 2.0,
                    "take_profit_risk_reward_ratio": 2.0
                },
                required_config=["period", "std_dev"],
                optional_config=["volume_filter", "timeframe"],
                config_schema={
                    "period": {"type": "integer", "min": 5, "max": 50},
                    "std_dev": {"type": "float", "min": 0.5, "max": 5.0}
                },
                parameter_schema={
                    "risk_per_trade": {"type": "float", "min": 0.1, "max": 10.0},
                    "stop_loss_atr_multiplier": {"type": "float", "min": 1.0, "max": 5.0},
                    "take_profit_risk_reward_ratio": {"type": "float", "min": 1.0, "max": 5.0}
                }
            ),
            StrategyConfigTemplate(
                strategy_type=StrategyType.MOMENTUM,
                name="RSI Momentum",
                description="A momentum strategy using RSI indicator",
                default_config={
                    "rsi_period": 14,
                    "rsi_overbought": 70,
                    "rsi_oversold": 30
                },
                default_parameters={
                    "risk_per_trade": 2.0,
                    "stop_loss_atr_multiplier": 2.0,
                    "take_profit_risk_reward_ratio": 2.0
                },
                required_config=["rsi_period", "rsi_overbought", "rsi_oversold"],
                optional_config=["volume_filter", "timeframe"],
                config_schema={
                    "rsi_period": {"type": "integer", "min": 5, "max": 50},
                    "rsi_overbought": {"type": "integer", "min": 50, "max": 90},
                    "rsi_oversold": {"type": "integer", "min": 10, "max": 50}
                },
                parameter_schema={
                    "risk_per_trade": {"type": "float", "min": 0.1, "max": 10.0},
                    "stop_loss_atr_multiplier": {"type": "float", "min": 1.0, "max": 5.0},
                    "take_profit_risk_reward_ratio": {"type": "float", "min": 1.0, "max": 5.0}
                }
            )
        ]
        
        # Filter by strategy type if specified
        if strategy_type:
            templates = [t for t in templates if t.strategy_type == strategy_type]
        
        return templates
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get strategy templates"
        )


@router.get("/stats", response_model=StrategyStats)
async def get_strategy_stats(
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Get strategy statistics"""
    try:
        stats = await strategy_service.get_strategy_stats(current_user.id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy stats not found"
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get strategy stats"
        )


@router.post("/{strategy_id}/alerts", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_strategy_alert(
    strategy_id: int,
    alert_data: StrategyAlert,
    current_user: User = Depends(get_current_user_from_token),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """Create a strategy alert"""
    try:
        # Verify strategy ownership
        strategy = await strategy_service.get_strategy(strategy_id, current_user.id)
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )
        
        # Create alert (simplified - would use alert service)
        alert_id = f"ALERT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        log_security_event(
            "strategy_alert_created",
            user_id=current_user.id,
            ip_address=None,
            details={
                "strategy_id": strategy_id,
                "alert_id": alert_id,
                "alert_type": alert_data.alert_type,
                "condition": alert_data.condition,
                "threshold": alert_data.threshold
            }
        )
        
        return {
            "alert_id": alert_id,
            "message": "Strategy alert created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "strategy_alert_creation_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create strategy alert"
        )


@router.get("/health")
async def strategy_health_check():
    """Strategy service health check"""
    return {
        "status": "healthy",
        "service": "strategies",
        "timestamp": datetime.utcnow().isoformat()
    }