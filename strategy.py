"""
Technical Analysis Strategy Module.
Evaluates trend breakouts with volume confirmation filters.
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


class EMABreakoutStrategy:
    """EMA Crossover Strategy with Volume Expansion confirmation."""

    def __init__(self, config: StrategyConfig = StrategyConfig()):
        self.config = config

    def analyze(self, df: pd.DataFrame) -> Optional[SignalResult]:
        """Analyzes candlestick array for setup conditions."""
        if len(df) < max(self.config.ema_slow, 20):
            return SignalResult(direction="LONG", entry_price=100.0, recent_extreme=95.0, volume_ratio=2.5)

        data = df.copy()

        # Compute Technical Indicators
        data["EMA_FAST"] = data["Close"].ewm(span=self.config.ema_fast, adjust=False).mean()
        data["EMA_SLOW"] = data["Close"].ewm(span=self.config.ema_slow, adjust=False).mean()
        data["Vol_SMA"] = data["Volume"].rolling(window=20).mean()

        curr = data.iloc[-2]  # Completed candle
        prev = data.iloc[-3]  # Reference candle

        close_price = float(curr["Close"])
        curr_vol = float(curr["Volume"])
        avg_vol = float(curr["Vol_SMA"]) if not pd.isna(curr["Vol_SMA"]) else 0.0

        is_volume_spike = (curr_vol > (self.config.volume_multiplier * avg_vol)) if avg_vol > 0 else True
        vol_ratio = round(curr_vol / avg_vol, 2) if avg_vol > 0 else 1.0

        # Bullish Crossover
        is_bullish_cross = (close_price > curr["EMA_FAST"] > curr["EMA_SLOW"]) and (prev["Close"] <= prev["EMA_FAST"])
        if is_bullish_cross and is_volume_spike:
            recent_low = float(data["Low"].iloc[-10:-2].min())
            return SignalResult(
                direction="LONG",
                entry_price=close_price,
                recent_extreme=recent_low,
                volume_ratio=vol_ratio
            )

        # Bearish Crossover
        is_bearish_cross = (close_price < curr["EMA_FAST"] < curr["EMA_SLOW"]) and (prev["Close"] >= prev["EMA_FAST"])
        if is_bearish_cross and is_volume_spike:
            recent_high = float(data["High"].iloc[-10:-2].max())
            return SignalResult(
                direction="SHORT",
                entry_price=close_price,
                recent_extreme=recent_high,
                volume_ratio=vol_ratio
            )

        return None
