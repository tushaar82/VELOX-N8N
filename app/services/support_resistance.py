"""
Support and Resistance level calculation service.
Uses swing highs/lows with ATR clustering algorithm.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from app.core.logging import LoggerMixin
from app.schemas.indicators import SupportResistanceLevel, SupportResistanceResponse


class SupportResistanceService(LoggerMixin):
    """
    Service for calculating support and resistance levels.
    
    Uses advanced algorithms:
    - Swing extrema detection with find_peaks
    - ATR-based dynamic prominence
    - Recency and volume weighting
    - Level clustering
    """
    
    def __init__(self):
        """Initialize the support/resistance service."""
        self.logger.info("SupportResistanceService initialized")
    
    def calculate_atr(
        self,
        df: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range.
        
        Args:
            df: DataFrame with high, low, close columns
            period: ATR period
        
        Returns:
            pd.Series: ATR values
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range calculation
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR is the moving average of TR
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def find_swing_extrema(
        self,
        df: pd.DataFrame,
        window: int = 3,
        prominence_mult: float = 0.5
    ) -> pd.DataFrame:
        """
        Find swing highs and lows using peak detection.
        
        Args:
            df: DataFrame with OHLCV data
            window: Window size for peak detection
            prominence_mult: Multiplier for ATR-based prominence
        
        Returns:
            pd.DataFrame: DataFrame with extrema points
        """
        # Calculate ATR for dynamic prominence
        atr = self.calculate_atr(df)
        avg_atr = atr.mean()
        prominence = avg_atr * prominence_mult
        
        # Find resistance levels (swing highs)
        resistance_peaks, resistance_properties = find_peaks(
            df['high'].values,
            distance=window,
            prominence=prominence
        )
        
        # Find support levels (swing lows) - invert the data
        support_peaks, support_properties = find_peaks(
            -df['low'].values,
            distance=window,
            prominence=prominence
        )
        
        # Create DataFrame for resistance levels
        resistance_df = pd.DataFrame({
            'price': df.iloc[resistance_peaks]['high'].values,
            'timestamp': df.iloc[resistance_peaks]['timestamp'].values,
            'type': 'resistance',
            'volume': df.iloc[resistance_peaks]['volume'].values,
            'index': resistance_peaks
        })
        
        # Create DataFrame for support levels
        support_df = pd.DataFrame({
            'price': df.iloc[support_peaks]['low'].values,
            'timestamp': df.iloc[support_peaks]['timestamp'].values,
            'type': 'support',
            'volume': df.iloc[support_peaks]['volume'].values,
            'index': support_peaks
        })
        
        # Combine and sort
        extrema_df = pd.concat([resistance_df, support_df], ignore_index=True)
        extrema_df = extrema_df.sort_values('timestamp').reset_index(drop=True)
        
        self.logger.info(
            f"Found {len(resistance_df)} resistance and {len(support_df)} support extrema"
        )
        
        return extrema_df
    
    def cluster_levels(
        self,
        points_df: pd.DataFrame,
        df: pd.DataFrame,
        half_life_bars: int = 200,
        atr_mult: float = 1.0
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Cluster nearby levels using ATR tolerance and weighting.
        
        Args:
            points_df: DataFrame with extrema points
            df: Original OHLCV DataFrame
            half_life_bars: Half-life for recency weighting
            atr_mult: Multiplier for ATR-based tolerance
        
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (support_levels, resistance_levels)
        """
        # Calculate ATR-based tolerance
        atr = self.calculate_atr(df)
        tolerance = atr.mean() * atr_mult
        
        # Separate support and resistance
        support_points = points_df[points_df['type'] == 'support'].copy()
        resistance_points = points_df[points_df['type'] == 'resistance'].copy()
        
        # Cluster support levels
        support_levels = self._cluster_points(
            support_points, df, tolerance, half_life_bars, 'support'
        )
        
        # Cluster resistance levels
        resistance_levels = self._cluster_points(
            resistance_points, df, tolerance, half_life_bars, 'resistance'
        )
        
        return support_levels, resistance_levels
    
    def _cluster_points(
        self,
        points: pd.DataFrame,
        df: pd.DataFrame,
        tolerance: float,
        half_life_bars: int,
        level_type: str
    ) -> pd.DataFrame:
        """
        Cluster individual points into levels.
        
        Args:
            points: DataFrame with extrema points
            df: Original OHLCV DataFrame
            tolerance: Price tolerance for clustering
            half_life_bars: Half-life for recency weighting
            level_type: 'support' or 'resistance'
        
        Returns:
            pd.DataFrame: Clustered levels
        """
        if len(points) == 0:
            return pd.DataFrame(columns=['price', 'strength', 'touches', 'last_touch'])
        
        # Sort by price
        points = points.sort_values('price').reset_index(drop=True)
        
        # Calculate recency weights (exponential decay)
        total_bars = len(df)
        decay_rate = np.log(2) / half_life_bars
        points['bars_ago'] = total_bars - points['index']
        points['recency_weight'] = np.exp(-decay_rate * points['bars_ago'])
        
        # Normalize volume for weighting
        max_volume = points['volume'].max()
        if max_volume > 0:
            points['volume_weight'] = points['volume'] / max_volume
        else:
            points['volume_weight'] = 1.0
        
        # Combined weight
        points['weight'] = points['recency_weight'] * points['volume_weight']
        
        # Cluster nearby points
        clusters = []
        used = set()
        
        for i, row in points.iterrows():
            if i in used:
                continue
            
            # Find all points within tolerance
            cluster_mask = (
                (abs(points['price'] - row['price']) <= tolerance) &
                (~points.index.isin(used))
            )
            cluster_points = points[cluster_mask]
            
            # Mark as used
            used.update(cluster_points.index.tolist())
            
            # Calculate weighted average price
            total_weight = cluster_points['weight'].sum()
            if total_weight > 0:
                avg_price = (cluster_points['price'] * cluster_points['weight']).sum() / total_weight
            else:
                avg_price = cluster_points['price'].mean()
            
            # Calculate strength (0-1 scale)
            strength = min(1.0, total_weight / len(points))
            
            # Get last touch timestamp
            last_touch = cluster_points['timestamp'].max()
            
            clusters.append({
                'price': avg_price,
                'strength': strength,
                'touches': len(cluster_points),
                'last_touch': last_touch,
                'level_type': level_type
            })
        
        # Create DataFrame and sort by strength
        levels_df = pd.DataFrame(clusters)
        levels_df = levels_df.sort_values('strength', ascending=False).reset_index(drop=True)
        
        return levels_df
    
    def compute_support_resistance(
        self,
        df: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> SupportResistanceResponse:
        """
        Compute support and resistance levels.
        
        Args:
            df: DataFrame with OHLCV data
            params: Optional parameters for customization
        
        Returns:
            SupportResistanceResponse: Complete S/R analysis
        
        Example:
            >>> service = SupportResistanceService()
            >>> response = service.compute_support_resistance(df)
            >>> print(response.support_levels)
        """
        params = params or {}
        
        # Extract parameters
        window = params.get('window', 3)
        prominence_mult = params.get('prominence_mult', 0.5)
        half_life_bars = params.get('half_life_bars', 200)
        atr_mult = params.get('atr_mult', 1.0)
        max_levels = params.get('max_levels', 10)
        
        self.logger.info("Computing support and resistance levels")
        
        # Find swing extrema
        extrema_df = self.find_swing_extrema(df, window, prominence_mult)
        
        # Cluster levels
        support_df, resistance_df = self.cluster_levels(
            extrema_df, df, half_life_bars, atr_mult
        )
        
        # Calculate tolerance
        atr = self.calculate_atr(df)
        tolerance = atr.mean() * atr_mult
        
        # Get current price
        current_price = float(df.iloc[-1]['close'])
        
        # Convert to SupportResistanceLevel models
        support_levels = []
        for _, row in support_df.head(max_levels).iterrows():
            level = SupportResistanceLevel(
                price=float(row['price']),
                level_type='support',
                strength=float(row['strength']),
                touches=int(row['touches']),
                last_touch=row['last_touch']
            )
            support_levels.append(level)
        
        resistance_levels = []
        for _, row in resistance_df.head(max_levels).iterrows():
            level = SupportResistanceLevel(
                price=float(row['price']),
                level_type='resistance',
                strength=float(row['strength']),
                touches=int(row['touches']),
                last_touch=row['last_touch']
            )
            resistance_levels.append(level)
        
        # Create response
        response = SupportResistanceResponse(
            symbol=params.get('symbol', 'UNKNOWN'),
            timeframe=params.get('timeframe', 'UNKNOWN'),
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            tolerance=float(tolerance),
            current_price=current_price,
            metadata={
                'total_extrema': len(extrema_df),
                'window': window,
                'prominence_mult': prominence_mult,
                'half_life_bars': half_life_bars,
                'atr_mult': atr_mult,
                'method': 'swing_extrema_atr_clustering'
            }
        )
        
        self.logger.info(
            f"Found {len(support_levels)} support and {len(resistance_levels)} resistance levels"
        )
        
        return response
    
    def calculate_pivot_points(
        self,
        df: pd.DataFrame,
        method: str = 'standard'
    ) -> Dict[str, float]:
        """
        Calculate classic pivot points.
        
        Args:
            df: DataFrame with OHLCV data
            method: Pivot calculation method ('standard', 'fibonacci', 'woodie')
        
        Returns:
            Dict[str, float]: Pivot points (PP, R1, R2, R3, S1, S2, S3)
        """
        # Use last complete candle
        high = float(df.iloc[-1]['high'])
        low = float(df.iloc[-1]['low'])
        close = float(df.iloc[-1]['close'])
        
        if method == 'standard':
            pp = (high + low + close) / 3
            r1 = 2 * pp - low
            r2 = pp + (high - low)
            r3 = high + 2 * (pp - low)
            s1 = 2 * pp - high
            s2 = pp - (high - low)
            s3 = low - 2 * (high - pp)
            
        elif method == 'fibonacci':
            pp = (high + low + close) / 3
            r1 = pp + 0.382 * (high - low)
            r2 = pp + 0.618 * (high - low)
            r3 = pp + 1.000 * (high - low)
            s1 = pp - 0.382 * (high - low)
            s2 = pp - 0.618 * (high - low)
            s3 = pp - 1.000 * (high - low)
            
        elif method == 'woodie':
            pp = (high + low + 2 * close) / 4
            r1 = 2 * pp - low
            r2 = pp + (high - low)
            r3 = high + 2 * (pp - low)
            s1 = 2 * pp - high
            s2 = pp - (high - low)
            s3 = low - 2 * (high - pp)
            
        else:
            raise ValueError(f"Unknown pivot method: {method}")
        
        return {
            'PP': pp,
            'R1': r1,
            'R2': r2,
            'R3': r3,
            'S1': s1,
            'S2': s2,
            'S3': s3
        }
    
    def filter_top_levels(
        self,
        levels: List[SupportResistanceLevel],
        top_n: int = 5
    ) -> List[SupportResistanceLevel]:
        """
        Filter to top N levels by strength.
        
        Args:
            levels: List of support/resistance levels
            top_n: Number of top levels to return
        
        Returns:
            List[SupportResistanceLevel]: Top N levels
        """
        # Sort by strength descending
        sorted_levels = sorted(levels, key=lambda x: x.strength, reverse=True)
        return sorted_levels[:top_n]


# Convenience function
def get_support_resistance_service() -> SupportResistanceService:
    """
    Get SupportResistanceService instance.
    
    Returns:
        SupportResistanceService: Service instance
    """
    return SupportResistanceService()
