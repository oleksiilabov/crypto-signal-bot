import ccxt
import pandas as pd
import logging
from config import CANDLE_LIMIT

logger = logging.getLogger(__name__)

def get_exchange_instance():
    return ccxt.bitget({
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'}
    })

def fetch_ohlcv_data(exchange, symbol: str, timeframe: str) -> pd.DataFrame:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=CANDLE_LIMIT)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()
