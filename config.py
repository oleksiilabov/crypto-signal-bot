"""
Configuration Management Module.
Loads environment variables and exposes typed parameters for strategy execution.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(frozen=True)
class StrategyConfig:
    """Trading strategy tunable parameters."""
    lookback_period: str = os.getenv("LOOKBACK_PERIOD", "5d")
    interval: str = os.getenv("INTERVAL", "15m")
    volume_multiplier: float = float(os.getenv("VOLUME_MULT", "1.5"))
    ema_fast: int = int(os.getenv("EMA_FAST", "20"))
    ema_slow: int = int(os.getenv("EMA_SLOW", "50"))
    risk_reward_ratio: float = float(os.getenv("RISK_REWARD_RATIO", "2.0"))


@dataclass(frozen=True)
class TelegramConfig:
    """Telegram Bot Credentials."""
    bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))

    def validate(self) -> None:
        """Validates that necessary Telegram tokens exist."""
        if not self.bot_token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.")


# Asset Registry Mapping
ASSETS_TO_SCAN: Dict[str, Dict[str, Any]] = {
    # FOREX MAJORS
    "EURUSD=X": {"name": "EUR/USD", "type": "FOREX", "platform": "Interactive Brokers (IBKR)"},
    "GBPUSD=X": {"name": "GBP/USD", "type": "FOREX", "platform": "Interactive Brokers (IBKR)"},
    "USDJPY=X": {"name": "USD/JPY", "type": "FOREX", "platform": "Interactive Brokers (IBKR)"},
    "AUDUSD=X": {"name": "AUD/USD", "type": "FOREX", "platform": "Interactive Brokers (IBKR)"},
    
    # MAJOR CRYPTO & ALTCOINS
    "BTC-USD":  {"name": "BTC/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "ETH-USD":  {"name": "ETH/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "SOL-USD":  {"name": "SOL/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "XRP-USD":  {"name": "XRP/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "ADA-USD":  {"name": "ADA/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "AVAX-USD": {"name": "AVAX/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "LINK-USD": {"name": "LINK/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "DOGE-USD": {"name": "DOGE/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "NEAR-USD": {"name": "NEAR/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"},
    "SUI-USD":  {"name": "SUI/USD", "type": "CRYPTO", "platform": "Bitget (Futures / Spot)"}
}
