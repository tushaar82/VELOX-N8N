# Micro-Candle Implementation Plan

## Implementation Roadmap

This document outlines the detailed implementation plan for the micro-candle generation system, including the data fetcher, generator, and integration components.

## Phase 1: Data Fetcher Implementation

### 1.1 Historical Data Fetcher

#### File Structure
```
backend/fastapi/app/services/
├── historical_data_fetcher.py
├── micro_candle_generator.py
├── pattern_analyzer.py
└── data_validator.py
```

#### HistoricalDataFetcher Class
```python
# backend/fastapi/app/services/historical_data_fetcher.py
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    symbol: str
    timeframe: str

class DataSource(ABC):
    @abstractmethod
    async def fetch_ohlc_data(self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime) -> List[Candle]:
        pass

class OpenAlgoDataSource(DataSource):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def _get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def fetch_ohlc_data(self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime) -> List[Candle]:
        session = await self._get_session()
        
        params = {
            'symbol': symbol,
            'timeframe': timeframe,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'api_key': self.api_key
        }
        
        url = f"{self.base_url}/api/v1/historical/ohlc"
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_candle_data(data, symbol, timeframe)
            else:
                raise Exception(f"Failed to fetch data: {response.status}")
    
    def _parse_candle_data(self, data: Dict, symbol: str, timeframe: str) -> List[Candle]:
        candles = []
        for item in data.get('candles', []):
            candle = Candle(
                timestamp=datetime.fromisoformat(item['timestamp']),
                open=float(item['open']),
                high=float(item['high']),
                low=float(item['low']),
                close=float(item['close']),
                volume=int(item['volume']),
                symbol=symbol,
                timeframe=timeframe
            )
            candles.append(candle)
        return candles

class HistoricalDataFetcher:
    def __init__(self, data_source: DataSource):
        self.data_source = data_source
        self.cache = {}
    
    async def fetch_data_for_micro_candles(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime,
        cache_key: Optional[str] = None
    ) -> List[Candle]:
        # Check cache first
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Fetch 1-minute data
        candles = await self.data_source.fetch_ohlc_data(
            symbol, '1m', start_date, end_date
        )
        
        # Cache the results
        if cache_key:
            self.cache[cache_key] = candles
        
        return candles
    
    async def fetch_with_buffer(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Candle]:
        # Fetch extra candle for next candle data
        buffered_end = end_date + timedelta(minutes=1)
        candles = await self.fetch_data_for_micro_candles(
            symbol, start_date, buffered_end
        )
        return candles
    
    def clear_cache(self):
        self.cache.clear()
```

### 1.2 Data Validation

#### DataValidator Class
```python
# backend/fastapi/app/services/data_validator.py
from typing import List, Tuple
from .historical_data_fetcher import Candle
import pandas as pd

class DataValidator:
    @staticmethod
    def validate_candle_data(candles: List[Candle]) -> Tuple[bool, List[str]]:
        errors = []
        
        if not candles:
            errors.append("No candle data provided")
            return False, errors
        
        # Check for chronological order
        timestamps = [c.timestamp for c in candles]
        if timestamps != sorted(timestamps):
            errors.append("Candle data is not in chronological order")
        
        # Check for gaps in data
        for i in range(1, len(candles)):
            time_diff = candles[i].timestamp - candles[i-1].timestamp
            if time_diff.total_seconds() > 120:  # More than 2 minutes gap
                errors.append(f"Data gap detected at {candles[i].timestamp}")
        
        # Validate OHLC relationships
        for i, candle in enumerate(candles):
            if not (candle.low <= candle.open <= candle.high):
                errors.append(f"Candle {i}: Open price not within High-Low range")
            if not (candle.low <= candle.close <= candle.high):
                errors.append(f"Candle {i}: Close price not within High-Low range")
            if candle.volume < 0:
                errors.append(f"Candle {i}: Negative volume")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def clean_candle_data(candles: List[Candle]) -> List[Candle]:
        # Remove duplicates
        unique_candles = []
        seen_timestamps = set()
        
        for candle in candles:
            if candle.timestamp not in seen_timestamps:
                unique_candles.append(candle)
                seen_timestamps.add(candle.timestamp)
        
        # Sort by timestamp
        unique_candles.sort(key=lambda x: x.timestamp)
        
        return unique_candles
    
    @staticmethod
    def fill_missing_candles(candles: List[Candle]) -> List[Candle]:
        if len(candles) < 2:
            return candles
        
        filled_candles = [candles[0]]
        
        for i in range(1, len(candles)):
            current_time = candles[i].timestamp
            prev_time = candles[i-1].timestamp
            expected_time = prev_time + timedelta(minutes=1)
            
            # Fill missing candles
            while expected_time < current_time:
                # Create synthetic candle using previous close
                synthetic_candle = Candle(
                    timestamp=expected_time,
                    open=candles[i-1].close,
                    high=candles[i-1].close,
                    low=candles[i-1].close,
                    close=candles[i-1].close,
                    volume=0,
                    symbol=candles[i].symbol,
                    timeframe=candles[i].timeframe
                )
                filled_candles.append(synthetic_candle)
                expected_time += timedelta(minutes=1)
            
            filled_candles.append(candles[i])
        
        return filled_candles
```

## Phase 2: Micro-Candle Generator Implementation

### 2.1 Pattern Analyzer

```python
# backend/fastapi/app/services/pattern_analyzer.py
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Tuple
from .historical_data_fetcher import Candle

class TrendDirection(Enum):
    UP = "up"
    DOWN = "down"
    SIDEWAYS = "sideways"

class VolumePattern(Enum):
    FRONT_LOADED = "front_loaded"
    BACK_LOADED = "back_loaded"
    U_SHAPED = "u_shaped"
    BELL_SHAPED = "bell_shaped"
    RANDOM = "random"

@dataclass
class MarketPattern:
    trend: TrendDirection
    volatility: float
    volume_pattern: VolumePattern
    strength: float  # 0-1, pattern strength
    price_momentum: float

class PatternAnalyzer:
    def __init__(self):
        self.trend_threshold = 0.001  # 0.1% minimum trend
        self.volatility_window = 5
    
    def analyze(self, current: Candle, next_candle: Candle) -> MarketPattern:
        # Calculate trend
        trend, momentum = self._calculate_trend(current, next_candle)
        
        # Calculate volatility
        volatility = self._calculate_volatility(current, next_candle)
        
        # Determine volume pattern
        volume_pattern = self._analyze_volume_pattern(current, next_candle, trend)
        
        # Calculate pattern strength
        strength = self._calculate_pattern_strength(current, next_candle)
        
        return MarketPattern(
            trend=trend,
            volatility=volatility,
            volume_pattern=volume_pattern,
            strength=strength,
            price_momentum=momentum
        )
    
    def _calculate_trend(self, current: Candle, next_candle: Candle) -> Tuple[TrendDirection, float]:
        price_change = (next_candle.close - current.open) / current.open
        
        if abs(price_change) < self.trend_threshold:
            return TrendDirection.SIDEWAYS, price_change
        elif price_change > 0:
            return TrendDirection.UP, price_change
        else:
            return TrendDirection.DOWN, price_change
    
    def _calculate_volatility(self, current: Candle, next_candle: Candle) -> float:
        current_vol = (current.high - current.low) / current.open
        next_vol = (next_candle.high - next_candle.low) / next_candle.open
        
        # Weighted average with more weight on current candle
        return (current_vol * 0.7 + next_vol * 0.3)
    
    def _analyze_volume_pattern(
        self, 
        current: Candle, 
        next_candle: Candle, 
        trend: TrendDirection
    ) -> VolumePattern:
        volume_change = (next_candle.volume - current.volume) / current.volume if current.volume > 0 else 0
        
        # Strong trends often have front-loaded volume
        if trend in [TrendDirection.UP, TrendDirection.DOWN] and abs(volume_change) > 0.3:
            return VolumePattern.FRONT_LOADED
        
        # Reversals often have back-loaded volume
        price_range = abs(current.close - current.open) / current.open
        if price_range < 0.002 and volume_change > 0.2:  # Small range, increasing volume
            return VolumePattern.BACK_LOADED
        
        # Consolidation often has bell-shaped volume
        if trend == TrendDirection.SIDEWAYS:
            return VolumePattern.BELL_SHAPED
        
        return VolumePattern.RANDOM
    
    def _calculate_pattern_strength(self, current: Candle, next_candle: Candle) -> float:
        # Calculate strength based on multiple factors
        trend_strength = abs(next_candle.close - current.open) / current.open
        volume_strength = min(next_candle.volume / max(current.volume, 1), 2.0) / 2.0
        range_strength = (current.high - current.low) / current.open
        
        # Combine factors
        strength = (trend_strength * 0.5 + volume_strength * 0.3 + range_strength * 0.2)
        return min(strength, 1.0)
```

### 2.2 Price Path Calculator

```python
# backend/fastapi/app/services/price_path_calculator.py
import numpy as np
from typing import List
from .historical_data_fetcher import Candle
from .pattern_analyzer import MarketPattern, TrendDirection

class PricePathCalculator:
    def __init__(self, noise_factor: float = 0.1):
        self.noise_factor = noise_factor
        self.micro_candles_per_minute = 10
    
    def calculate_path(
        self, 
        current: Candle, 
        next_candle: Candle, 
        pattern: MarketPattern
    ) -> List[float]:
        base_path = self._generate_base_path(current, next_candle, pattern)
        noisy_path = self._add_realistic_noise(base_path, pattern)
        constrained_path = self._apply_constraints(noisy_path, current, next_candle)
        
        return constrained_path
    
    def _generate_base_path(
        self, 
        current: Candle, 
        next_candle: Candle, 
        pattern: MarketPattern
    ) -> List[float]:
        path = []
        
        for i in range(self.micro_candles_per_minute + 1):
            progress = i / self.micro_candles_per_minute
            
            if pattern.trend == TrendDirection.UP:
                # Upward trend with pullbacks
                base_price = current.open + (next_candle.close - current.open) * progress
                if i % 3 == 1:  # Add pullback every 3rd point
                    pullback = np.random.uniform(0, 0.002) * current.open
                    base_price -= pullback
            elif pattern.trend == TrendDirection.DOWN:
                # Downward trend with bounces
                base_price = current.open - (current.open - next_candle.close) * progress
                if i % 3 == 1:  # Add bounce every 3rd point
                    bounce = np.random.uniform(0, 0.002) * current.open
                    base_price += bounce
            else:
                # Sideways - oscillate around mean
                mean_price = (current.open + next_candle.close) / 2
                oscillation = np.sin(i * np.pi / 5) * (current.high - current.low) * 0.3
                base_price = mean_price + oscillation
            
            path.append(base_price)
        
        return path
    
    def _add_realistic_noise(self, base_path: List[float], pattern: MarketPattern) -> List[float]:
        noisy_path = []
        
        for i, price in enumerate(base_path):
            # Noise magnitude based on volatility
            noise_magnitude = pattern.volatility * price * self.noise_factor
            
            # Add correlated noise (momentum)
            if i > 0:
                momentum_factor = 0.3  # 30% correlation with previous movement
                prev_change = noisy_path[i-1] - base_path[i-1] if i > 0 else 0
                momentum_noise = momentum_factor * prev_change
            else:
                momentum_noise = 0
            
            # Random noise
            random_noise = np.random.normal(0, noise_magnitude)
            
            # Combine noises
            noisy_price = price + momentum_noise + random_noise
            noisy_path.append(noisy_price)
        
        return noisy_path
    
    def _apply_constraints(
        self, 
        path: List[float], 
        current: Candle, 
        next_candle: Candle
    ) -> List[float]:
        constrained_path = []
        
        # Calculate bounds
        min_bound = min(current.low, next_candle.low)
        max_bound = max(current.high, next_candle.high)
        
        for i, price in enumerate(path):
            # Apply bounds
            constrained_price = max(min_bound, min(max_bound, price))
            
            # Special constraints for first and last points
            if i == 0:
                constrained_price = current.open
            elif i == len(path) - 1:
                # Last point should trend toward next candle open
                trend_factor = 0.7  # 70% toward next open
                target_price = current.open + (next_candle.open - current.open) * trend_factor
                constrained_price = (constrained_price + target_price) / 2
            
            constrained_path.append(constrained_price)
        
        return constrained_path
```

### 2.3 Volume Distributor

```python
# backend/fastapi/app/services/volume_distributor.py
import numpy as np
from typing import List
from .historical_data_fetcher import Candle
from .pattern_analyzer import MarketPattern, VolumePattern

class VolumeDistributor:
    def __init__(self):
        self.micro_candles_per_minute = 10
    
    def distribute(
        self, 
        current_volume: int, 
        next_volume: int, 
        pattern: MarketPattern
    ) -> List[float]:
        # Calculate average volume
        avg_volume = (current_volume + next_volume) / 2
        
        # Get base distribution weights
        weights = self._get_pattern_weights(pattern.volume_pattern)
        
        # Apply pattern strength
        adjusted_weights = self._apply_pattern_strength(weights, pattern.strength)
        
        # Normalize to ensure sum equals 1
        normalized_weights = np.array(adjusted_weights)
        normalized_weights = normalized_weights / np.sum(normalized_weights)
        
        # Calculate volume for each micro-candle
        micro_volumes = (normalized_weights * avg_volume).tolist()
        
        return micro_volumes
    
    def _get_pattern_weights(self, pattern: VolumePattern) -> List[float]:
        if pattern == VolumePattern.FRONT_LOADED:
            # Exponential decay
            weights = [np.exp(-0.5 * i) for i in range(self.micro_candles_per_minute)]
        elif pattern == VolumePattern.BACK_LOADED:
            # Exponential growth
            weights = [np.exp(-0.5 * (self.micro_candles_per_minute - 1 - i)) for i in range(self.micro_candles_per_minute)]
        elif pattern == VolumePattern.U_SHAPED:
            # High at start and end, low in middle
            weights = [1 - abs(i - 4.5) / 4.5 for i in range(self.micro_candles_per_minute)]
        elif pattern == VolumePattern.BELL_SHAPED:
            # Normal distribution centered in middle
            weights = [np.exp(-((i - 4.5) ** 2) / 8) for i in range(self.micro_candles_per_minute)]
        else:  # RANDOM
            # Random with slight bias toward middle
            weights = [np.random.uniform(0.5, 1.5) for _ in range(self.micro_candles_per_minute)]
        
        return weights
    
    def _apply_pattern_strength(self, weights: List[float], strength: float) -> List[float]:
        # Reduce pattern variation for weak patterns
        if strength < 0.5:
            # Move toward uniform distribution
            uniform_weight = 1.0 / len(weights)
            adjusted_weights = [
                w * strength + uniform_weight * (1 - strength) 
                for w in weights
            ]
            return adjusted_weights
        
        return weights
```

## Phase 3: Integration Components

### 3.1 Micro-Candle Generator Main Class

```python
# backend/fastapi/app/services/micro_candle_generator.py
from typing import List, Optional
from dataclasses import dataclass
from datetime import timedelta
from .historical_data_fetcher import Candle
from .pattern_analyzer import PatternAnalyzer, MarketPattern
from .price_path_calculator import PricePathCalculator
from .volume_distributor import VolumeDistributor

@dataclass
class MicroCandle:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    def to_tick(self):
        """Convert micro-candle to tick format for replay system"""
        return {
            'timestamp': self.timestamp,
            'price': self.close,
            'volume': self.volume,
            'micro_candle': True
        }

@dataclass
class MicroCandleConfig:
    micro_candles_per_minute: int = 10
    noise_factor: float = 0.1
    volatility_smoothing: float = 0.5
    enable_trend_following: bool = True
    enable_mean_reversion: bool = True
    enable_volatility_expansion: bool = True
    max_price_deviation: float = 0.05
    min_volume_per_micro: float = 0.01

class MicroCandleGenerator:
    def __init__(self, config: Optional[MicroCandleConfig] = None):
        self.config = config or MicroCandleConfig()
        self.pattern_analyzer = PatternAnalyzer()
        self.price_calculator = PricePathCalculator(self.config.noise_factor)
        self.volume_distributor = VolumeDistributor()
    
    def generate_micro_candles(
        self, 
        current: Candle, 
        next_candle: Candle
    ) -> List[MicroCandle]:
        # Analyze market pattern
        pattern = self.pattern_analyzer.analyze(current, next_candle)
        
        # Generate price path
        price_path = self.price_calculator.calculate_path(current, next_candle, pattern)
        
        # Distribute volume
        volume_distribution = self.volume_distributor.distribute(
            current.volume, next_candle.volume, pattern
        )
        
        # Create micro-candles
        micro_candles = []
        for i in range(self.config.micro_candles_per_minute):
            timestamp = current.timestamp + timedelta(seconds=i * 6)
            
            # Calculate OHLC for micro-candle
            open_price = price_path[i]
            close_price = price_path[i + 1]
            high_price = max(price_path[i:i + 2])
            low_price = min(price_path[i:i + 2])
            
            micro_candle = MicroCandle(
                timestamp=timestamp.isoformat(),
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=int(volume_distribution[i])
            )
            micro_candles.append(micro_candle)
        
        return micro_candles
    
    def generate_batch(
        self, 
        candles: List[Candle]
    ) -> List[MicroCandle]:
        if len(candles) < 2:
            return []
        
        all_micro_candles = []
        
        for i in range(len(candles) - 1):
            current = candles[i]
            next_candle = candles[i + 1]
            
            micro_candles = self.generate_micro_candles(current, next_candle)
            all_micro_candles.extend(micro_candles)
        
        return all_micro_candles
```

## Phase 4: API Integration

### 4.1 Enhanced API Endpoints

```python
# backend/fastapi/app/api/micro_candle_backtesting.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from ..services.micro_candle_generator import MicroCandleGenerator, MicroCandleConfig
from ..services.historical_data_fetcher import HistoricalDataFetcher, OpenAlgoDataSource
from ..services.data_validator import DataValidator

router = APIRouter(prefix="/api/v1/micro-candle", tags=["micro-candle"])

# Global instances
data_fetcher = None
micro_generator = None

async def get_data_fetcher():
    global data_fetcher
    if data_fetcher is None:
        # Initialize with your data source
        data_source = OpenAlgoDataSource(
            api_key="your-api-key",
            base_url="http://localhost:3000"
        )
        data_fetcher = HistoricalDataFetcher(data_source)
    return data_fetcher

async def get_micro_generator():
    global micro_generator
    if micro_generator is None:
        micro_generator = MicroCandleGenerator()
    return micro_generator

@router.post("/generate")
async def generate_micro_candles(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    config: Optional[MicroCandleConfig] = None,
    data_fetcher: HistoricalDataFetcher = Depends(get_data_fetcher),
    generator: MicroCandleGenerator = Depends(get_micro_generator)
):
    """Generate micro-candles for historical backtesting"""
    try:
        # Fetch historical data
        candles = await data_fetcher.fetch_with_buffer(symbol, start_date, end_date)
        
        # Validate data
        is_valid, errors = DataValidator.validate_candle_data(candles)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid data: {errors}")
        
        # Clean and fill missing data
        candles = DataValidator.clean_candle_data(candles)
        candles = DataValidator.fill_missing_candles(candles)
        
        # Update generator config if provided
        if config:
            generator.config = config
        
        # Generate micro-candles
        micro_candles = generator.generate_batch(candles)
        
        return {
            "symbol": symbol,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "original_candles": len(candles),
            "micro_candles_generated": len(micro_candles),
            "micro_candles": [mc.__dict__ for mc in micro_candles]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_generator_config():
    """Get current micro-candle generator configuration"""
    generator = await get_micro_generator()
    return generator.config

@router.post("/config")
async def update_generator_config(config: MicroCandleConfig):
    """Update micro-candle generator configuration"""
    generator = await get_micro_generator()
    generator.config = config
    return {"message": "Configuration updated successfully"}
```

This implementation plan provides a comprehensive framework for generating realistic micro-candles that can be integrated with the existing historical replay system for more granular backtesting of trading strategies.