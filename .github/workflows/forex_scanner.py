import os
import requests
import yfinance as yf
import pandas as pd

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Single dictionary containing both Forex and Crypto tickers
ASSETS_TO_SCAN = {
    # FOREX MAJORS
    "EURUSD=X": {"name": "EUR/USD", "type": "FOREX", "platform": "Interactive Brokers (IBKR)"},
    "GBPUSD=X": {"name": "GBP/USD", "type": "FOREX", "platform": "Interactive Brokers (IBKR)"},
    "USDJPY=X": {"name": "USD/JPY", "type": "FOREX", "platform": "Interactive Brokers (IBKR)"},
    "AUDUSD=X": {"name": "AUD/USD", "type": "FOREX", "platform": "Interactive Brokers (IBKR)"},
    
    # CRYPTO PAIRS
    "BTC-USD":  {"name": "BTC/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "ETH-USD":  {"name": "ETH/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "SOL-USD":  {"name": "SOL/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"}
}

def send_telegram_alert(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def analyze_asset(ticker_symbol: str, meta: dict):
    asset_name = meta["name"]
    asset_type = meta["type"]
    platform = meta["platform"]

    df = yf.download(tickers=ticker_symbol, period="5d", interval="15m", progress=False)
    
    if df.empty or len(df) < 50:
        print(f"Insufficient data for {asset_name}")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Indicator Calculations
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['Vol_SMA'] = df['Volume'].rolling(window=20).mean()

    curr = df.iloc[-2]
    prev = df.iloc[-3]
    
    close_price = float(curr['Close'])
    curr_volume = float(curr['Volume'])
    avg_volume = float(curr['Vol_SMA'])

    # Formatters depending on asset class
    if asset_type == "FOREX":
        pip_factor = 0.01 if "JPY" in asset_name else 0.0001
        decimals = 3 if "JPY" in asset_name else 5
        tag_icon = "🔵"
    else:  # CRYPTO
        pip_factor = 1.0 if close_price > 100 else 0.01
        decimals = 2 if close_price > 100 else 4
        tag_icon = "🟡"

    is_volume_spike = curr_volume > (1.5 * avg_volume) if avg_volume > 0 else True

    # ------------------
    # BULLISH / LONG SIGNAL
    # ------------------
    if (close_price > curr['EMA_20'] > curr['EMA_50']) and (prev['Close'] <= prev['EMA_20']) and is_volume_spike:
        recent_low = float(df['Low'].iloc[-10:-2].min())
        
        if asset_type == "FOREX":
            sl_pips = max(round((close_price - recent_low) / pip_factor, 1), 10.0)
            tp_pips = round(sl_pips * 2, 1)
            stop_loss = round(close_price - (sl_pips * pip_factor), decimals)
            take_profit = round(close_price + (tp_pips * pip_factor), decimals)
            sl_info = f"🛑 *Stop Loss:* `{stop_loss}` ({sl_pips} pips)\n🎯 *Take Profit:* `{take_profit}` ({tp_pips} pips)"
        else:
            stop_loss = round(recent_low, decimals)
            risk = close_price - stop_loss
            take_profit = round(close_price + (risk * 2), decimals)
            sl_info = f"🛑 *Stop Loss:* `{stop_loss}`\n🎯 *Take Profit:* `{take_profit}`"

        msg = (
            f"{tag_icon} *[{asset_type} SIGNAL]*\n"
            f"**Pair:** `{asset_name}`\n"
            f"📈 **Direction:** `LONG / BUY`\n"
            f"🏦 **Platform:** {platform}\n"
            f"───────────────\n"
            f"📍 *Entry:* `{close_price:.{decimals}f}`\n"
            f"{sl_info}\n"
            f"⚖️ *Risk/Reward:* 1:2\n"
            f"📊 *Volume Spike:* {round(curr_volume/avg_volume, 1)}x baseline\n"
            f"───────────────\n"
            f"📲 _Execute trade on {platform.split(' ')[0]}_"
        )
        send_telegram_alert(msg)

    # ------------------
    # BEARISH / SHORT SIGNAL
    # ------------------
    elif (close_price < curr['EMA_20'] < curr['EMA_50']) and (prev['Close'] >= prev['EMA_20']) and is_volume_spike:
        recent_high = float(df['High'].iloc[-10:-2].max())
        
        if asset_type == "FOREX":
            sl_pips = max(round((recent_high - close_price) / pip_factor, 1), 10.0)
            tp_pips = round(sl_pips * 2, 1)
            stop_loss = round(close_price + (sl_pips * pip_factor), decimals)
            take_profit = round(close_price - (tp_pips * pip_factor), decimals)
            sl_info = f"🛑 *Stop Loss:* `{stop_loss}` ({sl_pips} pips)\n🎯 *Take Profit:* `{take_profit}` ({tp_pips} pips)"
        else:
            stop_loss = round(recent_high, decimals)
            risk = stop_loss - close_price
            take_profit = round(close_price - (risk * 2), decimals)
            sl_info = f"🛑 *Stop Loss:* `{stop_loss}`\n🎯 *Take Profit:* `{take_profit}`"

        msg = (
            f"{tag_icon} *[{asset_type} SIGNAL]*\n"
            f"**Pair:** `{asset_name}`\n"
            f"📉 **Direction:** `SHORT / SELL`\n"
            f"🏦 **Platform:** {platform}\n"
            f"───────────────\n"
            f"📍 *Entry:* `{close_price:.{decimals}f}`\n"
            f"{sl_info}\n"
            f"⚖️ *Risk/Reward:* 1:2\n"
            f"📊 *Volume Spike:* {round(curr_volume/avg_volume, 1)}x baseline\n"
            f"───────────────\n"
            f"📲 _Execute trade on {platform.split(' ')[0]}_"
        )
        send_telegram_alert(msg)

def main():
    print("Scanning Forex and Crypto assets...")
    for symbol, meta in ASSETS_TO_SCAN.items():
        try:
            analyze_asset(symbol, meta)
        except Exception as e:
            print(f"Error scanning {meta['name']}: {e}")

if __name__ == "__main__":
    main()
