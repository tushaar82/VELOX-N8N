# Phase 3: Data Schemas

## Overview
Define all Pydantic models for request/response validation and data structures.

## Goals
- Create schemas for candles, indicators, and option chain data
- Establish type-safe data contracts
- Enable automatic API documentation
- Provide validation for all API inputs/outputs

## Dependencies
- Phase 2 must be completed

## File Changes

### app/schemas/candles.py (NEW)
Define Pydantic models for candle data:
- Candle model with fields: symbol (str), timestamp (datetime), open (float), high (float), low (float), close (float), volume (float), timeframe (str)
- CandleRequest model with: symbol (str), exchange (str), interval (str), start_date (str), end_date (str), include_current (bool, default=True)
- CandleResponse model with: candles (list[Candle]), current_candle (Optional[Candle]), metadata (dict)
- Use Field for validation and descriptions

### app/schemas/indicators.py (NEW)
Define Pydantic models for indicator requests/responses:
- IndicatorRequest model with: symbol (str), exchange (str), interval (str), start_date (Optional[str]), end_date (Optional[str]), indicators (Optional[list[str]]), indicator_params (Optional[dict])
- IndicatorValue model with: name (str), value (Union[float, dict]), timestamp (datetime)
- IndicatorResponse model with: symbol (str), timeframe (str), indicators (dict[str, list[float]]), timestamps (list[datetime]), metadata (dict)
- SupportResistanceLevel model with: price (float), level_type (str), strength (float), touches (int), last_touch (datetime)
- SupportResistanceResponse model with: symbol (str), timeframe (str), support_levels (list[SupportResistanceLevel]), resistance_levels (list[SupportResistanceLevel]), tolerance (float), current_price (float)
- WebSocketSubscription model with: action (str), symbols (list[str]), timeframes (list[str]), indicators (Optional[list[str]])

### app/schemas/option_chain.py (NEW)
Define Pydantic models for option chain data:
- OptionChainRequest model with: symbol (str), is_index (bool, default=True)
- OptionData model with: strike_price (float), call_oi (Optional[int]), put_oi (Optional[int]), call_volume (Optional[int]), put_volume (Optional[int]), call_ltp (Optional[float]), put_ltp (Optional[float]), call_iv (Optional[float]), put_iv (Optional[float])
- OptionChainResponse model with: symbol (str), expiry_dates (list[str]), underlying_value (float), options (list[OptionData]), timestamp (datetime), metadata (dict)
- Use Field for validation and descriptions

## Completion Criteria
- [ ] All schemas defined with proper types
- [ ] Field validations are in place
- [ ] Descriptions added for API documentation
- [ ] Optional vs required fields correctly specified
- [ ] Models can be imported without errors

## Next Phase
Phase 4: Market Data & Indicator Services
