"""
API endpoints for NSE option chain data.
"""

from typing import Optional

try:
    from fastapi import APIRouter, HTTPException, Query
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None
    HTTPException = Exception
    Query = None

from app.core.logging import get_logger
from app.schemas.option_chain import (
    OptionChainRequest,
    OptionChainResponse,
    OptionChainAnalysis,
    OptionChainFilter
)
from app.services.option_chain import get_option_chain_service
from app.utils.validators import validate_symbol

logger = get_logger(__name__)

# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/option-chain", tags=["option-chain"])
else:
    router = None


if FASTAPI_AVAILABLE:
    @router.post("/", response_model=OptionChainResponse)
    async def get_option_chain(request: OptionChainRequest):
        """
        Fetch option chain data for a symbol.
        
        Args:
            request: OptionChainRequest with symbol and is_index flag
        
        Returns:
            OptionChainResponse: Complete option chain data
        
        Example:
            POST /api/v1/option-chain/
            {
                "symbol": "NIFTY",
                "is_index": true
            }
        """
        try:
            # Validate symbol
            is_valid, error = validate_symbol(request.symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(
                f"Fetching option chain for {request.symbol} "
                f"(is_index={request.is_index})"
            )
            
            # Fetch option chain
            service = get_option_chain_service()
            response = await service.fetch_option_chain(
                symbol=request.symbol,
                is_index=request.is_index,
                use_v3_api=True
            )
            
            logger.info(
                f"Fetched option chain: {len(response.options)} strikes, "
                f"{len(response.expiry_dates)} expiries"
            )
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching option chain: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/{symbol}", response_model=OptionChainResponse)
    async def get_option_chain_simple(
        symbol: str,
        is_index: bool = Query(True, description="Whether symbol is an index"),
        expiry: Optional[str] = Query(None, description="Specific expiry date (e.g., 30-Jan-2025)")
    ):
        """
        Fetch option chain data (simplified GET endpoint).
        
        Args:
            symbol: Trading symbol (NIFTY, BANKNIFTY, etc.)
            is_index: Whether the symbol is an index
            expiry: Optional specific expiry date
        
        Returns:
            OptionChainResponse: Complete option chain data
        
        Example:
            GET /api/v1/option-chain/NIFTY?is_index=true&expiry=30-Jan-2025
        """
        try:
            # Validate symbol
            is_valid, error = validate_symbol(symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(
                f"Fetching option chain for {symbol} "
                f"(is_index={is_index}, expiry={expiry})"
            )
            
            # Fetch option chain
            service = get_option_chain_service()
            response = await service.fetch_option_chain(
                symbol=symbol,
                is_index=is_index,
                expiry=expiry,
                use_v3_api=True
            )
            
            logger.info(
                f"Fetched option chain: {len(response.options)} strikes"
            )
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching option chain: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/{symbol}/analysis", response_model=OptionChainAnalysis)
    async def get_option_chain_analysis(
        symbol: str,
        is_index: bool = Query(True, description="Whether symbol is an index"),
        expiry: Optional[str] = Query(None, description="Specific expiry date")
    ):
        """
        Get option chain analysis with PCR, max pain, support/resistance.
        
        Args:
            symbol: Trading symbol
            is_index: Whether symbol is an index
            expiry: Optional specific expiry date
        
        Returns:
            OptionChainAnalysis: Analysis with PCR, max pain, S/R levels
        
        Example:
            GET /api/v1/option-chain/NIFTY/analysis?is_index=true
        """
        try:
            # Validate symbol
            is_valid, error = validate_symbol(symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(f"Analyzing option chain for {symbol}")
            
            # Fetch option chain
            service = get_option_chain_service()
            response = await service.fetch_option_chain(
                symbol=symbol,
                is_index=is_index,
                expiry=expiry,
                use_v3_api=True
            )
            
            # Analyze
            analysis = service.analyze_option_chain(response)
            
            logger.info(
                f"Analysis complete: ATM={analysis.atm_strike}, "
                f"PCR(OI)={analysis.pcr_oi:.2f}, MaxPain={analysis.max_pain}"
            )
            
            return analysis
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error analyzing option chain: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.post("/{symbol}/filter", response_model=OptionChainResponse)
    async def filter_option_chain(
        symbol: str,
        is_index: bool = Query(True, description="Whether symbol is an index"),
        expiry: Optional[str] = Query(None, description="Specific expiry date"),
        min_oi: Optional[int] = Query(None, description="Minimum open interest", ge=0),
        min_volume: Optional[int] = Query(None, description="Minimum volume", ge=0),
        strike_range: Optional[int] = Query(None, description="Strikes above/below ATM", ge=1, le=50)
    ):
        """
        Fetch and filter option chain data.
        
        Args:
            symbol: Trading symbol
            is_index: Whether symbol is an index
            expiry: Optional specific expiry date
            min_oi: Minimum open interest filter
            min_volume: Minimum volume filter
            strike_range: Number of strikes above/below ATM
        
        Returns:
            OptionChainResponse: Filtered option chain data
        
        Example:
            POST /api/v1/option-chain/NIFTY/filter?min_oi=10000&strike_range=10
        """
        try:
            # Validate symbol
            is_valid, error = validate_symbol(symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(
                f"Fetching and filtering option chain for {symbol} "
                f"(min_oi={min_oi}, min_volume={min_volume}, strike_range={strike_range})"
            )
            
            # Fetch option chain
            service = get_option_chain_service()
            response = await service.fetch_option_chain(
                symbol=symbol,
                is_index=is_index,
                expiry=expiry,
                use_v3_api=True
            )
            
            # Apply filters
            filtered_response = service.filter_option_chain(
                response,
                min_oi=min_oi,
                min_volume=min_volume,
                strike_range=strike_range
            )
            
            logger.info(
                f"Filtered from {len(response.options)} to "
                f"{len(filtered_response.options)} strikes"
            )
            
            return filtered_response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error filtering option chain: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/{symbol}/pcr")
    async def get_pcr(
        symbol: str,
        is_index: bool = Query(True, description="Whether symbol is an index"),
        expiry: Optional[str] = Query(None, description="Specific expiry date")
    ):
        """
        Get Put-Call Ratio (PCR) for a symbol.
        
        Args:
            symbol: Trading symbol
            is_index: Whether symbol is an index
            expiry: Optional specific expiry date
        
        Returns:
            Dict: PCR data (OI and volume based)
        
        Example:
            GET /api/v1/option-chain/NIFTY/pcr
        """
        try:
            # Validate symbol
            is_valid, error = validate_symbol(symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(f"Calculating PCR for {symbol}")
            
            # Fetch and analyze
            service = get_option_chain_service()
            response = await service.fetch_option_chain(
                symbol=symbol,
                is_index=is_index,
                expiry=expiry,
                use_v3_api=True
            )
            
            analysis = service.analyze_option_chain(response)
            
            return {
                "symbol": symbol,
                "expiry_dates": response.expiry_dates,
                "underlying_value": response.underlying_value,
                "pcr_oi": analysis.pcr_oi,
                "pcr_volume": analysis.pcr_volume,
                "total_call_oi": analysis.total_call_oi,
                "total_put_oi": analysis.total_put_oi,
                "total_call_volume": analysis.total_call_volume,
                "total_put_volume": analysis.total_put_volume,
                "timestamp": response.timestamp.isoformat()
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error calculating PCR: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/{symbol}/max-pain")
    async def get_max_pain(
        symbol: str,
        is_index: bool = Query(True, description="Whether symbol is an index"),
        expiry: Optional[str] = Query(None, description="Specific expiry date")
    ):
        """
        Get max pain strike price for a symbol.
        
        Args:
            symbol: Trading symbol
            is_index: Whether symbol is an index
            expiry: Optional specific expiry date
        
        Returns:
            Dict: Max pain data
        
        Example:
            GET /api/v1/option-chain/NIFTY/max-pain
        """
        try:
            # Validate symbol
            is_valid, error = validate_symbol(symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(f"Calculating max pain for {symbol}")
            
            # Fetch and analyze
            service = get_option_chain_service()
            response = await service.fetch_option_chain(
                symbol=symbol,
                is_index=is_index,
                expiry=expiry,
                use_v3_api=True
            )
            
            analysis = service.analyze_option_chain(response)
            
            return {
                "symbol": symbol,
                "underlying_value": response.underlying_value,
                "max_pain": analysis.max_pain,
                "atm_strike": analysis.atm_strike,
                "distance_from_max_pain": abs(response.underlying_value - (analysis.max_pain or 0)),
                "timestamp": response.timestamp.isoformat()
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error calculating max pain: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/{symbol}/oi-analysis")
    async def get_oi_analysis(
        symbol: str,
        is_index: bool = Query(True, description="Whether symbol is an index"),
        expiry: Optional[str] = Query(None, description="Specific expiry date"),
        top_n: int = Query(5, description="Number of top strikes", ge=1, le=20)
    ):
        """
        Get open interest analysis with top strikes.
        
        Args:
            symbol: Trading symbol
            is_index: Whether symbol is an index
            expiry: Optional specific expiry date
            top_n: Number of top strikes to return
        
        Returns:
            Dict: OI analysis with top call and put strikes
        
        Example:
            GET /api/v1/option-chain/NIFTY/oi-analysis?top_n=5
        """
        try:
            # Validate symbol
            is_valid, error = validate_symbol(symbol)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            logger.info(f"Analyzing OI for {symbol}")
            
            # Fetch option chain
            service = get_option_chain_service()
            response = await service.fetch_option_chain(
                symbol=symbol,
                is_index=is_index,
                expiry=expiry,
                use_v3_api=True
            )
            
            # Sort by OI
            call_oi_sorted = sorted(
                response.options,
                key=lambda x: x.call_oi or 0,
                reverse=True
            )[:top_n]
            
            put_oi_sorted = sorted(
                response.options,
                key=lambda x: x.put_oi or 0,
                reverse=True
            )[:top_n]
            
            return {
                "symbol": symbol,
                "underlying_value": response.underlying_value,
                "top_call_oi": [
                    {
                        "strike": opt.strike_price,
                        "oi": opt.call_oi,
                        "volume": opt.call_volume,
                        "ltp": opt.call_ltp,
                        "change_oi": opt.call_change_oi
                    }
                    for opt in call_oi_sorted
                ],
                "top_put_oi": [
                    {
                        "strike": opt.strike_price,
                        "oi": opt.put_oi,
                        "volume": opt.put_volume,
                        "ltp": opt.put_ltp,
                        "change_oi": opt.put_change_oi
                    }
                    for opt in put_oi_sorted
                ],
                "timestamp": response.timestamp.isoformat()
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error analyzing OI: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
