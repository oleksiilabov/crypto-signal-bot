import logging
from config import SYMBOLS, TIMEFRAME
from data import get_exchange_instance, fetch_ohlcv_data
from indicators import calculate_indicators
from strategy import evaluate_symbol
from telegram import send_telegram_signal

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_single_scan():
    logger = logging.getLogger(__name__)
    logger.info("Executing scheduled market scan...")
    exchange = get_exchange_instance()

    for symbol in SYMBOLS:
        try:
            df = fetch_ohlcv_data(exchange, symbol, TIMEFRAME)
            if df.empty:
                continue
                
            df = calculate_indicators(df)
            signal = evaluate_symbol(symbol, df)
            
            if signal:
                logger.info(f"Signal found for {symbol}: {signal['side']}")
                send_telegram_signal(signal)
            else:
                logger.info(f"No signal for {symbol}")
                
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")

if __name__ == "__main__":
    run_single_scan()
