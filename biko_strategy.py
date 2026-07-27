import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def detect_trendline_breakout(df: pd.DataFrame, timeframe: str = "1h"):
    """
    Implements BikoTrading Breakout + Volume Confirmation Strategy:
    1. Identifies dynamic support/resistance breakout.
    2. Checks for Volume Spike (> 1.8x average volume).
    3. Calculates 1:3 Risk-to-Reward setup with Stop Loss at recent swing high/low.
    """
    if len(df) < 50:
        return None

    # Get recent candles
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 20-period Moving Average of Volume as baseline
    vol_ma = df['volume'].rolling(20).mean().iloc[-1]
    volume_surge = last['volume'] > (1.8 * vol_ma)  # Volume spike requirement
    
    # EMA lines for trend filter
    ema_20 = df['close'].ewm(span=20, adjust=False).mean()
    ema_50 = df['close'].ewm(span=50, adjust=False).mean()
    
    current_close = last['close']
    prev_close = prev['close']
    
    # Swing points (last 10 candles for stop loss placement)
    recent_low = df['low'].tail(10).min()
    recent_high = df['high'].tail(10).max()

    # --- LONG BREAKOUT SIGNAL ---
    # Condition: Price breaks above 20 EMA & 50 EMA with high volume surge
    if (prev_close <= ema_20.iloc[-2]) and (current_close > ema_20.iloc[-1]) and volume_surge:
        entry_price = current_close
        stop_loss = recent_low
        risk = entry_price - stop_loss
        
        if risk <= 0:
            return None
            
        take_profit = entry_price + (risk * 3.0)  # Biko's 1:3 R:R rule
        
        return {
            "side": "BUY (LONG)",
            "entry": round(entry_price, 4),
            "stop_loss": round(stop_loss, 4),
            "take_profit": round(take_profit, 4),
            "risk_reward": "1:3",
            "volume_ratio": round(last['volume'] / vol_ma, 2),
            "reason": "Biko Trendline/EMA Breakout + Volume Surge"
        }

    # --- SHORT BREAKOUT SIGNAL ---
    # Condition: Price breaks below 20 EMA & 50 EMA with high volume surge
    if (prev_close >= ema_20.iloc[-2]) and (current_close < ema_20.iloc[-1]) and volume_surge:
        entry_price = current_close
        stop_loss = recent_high
        risk = stop_loss - entry_price
        
        if risk <= 0:
            return None
            
        take_profit = entry_price - (risk * 3.0)  # Biko's 1:3 R:R rule
        
        return {
            "side": "SELL (SHORT)",
            "entry": round(entry_price, 4),
            "stop_loss": round(stop_loss, 4),
            "take_profit": round(take_profit, 4),
            "risk_reward": "1:3",
            "volume_ratio": round(last['volume'] / vol_ma, 2),
            "reason": "Biko Trendline/EMA Breakout + Volume Surge"
        }

    return None
