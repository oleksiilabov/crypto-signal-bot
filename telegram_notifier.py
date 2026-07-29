"""
Telegram Alert Dispatcher.
Formats and transmits technical signals to designated Telegram chat.
"""

import logging
import requests
from config import TelegramConfig
from risk import TradeParameters

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Service class for transmitting alerts."""

    def __init__(self, config: TelegramConfig = TelegramConfig()):
        self.config = config

    def send_signal_alert(
        self,
        asset_name: str,
        asset_type: str,
        platform: str,
        direction: str,
        risk_params: TradeParameters,
        volume_ratio: float
    ) -> bool:
        """Formats and transmits signal payload."""
        try:
            self.config.validate()
        except ValueError as err:
            logger.error(f"Telegram Notification aborted: {err}")
            return False

        tag_icon = "🔵" if asset_type == "FOREX" else "🟡"
        direction_icon = "📈" if direction == "LONG" else "📉"

        if asset_type == "FOREX":
            sl_info = (
                f"🛑 *Stop Loss:* `{risk_params.stop_loss}` ({risk_params.sl_pips} pips)\n"
                f"🎯 *Take Profit:* `{risk_params.take_profit}` ({risk_params.tp_pips} pips)"
            )
        else:
            sl_info = (
                f"🛑 *Stop Loss:* `{risk_params.stop_loss}`\n"
                f"🎯 *Take Profit:* `{risk_params.take_profit}`"
            )

        platform_short = platform.split(" ")[0]
        message = (
            f"{tag_icon} *[{asset_type} SIGNAL]*\n"
            f"*Pair:* `{asset_name}`\n"
            f"{direction_icon} *Direction:* `{direction} / {'BUY' if direction == 'LONG' else 'SELL'}`\n"
            f"🏦 *Platform:* {platform}\n"
            f"───────────────\n"
            f"📍 *Entry:* `{risk_params.entry_price:.{risk_params.decimals}f}`\n"
            f"{sl_info}\n"
            f"⚖️ *Risk/Reward:* 1:{risk_params.risk_reward_ratio}\n"
            f"📊 *Volume Spike:* {volume_ratio}x baseline\n"
            f"───────────────\n"
            f"📲 _Execute trade on {platform_short}_"
        )

        url = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"
        payload = {
            "chat_id": self.config.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Successfully transmitted signal for {asset_name}")
                return True
            else:
                logger.error(f"Telegram API responded with code {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to post alert to Telegram: {e}", exc_info=True)
            return False
