import os

# Telegram Settings (Read from GitHub Secrets)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Exchange Settings
EXCHANGE_ID = "bitget"
SYMBOLS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
    "BNB/USDT:USDT",
    "XRP/USDT:USDT"
]

TIMEFRAME = "4h"
CANDLE_LIMIT = 250

# Strategy Thresholds
MIN_CONFIDENCE_THRESHOLD = 0.0
MIN_RISK_REWARD = 2.0

# Indicator Weights
WEIGHTS = {
    "ema_trend": 25,
    "macd": 25,
    "rsi": 20,
    "volume": 20,
    "atr_volatility": 10
}
