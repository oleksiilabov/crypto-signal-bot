import requests
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

def send_telegram_signal(signal: dict):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram token or Chat ID is missing!")
        return

    emoji = "🚀" if signal['side'] == "LONG" else "🔻"
    reasons_formatted = "\n".join([f"✔ {r}" for r in signal['reasons']])
    
    message = (
        f"{emoji} <b>{signal['side']} SIGNAL</b>\n\n"
        f"<b>Pair:</b> #{signal['symbol']}\n"
        f"<b>Current Price:</b> {signal['price']}\n\n"
        f"<b>Entry Zone:</b>\n{signal['entry']}\n\n"
        f"<b>Stop Loss:</b>\n{signal['stop_loss']}\n\n"
        f"<b>Take Profit Targets:</b>\n"
        f"🎯 TP1: {signal['tp1']}\n"
        f"🎯 TP2: {signal['tp2']}\n"
        f"🎯 TP3: {signal['tp3']}\n\n"
        f"<b>Risk / Reward Ratio:</b> {signal['rr_ratio']}\n"
        f"<b>Confidence Score:</b> {signal['confidence']:.0f}%\n\n"
        f"<b>Signal Reasons:</b>\n{reasons_formatted}"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        logger.info(f"Signal for {signal['symbol']} sent to Telegram.")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
