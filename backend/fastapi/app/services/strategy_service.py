"""
VELOX-N8N Strategy Service
Business logic for strategy management and execution
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta
import logging
import uuid
import asyncio
import json

from app.core.database import get_db
from app.models.strategy import Strategy, StrategyPerformance
from app.models.user import User
from app.models.trade import Trade, Position
from app.schemas.strategy import (
    StrategyCreate, StrategyUpdate, StrategyResponse, StrategyListRequest,
    StrategyPerformanceRequest, StrategyBacktestRequest, StrategyBacktestResponse,
    StrategyCloneRequest, StrategyConfigTemplate, StrategyOptimizationRequest,
    StrategyOptimizationResult, StrategyComparisonRequest, StrategyComparisonResult,
    StrategyAlert, StrategyStats, StrategyType, StrategyStatus, ExecutionMode
)
from app.core.logging import log_trading_event, log_error
from app.core.security import generate_api_key

logger = logging.getLogger(__name__)


class StrategyService:
    """Service for strategy management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_strategy(self, strategy_data: StrategyCreate, user_id: int) -> Strategy:
        """Create a new trading strategy"""
        try:
            # Validate strategy configuration
            strategy = Strategy(
                name=strategy_data.name,
                description=strategy_data.description,
                strategy_type=strategy_data.strategy_type.value,
                config=strategy_data.config,
                parameters=strategy_data.parameters,
                risk_settings=strategy_data.risk_settings,
                max_position_size=strategy_data.max_position_size,
                risk_per_trade=strategy_data.risk_per_trade,
                max_daily_loss=strategy_data.max_daily_loss,
                symbols=strategy_data.symbols,
                timeframes=strategy_data.timeframes,
                execution_mode=strategy_data.execution_mode.value,
                n8n_workflow_id=strategy_data.n8n_workflow_id,
                n8n_workflow_config=strategy_data.n8n_workflow_config,
                created_by=user_id,
                status=StrategyStatus.DRAFT.value,
                is_active=False,
                is_enabled=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Validate strategy
            is_valid, errors = strategy.validate_config()
            if not is_valid:
                raise ValueError(f"Strategy validation failed: {', '.join(errors)}")
            
            # Save to database
            self.db.add(strategy)
            self.db.commit()
            self.db.refresh(strategy)
            
            # Log trading event
            log_trading_event(
                "strategy_created",
                {
                    "strategy_id": strategy.id,
                    "name": strategy.name,
                    "type": strategy.strategy_type,
                    "symbols": strategy.symbols
                },
                user_id=user_id
            )
            
            logger.info(f"Created strategy {strategy.name} for user {user_id}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error creating strategy: {e}")
            self.db.rollback()
            raise
    
    async def update_strategy(self, strategy_id: int, strategy_update: StrategyUpdate, user_id: int) -> Optional[Strategy]:
        """Update an existing strategy"""
        try:
            # Get strategy
            strategy = self.db.query(Strategy).filter(
                and_(
                    Strategy.id == strategy_id,
                    Strategy.created_by == user_id
                )
            ).first()
            
            if not strategy:
                logger.warning(f"Strategy {strategy_id} not found or not updatable")
                return None
            
            # Check if strategy is active (restrict updates)
            if strategy.is_active:
                raise ValueError("Cannot update active strategy. Stop it first.")
            
            # Update strategy fields
            if strategy_update.name is not None:
                strategy.name = strategy_update.name
            
            if strategy_update.description is not None:
                strategy.description = strategy_update.description
            
            if strategy_update.config is not None:
                strategy.config = strategy_update.config
            
            if strategy_update.parameters is not None:
                strategy.parameters = strategy_update.parameters
            
            if strategy_update.risk_settings is not None:
                strategy.risk_settings = strategy_update.risk_settings
            
            if strategy_update.max_position_size is not None:
                strategy.max_position_size = strategy_update.max_position_size
            
            if strategy_update.risk_per_trade is not None:
                strategy.risk_per_trade = strategy_update.risk_per_trade
            
            if strategy_update.max_daily_loss is not None:
                strategy.max_daily_loss = strategy_update.max_daily_loss
            
            if strategy_update.symbols is not None:
                strategy.symbols = strategy_update.symbols
            
            if strategy_update.timeframes is not None:
                strategy.timeframes = strategy_update.timeframes
            
            if strategy_update.execution_mode is not None:
                strategy.execution_mode = strategy_update.execution_mode.value
            
            if strategy_update.n8n_workflow_id is not None:
                strategy.n8n_workflow_id = strategy_update.n8n_workflow_id
            
            if strategy_update.n8n_workflow_config is not None:
                strategy.n8n_workflow_config = strategy_update.n8n_workflow_config
            
            strategy.updated_at = datetime.utcnow()
            
            # Validate updated strategy
            is_valid, errors = strategy.validate_config()
            if not is_valid:
                raise ValueError(f"Strategy validation failed: {', '.join(errors)}")
            
            self.db.commit()
            self.db.refresh(strategy)
            
            # Log trading event
            log_trading_event(
                "strategy_updated",
                {
                    "strategy_id": strategy.id,
                    "name": strategy.name,
                    "updates": strategy_update.dict(exclude_unset=True)
                },
                user_id=user_id
            )
            
            logger.info(f"Updated strategy {strategy.name}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error updating strategy: {e}")
            self.db.rollback()
            raise
    
    async def delete_strategy(self, strategy_id: int, user_id: int) -> bool:
        """Delete a strategy"""
        try:
            # Get strategy
            strategy = self.db.query(Strategy).filter(
                and_(
                    Strategy.id == strategy_id,
                    Strategy.created_by == user_id
                )
            ).first()
            
            if not strategy:
                logger.warning(f"Strategy {strategy_id} not found")
                return False
            
            # Check if strategy is active
            if strategy.is_active:
                raise ValueError("Cannot delete active strategy. Stop it first.")
            
            # Delete strategy
            self.db.delete(strategy)
            self.db.commit()
            
            # Log trading event
            log_trading_event(
                "strategy_deleted",
                {
                    "strategy_id": strategy.id,
                    "name": strategy.name,
                    "type": strategy.strategy_type
                },
                user_id=user_id
            )
            
            logger.info(f"Deleted strategy {strategy.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting strategy: {e}")
            self.db.rollback()
            return False
    
    async def get_strategy(self, strategy_id: int, user_id: int) -> Optional[Strategy]:
        """Get strategy by ID"""
        try:
            return self.db.query(Strategy).filter(
                and_(
                    Strategy.id == strategy_id,
                    Strategy.created_by == user_id
                )
            ).first()
        except Exception as e:
            logger.error(f"Error getting strategy {strategy_id}: {e}")
            return None
    
    async def get_strategies(self, user_id: int, request: StrategyListRequest) -> Tuple[List[Strategy], int]:
        """Get user strategies with pagination"""
        try:
            query = self.db.query(Strategy).filter(Strategy.created_by == user_id)
            
            # Apply filters
            if request.strategy_type:
                query = query.filter(Strategy.strategy_type == request.strategy_type.value)
            
            if request.status:
                query = query.filter(Strategy.status == request.status.value)
            
            if request.execution_mode:
                query = query.filter(Strategy.execution_mode == request.execution_mode.value)
            
            if request.symbol:
                # Filter strategies that include this symbol
                query = query.filter(Strategy.symbols.contains([request.symbol]))
            
            if request.created_by:
                query = query.filter(Strategy.created_by == request.created_by)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (request.page - 1) * request.per_page
            strategies = query.order_by(desc(Strategy.updated_at)).offset(offset).limit(request.per_page).all()
            
            return strategies, total
            
        except Exception as e:
            logger.error(f"Error getting strategies: {e}")
            return [], 0
    
    async def start_strategy(self, strategy_id: int, user_id: int) -> Optional[Strategy]:
        """Start a strategy"""
        try:
            # Get strategy
            strategy = await self.get_strategy(strategy_id, user_id)
            
            if not strategy:
                logger.warning(f"Strategy {strategy_id} not found")
                return None
            
            # Check if strategy is ready to start
            if strategy.status != StrategyStatus.DRAFT.value and strategy.status != StrategyStatus.TESTING.value:
                raise ValueError("Only draft or testing strategies can be started")
            
            # Start strategy
            strategy.is_active = True
            strategy.status = StrategyStatus.ACTIVE.value
            strategy.last_executed = datetime.utcnow()
            strategy.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(strategy)
            
            # Log trading event
            log_trading_event(
                "strategy_started",
                {
                    "strategy_id": strategy.id,
                    "name": strategy.name,
                    "type": strategy.strategy_type,
                    "execution_mode": strategy.execution_mode
                },
                user_id=user_id
            )
            
            # Start strategy execution (async)
            asyncio.create_task(self._execute_strategy(strategy))
            
            logger.info(f"Started strategy {strategy.name}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error starting strategy: {e}")
            self.db.rollback()
            raise
    
    async def stop_strategy(self, strategy_id: int, user_id: int) -> Optional[Strategy]:
        """Stop a strategy"""
        try:
            # Get strategy
            strategy = await self.get_strategy(strategy_id, user_id)
            
            if not strategy:
                logger.warning(f"Strategy {strategy_id} not found")
                return None
            
            # Stop strategy
            strategy.is_active = False
            strategy.status = StrategyStatus.PAUSED.value
            strategy.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(strategy)
            
            # Log trading event
            log_trading_event(
                "strategy_stopped",
                {
                    "strategy_id": strategy.id,
                    "name": strategy.name,
                    "type": strategy.strategy_type
                },
                user_id=user_id
            )
            
            logger.info(f"Stopped strategy {strategy.name}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error stopping strategy: {e}")
            self.db.rollback()
            raise
    
    async def clone_strategy(self, strategy_id: int, clone_request: StrategyCloneRequest, user_id: int) -> Optional[Strategy]:
        """Clone a strategy"""
        try:
            # Get original strategy
            original_strategy = await self.get_strategy(strategy_id, user_id)
            
            if not original_strategy:
                logger.warning(f"Strategy {strategy_id} not found")
                return None
            
            # Create cloned strategy
            cloned_strategy = original_strategy.clone(
                clone_request.name,
                user_id
            )
            
            # Update cloned strategy with request data
            if clone_request.description is not None:
                cloned_strategy.description = clone_request.description
            
            if clone_request.execution_mode is not None:
                cloned_strategy.execution_mode = clone_request.execution_mode.value
            
            # Save to database
            self.db.add(cloned_strategy)
            self.db.commit()
            self.db.refresh(cloned_strategy)
            
            # Log trading event
            log_trading_event(
                "strategy_cloned",
                {
                    "original_strategy_id": original_strategy.id,
                    "cloned_strategy_id": cloned_strategy.id,
                    "original_name": original_strategy.name,
                    "cloned_name": cloned_strategy.name
                },
                user_id=user_id
            )
            
            logger.info(f"Cloned strategy {original_strategy.name} to {cloned_strategy.name}")
            return cloned_strategy
            
        except Exception as e:
            logger.error(f"Error cloning strategy: {e}")
            self.db.rollback()
            raise
    
    async def backtest_strategy(self, strategy_id: int, backtest_request: StrategyBacktestRequest, user_id: int) -> Optional[StrategyBacktestResponse]:
        """Backtest a strategy"""
        try:
            # Get strategy
            strategy = await self.get_strategy(strategy_id, user_id)
            
            if not strategy:
                logger.warning(f"Strategy {strategy_id} not found")
                return None
            
            # Generate backtest ID
            backtest_id = f"BT_{uuid.uuid4().hex[:12].upper()}"
            
            # Run backtest (async)
            result = await self._run_backtest(strategy, backtest_request)
            
            # Create backtest response
            backtest_response = StrategyBacktestResponse(
                backtest_id=backtest_id,
                strategy_id=strategy.id,
                start_date=backtest_request.start_date,
                end_date=backtest_request.end_date,
                initial_capital=backtest_request.initial_capital,
                final_capital=result["final_capital"],
                total_return=result["total_return"],
                return_percentage=result["return_percentage"],
                total_trades=result["total_trades"],
                winning_trades=result["winning_trades"],
                losing_trades=result["losing_trades"],
                win_rate=result["win_rate"],
                gross_profit=result["gross_profit"],
                gross_loss=result["gross_loss"],
                profit_factor=result["profit_factor"],
                max_drawdown=result["max_drawdown"],
                max_drawdown_percentage=result["max_drawdown_percentage"],
                sharpe_ratio=result["sharpe_ratio"],
                sortino_ratio=result["sortino_ratio"],
                calmar_ratio=result["calmar_ratio"],
                average_trade_duration=result["average_trade_duration"],
                best_trade=result["best_trade"],
                worst_trade=result["worst_trade"],
                commission_paid=result["commission_paid"],
                slippage_cost=result["slippage_cost"],
                net_profit=result["net_profit"],
                equity_curve=result["equity_curve"],
                trade_history=result["trade_history"],
                performance_metrics=result["performance_metrics"],
                created_at=datetime.utcnow()
            )
            
            # Update strategy last backtested date
            strategy.last_backtested = datetime.utcnow()
            self.db.commit()
            
            # Log trading event
            log_trading_event(
                "strategy_backtested",
                {
                    "strategy_id": strategy.id,
                    "backtest_id": backtest_id,
                    "return_percentage": result["return_percentage"],
                    "sharpe_ratio": result["sharpe_ratio"]
                },
                user_id=user_id
            )
            
            logger.info(f"Backtested strategy {strategy.name} with return {result['return_percentage']:.2f}%")
            return backtest_response
            
        except Exception as e:
            logger.error(f"Error backtesting strategy: {e}")
            raise
    
    async def get_strategy_performance(self, strategy_id: int, request: StrategyPerformanceRequest, user_id: int) -> Tuple[List[StrategyPerformance], int]:
        """Get strategy performance with pagination"""
        try:
            # Verify strategy ownership
            strategy = await self.get_strategy(strategy_id, user_id)
            if not strategy:
                logger.warning(f"Strategy {strategy_id} not found")
                return [], 0
            
            # Query performance records
            query = self.db.query(StrategyPerformance).filter(
                StrategyPerformance.strategy_id == strategy_id
            )
            
            # Apply date filters
            if request.start_date:
                query = query.filter(StrategyPerformance.date >= request.start_date)
            
            if request.end_date:
                query = query.filter(StrategyPerformance.date <= request.end_date)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (request.page - 1) * request.per_page
            performance_records = query.order_by(desc(StrategyPerformance.date)).offset(offset).limit(request.per_page).all()
            
            return performance_records, total
            
        except Exception as e:
            logger.error(f"Error getting strategy performance: {e}")
            return [], 0
    
    async def get_strategy_stats(self, user_id: int) -> Optional[StrategyStats]:
        """Get strategy statistics"""
        try:
            # Get all strategies for user
            strategies = self.db.query(Strategy).filter(Strategy.created_by == user_id).all()
            
            if not strategies:
                return None
            
            # Calculate statistics
            total_strategies = len(strategies)
            active_strategies = len([s for s in strategies if s.is_active])
            paused_strategies = len([s for s in strategies if s.status == StrategyStatus.PAUSED.value])
            draft_strategies = len([s for s in strategies if s.status == StrategyStatus.DRAFT.value])
            archived_strategies = len([s for s in strategies if s.status == StrategyStatus.ARCHIVED.value])
            paper_trading_strategies = len([s for s in strategies if s.execution_mode == ExecutionMode.PAPER.value])
            live_trading_strategies = len([s for s in strategies if s.execution_mode == ExecutionMode.LIVE.value])
            
            # Count by type
            strategies_by_type = {}
            for strategy in strategies:
                strategy_type = strategy.strategy_type
                strategies_by_type[strategy_type] = strategies_by_type.get(strategy_type, 0) + 1
            
            # Count by status
            strategies_by_status = {}
            for strategy in strategies:
                status = strategy.status
                strategies_by_status[status] = strategies_by_status.get(status, 0) + 1
            
            # Calculate total trades and P&L
            total_trades = sum(s.total_trades for s in strategies)
            total_pnl = sum(s.total_pnl for s in strategies)
            average_return = total_pnl / total_strategies if total_strategies > 0 else 0
            
            # Find best and worst performing strategies
            best_strategy = max(strategies, key=lambda s: s.total_pnl) if strategies else None
            worst_strategy = min(strategies, key=lambda s: s.total_pnl) if strategies else None
            
            return StrategyStats(
                total_strategies=total_strategies,
                active_strategies=active_strategies,
                paused_strategies=paused_strategies,
                draft_strategies=draft_strategies,
                archived_strategies=archived_strategies,
                paper_trading_strategies=paper_trading_strategies,
                live_trading_strategies=live_trading_strategies,
                strategies_by_type=strategies_by_type,
                strategies_by_status=strategies_by_status,
                total_trades=total_trades,
                total_pnl=total_pnl,
                average_return=average_return,
                best_performing_strategy=best_strategy.to_dict() if best_strategy else None,
                worst_performing_strategy=worst_strategy.to_dict() if worst_strategy else None
            )
            
        except Exception as e:
            logger.error(f"Error getting strategy stats: {e}")
            return None
    
    async def _execute_strategy(self, strategy: Strategy):
        """Execute strategy (async)"""
        try:
            # This would integrate with N8N workflow execution
            # For now, simulate strategy execution
            
            # Simulate some delay
            await asyncio.sleep(2)
            
            # Log strategy execution
            log_trading_event(
                "strategy_execution_started",
                {
                    "strategy_id": strategy.id,
                    "name": strategy.name,
                    "symbols": strategy.symbols,
                    "timeframes": strategy.timeframes
                },
                user_id=strategy.created_by
            )
            
            # In a real implementation, this would:
            # 1. Connect to N8N API
            # 2. Start the workflow
            # 3. Monitor execution
            # 4. Handle signals and place orders
            
            logger.info(f"Started execution of strategy {strategy.name}")
            
        except Exception as e:
            logger.error(f"Error executing strategy: {e}")
    
    async def _run_backtest(self, strategy: Strategy, backtest_request: StrategyBacktestRequest) -> Dict[str, Any]:
        """Run backtest (async)"""
        try:
            # This would integrate with historical data and strategy execution
            # For now, simulate backtest results
            
            # Simulate some delay
            await asyncio.sleep(3)
            
            # Calculate backtest period in days
            backtest_days = (backtest_request.end_date - backtest_request.start_date).days
            
            # Generate mock results
            total_trades = int(backtest_days * 2.5)  # Average 2.5 trades per day
            winning_trades = int(total_trades * 0.55)  # 55% win rate
            losing_trades = total_trades - winning_trades
            
            # Calculate P&L
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            avg_win = backtest_request.initial_capital * 0.02  # 2% average win
            avg_loss = backtest_request.initial_capital * 0.015  # 1.5% average loss
            gross_profit = winning_trades * avg_win
            gross_loss = losing_trades * avg_loss
            total_pnl = gross_profit - gross_loss
            
            # Apply commission and slippage
            commission_rate = backtest_request.commission / 100
            slippage_rate = backtest_request.slippage / 100
            commission_paid = total_trades * backtest_request.initial_capital * commission_rate
            slippage_cost = total_trades * backtest_request.initial_capital * slippage_rate
            net_profit = total_pnl - commission_paid - slippage_cost
            
            # Calculate final capital and return
            final_capital = backtest_request.initial_capital + net_profit
            total_return = net_profit
            return_percentage = (net_profit / backtest_request.initial_capital) * 100
            
            # Calculate other metrics
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            max_drawdown = backtest_request.initial_capital * 0.15  # 15% max drawdown
            max_drawdown_percentage = 15.0
            sharpe_ratio = 1.2  # Placeholder
            sortino_ratio = 1.5  # Placeholder
            calmar_ratio = return_percentage / max_drawdown_percentage if max_drawdown_percentage > 0 else 0
            
            # Generate equity curve (simplified)
            equity_curve = []
            current_equity = backtest_request.initial_capital
            for day in range(backtest_days):
                # Simulate daily equity change
                daily_change = (net_profit / backtest_days) + (0.1 * (2 * (day % 2) - 1))  # Add some randomness
                current_equity += daily_change
                equity_curve.append({
                    "date": (backtest_request.start_date + timedelta(days=day)).isoformat(),
                    "equity": current_equity
                })
            
            # Generate trade history (simplified)
            trade_history = []
            for i in range(total_trades):
                is_win = i < winning_trades
                trade_pnl = avg_win if is_win else -avg_loss
                trade_history.append({
                    "date": (backtest_request.start_date + timedelta(days=i * (backtest_days / total_trades))).isoformat(),
                    "symbol": strategy.symbols[0] if strategy.symbols else "SYMBOL",
                    "side": "BUY" if i % 2 == 0 else "SELL",
                    "quantity": 100,
                    "entry_price": 100.0,
                    "exit_price": 100.0 + (trade_pnl / 100),
                    "pnl": trade_pnl,
                    "is_win": is_win
                })
            
            # Generate performance metrics
            performance_metrics = {
                "average_trade_duration": 24.0,  # Hours
                "best_trade": max(avg_win, avg_loss),
                "worst_trade": min(-avg_win, -avg_loss),
                "average_win": avg_win,
                "average_loss": avg_loss,
                "volatility": 15.0,  # Percentage
                "var_95": backtest_request.initial_capital * 0.02,  # 2% VaR
                "max_consecutive_losses": 5,
                "max_consecutive_wins": 3
            }
            
            return {
                "final_capital": final_capital,
                "total_return": total_return,
                "return_percentage": return_percentage,
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": win_rate * 100,
                "gross_profit": gross_profit,
                "gross_loss": gross_loss,
                "profit_factor": profit_factor,
                "max_drawdown": max_drawdown,
                "max_drawdown_percentage": max_drawdown_percentage,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "calmar_ratio": calmar_ratio,
                "average_trade_duration": performance_metrics["average_trade_duration"],
                "best_trade": performance_metrics["best_trade"],
                "worst_trade": performance_metrics["worst_trade"],
                "commission_paid": commission_paid,
                "slippage_cost": slippage_cost,
                "net_profit": net_profit,
                "equity_curve": equity_curve,
                "trade_history": trade_history,
                "performance_metrics": performance_metrics
            }
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise