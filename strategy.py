from config import WEIGHTS, MIN_CONFIDENCE_THRESHOLD, MIN_RISK_REWARD

def evaluate_symbol(symbol: str, df):
    if df.empty or len(df) < 200:
        return None
    
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    long_score = 0.0
    short_score = 0.0
    long_reasons, short_reasons = [], []
    
    # 1. EMA Trend
    if curr['close'] > curr['ema_50'] > curr['ema_200']:
        long_score += WEIGHTS['ema_trend']
        long_reasons.append("EMA trend bullish (Price > EMA50 > EMA200)")
    elif curr['close'] < curr['ema_50'] < curr['ema_200']:
        short_score += WEIGHTS['ema_trend']
        short_reasons.append("EMA trend bearish (Price < EMA50 < EMA200)")
        
    # 2. MACD
    if (prev['macd'] <= prev['macd_signal'] and curr['macd'] > curr['macd_signal']):
        long_score += WEIGHTS['macd']
        long_reasons.append("MACD bullish crossover")
    elif curr['macd'] > curr['macd_signal'] and curr['macd_hist'] > prev['macd_hist']:
        long_score += WEIGHTS['macd'] * 0.7
        long_reasons.append("MACD momentum expansion")

    if (prev['macd'] >= prev['macd_signal'] and curr['macd'] < curr['macd_signal']):
        short_score += WEIGHTS['macd']
        short_reasons.append("MACD bearish crossover")
    elif curr['macd'] < curr['macd_signal'] and curr['macd_hist'] < prev['macd_hist']:
        short_score += WEIGHTS['macd'] * 0.7
        short_reasons.append("MACD momentum downside expansion")
        
    # 3. RSI
    if 50 <= curr['rsi'] <= 68:
        long_score += WEIGHTS['rsi']
        long_reasons.append(f"RSI bullish momentum ({curr['rsi']:.1f})")
    elif 32 <= curr['rsi'] <= 50:
        short_score += WEIGHTS['rsi']
        short_reasons.append(f"RSI bearish momentum ({curr['rsi']:.1f})")
        
    # 4. Volume
    if curr['vol_ratio'] >= 1.5:
        vol_pct = (curr['vol_ratio'] - 1) * 100
        reason_text = f"Volume spike (+{vol_pct:.0f}% vs 20-MA)"
        long_score += WEIGHTS['volume']
        short_score += WEIGHTS['volume']
        long_reasons.append(reason_text)
        short_reasons.append(reason_text)
        
    # 5. Volatility
    if curr['atr'] > 0:
        long_score += WEIGHTS['atr_volatility']
        short_score += WEIGHTS['atr_volatility']
        long_reasons.append("ATR confirms active volatility")

    # Evaluate Thresholds
    side, confidence, reasons = None, 0.0, []
    if long_score >= short_score and long_score >= MIN_CONFIDENCE_THRESHOLD:
        side, confidence, reasons = "LONG", long_score, long_reasons
    elif short_score > long_score and short_score >= MIN_CONFIDENCE_THRESHOLD:
        side, confidence, reasons = "SHORT", short_score, short_reasons
    else:
        return None

    price = curr['close']
    atr = curr['atr']
    
    if side == "LONG":
        entry_min = round(price * 0.998, 4)
        entry_max = round(price * 1.001, 4)
        stop_loss = round(price - (atr * 1.8), 4)
        risk = price - stop_loss
        tp1 = round(price + (risk * 1.5), 4)
        tp2 = round(price + (risk * 2.5), 4)
        tp3 = round(price + (risk * 3.5), 4)
        rr_ratio = round((tp2 - price) / risk, 2)
    else:
        entry_min = round(price * 0.999, 4)
        entry_max = round(price * 1.002, 4)
        stop_loss = round(price + (atr * 1.8), 4)
        risk = stop_loss - price
        tp1 = round(price - (risk * 1.5), 4)
        tp2 = round(price - (risk * 2.5), 4)
        tp3 = round(price - (risk * 3.5), 4)
        rr_ratio = round((price - tp2) / risk, 2)

    if rr_ratio < MIN_RISK_REWARD:
        return None

    return {
        "symbol": symbol.split('/')[0],
        "side": side,
        "price": price,
        "entry": f"{entry_min} - {entry_max}",
        "stop_loss": stop_loss,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "rr_ratio": rr_ratio,
        "confidence": confidence,
        "reasons": reasons
    }
