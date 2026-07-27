import logging
from config import TIMEFRAME
from data import get_exchange_instance, fetch_qualified_symbols, fetch_ohlcv_data
from biko_strategy import detect_trendline_breakout
from telegram import send_telegram_signal

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_biko_bot():
    logger = logging.getLogger(__name__)
    logger.info("Executing BikoTrading Strategy Market Scan...")
    
    exchange = get_exchange_instance()
    
    # 1. Fetch high liquidity pairs ($300M Vol & $100M OI)
    symbols = fetch_qualified_symbols(exchange)
    
    if not symbols:
        logger.info("No trading pairs currently meet liquidity criteria.")
        return

    # 2. Scan pairs for Biko Breakouts
    for symbol in symbols:
        try:
            df = fetch_ohlcv_data(exchange, symbol, TIMEFRAME)
            if df.empty:
                continue
                
            signal = detect_trendline_breakout(df, TIMEFRAME)
            
            if signal:
                logger.info(f"🎯 Biko Signal found for {symbol}: {signal['side']}")
                # Format signal payload for Telegram
                payload = {
                    "symbol": symbol,
                    "side": signal["side"],
                    "confidence": 85.0,  # High confidence due to volume surge
                    "close": signal["entry"],
                    "tp": signal["take_profit"],
                    "sl": signal["stop_loss"],
                    "rr": signal["risk_reward"]
                }
                send_telegram_signal(payload)
            else:
                logger.info(f"No Biko breakout signal for {symbol}")
                
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")

if __name__ == "__main__":
    run_biko_bot()
