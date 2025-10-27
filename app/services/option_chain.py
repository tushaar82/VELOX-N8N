"""
Option chain service for fetching NSE option chain data.
Uses Playwright for web scraping with proper cookie handling.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING
import json

try:
    from playwright.async_api import async_playwright
    if TYPE_CHECKING:
        from playwright.async_api import Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Define dummy types for when Playwright is not installed
    Browser = None
    BrowserContext = None
    Page = None

from app.core.logging import LoggerMixin
from app.schemas.option_chain import (
    OptionChainResponse,
    OptionData,
    OptionChainAnalysis
)


class OptionChainService(LoggerMixin):
    """
    Service for fetching NSE option chain data.
    
    Uses Playwright to:
    1. Navigate to NSE website to establish cookies
    2. Make API requests with proper headers
    3. Parse and structure option chain data
    """
    
    # NSE URLs
    NSE_BASE_URL = "https://www.nseindia.com"
    NSE_OPTION_CHAIN_URL = "https://www.nseindia.com/option-chain"
    
    # API endpoints (v3 with type parameter)
    NSE_OPTION_CHAIN_API_V3 = "https://www.nseindia.com/api/option-chain-v3"
    
    # Legacy endpoints (kept for backward compatibility)
    NSE_INDEX_API = "https://www.nseindia.com/api/option-chain-indices"
    NSE_EQUITY_API = "https://www.nseindia.com/api/option-chain-equities"
    
    def __init__(self):
        """Initialize the option chain service."""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning(
                "Playwright not available. Install with: pip install playwright && playwright install chromium"
            )
        self.logger.info("OptionChainService initialized")
    
    async def fetch_option_chain(
        self,
        symbol: str,
        is_index: bool = True,
        expiry: Optional[str] = None,
        use_v3_api: bool = True,
        max_retries: int = 3
    ) -> OptionChainResponse:
        """
        Fetch option chain data for a symbol.
        
        Args:
            symbol: Symbol name (e.g., NIFTY, BANKNIFTY, RELIANCE)
            is_index: Whether the symbol is an index
            expiry: Specific expiry date (e.g., "30-Jan-2025"). If None, fetches all expiries
            use_v3_api: Use v3 API with type parameter (recommended)
            max_retries: Maximum number of retry attempts
        
        Returns:
            OptionChainResponse: Parsed option chain data
        
        Raises:
            ImportError: If Playwright is not installed
            Exception: If fetching fails after retries
        
        Example:
            >>> service = OptionChainService()
            >>> # Fetch with v3 API (recommended)
            >>> response = await service.fetch_option_chain("NIFTY", is_index=True, expiry="30-Jan-2025")
            >>> # Fetch all expiries
            >>> response = await service.fetch_option_chain("NIFTY", is_index=True)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is required for option chain fetching. "
                "Install with: pip install playwright && playwright install chromium"
            )
        
        symbol = symbol.upper()
        self.logger.info(f"Fetching option chain for {symbol} (is_index={is_index})")
        
        for attempt in range(max_retries):
            try:
                async with async_playwright() as p:
                    # Launch browser
                    browser = await p.chromium.launch(headless=True)
                    
                    try:
                        # Fetch data
                        data = await self._fetch_with_browser(
                            browser, symbol, is_index, expiry, use_v3_api
                        )
                        
                        # Parse response
                        response = self.parse_option_chain_data(data, symbol)
                        
                        self.logger.info(
                            f"Successfully fetched option chain for {symbol}: "
                            f"{len(response.options)} strikes"
                        )
                        
                        return response
                        
                    finally:
                        await browser.close()
                        
            except Exception as e:
                self.logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed for {symbol}: {e}"
                )
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"All retry attempts failed for {symbol}")
                    raise
    
    async def _fetch_with_browser(
        self,
        browser,  # Browser type
        symbol: str,
        is_index: bool,
        expiry: Optional[str] = None,
        use_v3_api: bool = True
    ) -> Dict:
        """
        Fetch option chain data using browser context.
        
        Args:
            browser: Playwright browser instance
            symbol: Symbol name
            is_index: Whether symbol is an index
            expiry: Specific expiry date (optional)
            use_v3_api: Use v3 API format
        
        Returns:
            Dict: Raw API response data
        """
        # Create browser context with realistic headers
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="en-IN"
        )
        
        try:
            page = await context.new_page()
            
            # Step 1: Visit option chain page to establish cookies
            self.logger.debug(f"Visiting {self.NSE_OPTION_CHAIN_URL}")
            await page.goto(self.NSE_OPTION_CHAIN_URL, wait_until="networkidle")
            
            # Wait a bit for cookies and bot checks
            await asyncio.sleep(2)
            
            # Step 2: Construct API URL
            if use_v3_api:
                # Use v3 API with type parameter
                market_type = "INDEX" if is_index else "EQUITY"
                api_url = f"{self.NSE_OPTION_CHAIN_API_V3}?type={market_type}&symbol={symbol}"
                if expiry:
                    api_url += f"&expiry={expiry}"
            else:
                # Use legacy API (separate endpoints for index/equity)
                api_url = self.NSE_INDEX_API if is_index else self.NSE_EQUITY_API
                api_url = f"{api_url}?symbol={symbol}"
            
            self.logger.debug(f"Fetching from API: {api_url}")
            
            # Set additional headers
            await page.set_extra_http_headers({
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": self.NSE_OPTION_CHAIN_URL,
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin"
            })
            
            # Navigate to API endpoint
            response = await page.goto(api_url, wait_until="networkidle")
            
            if response.status != 200:
                raise Exception(f"API returned status {response.status}")
            
            # Get JSON response
            content = await response.text()
            data = json.loads(content)
            
            return data
            
        finally:
            await context.close()
    
    def parse_option_chain_data(
        self,
        raw_data: Dict,
        symbol: str
    ) -> OptionChainResponse:
        """
        Parse raw NSE API response into OptionChainResponse.
        
        Args:
            raw_data: Raw API response
            symbol: Symbol name
        
        Returns:
            OptionChainResponse: Parsed option chain data
        """
        self.logger.debug(f"Parsing option chain data for {symbol}")
        
        # Extract records
        records = raw_data.get("records", {})
        data_list = records.get("data", [])
        
        # Extract expiry dates
        expiry_dates = records.get("expiryDates", [])
        
        # Extract underlying value
        underlying_value = records.get("underlyingValue", 0)
        
        # Parse option data
        options = []
        
        for item in data_list:
            strike_price = item.get("strikePrice", 0)
            
            # Extract call data
            call_data = item.get("CE", {})
            call_oi = call_data.get("openInterest")
            call_volume = call_data.get("totalTradedVolume")
            call_ltp = call_data.get("lastPrice")
            call_iv = call_data.get("impliedVolatility")
            call_change_oi = call_data.get("changeinOpenInterest")
            call_bid = call_data.get("bidprice")
            call_ask = call_data.get("askPrice")
            
            # Extract put data
            put_data = item.get("PE", {})
            put_oi = put_data.get("openInterest")
            put_volume = put_data.get("totalTradedVolume")
            put_ltp = put_data.get("lastPrice")
            put_iv = put_data.get("impliedVolatility")
            put_change_oi = put_data.get("changeinOpenInterest")
            put_bid = put_data.get("bidprice")
            put_ask = put_data.get("askPrice")
            
            # Calculate PCR
            pcr_oi = None
            pcr_volume = None
            
            if call_oi and put_oi and call_oi > 0:
                pcr_oi = put_oi / call_oi
            
            if call_volume and put_volume and call_volume > 0:
                pcr_volume = put_volume / call_volume
            
            # Create OptionData
            option = OptionData(
                strike_price=float(strike_price),
                call_oi=call_oi,
                call_volume=call_volume,
                call_ltp=call_ltp,
                call_iv=call_iv,
                call_change_oi=call_change_oi,
                call_bid=call_bid,
                call_ask=call_ask,
                put_oi=put_oi,
                put_volume=put_volume,
                put_ltp=put_ltp,
                put_iv=put_iv,
                put_change_oi=put_change_oi,
                put_bid=put_bid,
                put_ask=put_ask,
                pcr_oi=pcr_oi,
                pcr_volume=pcr_volume
            )
            
            options.append(option)
        
        # Create response
        response = OptionChainResponse(
            symbol=symbol,
            expiry_dates=expiry_dates,
            underlying_value=float(underlying_value),
            options=options,
            timestamp=datetime.now(),
            metadata={
                "total_strikes": len(options),
                "is_index": symbol in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"],
                "data_source": "NSE"
            }
        )
        
        return response
    
    def analyze_option_chain(
        self,
        response: OptionChainResponse
    ) -> OptionChainAnalysis:
        """
        Analyze option chain to derive insights.
        
        Args:
            response: OptionChainResponse object
        
        Returns:
            OptionChainAnalysis: Analysis with PCR, max pain, support/resistance
        """
        self.logger.debug(f"Analyzing option chain for {response.symbol}")
        
        # Find ATM strike
        atm_strike = min(
            response.options,
            key=lambda x: abs(x.strike_price - response.underlying_value)
        ).strike_price
        
        # Calculate totals
        total_call_oi = sum(opt.call_oi or 0 for opt in response.options)
        total_put_oi = sum(opt.put_oi or 0 for opt in response.options)
        total_call_volume = sum(opt.call_volume or 0 for opt in response.options)
        total_put_volume = sum(opt.put_volume or 0 for opt in response.options)
        
        # Calculate PCR
        pcr_oi = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        pcr_volume = total_put_volume / total_call_volume if total_call_volume > 0 else 0
        
        # Find max pain (strike with maximum total loss for option writers)
        max_pain = self._calculate_max_pain(response.options, response.underlying_value)
        
        # Find support levels (high put OI)
        support_levels = self._find_support_levels(response.options, top_n=3)
        
        # Find resistance levels (high call OI)
        resistance_levels = self._find_resistance_levels(response.options, top_n=3)
        
        # Create analysis
        analysis = OptionChainAnalysis(
            symbol=response.symbol,
            atm_strike=atm_strike,
            max_pain=max_pain,
            pcr_oi=pcr_oi,
            pcr_volume=pcr_volume,
            total_call_oi=int(total_call_oi),
            total_put_oi=int(total_put_oi),
            total_call_volume=int(total_call_volume),
            total_put_volume=int(total_put_volume),
            support_levels=support_levels,
            resistance_levels=resistance_levels
        )
        
        return analysis
    
    def _calculate_max_pain(
        self,
        options: List[OptionData],
        current_price: float
    ) -> Optional[float]:
        """Calculate max pain strike price."""
        if not options:
            return None
        
        max_pain_strike = None
        min_total_loss = float('inf')
        
        for option in options:
            strike = option.strike_price
            total_loss = 0
            
            # Calculate loss for call writers
            for opt in options:
                if opt.strike_price < strike and opt.call_oi:
                    total_loss += (strike - opt.strike_price) * opt.call_oi
            
            # Calculate loss for put writers
            for opt in options:
                if opt.strike_price > strike and opt.put_oi:
                    total_loss += (opt.strike_price - strike) * opt.put_oi
            
            if total_loss < min_total_loss:
                min_total_loss = total_loss
                max_pain_strike = strike
        
        return max_pain_strike
    
    def _find_support_levels(
        self,
        options: List[OptionData],
        top_n: int = 3
    ) -> List[float]:
        """Find support levels based on put OI."""
        # Sort by put OI descending
        sorted_options = sorted(
            options,
            key=lambda x: x.put_oi or 0,
            reverse=True
        )
        
        return [opt.strike_price for opt in sorted_options[:top_n]]
    
    def _find_resistance_levels(
        self,
        options: List[OptionData],
        top_n: int = 3
    ) -> List[float]:
        """Find resistance levels based on call OI."""
        # Sort by call OI descending
        sorted_options = sorted(
            options,
            key=lambda x: x.call_oi or 0,
            reverse=True
        )
        
        return [opt.strike_price for opt in sorted_options[:top_n]]
    
    def filter_option_chain(
        self,
        response: OptionChainResponse,
        min_oi: Optional[int] = None,
        min_volume: Optional[int] = None,
        strike_range: Optional[int] = None
    ) -> OptionChainResponse:
        """
        Filter option chain data.
        
        Args:
            response: Original OptionChainResponse
            min_oi: Minimum open interest
            min_volume: Minimum volume
            strike_range: Number of strikes above/below ATM
        
        Returns:
            OptionChainResponse: Filtered response
        """
        filtered_options = response.options
        
        # Filter by OI
        if min_oi is not None:
            filtered_options = [
                opt for opt in filtered_options
                if (opt.call_oi or 0) >= min_oi or (opt.put_oi or 0) >= min_oi
            ]
        
        # Filter by volume
        if min_volume is not None:
            filtered_options = [
                opt for opt in filtered_options
                if (opt.call_volume or 0) >= min_volume or (opt.put_volume or 0) >= min_volume
            ]
        
        # Filter by strike range
        if strike_range is not None:
            atm = response.underlying_value
            filtered_options = sorted(
                filtered_options,
                key=lambda x: abs(x.strike_price - atm)
            )[:strike_range * 2 + 1]
        
        # Create new response
        return OptionChainResponse(
            symbol=response.symbol,
            expiry_dates=response.expiry_dates,
            underlying_value=response.underlying_value,
            options=filtered_options,
            timestamp=response.timestamp,
            metadata={
                **response.metadata,
                "filtered": True,
                "original_count": len(response.options),
                "filtered_count": len(filtered_options)
            }
        )


# Convenience function
def get_option_chain_service() -> OptionChainService:
    """
    Get OptionChainService instance.
    
    Returns:
        OptionChainService: Service instance
    """
    return OptionChainService()
