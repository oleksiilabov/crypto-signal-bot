import os

# Telegram Settings
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Exchange Settings
EXCHANGE_ID = "bitget"
TIMEFRAME = "4h"
CANDLE_LIMIT = 250

# Market Liquidity Filters (in USD)
MIN_24H_VOLUME_USD = 300_000_000     # $300M 24h volume
MIN_OPEN_INTEREST_USD = 100_000_000  # $100M Open Interest

# Strategy Thresholds
MIN_CONFIDENCE_THRESHOLD = 65.0
MIN_RISK_REWARD = 2.0

# Indicator Weights
WEIGHTS = {
    "ema_trend": 25,
    "macd": 25,
    "rsi": 20,
    "volume": 20,
    "atr_volatility": 10
}
