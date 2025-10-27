# Phase 5: Option Chain Service

## Overview
Implement NSE option chain scraping using Playwright for real-time options data.

## Goals
- Scrape NSE option chain data
- Handle both index and equity options
- Implement retry logic and error handling
- Parse and structure option chain data

## Dependencies
- Phase 3 must be completed

## File Changes

### app/services/option_chain.py (NEW)
**References:** app/schemas/option_chain.py

Create OptionChainService class for NSE option chain scraping:
- Import playwright.async_api
- Create async method fetch_option_chain(symbol, is_index=True) that:
  - Determines API URL based on is_index (indices vs equities endpoint)
  - Launches Playwright browser in headless mode
  - Creates browser context with realistic User-Agent and headers
  - Navigates to https://www.nseindia.com/option-chain to establish cookies
  - Waits for page load and adds small delay for cookie/bot check completion
  - Makes API request to option chain JSON endpoint with proper headers (accept, referer, sec-fetch-site)
  - Parses JSON response
  - Closes browser
  - Returns parsed data
- Create method parse_option_chain_data(raw_data) that:
  - Extracts expiry dates, underlying value
  - Parses option data (strikes, OI, volume, LTP, IV for calls and puts)
  - Converts to OptionChainResponse model from app/schemas/option_chain.py
- Add retry logic with exponential backoff for 401/403 errors
- Add error handling for network failures
- Consider browser context pooling for performance (optional)
- Add method to filter option chain by strike range or OI threshold

## Completion Criteria
- [ ] Successfully scrapes NSE option chain for indices
- [ ] Successfully scrapes NSE option chain for equities
- [ ] Retry logic handles temporary failures
- [ ] Browser cleanup happens properly
- [ ] Data is parsed correctly into response models

## Next Phase
Phase 6: Real-time WebSocket Infrastructure
