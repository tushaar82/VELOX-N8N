I have created the following plan after thorough exploration and analysis of the codebase. Follow the below plan verbatim. Trust the files and references. Do not re-verify what's written in the plan. Explore only when absolutely necessary. First implement all the proposed file changes and then I'll review all the changes together at the end.

### Observations

The workspace is empty - this is a **greenfield project** to build a comprehensive FastAPI application for real-time technical analysis and market data. The system will integrate multiple components:

- **OpenAlgo** for historical OHLCV data
- **ta library** for 43+ technical indicators
- **Playwright** for NSE option chain scraping
- **WebSocket** for real-time tick-by-tick updates
- **Multi-timeframe** candle aggregation
- **Support/Resistance** calculations using swing highs/lows with ATR clustering

The architecture follows **FastAPI 2025 best practices** with async-first design, feature-based modular structure, and separation of concerns (routers, services, schemas, core utilities).


### Approach

Create a **production-ready FastAPI application** with:

1. **Modular structure**: Separate routers for indicators, option chain, WebSocket, and metadata
2. **Service layer**: Dedicated services for market data, indicators, support/resistance, option chain, and tick streaming
3. **Real-time processing**: Async tick aggregation with multi-symbol, multi-timeframe support
4. **Configuration management**: Environment-based settings using pydantic-settings
5. **WebSocket broadcasting**: Connection manager for real-time indicator updates
6. **Comprehensive endpoints**: Historical indicators, real-time calculations, option chain, support/resistance levels

The system will maintain in-memory state for active symbols/timeframes and broadcast updates to connected WebSocket clients.


### Reasoning

Started with an empty workspace. Searched the web for OpenAlgo repository information, NSE option chain scraping patterns with Playwright, FastAPI WebSocket implementation, ta library indicators list, support/resistance algorithms, FastAPI 2025 best practices, and real-time candle aggregation patterns. Gathered comprehensive technical information to design a production-ready architecture.


## Mermaid Diagram

sequenceDiagram
    participant Client
    participant FastAPI
    participant MarketData
    participant OpenAlgo
    participant IndicatorService
    participant TickStream
    participant WebSocket
    participant NSE

    Note over Client,NSE: Historical Indicator Calculation Flow
    Client->>FastAPI: POST /api/v1/indicators/calculate
    FastAPI->>MarketData: fetch_historical_candles()
    MarketData->>OpenAlgo: history API call
    OpenAlgo-->>MarketData: OHLCV DataFrame
    MarketData->>MarketData: append current candle
    MarketData-->>FastAPI: Candles
    FastAPI->>IndicatorService: calculate_all_indicators()
    IndicatorService->>IndicatorService: Apply ta library (RSI, MACD, etc.)
    IndicatorService-->>FastAPI: Indicator values
    FastAPI-->>Client: IndicatorResponse JSON

    Note over Client,NSE: Real-time WebSocket Flow
    Client->>WebSocket: Connect /api/v1/ws/stream
    WebSocket-->>Client: Connection accepted
    Client->>WebSocket: {"action":"subscribe","symbols":["AAPL"],"timeframes":["1m","5m"]}
    WebSocket->>TickStream: register subscription
    TickStream->>TickStream: create aggregators per timeframe
    WebSocket-->>Client: {"type":"ack","action":"subscribed"}
    
    loop Every Tick
        TickStream->>TickStream: process_tick()
        TickStream->>TickStream: aggregate to candles
        TickStream->>IndicatorService: calculate_indicators_realtime()
        IndicatorService-->>TickStream: updated indicators
        TickStream->>WebSocket: broadcast_candle_update()
        WebSocket-->>Client: {"type":"candle","data":{...}}
        WebSocket-->>Client: {"type":"indicator","indicators":{...}}
    end

    Note over Client,NSE: Option Chain Fetch Flow
    Client->>FastAPI: POST /api/v1/option-chain/fetch
    FastAPI->>OptionChainService: fetch_option_chain()
    OptionChainService->>NSE: Playwright: visit option-chain page
    NSE-->>OptionChainService: cookies established
    OptionChainService->>NSE: API call with cookies
    NSE-->>OptionChainService: JSON option chain data
    OptionChainService->>OptionChainService: parse_option_chain_data()
    OptionChainService-->>FastAPI: OptionChainResponse
    FastAPI-->>Client: Option chain JSON

    Note over Client,NSE: Support/Resistance Calculation
    Client->>FastAPI: POST /api/v1/indicators/support-resistance
    FastAPI->>MarketData: fetch_historical_candles()
    MarketData->>OpenAlgo: history API
    OpenAlgo-->>MarketData: OHLCV data
    MarketData-->>FastAPI: DataFrame
    FastAPI->>SupportResistanceService: compute_support_resistance()
    SupportResistanceService->>SupportResistanceService: find_swing_extrema()
    SupportResistanceService->>SupportResistanceService: cluster_levels()
    SupportResistanceService-->>FastAPI: Support/Resistance levels
    FastAPI-->>Client: SupportResistanceResponse JSON

## Proposed File Changes

### README.md(NEW)

Create comprehensive project documentation including:
- Project overview and features
- Installation instructions (clone OpenAlgo reference, install dependencies)
- Required dependencies: `fastapi`, `uvicorn`, `openalgo`, `ta`, `playwright`, `pandas`, `numpy`, `scipy`, `pydantic-settings`, `websockets`, `aiohttp`
- Environment variables setup (OpenAlgo API key, host URL)
- Playwright browser installation command: `playwright install chromium`
- API endpoints documentation with examples
- WebSocket usage examples
- Multi-timeframe support explanation
- Available indicators list from ta library

### requirements.txt(NEW)

List all required Python packages:
- fastapi>=0.109.0
- uvicorn[standard]>=0.27.0
- openalgo>=1.0.3
- ta>=0.11.0
- playwright>=1.40.0
- pandas>=2.1.0
- numpy>=1.26.0
- scipy>=1.11.0
- pydantic>=2.5.0
- pydantic-settings>=2.1.0
- websockets>=12.0
- aiohttp>=3.9.0
- python-multipart>=0.0.6
- orjson>=3.9.0

### .env.example(NEW)

Create environment variables template:
- OPENALGO_API_KEY: API key for OpenAlgo authentication
- OPENALGO_HOST: OpenAlgo server URL (default: http://127.0.0.1:5000)
- OPENALGO_VERSION: API version (default: v1)
- CORS_ORIGINS: Comma-separated allowed origins for CORS
- LOG_LEVEL: Logging level (default: INFO)
- MAX_WEBSOCKET_CONNECTIONS: Maximum concurrent WebSocket connections (default: 100)
- TICK_BUFFER_SIZE: Size of tick buffer per symbol (default: 1000)
- DEFAULT_TIMEFRAMES: Comma-separated default timeframes (default: 1m,5m,15m,1h,1d)

### .gitignore(NEW)

Standard Python gitignore with:
- __pycache__/, *.py[cod], *$py.class
- .env, .venv/, venv/, env/
- *.log
- .pytest_cache/, .coverage
- .vscode/, .idea/
- *.db, *.sqlite
- playwright/.browsers/ (Playwright browser binaries)

### app(NEW)

Create main application directory to house all application code

### app/__init__.py(NEW)

Empty init file to make app a Python package

### app/main.py(NEW)

References: 

- app/core/config.py(NEW)
- app/api/v1/router.py(NEW)

Create FastAPI application instance with:
- Import FastAPI, CORSMiddleware
- Initialize FastAPI app with title, description, version
- Configure CORS middleware using settings from `app/core/config.py`
- Include routers from `app/api/v1/router.py` with /api/v1 prefix
- Add startup event handler to initialize OpenAlgo client, start background tick aggregation tasks
- Add shutdown event handler to cleanup resources (close WebSocket connections, stop background tasks)
- Add root endpoint (/) returning API info and health status
- Add health check endpoint (/health) returning service status

### app/core(NEW)

Create core utilities directory

### app/core/__init__.py(NEW)

Empty init file

### app/core/config.py(NEW)

Define Settings class using pydantic-settings BaseSettings:
- openalgo_api_key: str (required)
- openalgo_host: str (default: http://127.0.0.1:5000)
- openalgo_version: str (default: v1)
- cors_origins: list[str] (parse from comma-separated string)
- log_level: str (default: INFO)
- max_websocket_connections: int (default: 100)
- tick_buffer_size: int (default: 1000)
- default_timeframes: list[str] (default: [1m, 5m, 15m, 1h, 1d])
- model_config with env_file=.env, case_sensitive=False

Create cached get_settings() function using lru_cache to return singleton Settings instance

### app/core/logging.py(NEW)

References: 

- app/core/config.py(NEW)

Configure application logging:
- Import logging, sys
- Create setup_logging() function that configures root logger with level from settings in `app/core/config.py`
- Set format with timestamp, level, module, message
- Add StreamHandler to stdout
- Create get_logger(name) helper function returning configured logger for module

### app/schemas(NEW)

Create schemas directory for Pydantic models

### app/schemas/__init__.py(NEW)

Empty init file

### app/schemas/candles.py(NEW)

Define Pydantic models for candle data:
- Candle model with fields: symbol (str), timestamp (datetime), open (float), high (float), low (float), close (float), volume (float), timeframe (str)
- CandleRequest model with: symbol (str), exchange (str), interval (str), start_date (str), end_date (str), include_current (bool, default=True)
- CandleResponse model with: candles (list[Candle]), current_candle (Optional[Candle]), metadata (dict)
- Use Field for validation and descriptions

### app/schemas/indicators.py(NEW)

Define Pydantic models for indicator requests/responses:
- IndicatorRequest model with: symbol (str), exchange (str), interval (str), start_date (Optional[str]), end_date (Optional[str]), indicators (Optional[list[str]]), indicator_params (Optional[dict])
- IndicatorValue model with: name (str), value (Union[float, dict]), timestamp (datetime)
- IndicatorResponse model with: symbol (str), timeframe (str), indicators (dict[str, list[float]]), timestamps (list[datetime]), metadata (dict)
- SupportResistanceLevel model with: price (float), level_type (str), strength (float), touches (int), last_touch (datetime)
- SupportResistanceResponse model with: symbol (str), timeframe (str), support_levels (list[SupportResistanceLevel]), resistance_levels (list[SupportResistanceLevel]), tolerance (float), current_price (float)
- WebSocketSubscription model with: action (str), symbols (list[str]), timeframes (list[str]), indicators (Optional[list[str]])

### app/schemas/option_chain.py(NEW)

Define Pydantic models for option chain data:
- OptionChainRequest model with: symbol (str), is_index (bool, default=True)
- OptionData model with: strike_price (float), call_oi (Optional[int]), put_oi (Optional[int]), call_volume (Optional[int]), put_volume (Optional[int]), call_ltp (Optional[float]), put_ltp (Optional[float]), call_iv (Optional[float]), put_iv (Optional[float])
- OptionChainResponse model with: symbol (str), expiry_dates (list[str]), underlying_value (float), options (list[OptionData]), timestamp (datetime), metadata (dict)
- Use Field for validation and descriptions

### app/services(NEW)

Create services directory for business logic

### app/services/__init__.py(NEW)

Empty init file

### app/services/market_data.py(NEW)

References: 

- app/core/config.py(NEW)
- app/schemas/candles.py(NEW)

Create MarketDataService class to wrap OpenAlgo client:
- Initialize with settings from `app/core/config.py`
- Import openalgo.orders.api
- Create async method fetch_historical_candles(symbol, exchange, interval, start_date, end_date) that calls OpenAlgo history API and returns pandas DataFrame
- Create async method fetch_current_quote(symbol, exchange) for latest price
- Add error handling for API failures
- Add method to convert OpenAlgo DataFrame to list of Candle models from `app/schemas/candles.py`
- Add method to validate and normalize timeframe strings (1m, 5m, 15m, 1h, 1d, etc.)
- Cache client instance as singleton

### app/services/tick_stream.py(NEW)

References: 

- app/services/websocket_manager.py(NEW)

Create TickStreamService for real-time tick aggregation:
- Define Tick dataclass with: symbol, timestamp, price, size
- Define CandleAggregator class (based on web search pattern) with:
  - __init__(interval_sec, on_candle_callback, on_partial_callback)
  - async on_tick(tick) method that aggregates ticks into OHLCV candles
  - _bucket_start(timestamp) to calculate candle bucket
  - Handle out-of-order ticks with configurable tolerance
  - Maintain per-symbol state dict with current candle data
  - Emit completed candles and partial updates
  - Calculate VWAP alongside OHLCV
- Create TickStreamManager class with:
  - Dict of aggregators per (symbol, timeframe) tuple
  - async subscribe(symbol, timeframes) to create aggregators
  - async unsubscribe(symbol, timeframes)
  - async process_tick(tick) to route to all relevant aggregators
  - Callback registration for candle completion
  - Integration with WebSocket broadcast from `app/services/websocket_manager.py`

### app/services/indicators.py(NEW)

Create IndicatorService class for technical indicator calculations:
- Import ta library (all indicator classes)
- Create method calculate_all_indicators(df: pd.DataFrame) that:
  - Takes DataFrame with OHLCV columns
  - Calculates all 43+ indicators from ta library organized by category
  - Returns dict with indicator names as keys and Series/values as values
- Create method calculate_specific_indicators(df, indicator_list, params) for selective calculation
- Implement indicator categories:
  - Volume: MFI, ADI, OBV, CMF, ForceIndex, EaseOfMovement, VPT, NVI, VWAP
  - Volatility: ATR, BollingerBands, KeltnerChannel, DonchianChannel, UlcerIndex
  - Trend: SMA, EMA, WMA, MACD, ADX, VortexIndicator, TRIX, MassIndex, CCI, DPO, KST, Ichimoku, PSAR, STC, Aroon
  - Momentum: RSI, StochRSI, TSI, UltimateOscillator, StochasticOscillator, WilliamsR, AwesomeOscillator, KAMA, ROC, PPO, PVO
  - Others: DailyReturn, DailyLogReturn, CumulativeReturn
- Add error handling for insufficient data (NaN handling)
- Create method to format indicators for JSON response
- Add method calculate_indicators_realtime(candles, previous_indicators) for incremental updates

### app/services/support_resistance.py(NEW)

References: 

- app/schemas/indicators.py(NEW)

Create SupportResistanceService class (based on web search algorithm):
- Import scipy.signal.find_peaks, numpy, pandas
- Create method calculate_atr(df, period=14) for Average True Range
- Create method find_swing_extrema(df, window=3, prominence_mult=0.5) that:
  - Uses find_peaks on High prices for resistance candidates
  - Uses find_peaks on inverted Low prices for support candidates
  - Uses ATR-based dynamic prominence
  - Returns DataFrame with price, timestamp, type (S/R), volume
- Create method cluster_levels(points_df, df, half_life_bars=200, atr_mult=1.0) that:
  - Calculates tolerance based on ATR
  - Applies recency weighting (exponential decay)
  - Applies volume weighting
  - Clusters nearby levels using 1D streaming merge
  - Returns separate DataFrames for support and resistance levels
- Create main method compute_support_resistance(df, params) that:
  - Calls find_swing_extrema
  - Calls cluster_levels
  - Returns SupportResistanceResponse model from `app/schemas/indicators.py`
  - Includes level strength, touch count, last touch timestamp
- Add method to calculate classic pivot points as alternative
- Add method to filter top-N levels by strength

### app/services/option_chain.py(NEW)

References: 

- app/schemas/option_chain.py(NEW)

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
  - Converts to OptionChainResponse model from `app/schemas/option_chain.py`
- Add retry logic with exponential backoff for 401/403 errors
- Add error handling for network failures
- Consider browser context pooling for performance (optional)
- Add method to filter option chain by strike range or OI threshold

### app/services/websocket_manager.py(NEW)

References: 

- app/core/config.py(NEW)
- app/services/tick_stream.py(NEW)

Create WebSocketManager class for connection management and broadcasting:
- Define ConnectionManager class with:
  - active_connections: Set[WebSocket]
  - subscriptions: Dict[WebSocket, dict] with symbol/timeframe/indicator subscriptions
  - async connect(websocket) to accept and register connection
  - disconnect(websocket) to remove connection and cleanup subscriptions
  - async update_subscription(websocket, subscription_data) to modify client subscriptions
  - async broadcast_to_subscribers(message, symbol, timeframe) to send updates to relevant clients
  - async send_personal_message(websocket, message)
  - Connection limit enforcement based on settings from `app/core/config.py`
- Create WebSocketBroadcaster class with:
  - Integration with TickStreamManager from `app/services/tick_stream.py`
  - async broadcast_candle_update(candle, indicators) to send real-time updates
  - async broadcast_indicator_update(symbol, timeframe, indicators)
  - Message formatting using orjson for performance
  - Error handling for disconnected clients
- Add heartbeat/ping mechanism to detect stale connections
- Add message queue per connection to handle backpressure

### app/api(NEW)

Create API directory

### app/api/__init__.py(NEW)

Empty init file

### app/api/v1(NEW)

Create v1 API version directory

### app/api/v1/__init__.py(NEW)

Empty init file

### app/api/v1/router.py(NEW)

References: 

- app/api/v1/endpoints/indicators.py(NEW)
- app/api/v1/endpoints/option_chain.py(NEW)
- app/api/v1/endpoints/websocket.py(NEW)
- app/api/v1/endpoints/meta.py(NEW)

Create main v1 router that aggregates all feature routers:
- Import APIRouter
- Import routers from endpoints: indicators, option_chain, websocket, meta
- Create v1_router = APIRouter()
- Include indicators_router from `app/api/v1/endpoints/indicators.py` with prefix /indicators, tags=["indicators"]
- Include option_chain_router from `app/api/v1/endpoints/option_chain.py` with prefix /option-chain, tags=["option-chain"]
- Include websocket_router from `app/api/v1/endpoints/websocket.py` with prefix /ws, tags=["websocket"]
- Include meta_router from `app/api/v1/endpoints/meta.py` with prefix /meta, tags=["metadata"]

### app/api/v1/endpoints(NEW)

Create endpoints directory

### app/api/v1/endpoints/__init__.py(NEW)

Empty init file

### app/api/v1/endpoints/indicators.py(NEW)

References: 

- app/schemas/indicators.py(NEW)
- app/services/market_data.py(NEW)
- app/services/indicators.py(NEW)
- app/services/support_resistance.py(NEW)

Create indicators router with endpoints:

1. POST /calculate - Calculate indicators for historical data:
   - Accept IndicatorRequest from `app/schemas/indicators.py`
   - Use MarketDataService from `app/services/market_data.py` to fetch historical candles
   - Optionally append current forming candle if include_current=True
   - Use IndicatorService from `app/services/indicators.py` to calculate indicators
   - Return IndicatorResponse with all calculated indicators
   - Support indicator filtering via indicators parameter

2. POST /calculate-all - Calculate all 43+ indicators:
   - Similar to /calculate but forces all indicators
   - Returns comprehensive indicator data organized by category

3. GET /available - List all available indicators:
   - Return dict of indicator categories and names
   - Include parameter requirements for each indicator

4. POST /support-resistance - Calculate support and resistance levels:
   - Accept symbol, exchange, interval, lookback period
   - Use MarketDataService to fetch historical data
   - Use SupportResistanceService from `app/services/support_resistance.py`
   - Return SupportResistanceResponse with levels, strength, touches

5. POST /multi-timeframe - Calculate indicators across multiple timeframes:
   - Accept list of timeframes
   - Fetch data for each timeframe in parallel
   - Calculate indicators for each
   - Return dict keyed by timeframe

Add proper error handling, validation, and response models for all endpoints

### app/api/v1/endpoints/option_chain.py(NEW)

References: 

- app/schemas/option_chain.py(NEW)
- app/services/option_chain.py(NEW)

Create option chain router with endpoints:

1. POST /fetch - Fetch option chain data:
   - Accept OptionChainRequest from `app/schemas/option_chain.py`
   - Use OptionChainService from `app/services/option_chain.py` to scrape NSE data
   - Return OptionChainResponse with strikes, OI, volume, LTP, IV
   - Handle both index (NIFTY, BANKNIFTY) and equity symbols

2. POST /fetch-index - Convenience endpoint for index option chains:
   - Hardcoded is_index=True
   - Accept symbol parameter
   - Return option chain data

3. POST /fetch-stock - Convenience endpoint for stock option chains:
   - Hardcoded is_index=False
   - Accept symbol parameter
   - Return option chain data

4. GET /supported-symbols - List supported index symbols:
   - Return list of common indices (NIFTY, BANKNIFTY, FINNIFTY, etc.)

Add rate limiting consideration (NSE may block excessive requests)
Add caching for option chain data (short TTL, e.g., 30 seconds)
Add proper error handling for Playwright failures and NSE API errors

### app/api/v1/endpoints/websocket.py(NEW)

References: 

- app/services/websocket_manager.py(NEW)
- app/schemas/indicators.py(NEW)
- app/services/tick_stream.py(NEW)

Create WebSocket router with endpoint:

1. WebSocket /stream - Real-time tick and indicator updates:
   - Accept WebSocket connection
   - Use WebSocketManager from `app/services/websocket_manager.py`
   - Handle connection lifecycle (connect, disconnect)
   - Accept subscription messages in JSON format:
     - {"action": "subscribe", "symbols": ["AAPL", "MSFT"], "timeframes": ["1m", "5m"], "indicators": ["RSI", "MACD"]}
     - {"action": "unsubscribe", "symbols": ["AAPL"]}
   - Validate subscription requests using WebSocketSubscription from `app/schemas/indicators.py`
   - Register client with TickStreamManager from `app/services/tick_stream.py`
   - Broadcast real-time updates:
     - Partial candle updates (tick by tick)
     - Completed candle updates
     - Indicator value updates
   - Send acknowledgment messages for subscriptions
   - Handle client disconnection gracefully
   - Implement error handling for invalid messages
   - Add connection limit enforcement

Message format for broadcasts:
- {"type": "candle", "symbol": "AAPL", "timeframe": "1m", "data": {...}}
- {"type": "indicator", "symbol": "AAPL", "timeframe": "1m", "indicators": {...}}
- {"type": "error", "message": "..."}
- {"type": "ack", "action": "subscribed", "symbols": [...]}

Note: Actual tick data ingestion mechanism needs to be implemented separately (could be from OpenAlgo WebSocket if available, or external feed)

### app/api/v1/endpoints/meta.py(NEW)

Create metadata router with endpoints:

1. GET /indicators - List all available indicators:
   - Return comprehensive list of 43+ indicators from ta library
   - Organize by category (Volume, Volatility, Trend, Momentum, Others)
   - Include indicator names, descriptions, required parameters

2. GET /timeframes - List supported timeframes:
   - Return list of supported interval strings
   - Include OpenAlgo-compatible formats (1m, 5m, 15m, 30m, 1h, 1d, etc.)

3. GET /exchanges - List supported exchanges:
   - Return list of exchanges supported by OpenAlgo (NSE, BSE, NFO, etc.)

4. GET /active-subscriptions - Get current WebSocket subscriptions:
   - Return count of active WebSocket connections
   - Return list of actively subscribed symbols and timeframes
   - Useful for monitoring and debugging

5. GET /system-status - System health and statistics:
   - Return service status
   - Return OpenAlgo connection status
   - Return active WebSocket connection count
   - Return memory usage statistics
   - Return tick processing statistics

All endpoints return JSON responses with appropriate status codes

### app/utils(NEW)

Create utilities directory

### app/utils/__init__.py(NEW)

Empty init file

### app/utils/timeframes.py(NEW)

Create timeframe utility functions:
- parse_timeframe(interval_str) to convert string (1m, 5m, 1h, 1d) to seconds
- validate_timeframe(interval_str) to check if timeframe is supported
- get_candle_count(start_date, end_date, interval) to calculate expected candle count
- normalize_timeframe(interval_str) to standardize format
- timeframe_to_pandas_freq(interval_str) to convert to pandas resample frequency
- Map of common timeframe aliases (1min -> 1m, 1hour -> 1h, etc.)

### app/utils/validators.py(NEW)

Create validation utility functions:
- validate_symbol(symbol) to check symbol format
- validate_exchange(exchange) to verify exchange is supported
- validate_date_range(start_date, end_date) to ensure valid date range
- validate_indicator_params(indicator_name, params) to check indicator-specific parameters
- sanitize_symbol(symbol) to clean and uppercase symbol strings
- validate_strike_price(strike) for option chain validation

### tests(NEW)

Create tests directory mirroring app structure

### tests/__init__.py(NEW)

Empty init file

### tests/conftest.py(NEW)

Create pytest fixtures:
- test_app fixture that creates FastAPI TestClient
- mock_openalgo_client fixture for testing without real API calls
- sample_ohlcv_data fixture with test DataFrame
- mock_websocket fixture for WebSocket testing
- Override dependencies using app.dependency_overrides
- Setup and teardown for test isolation

### tests/test_indicators.py(NEW)

Create unit tests for indicator calculations:
- Test calculate_all_indicators with sample data
- Test individual indicator calculations (RSI, MACD, Bollinger Bands, etc.)
- Test error handling for insufficient data
- Test indicator parameter validation
- Test multi-timeframe calculations
- Use pytest parametrize for testing multiple indicators

### tests/test_support_resistance.py(NEW)

Create unit tests for support/resistance calculations:
- Test swing extrema detection
- Test level clustering algorithm
- Test ATR calculation
- Test recency and volume weighting
- Test with various market conditions (trending, ranging, volatile)
- Verify level strength calculations

### tests/test_tick_stream.py(NEW)

Create unit tests for tick aggregation:
- Test candle aggregation from ticks
- Test multi-timeframe aggregation
- Test out-of-order tick handling
- Test partial candle updates
- Test VWAP calculation
- Test bucket boundary handling
- Test gap handling (no ticks for a period)

### tests/test_api.py(NEW)

Create integration tests for API endpoints:
- Test POST /api/v1/indicators/calculate endpoint
- Test POST /api/v1/indicators/support-resistance endpoint
- Test POST /api/v1/option-chain/fetch endpoint (with mocked Playwright)
- Test WebSocket /api/v1/ws/stream connection and subscription
- Test error responses for invalid inputs
- Test rate limiting and validation
- Use TestClient for HTTP endpoints
- Use WebSocket test client for WebSocket endpoint

### scripts(NEW)

Create scripts directory for utility scripts

### scripts/clone_openalgo.sh(NEW)

Create bash script to clone OpenAlgo repository:
- Clone https://github.com/marketcalls/openalgo to a reference directory
- Clone https://github.com/marketcalls/openalgo-python-library for library reference
- Add instructions for setting up OpenAlgo server if needed
- Make script executable
- Add error handling

### scripts/setup.sh(NEW)

Create setup script:
- Create virtual environment
- Install dependencies from requirements.txt
- Install Playwright browsers: playwright install chromium
- Copy .env.example to .env
- Print setup instructions
- Check Python version (require 3.10+)
- Make script executable

### scripts/run_dev.sh(NEW)

Create development run script:
- Activate virtual environment
- Run FastAPI with: fastapi dev app/main.py
- Set reload=True for development
- Set host=0.0.0.0 and port=8000
- Make script executable

### scripts/run_prod.sh(NEW)

Create production run script:
- Activate virtual environment
- Run FastAPI with: fastapi run app/main.py
- Set workers based on CPU count
- Set host and port from environment or defaults
- Add logging configuration
- Make script executable

### Dockerfile(NEW)

Create Dockerfile for containerization:
- Use python:3.11-slim as base image
- Install system dependencies for Playwright
- Copy requirements.txt and install Python packages
- Install Playwright browsers
- Copy application code
- Set working directory
- Expose port 8000
- Set environment variables
- Use fastapi run as CMD
- Add healthcheck
- Use non-root user for security

### docker-compose.yml(NEW)

Create docker-compose configuration:
- Define service for FastAPI application
- Mount .env file for configuration
- Expose port 8000
- Set restart policy
- Add volume mounts if needed
- Optional: Add Redis service for caching
- Optional: Add monitoring service (Prometheus/Grafana)
- Set network configuration

### docs(NEW)

Create documentation directory

### docs/API.md(NEW)

Create comprehensive API documentation:
- Overview of all endpoints
- Request/response examples for each endpoint
- WebSocket protocol documentation
- Authentication requirements
- Rate limiting information
- Error codes and handling
- Example curl commands
- Example Python client code
- WebSocket subscription examples

### docs/INDICATORS.md(NEW)

Create indicators documentation:
- List all 43+ indicators from ta library
- Organize by category (Volume, Volatility, Trend, Momentum, Others)
- Include description for each indicator
- Document required parameters
- Provide calculation formulas or references
- Include usage examples
- Document minimum data requirements (periods needed)

### docs/ARCHITECTURE.md(NEW)

Create architecture documentation:
- System overview diagram
- Component descriptions (services, routers, schemas)
- Data flow diagrams for real-time processing
- WebSocket architecture
- Tick aggregation pipeline
- Multi-timeframe handling
- State management approach
- Scalability considerations
- Performance optimization strategies
- Integration points (OpenAlgo, NSE, ta library)

### docs/DEPLOYMENT.md(NEW)

Create deployment documentation:
- Local development setup
- Production deployment options
- Docker deployment instructions
- Environment variable configuration
- OpenAlgo server setup
- Playwright browser installation
- Monitoring and logging setup
- Performance tuning
- Security considerations
- Backup and recovery