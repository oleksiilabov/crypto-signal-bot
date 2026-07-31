"""
Telegram Notification Module.
Formats and dispatches trade signal alerts to Telegram.
"""

import logging
import os
import requests
from strategy import SignalResult

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Handles sending formatted signal messages to a Telegram chat."""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_signal(self, symbol: str, signal: SignalResult) -> bool:
        """Formats signal metrics and posts to Telegram."""
        if not self.token or not self.chat_id:
            logger.error("Telegram Notification aborted: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.")
            return False

        # Risk Management Calculations (Risk-to-Reward 1:2)
        entry = signal.entry_price
        stop_loss = signal.recent_extreme
        
        if signal.direction == "LONG":
            risk = entry - stop_loss
            take_profit = round(entry + (risk * 2.0), 5)
        else:
            risk = stop_loss - entry
            take_profit = round(entry - (risk * 2.0), 5)

        # Formatted Markdown Message with Grade & Probability
        msg = (
            f"🚨 *TRADE ALERT: {symbol} ({signal.direction})*\n\n"
            f"📊 *Signal Grade:* `{signal.signal_grade}`\n"
            f"🎯 *Est. Win Rate:* `{signal.est_win_probability}`\n\n"
            f"💵 *Entry Price:* `{entry}`\n"
            f"🛑 *Stop Loss:* `{stop_loss}`\n"
            f"🎯 *Take Profit (1:2):* `{take_profit}`\n\n"
            f"📈 *RSI (14):* `{signal.rsi_val}`\n"
            f"🔊 *Volume Ratio:* `{signal.volume_ratio}x`"
        )

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": msg,
            "parse_mode": "Markdown"
        }

        try:
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                logger.info(f"Successfully sent Telegram alert for {symbol}")
                return True
            else:
                logger.error(f"Telegram API error {res.status_code}: {res.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
