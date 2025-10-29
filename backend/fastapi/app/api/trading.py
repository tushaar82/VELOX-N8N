"""
VELOX-N8N Trading API
REST API endpoints for trading operations and order management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user_from_token
from app.models.user import User
from app.models.trade import TradeStatus, OrderSide, OrderType, PositionType
from app.services.trading_service import TradingService
from app.schemas.trading import (
    OrderCreate, OrderUpdate, OrderCancel, OrderResponse,
    PositionResponse, PortfolioSummary, TradeHistoryRequest,
    PositionHistoryRequest, OrderBookRequest, OrderBookResponse,
    MarketStats, TradingAnalytics
)
from app.core.logging import log_api_request, log_security_event

router = APIRouter(prefix="/trading", tags=["trading"])


def get_trading_service(db: Session = Depends(get_db)) -> TradingService:
    """Get trading service instance"""
    return TradingService(db)


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Create a new trading order"""
    try:
        # Validate user permissions
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        # Create order
        trade = await trading_service.create_order(order_data, current_user.id)
        
        log_security_event(
            "order_created",
            user_id=current_user.id,
            ip_address=None,  # Will be set by middleware
            details={
                "order_id": trade.order_id,
                "symbol": order_data.symbol,
                "order_type": order_data.order_type.value,
                "order_side": order_data.order_side.value,
                "quantity": order_data.quantity
            }
        )
        
        return OrderResponse.from_orm(trade)
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "order_creation_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )


@router.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Update an existing order"""
    try:
        # Update order
        trade = await trading_service.update_order(order_update, current_user.id)
        
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not updatable"
            )
        
        log_security_event(
            "order_updated",
            user_id=current_user.id,
            ip_address=None,
            details={
                "order_id": order_id,
                "updates": order_update.dict(exclude_unset=True)
            }
        )
        
        return OrderResponse.from_orm(trade)
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "order_update_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order"
        )


@router.delete("/orders/{order_id}", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    order_cancel: OrderCancel,
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Cancel an existing order"""
    try:
        # Cancel order
        trade = await trading_service.cancel_order(order_cancel, current_user.id)
        
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not cancellable"
            )
        
        log_security_event(
            "order_cancelled",
            user_id=current_user.id,
            ip_address=None,
            details={
                "order_id": order_id,
                "reason": order_cancel.reason
            }
        )
        
        return OrderResponse.from_orm(trade)
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "order_cancellation_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order"
        )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get order by ID"""
    try:
        trade = await trading_service.get_order(order_id, current_user.id)
        
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return OrderResponse.from_orm(trade)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order"
        )


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    status: Optional[TradeStatus] = Query(None, description="Filter by order status"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of orders to return"),
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get user orders"""
    try:
        trades = await trading_service.get_orders(current_user.id, status, symbol, limit)
        return [OrderResponse.from_orm(trade) for trade in trades]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get orders"
        )


@router.get("/orders/history", response_model=dict)
async def get_trade_history(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    order_type: Optional[OrderType] = Query(None, description="Filter by order type"),
    order_side: Optional[OrderSide] = Query(None, description="Filter by order side"),
    status: Optional[TradeStatus] = Query(None, description="Filter by status"),
    strategy_id: Optional[int] = Query(None, description="Filter by strategy ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get trade history with pagination"""
    try:
        request = TradeHistoryRequest(
            symbol=symbol,
            exchange=exchange,
            order_type=order_type,
            order_side=order_side,
            status=status,
            strategy_id=strategy_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )
        
        trades, total = await trading_service.get_trade_history(request, current_user.id)
        
        return {
            "trades": [OrderResponse.from_orm(trade) for trade in trades],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trade history"
        )


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get user positions"""
    try:
        positions = await trading_service.get_positions(current_user.id, symbol)
        return [PositionResponse.from_orm(position) for position in positions]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get positions"
        )


@router.get("/positions/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: int,
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get position by ID"""
    try:
        position = await trading_service.get_position(position_id, current_user.id)
        
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Position not found"
            )
        
        return PositionResponse.from_orm(position)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get position"
        )


@router.post("/positions/{position_id}/close", response_model=PositionResponse)
async def close_position(
    position_id: int,
    closing_price: float = Query(..., description="Closing price"),
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Close a position"""
    try:
        position = await trading_service.close_position(position_id, current_user.id, closing_price)
        
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Position not found or not closable"
            )
        
        log_security_event(
            "position_closed",
            user_id=current_user.id,
            ip_address=None,
            details={
                "position_id": position_id,
                "closing_price": closing_price,
                "pnl": position.total_pnl
            }
        )
        
        return PositionResponse.from_orm(position)
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "position_closure_failed",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to close position"
        )


@router.get("/positions/history", response_model=dict)
async def get_position_history(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    position_type: Optional[PositionType] = Query(None, description="Filter by position type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    strategy_id: Optional[int] = Query(None, description="Filter by strategy ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get position history with pagination"""
    try:
        request = PositionHistoryRequest(
            symbol=symbol,
            exchange=exchange,
            position_type=position_type,
            status=status,
            strategy_id=strategy_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )
        
        positions, total = await trading_service.get_position_history(request, current_user.id)
        
        return {
            "positions": [PositionResponse.from_orm(position) for position in positions],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get position history"
        )


@router.get("/portfolio/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get portfolio summary"""
    try:
        summary = await trading_service.get_portfolio_summary(current_user.id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio summary not found"
            )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio summary"
        )


@router.get("/market/orderbook", response_model=OrderBookResponse)
async def get_order_book(
    symbol: str = Query(..., description="Trading symbol"),
    exchange: str = Query(..., description="Exchange name"),
    depth: int = Query(5, ge=1, le=20, description="Order book depth"),
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get order book for symbol"""
    try:
        request = OrderBookRequest(
            symbol=symbol,
            exchange=exchange,
            depth=depth
        )
        
        order_book = await trading_service.get_order_book(request)
        
        if not order_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order book not found"
            )
        
        return OrderBookResponse(**order_book)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order book"
        )


@router.get("/market/stats", response_model=MarketStats)
async def get_market_stats(
    symbol: str = Query(..., description="Trading symbol"),
    exchange: str = Query(..., description="Exchange name"),
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get market statistics for symbol"""
    try:
        stats = await trading_service.get_market_stats(symbol, exchange)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Market stats not found"
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get market stats"
        )


@router.get("/analytics", response_model=TradingAnalytics)
async def get_trading_analytics(
    start_date: datetime = Query(..., description="Start date for analytics"),
    end_date: datetime = Query(..., description="End date for analytics"),
    current_user: User = Depends(get_current_user_from_token),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get trading analytics for period"""
    try:
        analytics = await trading_service.get_trading_analytics(
            current_user.id, start_date, end_date
        )
        
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No trading data found for the specified period"
            )
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trading analytics"
        )


@router.post("/market/price-update")
async def update_market_price(
    symbol: str,
    price: float,
    trading_service: TradingService = Depends(get_trading_service)
):
    """Update market price (internal endpoint)"""
    try:
        await trading_service.process_market_data_update(symbol, price)
        
        return {"message": "Market price updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update market price"
        )


@router.get("/health")
async def trading_health_check():
    """Trading service health check"""
    return {
        "status": "healthy",
        "service": "trading",
        "timestamp": datetime.utcnow().isoformat()
    }