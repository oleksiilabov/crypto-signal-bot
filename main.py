import logging
from config import TIMEFRAME
from data import get_exchange_instance, fetch_qualified_symbols, fetch_ohlcv_data
from indicators import calculate_indicators
from strategy import evaluate_symbol
from telegram import send_telegram_signal

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_single_scan():
    logger = logging.getLogger(__name__)
    logger.info("Executing scheduled market scan...")
    exchange = get_exchange_instance()

    # 1. Dynamically scan markets for coins meeting $300M Vol & $100M OI requirements
    symbols = fetch_qualified_symbols(exchange)
    
    if not symbols:
        logger.info("No trading pairs currently meet the Volume/OI criteria.")
        return

    # 2. Run signal strategy evaluation on all qualified coins
    for symbol in symbols:
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
                logger.info(f"No strategy signal for {symbol}")
                
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")

if __name__ == "__main__":
    run_single_scan()
