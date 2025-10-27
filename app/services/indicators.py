"""
Technical indicators service using the ta library.
Calculates 43+ technical indicators across all categories.
"""

from typing import Dict, List, Optional, Any

import pandas as pd
import ta

from app.core.logging import LoggerMixin


class IndicatorService(LoggerMixin):
    """
    Service for calculating technical indicators.
    
    Supports 43+ indicators from the ta library organized by category:
    - Volume indicators
    - Volatility indicators
    - Trend indicators
    - Momentum indicators
    - Others
    """
    
    def __init__(self):
        """Initialize the indicator service."""
        self.logger.info("IndicatorService initialized")
    
    def calculate_all_indicators(
        self,
        df: pd.DataFrame,
        params: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, pd.Series]:
        """
        Calculate all 43+ technical indicators.
        
        Args:
            df: DataFrame with OHLCV columns (open, high, low, close, volume)
            params: Optional custom parameters for specific indicators
        
        Returns:
            Dict[str, pd.Series]: Dictionary of indicator name to values
        
        Example:
            >>> service = IndicatorService()
            >>> indicators = service.calculate_all_indicators(df)
            >>> rsi = indicators['RSI']
        """
        params = params or {}
        indicators = {}
        
        self.logger.info("Calculating all indicators")
        
        # Volume Indicators
        indicators.update(self._calculate_volume_indicators(df, params))
        
        # Volatility Indicators
        indicators.update(self._calculate_volatility_indicators(df, params))
        
        # Trend Indicators
        indicators.update(self._calculate_trend_indicators(df, params))
        
        # Momentum Indicators
        indicators.update(self._calculate_momentum_indicators(df, params))
        
        # Others
        indicators.update(self._calculate_other_indicators(df, params))
        
        self.logger.info(f"Calculated {len(indicators)} indicators")
        
        return indicators
    
    def _calculate_volume_indicators(
        self,
        df: pd.DataFrame,
        params: Dict[str, Dict[str, Any]]
    ) -> Dict[str, pd.Series]:
        """Calculate volume-based indicators."""
        indicators = {}
        
        try:
            # Money Flow Index
            mfi_params = params.get('MFI', {})
            indicators['MFI'] = ta.volume.MFIIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                volume=df['volume'],
                window=mfi_params.get('window', 14)
            ).money_flow_index()
            
            # Accumulation/Distribution Index
            indicators['ADI'] = ta.volume.AccDistIndexIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                volume=df['volume']
            ).acc_dist_index()
            
            # On-Balance Volume
            indicators['OBV'] = ta.volume.OnBalanceVolumeIndicator(
                close=df['close'],
                volume=df['volume']
            ).on_balance_volume()
            
            # Chaikin Money Flow
            cmf_params = params.get('CMF', {})
            indicators['CMF'] = ta.volume.ChaikinMoneyFlowIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                volume=df['volume'],
                window=cmf_params.get('window', 20)
            ).chaikin_money_flow()
            
            # Force Index
            fi_params = params.get('ForceIndex', {})
            indicators['ForceIndex'] = ta.volume.ForceIndexIndicator(
                close=df['close'],
                volume=df['volume'],
                window=fi_params.get('window', 13)
            ).force_index()
            
            # Ease of Movement
            eom_params = params.get('EaseOfMovement', {})
            indicators['EaseOfMovement'] = ta.volume.EaseOfMovementIndicator(
                high=df['high'],
                low=df['low'],
                volume=df['volume'],
                window=eom_params.get('window', 14)
            ).ease_of_movement()
            
            # Volume Price Trend
            indicators['VPT'] = ta.volume.VolumePriceTrendIndicator(
                close=df['close'],
                volume=df['volume']
            ).volume_price_trend()
            
            # Negative Volume Index
            indicators['NVI'] = ta.volume.NegativeVolumeIndexIndicator(
                close=df['close'],
                volume=df['volume']
            ).negative_volume_index()
            
            # Volume Weighted Average Price
            vwap_params = params.get('VWAP', {})
            indicators['VWAP'] = ta.volume.VolumeWeightedAveragePrice(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                volume=df['volume'],
                window=vwap_params.get('window', 14)
            ).volume_weighted_average_price()
            
        except Exception as e:
            self.logger.error(f"Error calculating volume indicators: {e}")
        
        return indicators
    
    def _calculate_volatility_indicators(
        self,
        df: pd.DataFrame,
        params: Dict[str, Dict[str, Any]]
    ) -> Dict[str, pd.Series]:
        """Calculate volatility indicators."""
        indicators = {}
        
        try:
            # Average True Range
            atr_params = params.get('ATR', {})
            atr = ta.volatility.AverageTrueRange(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=atr_params.get('window', 14)
            )
            indicators['ATR'] = atr.average_true_range()
            
            # Bollinger Bands
            bb_params = params.get('BollingerBands', {})
            bb = ta.volatility.BollingerBands(
                close=df['close'],
                window=bb_params.get('window', 20),
                window_dev=bb_params.get('window_dev', 2)
            )
            indicators['BB_High'] = bb.bollinger_hband()
            indicators['BB_Mid'] = bb.bollinger_mavg()
            indicators['BB_Low'] = bb.bollinger_lband()
            indicators['BB_Width'] = bb.bollinger_wband()
            indicators['BB_Percent'] = bb.bollinger_pband()
            
            # Keltner Channel
            kc_params = params.get('KeltnerChannel', {})
            kc = ta.volatility.KeltnerChannel(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=kc_params.get('window', 20)
            )
            indicators['KC_High'] = kc.keltner_channel_hband()
            indicators['KC_Mid'] = kc.keltner_channel_mband()
            indicators['KC_Low'] = kc.keltner_channel_lband()
            
            # Donchian Channel
            dc_params = params.get('DonchianChannel', {})
            dc = ta.volatility.DonchianChannel(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=dc_params.get('window', 20)
            )
            indicators['DC_High'] = dc.donchian_channel_hband()
            indicators['DC_Mid'] = dc.donchian_channel_mband()
            indicators['DC_Low'] = dc.donchian_channel_lband()
            
            # Ulcer Index
            ui_params = params.get('UlcerIndex', {})
            indicators['UlcerIndex'] = ta.volatility.UlcerIndex(
                close=df['close'],
                window=ui_params.get('window', 14)
            ).ulcer_index()
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility indicators: {e}")
        
        return indicators
    
    def _calculate_trend_indicators(
        self,
        df: pd.DataFrame,
        params: Dict[str, Dict[str, Any]]
    ) -> Dict[str, pd.Series]:
        """Calculate trend indicators."""
        indicators = {}
        
        try:
            # Simple Moving Average
            for period in [10, 20, 50, 200]:
                sma_params = params.get(f'SMA_{period}', {})
                indicators[f'SMA_{period}'] = ta.trend.SMAIndicator(
                    close=df['close'],
                    window=sma_params.get('window', period)
                ).sma_indicator()
            
            # Exponential Moving Average
            for period in [12, 20, 26, 50]:
                ema_params = params.get(f'EMA_{period}', {})
                indicators[f'EMA_{period}'] = ta.trend.EMAIndicator(
                    close=df['close'],
                    window=ema_params.get('window', period)
                ).ema_indicator()
            
            # Weighted Moving Average
            wma_params = params.get('WMA', {})
            indicators['WMA'] = ta.trend.WMAIndicator(
                close=df['close'],
                window=wma_params.get('window', 20)
            ).wma()
            
            # MACD
            macd_params = params.get('MACD', {})
            macd = ta.trend.MACD(
                close=df['close'],
                window_slow=macd_params.get('window_slow', 26),
                window_fast=macd_params.get('window_fast', 12),
                window_sign=macd_params.get('window_sign', 9)
            )
            indicators['MACD'] = macd.macd()
            indicators['MACD_Signal'] = macd.macd_signal()
            indicators['MACD_Diff'] = macd.macd_diff()
            
            # ADX
            adx_params = params.get('ADX', {})
            adx = ta.trend.ADXIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=adx_params.get('window', 14)
            )
            indicators['ADX'] = adx.adx()
            indicators['ADX_Pos'] = adx.adx_pos()
            indicators['ADX_Neg'] = adx.adx_neg()
            
            # Vortex Indicator
            vi_params = params.get('VortexIndicator', {})
            vi = ta.trend.VortexIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=vi_params.get('window', 14)
            )
            indicators['VI_Pos'] = vi.vortex_indicator_pos()
            indicators['VI_Neg'] = vi.vortex_indicator_neg()
            
            # TRIX
            trix_params = params.get('TRIX', {})
            indicators['TRIX'] = ta.trend.TRIXIndicator(
                close=df['close'],
                window=trix_params.get('window', 15)
            ).trix()
            
            # Mass Index
            mi_params = params.get('MassIndex', {})
            indicators['MassIndex'] = ta.trend.MassIndex(
                high=df['high'],
                low=df['low'],
                window_fast=mi_params.get('window_fast', 9),
                window_slow=mi_params.get('window_slow', 25)
            ).mass_index()
            
            # CCI
            cci_params = params.get('CCI', {})
            indicators['CCI'] = ta.trend.CCIIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=cci_params.get('window', 20)
            ).cci()
            
            # DPO
            dpo_params = params.get('DPO', {})
            indicators['DPO'] = ta.trend.DPOIndicator(
                close=df['close'],
                window=dpo_params.get('window', 20)
            ).dpo()
            
            # KST
            indicators['KST'] = ta.trend.KSTIndicator(
                close=df['close']
            ).kst()
            indicators['KST_Signal'] = ta.trend.KSTIndicator(
                close=df['close']
            ).kst_sig()
            
            # Ichimoku
            ichimoku = ta.trend.IchimokuIndicator(
                high=df['high'],
                low=df['low']
            )
            indicators['Ichimoku_A'] = ichimoku.ichimoku_a()
            indicators['Ichimoku_B'] = ichimoku.ichimoku_b()
            indicators['Ichimoku_Base'] = ichimoku.ichimoku_base_line()
            indicators['Ichimoku_Conversion'] = ichimoku.ichimoku_conversion_line()
            
            # Parabolic SAR
            psar_params = params.get('PSAR', {})
            psar = ta.trend.PSARIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                step=psar_params.get('step', 0.02),
                max_step=psar_params.get('max_step', 0.2)
            )
            indicators['PSAR'] = psar.psar()
            indicators['PSAR_Up'] = psar.psar_up()
            indicators['PSAR_Down'] = psar.psar_down()
            
            # STC
            stc_params = params.get('STC', {})
            indicators['STC'] = ta.trend.STCIndicator(
                close=df['close'],
                window_slow=stc_params.get('window_slow', 50),
                window_fast=stc_params.get('window_fast', 23)
            ).stc()
            
            # Aroon
            aroon_params = params.get('Aroon', {})
            aroon = ta.trend.AroonIndicator(
                high=df['high'],
                low=df['low'],
                window=aroon_params.get('window', 25)
            )
            indicators['Aroon_Up'] = aroon.aroon_up()
            indicators['Aroon_Down'] = aroon.aroon_down()
            indicators['Aroon_Indicator'] = aroon.aroon_indicator()
            
        except Exception as e:
            self.logger.error(f"Error calculating trend indicators: {e}")
        
        return indicators
    
    def _calculate_momentum_indicators(
        self,
        df: pd.DataFrame,
        params: Dict[str, Dict[str, Any]]
    ) -> Dict[str, pd.Series]:
        """Calculate momentum indicators."""
        indicators = {}
        
        try:
            # RSI
            rsi_params = params.get('RSI', {})
            indicators['RSI'] = ta.momentum.RSIIndicator(
                close=df['close'],
                window=rsi_params.get('window', 14)
            ).rsi()
            
            # Stochastic RSI
            stochrsi_params = params.get('StochRSI', {})
            stochrsi = ta.momentum.StochRSIIndicator(
                close=df['close'],
                window=stochrsi_params.get('window', 14),
                smooth1=stochrsi_params.get('smooth1', 3),
                smooth2=stochrsi_params.get('smooth2', 3)
            )
            indicators['StochRSI'] = stochrsi.stochrsi()
            indicators['StochRSI_K'] = stochrsi.stochrsi_k()
            indicators['StochRSI_D'] = stochrsi.stochrsi_d()
            
            # TSI
            tsi_params = params.get('TSI', {})
            indicators['TSI'] = ta.momentum.TSIIndicator(
                close=df['close'],
                window_slow=tsi_params.get('window_slow', 25),
                window_fast=tsi_params.get('window_fast', 13)
            ).tsi()
            
            # Ultimate Oscillator
            uo_params = params.get('UltimateOscillator', {})
            indicators['UltimateOscillator'] = ta.momentum.UltimateOscillator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window1=uo_params.get('window1', 7),
                window2=uo_params.get('window2', 14),
                window3=uo_params.get('window3', 28)
            ).ultimate_oscillator()
            
            # Stochastic Oscillator
            stoch_params = params.get('StochasticOscillator', {})
            stoch = ta.momentum.StochasticOscillator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=stoch_params.get('window', 14),
                smooth_window=stoch_params.get('smooth_window', 3)
            )
            indicators['Stoch_K'] = stoch.stoch()
            indicators['Stoch_D'] = stoch.stoch_signal()
            
            # Williams %R
            wr_params = params.get('WilliamsR', {})
            indicators['WilliamsR'] = ta.momentum.WilliamsRIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                lbp=wr_params.get('lbp', 14)
            ).williams_r()
            
            # Awesome Oscillator
            indicators['AwesomeOscillator'] = ta.momentum.AwesomeOscillatorIndicator(
                high=df['high'],
                low=df['low']
            ).awesome_oscillator()
            
            # KAMA
            kama_params = params.get('KAMA', {})
            indicators['KAMA'] = ta.momentum.KAMAIndicator(
                close=df['close'],
                window=kama_params.get('window', 10),
                pow1=kama_params.get('pow1', 2),
                pow2=kama_params.get('pow2', 30)
            ).kama()
            
            # ROC
            roc_params = params.get('ROC', {})
            indicators['ROC'] = ta.momentum.ROCIndicator(
                close=df['close'],
                window=roc_params.get('window', 12)
            ).roc()
            
            # PPO
            ppo_params = params.get('PPO', {})
            ppo = ta.momentum.PercentagePriceOscillator(
                close=df['close'],
                window_slow=ppo_params.get('window_slow', 26),
                window_fast=ppo_params.get('window_fast', 12),
                window_sign=ppo_params.get('window_sign', 9)
            )
            indicators['PPO'] = ppo.ppo()
            indicators['PPO_Signal'] = ppo.ppo_signal()
            indicators['PPO_Hist'] = ppo.ppo_hist()
            
            # PVO
            pvo_params = params.get('PVO', {})
            pvo = ta.momentum.PercentageVolumeOscillator(
                volume=df['volume'],
                window_slow=pvo_params.get('window_slow', 26),
                window_fast=pvo_params.get('window_fast', 12),
                window_sign=pvo_params.get('window_sign', 9)
            )
            indicators['PVO'] = pvo.pvo()
            indicators['PVO_Signal'] = pvo.pvo_signal()
            indicators['PVO_Hist'] = pvo.pvo_hist()
            
        except Exception as e:
            self.logger.error(f"Error calculating momentum indicators: {e}")
        
        return indicators
    
    def _calculate_other_indicators(
        self,
        df: pd.DataFrame,
        params: Dict[str, Dict[str, Any]]
    ) -> Dict[str, pd.Series]:
        """Calculate other indicators."""
        indicators = {}
        
        try:
            # Daily Return
            indicators['DailyReturn'] = ta.others.DailyReturnIndicator(
                close=df['close']
            ).daily_return()
            
            # Daily Log Return
            indicators['DailyLogReturn'] = ta.others.DailyLogReturnIndicator(
                close=df['close']
            ).daily_log_return()
            
            # Cumulative Return
            indicators['CumulativeReturn'] = ta.others.CumulativeReturnIndicator(
                close=df['close']
            ).cumulative_return()
            
        except Exception as e:
            self.logger.error(f"Error calculating other indicators: {e}")
        
        return indicators
    
    def calculate_specific_indicators(
        self,
        df: pd.DataFrame,
        indicator_list: List[str],
        params: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, pd.Series]:
        """
        Calculate specific indicators from a list.
        
        Args:
            df: DataFrame with OHLCV data
            indicator_list: List of indicator names to calculate
            params: Optional custom parameters
        
        Returns:
            Dict[str, pd.Series]: Dictionary of requested indicators
        
        Example:
            >>> indicators = service.calculate_specific_indicators(
            ...     df, ["RSI", "MACD", "EMA_20"]
            ... )
        """
        params = params or {}
        all_indicators = self.calculate_all_indicators(df, params)
        
        # Filter to requested indicators
        result = {}
        for indicator_name in indicator_list:
            if indicator_name in all_indicators:
                result[indicator_name] = all_indicators[indicator_name]
            else:
                self.logger.warning(f"Indicator not found: {indicator_name}")
        
        return result
    
    def format_indicators_for_response(
        self,
        indicators: Dict[str, pd.Series]
    ) -> Dict[str, List[float]]:
        """
        Format indicators for JSON response.
        
        Converts pandas Series to lists and handles NaN values.
        
        Args:
            indicators: Dictionary of indicator Series
        
        Returns:
            Dict[str, List[float]]: Formatted indicators
        """
        formatted = {}
        
        for name, series in indicators.items():
            # Convert to list, replacing NaN with None
            values = series.replace({pd.NA: None}).tolist()
            formatted[name] = values
        
        return formatted
    
    def calculate_indicators_realtime(
        self,
        candles: pd.DataFrame,
        previous_indicators: Optional[Dict[str, pd.Series]] = None
    ) -> Dict[str, pd.Series]:
        """
        Calculate indicators for real-time updates.
        
        This is optimized for incremental updates where only the
        latest values need to be calculated.
        
        Args:
            candles: Recent candles DataFrame
            previous_indicators: Previously calculated indicators
        
        Returns:
            Dict[str, pd.Series]: Updated indicators
        """
        # For now, recalculate all indicators
        # TODO: Optimize for incremental calculation
        return self.calculate_all_indicators(candles)


# Convenience function
def get_indicator_service() -> IndicatorService:
    """
    Get IndicatorService instance.
    
    Returns:
        IndicatorService: Service instance
    """
    return IndicatorService()
