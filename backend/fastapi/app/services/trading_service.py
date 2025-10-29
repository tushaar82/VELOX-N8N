"""
VELOX-N8N Trading Service
Business logic for trading operations and order management
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta
import logging
import uuid
import asyncio

from app.core.database import get_db
from app.models.trade import Trade, Position, OrderType, OrderSide, TradeStatus, PositionType
from app.models.user import User
from app.models.strategy import Strategy
from app.schemas.trading import (
    OrderCreate, OrderUpdate, OrderCancel, OrderResponse,
    PositionResponse, PortfolioSummary, TradeHistoryRequest,
    PositionHistoryRequest, OrderBookRequest, MarketStats,
    TradingSession, RiskMetrics, TradingAnalytics
)
from app.core.logging import log_trading_event, log_error
from app.core.security import generate_api_key

logger = logging.getLogger(__name__)


class TradingService:
    """Service for trading operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_order(self, order_data: OrderCreate, user_id: int) -> Trade:
        """Create a new trading order"""
        try:
            # Generate unique order ID
            order_id = f"ORD_{uuid.uuid4().hex[:12].upper()}"
            
            # Create trade record
            trade = Trade(
                order_id=order_id,
                symbol=order_data.symbol,
                exchange=order_data.exchange,
                instrument_type=order_data.instrument_type,
                order_type=order_data.order_type,
                order_side=order_data.order_side,
                quantity=order_data.quantity,
                price=order_data.price,
                trigger_price=order_data.trigger_price,
                stop_loss=order_data.stop_loss,
                take_profit=order_data.take_profit,
                trailing_stop=order_data.trailing_stop,
                strategy_id=order_data.strategy_id,
                user_id=user_id,
                status=TradeStatus.PENDING,
                tags=order_data.tags,
                notes=order_data.notes,
                created_at=datetime.utcnow(),
                placed_at=datetime.utcnow()
            )
            
            # Calculate order value
            if order_data.price:
                trade.order_value = order_data.quantity * order_data.price
            
            # Save to database
            self.db.add(trade)
            self.db.commit()
            self.db.refresh(trade)
            
            # Log trading event
            log_trading_event(
                "order_created",
                {
                    "order_id": order_id,
                    "symbol": order_data.symbol,
                    "order_type": order_data.order_type.value,
                    "order_side": order_data.order_side.value,
                    "quantity": order_data.quantity,
                    "price": order_data.price
                },
                user_id=user_id
            )
            
            # Send order to broker (async)
            asyncio.create_task(self._send_order_to_broker(trade))
            
            logger.info(f"Created order {order_id} for user {user_id}")
            return trade
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            self.db.rollback()
            raise
    
    async def update_order(self, order_update: OrderUpdate, user_id: int) -> Optional[Trade]:
        """Update an existing order"""
        try:
            # Get order
            trade = self.db.query(Trade).filter(
                and_(
                    Trade.order_id == order_update.order_id,
                    Trade.user_id == user_id,
                    Trade.status.in_([TradeStatus.PENDING, TradeStatus.PLACED])
                )
            ).first()
            
            if not trade:
                logger.warning(f"Order {order_update.order_id} not found or not updatable")
                return None
            
            # Update order fields
            if order_update.price is not None:
                trade.price = order_update.price
                trade.order_value = trade.quantity * order_update.price
            
            if order_update.quantity is not None:
                trade.quantity = order_update.quantity
                trade.order_value = trade.quantity * (trade.price or 0)
            
            if order_update.stop_loss is not None:
                trade.stop_loss = order_update.stop_loss
            
            if order_update.take_profit is not None:
                trade.take_profit = order_update.take_profit
            
            if order_update.trailing_stop is not None:
                trade.trailing_stop = order_update.trailing_stop
            
            if order_update.notes:
                if not trade.notes:
                    trade.notes = ""
                trade.notes += f"\nUpdated: {order_update.notes}"
            
            trade.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(trade)
            
            # Log trading event
            log_trading_event(
                "order_updated",
                {
                    "order_id": order_update.order_id,
                    "updates": order_update.dict(exclude_unset=True)
                },
                user_id=user_id
            )
            
            logger.info(f"Updated order {order_update.order_id}")
            return trade
            
        except Exception as e:
            logger.error(f"Error updating order: {e}")
            self.db.rollback()
            raise
    
    async def cancel_order(self, order_cancel: OrderCancel, user_id: int) -> Optional[Trade]:
        """Cancel an existing order"""
        try:
            # Get order
            trade = self.db.query(Trade).filter(
                and_(
                    Trade.order_id == order_cancel.order_id,
                    Trade.user_id == user_id,
                    Trade.status.in_([TradeStatus.PENDING, TradeStatus.PLACED, TradeStatus.PARTIALLY_EXECUTED])
                )
            ).first()
            
            if not trade:
                logger.warning(f"Order {order_cancel.order_id} not found or not cancellable")
                return None
            
            # Cancel order
            trade.cancel(order_cancel.reason)
            
            self.db.commit()
            self.db.refresh(trade)
            
            # Log trading event
            log_trading_event(
                "order_cancelled",
                {
                    "order_id": order_cancel.order_id,
                    "reason": order_cancel.reason
                },
                user_id=user_id
            )
            
            logger.info(f"Cancelled order {order_cancel.order_id}")
            return trade
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            self.db.rollback()
            raise
    
    async def get_order(self, order_id: str, user_id: int) -> Optional[Trade]:
        """Get order by ID"""
        try:
            return self.db.query(Trade).filter(
                and_(
                    Trade.order_id == order_id,
                    Trade.user_id == user_id
                )
            ).first()
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            return None
    
    async def get_orders(self, user_id: int, status: Optional[TradeStatus] = None, 
                      symbol: Optional[str] = None, limit: int = 100) -> List[Trade]:
        """Get user orders"""
        try:
            query = self.db.query(Trade).filter(Trade.user_id == user_id)
            
            if status:
                query = query.filter(Trade.status == status)
            
            if symbol:
                query = query.filter(Trade.symbol == symbol)
            
            return query.order_by(desc(Trade.created_at)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    async def get_trade_history(self, request: TradeHistoryRequest, user_id: int) -> Tuple[List[Trade], int]:
        """Get trade history with pagination"""
        try:
            query = self.db.query(Trade).filter(Trade.user_id == user_id)
            
            # Apply filters
            if request.symbol:
                query = query.filter(Trade.symbol == request.symbol)
            
            if request.exchange:
                query = query.filter(Trade.exchange == request.exchange)
            
            if request.order_type:
                query = query.filter(Trade.order_type == request.order_type)
            
            if request.order_side:
                query = query.filter(Trade.order_side == request.order_side)
            
            if request.status:
                query = query.filter(Trade.status == request.status)
            
            if request.strategy_id:
                query = query.filter(Trade.strategy_id == request.strategy_id)
            
            if request.start_date:
                query = query.filter(Trade.created_at >= request.start_date)
            
            if request.end_date:
                query = query.filter(Trade.created_at <= request.end_date)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (request.page - 1) * request.per_page
            trades = query.order_by(desc(Trade.created_at)).offset(offset).limit(request.per_page).all()
            
            return trades, total
            
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return [], 0
    
    async def get_positions(self, user_id: int, symbol: Optional[str] = None) -> List[Position]:
        """Get user positions"""
        try:
            query = self.db.query(Position).filter(Position.user_id == user_id)
            
            if symbol:
                query = query.filter(Position.symbol == symbol)
            
            return query.order_by(desc(Position.updated_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    async def get_position(self, position_id: int, user_id: int) -> Optional[Position]:
        """Get position by ID"""
        try:
            return self.db.query(Position).filter(
                and_(
                    Position.id == position_id,
                    Position.user_id == user_id
                )
            ).first()
        except Exception as e:
            logger.error(f"Error getting position {position_id}: {e}")
            return None
    
    async def get_position_history(self, request: PositionHistoryRequest, user_id: int) -> Tuple[List[Position], int]:
        """Get position history with pagination"""
        try:
            query = self.db.query(Position).filter(Position.user_id == user_id)
            
            # Apply filters
            if request.symbol:
                query = query.filter(Position.symbol == request.symbol)
            
            if request.exchange:
                query = query.filter(Position.exchange == request.exchange)
            
            if request.position_type:
                query = query.filter(Position.position_type == request.position_type)
            
            if request.status:
                query = query.filter(Position.status == request.status)
            
            if request.strategy_id:
                query = query.filter(Position.strategy_id == request.strategy_id)
            
            if request.start_date:
                query = query.filter(Position.created_at >= request.start_date)
            
            if request.end_date:
                query = query.filter(Position.created_at <= request.end_date)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (request.page - 1) * request.per_page
            positions = query.order_by(desc(Position.updated_at)).offset(offset).limit(request.per_page).all()
            
            return positions, total
            
        except Exception as e:
            logger.error(f"Error getting position history: {e}")
            return [], 0
    
    async def get_portfolio_summary(self, user_id: int) -> Optional[PortfolioSummary]:
        """Get portfolio summary"""
        try:
            # Get all positions
            positions = self.db.query(Position).filter(
                and_(
                    Position.user_id == user_id,
                    Position.status == 'OPEN'
                )
            ).all()
            
            # Calculate portfolio metrics
            total_value = sum(p.current_value or 0 for p in positions)
            total_exposure = sum(abs(p.quantity) * (p.current_price or 0) for p in positions)
            net_exposure = sum(p.quantity * (p.current_price or 0) for p in positions)
            total_pnl = sum(p.total_pnl or 0 for p in positions)
            unrealized_pnl = sum(p.unrealized_pnl or 0 for p in positions)
            realized_pnl = sum(p.realized_pnl or 0 for p in positions)
            
            # Count positions
            active_positions = len(positions)
            long_positions = len([p for p in positions if p.is_long])
            short_positions = len([p for p in positions if p.is_short])
            
            # Calculate max drawdown (simplified)
            max_drawdown = max([p.max_drawdown or 0 for p in positions] + [0])
            
            # Calculate leverage ratio
            investment_value = sum(p.investment_value or 0 for p in positions)
            leverage_ratio = total_exposure / investment_value if investment_value > 0 else 1.0
            
            # Get user's cash balance (simplified - would come from account service)
            available_cash = 100000.0  # Placeholder
            used_margin = total_exposure * 0.5  # Placeholder
            available_margin = available_cash - used_margin
            margin_call_level = (used_margin / available_cash * 100) if available_cash > 0 else 0
            
            # Calculate daily P&L (simplified)
            daily_pnl = sum(p.total_pnl or 0 for p in positions 
                           if p.last_updated_at and p.last_updated_at.date() == datetime.utcnow().date())
            
            return PortfolioSummary(
                total_value=total_value,
                total_exposure=total_exposure,
                net_exposure=net_exposure,
                available_cash=available_cash,
                used_margin=used_margin,
                available_margin=available_margin,
                margin_call_level=margin_call_level,
                total_pnl=total_pnl,
                daily_pnl=daily_pnl,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl,
                total_positions=active_positions,
                active_positions=active_positions,
                long_positions=long_positions,
                short_positions=short_positions,
                max_drawdown=max_drawdown,
                leverage_ratio=leverage_ratio
            )
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return None
    
    async def get_order_book(self, request: OrderBookRequest) -> Optional[Dict[str, Any]]:
        """Get order book for symbol"""
        try:
            # This would typically come from market data service
            # For now, return mock data
            return {
                "symbol": request.symbol,
                "exchange": request.exchange,
                "timestamp": datetime.utcnow(),
                "bid_levels": [
                    {"price": 100.50, "quantity": 1000, "orders": 5},
                    {"price": 100.49, "quantity": 500, "orders": 3},
                    {"price": 100.48, "quantity": 750, "orders": 4}
                ],
                "ask_levels": [
                    {"price": 100.51, "quantity": 800, "orders": 4},
                    {"price": 100.52, "quantity": 1200, "orders": 6},
                    {"price": 100.53, "quantity": 600, "orders": 3}
                ],
                "best_bid": 100.50,
                "best_ask": 100.51,
                "spread": 0.01,
                "mid_price": 100.505,
                "total_bid_quantity": 2250,
                "total_ask_quantity": 2600
            }
            
        except Exception as e:
            logger.error(f"Error getting order book: {e}")
            return None
    
    async def get_market_stats(self, symbol: str, exchange: str) -> Optional[MarketStats]:
        """Get market statistics for symbol"""
        try:
            # This would typically come from market data service
            # For now, return mock data
            return MarketStats(
                symbol=symbol,
                exchange=exchange,
                last_price=100.50,
                bid_price=100.49,
                ask_price=100.51,
                last_quantity=100,
                total_volume=50000,
                total_buy_volume=25000,
                total_sell_volume=25000,
                trade_count=500,
                price_change=0.50,
                price_change_percent=0.50,
                high_price=101.00,
                low_price=99.50,
                open_price=100.00,
                vwap=100.45,
                open_interest=10000,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting market stats: {e}")
            return None
    
    async def close_position(self, position_id: int, user_id: int, closing_price: float) -> Optional[Position]:
        """Close a position"""
        try:
            # Get position
            position = self.db.query(Position).filter(
                and_(
                    Position.id == position_id,
                    Position.user_id == user_id,
                    Position.status == 'OPEN'
                )
            ).first()
            
            if not position:
                logger.warning(f"Position {position_id} not found or not closable")
                return None
            
            # Close position
            position.close_position(closing_price)
            
            self.db.commit()
            self.db.refresh(position)
            
            # Log trading event
            log_trading_event(
                "position_closed",
                {
                    "position_id": position_id,
                    "symbol": position.symbol,
                    "closing_price": closing_price,
                    "pnl": position.total_pnl
                },
                user_id=user_id
            )
            
            logger.info(f"Closed position {position_id}")
            return position
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            self.db.rollback()
            raise
    
    async def _send_order_to_broker(self, trade: Trade):
        """Send order to broker (async)"""
        try:
            # This would integrate with OpenAlgo or other broker APIs
            # For now, simulate order execution
            
            # Simulate some delay
            await asyncio.sleep(1)
            
            # Update order status
            trade.status = TradeStatus.PLACED
            trade.placed_at = datetime.utcnow()
            
            # Simulate partial fill
            if trade.quantity > 100:
                filled_qty = trade.quantity * 0.5
                avg_price = trade.price or 100.0
                trade.update_execution(filled_qty, avg_price)
            
            self.db.commit()
            
            # Log event
            log_trading_event(
                "order_sent_to_broker",
                {
                    "order_id": trade.order_id,
                    "broker_order_id": f"BRK_{uuid.uuid4().hex[:8].upper()}",
                    "status": trade.status.value
                },
                user_id=trade.user_id
            )
            
        except Exception as e:
            logger.error(f"Error sending order to broker: {e}")
            # Update order status to failed
            trade.status = TradeStatus.FAILED
            self.db.commit()
    
    async def process_market_data_update(self, symbol: str, price: float):
        """Process market data update and update positions"""
        try:
            # Get all open positions for this symbol
            positions = self.db.query(Position).filter(
                and_(
                    Position.symbol == symbol,
                    Position.status == 'OPEN'
                )
            ).all()
            
            for position in positions:
                # Update position with new price
                position.update_current_price(price)
            
            self.db.commit()
            
            logger.debug(f"Updated {len(positions)} positions for {symbol} with price {price}")
            
        except Exception as e:
            logger.error(f"Error processing market data update: {e}")
            self.db.rollback()
    
    async def get_trading_analytics(self, user_id: int, start_date: datetime, end_date: datetime) -> Optional[TradingAnalytics]:
        """Get trading analytics for period"""
        try:
            # Get trades in period
            trades = self.db.query(Trade).filter(
                and_(
                    Trade.user_id == user_id,
                    Trade.executed_at >= start_date,
                    Trade.executed_at <= end_date,
                    Trade.status == TradeStatus.EXECUTED
                )
            ).all()
            
            if not trades:
                return None
            
            # Calculate analytics
            total_trades = len(trades)
            winning_trades = len([t for t in trades if (t.total_pnl or 0) > 0])
            losing_trades = total_trades - winning_trades
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            total_pnl = sum(t.total_pnl or 0 for t in trades)
            gross_profit = sum(t.total_pnl or 0 for t in trades if (t.total_pnl or 0) > 0)
            gross_loss = abs(sum(t.total_pnl or 0 for t in trades if (t.total_pnl or 0) < 0))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            winning_trades_list = [t for t in trades if (t.total_pnl or 0) > 0]
            losing_trades_list = [t for t in trades if (t.total_pnl or 0) < 0]
            
            average_win = sum(t.total_pnl or 0 for t in winning_trades_list) / len(winning_trades_list) if winning_trades_list else 0
            average_loss = sum(t.total_pnl or 0 for t in losing_trades_list) / len(losing_trades_list) if losing_trades_list else 0
            
            largest_win = max([t.total_pnl or 0 for t in trades] + [0])
            largest_loss = min([t.total_pnl or 0 for t in trades] + [0])
            
            # Calculate average trade duration (simplified)
            avg_duration = 24.0  # Placeholder in hours
            
            # Calculate Sharpe ratio (simplified)
            sharpe_ratio = 1.5  # Placeholder
            
            # Calculate max drawdown (simplified)
            max_drawdown = 5.0  # Placeholder in percentage
            
            # Calculate total commission
            total_commission = sum(t.calculate_charges() for t in trades)
            
            # Calculate return on investment
            total_investment = sum(t.executed_value or 0 for t in trades)
            roi = (total_pnl / total_investment * 100) if total_investment > 0 else 0
            
            return TradingAnalytics(
                period_start=start_date,
                period_end=end_date,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                total_pnl=total_pnl,
                gross_profit=gross_profit,
                gross_loss=gross_loss,
                profit_factor=profit_factor,
                average_win=average_win,
                average_loss=average_loss,
                largest_win=largest_win,
                largest_loss=largest_loss,
                average_trade_duration=avg_duration,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=None,  # Placeholder
                max_drawdown=max_drawdown,
                max_drawdown_duration=5,  # Placeholder in days
                total_commission=total_commission,
                net_pnl=total_pnl - total_commission,
                return_on_investment=roi
            )
            
        except Exception as e:
            logger.error(f"Error calculating trading analytics: {e}")
            return None