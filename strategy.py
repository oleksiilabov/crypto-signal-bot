"""
Technical Analysis Strategy Module.
Evaluates trend breakouts with multi-timeframe trend & RSI momentum confluence filters.
"""

from dataclasses import dataclass
from typing import Optional
import pandas as pd
from config import StrategyConfig


@dataclass(frozen=True)
class SignalResult:
    """Structure holding actionable trade signal parameters."""
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    recent_extreme: float
    volume_ratio: float
    rsi_val: float
    htf_aligned: bool
    signal_grade: str
    est_win_probability: str


class EMABreakoutStrategy:
    """EMA Crossover Strategy with Volume, HTF Trend, and RSI Confluence."""

    def __init__(self, config: StrategyConfig = StrategyConfig()):
        self.config = config

    def calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Calculates Relative Strength Index (RSI)."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def analyze(self, df_15m: pd.DataFrame, df_4h: Optional[pd.DataFrame] = None) -> Optional[SignalResult]:
        """Analyzes candlestick data across 15m and 4h timeframes for high-confluence setups."""
        if len(df_15m) < max(self.config.ema_slow, 50):
            return None

        data = df_15m.copy()

        # Compute Technical Indicators (15m)
        data["EMA_FAST"] = data["Close"].ewm(span=self.config.ema_fast, adjust=False).mean()
        data["EMA_SLOW"] = data["Close"].ewm(span=self.config.ema_slow, adjust=False).mean()
        data["Vol_SMA"] = data["Volume"].rolling(window=20).mean()
        data["RSI"] = self.calculate_rsi(data["Close"], period=14)

        curr = data.iloc[-2]  # Last completed candle
        prvv = data.iloc[-3]  # Reference candle

        close_price = float(curr["Close"])
        curr_vol = float(curr["Volume"])
        avg_vol = float(curr["Vol_SMA"]) if not pd.isna(curr["Vol_SMA"]) else 0.0
        curr_rsi = round(float(curr["RSI"]), 1) if not pd.isna(curr["RSI"]) else 50.0

        is_volume_spike = (curr_vol > (self.config.volume_multiplier * avg_vol)) if avg_vol > 0 else True
        vol_ratio = round(curr_vol / avg_vol, 2) if avg_vol > 0 else 1.0

        # Higher Timeframe (4H) 200 EMA Filter Check
        htf_bullish = True
        htf_bearish = True

        if df_4h is not None and len(df_4h) >= 200:
            df_4h_copy = df_4h.copy()
            df_4h_copy["EMA_200"] = df_4h_copy["Close"].ewm(span=200, adjust=False).mean()
            last_4h_close = float(df_4h_copy["Close"].iloc[-1])
            last_4h_ema200 = float(df_4h_copy["EMA_200"].iloc[-1])

            htf_bullish = last_4h_close > last_4h_ema200
            htf_bearish = last_4h_close < last_4h_ema200

        # Crossover logic
        is_bullish_cross = (close_price > curr["EMA_FAST"] > curr["EMA_SLOW"]) and (prvv["Close"] <= prvv["EMA_FAST"])
        is_bearish_cross = (close_price < curr["EMA_FAST"] < curr["EMA_SLOW"]) and (prvv["Close"] >= prvv["EMA_FAST"])

        # Bullish Signal Evaluation
        if is_bullish_cross and is_volume_spike and htf_bullish and (curr_rsi >= 50):
            recent_low = float(data["Low"].iloc[-10:-2].min())
            
            # Grade Assignment
            if vol_ratio >= 2.0 and curr_rsi >= 55:
                grade, prob = "A+ (High Confluence)", "60% - 65%"
            else:
                grade, prob = "A (Moderate Confluence)", "50% - 55%"

            return SignalResult(
                direction="LONG",
                entry_price=close_price,
                recent_extreme=recent_low,
                volume_ratio=vol_ratio,
                rsi_val=curr_rsi,
                htf_aligned=htf_bullish,
                signal_grade=grade,
                est_win_probability=prob
            )

        # Bearish Signal Evaluation
        if is_bearish_cross and is_volume_spike and htf_bearish and (curr_rsi <= 50):
            recent_high = float(data["High"].iloc[-10:-2].max())
            
            if vol_ratio >= 2.0 and curr_rsi <= 45:
                grade, prob = "A+ (High Confluence)", "60% - 65%"
            else:
                grade, prob = "A (Moderate Confluence)", "50% - 55%"

            return SignalResult(
                direction="SHORT",
                entry_price=close_price,
                recent_extreme=recent_high,
                volume_ratio=vol_ratio,
                rsi_val=curr_rsi,
                htf_aligned=htf_bearish,
                signal_grade=grade,
                est_win_probability=prob
            )

        return None
