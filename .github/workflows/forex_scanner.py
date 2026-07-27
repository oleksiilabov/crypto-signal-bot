import os
import requests
import yfinance as yf
import pandas as pd

# Reuse existing secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

FOREX_PAIRS = {
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
    "USDJPY=X": "USD/JPY",
    "AUDUSD=X": "AUD/USD"
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

def analyze_pair(ticker_symbol: str, pair_name: str):
    df = yf.download(tickers=ticker_symbol, period="5d", interval="15m", progress=False)
    
    if df.empty or len(df) < 50:
        print(f"Insufficient data for {pair_name}")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['Vol_SMA'] = df['Volume'].rolling(window=20).mean()

    curr = df.iloc[-2]
    prev = df.iloc[-3]
    
    close_price = float(curr['Close'])
    curr_volume = float(curr['Volume'])
    avg_volume = float(curr['Vol_SMA'])

    pip_factor = 0.01 if "JPY" in pair_name else 0.0001
    is_volume_spike = curr_volume > (1.5 * avg_volume) if avg_volume > 0 else True

    # Bullish Signal
    if (close_price > curr['EMA_20'] > curr['EMA_50']) and (prev['Close'] <= prev['EMA_20']) and is_volume_spike:
        recent_low = float(df['Low'].iloc[-10:-2].min())
        sl_pips = round((close_price - recent_low) / pip_factor, 1)
        sl_pips = max(sl_pips, 10.0)
        tp_pips = round(sl_pips * 2, 1)

        stop_loss_price = round(close_price - (sl_pips * pip_factor), 5 if "JPY" not in pair_name else 3)
        take_profit_price = round(close_price + (tp_pips * pip_factor), 5 if "JPY" not in pair_name else 3)

        msg = (
            f"🚀 *FOREX BUY SIGNAL: {pair_name}*\n"
            f"───────────────\n"
            f"📍 *Entry:* `{close_price:.5f}`\n"
            f"🛑 *Stop Loss:* `{stop_loss_price}` ({sl_pips} pips)\n"
            f"🎯 *Take Profit:* `{take_profit_price}` ({tp_pips} pips)\n"
            f"⚖️ *Risk/Reward:* 1:2\n"
            f"📊 *Volume:* {round(curr_volume/avg_volume, 1)}x baseline\n"
            f"───────────────\n"
            f"📲 _Open IBKR Mobile to place order._"
        )
        send_telegram_alert(msg)

    # Bearish Signal
    elif (close_price < curr['EMA_20'] < curr['EMA_50']) and (prev['Close'] >= prev['EMA_20']) and is_volume_spike:
        recent_high = float(df['High'].iloc[-10:-2].max())
        sl_pips = round((recent_high - close_price) / pip_factor, 1)
        sl_pips = max(sl_pips, 10.0)
        tp_pips = round(sl_pips * 2, 1)

        stop_loss_price = round(close_price + (sl_pips * pip_factor), 5 if "JPY" not in pair_name else 3)
        take_profit_price = round(close_price - (tp_pips * pip_factor), 5 if "JPY" not in pair_name else 3)

        msg = (
            f"🔻 *FOREX SELL SIGNAL: {pair_name}*\n"
            f"───────────────\n"
            f"📍 *Entry:* `{close_price:.5f}`\n"
            f"🛑 *Stop Loss:* `{stop_loss_price}` ({sl_pips} pips)\n"
            f"🎯 *Take Profit:* `{take_profit_price}` ({tp_pips} pips)\n"
            f"⚖️ *Risk/Reward:* 1:2\n"
            f"📊 *Volume:* {round(curr_volume/avg_volume, 1)}x baseline\n"
            f"───────────────\n"
            f"📲 _Open IBKR Mobile to place order._"
        )
        send_telegram_alert(msg)

def main():
    print("Scanning Forex Pairs...")
    for symbol, name in FOREX_PAIRS.items():
        try:
            analyze_pair(symbol, name)
        except Exception as e:
            print(f"Error scanning {name}: {e}")

if __name__ == "__main__":
    main()
