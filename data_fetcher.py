import ccxt
import pandas as pd
import logging
from config import CANDLE_LIMIT, MIN_24H_VOLUME_USD, MIN_OPEN_INTEREST_USD

logger = logging.getLogger(__name__)

def get_exchange_instance():
    return ccxt.bitget({
        'enableRateLimit': True,
        'timeout': 30000,
        'options': {'defaultType': 'swap'}  # USDT Futures
    })

def fetch_qualified_symbols(exchange) -> list:
    """Dynamically fetches Bitget USDT futures pairs that satisfy Volume and Open Interest filters."""
    logger.info("Scanning Bitget market for high-volume / high-OI pairs...")
    qualified_symbols = []
    
    try:
        # 1. Load markets and fetch 24h tickers
        markets = exchange.load_markets()
        tickers = exchange.fetch_tickers()
        
        for symbol, ticker in tickers.items():
            # Focus on USDT Perpetual Futures
            if not symbol.endswith(":USDT"):
                continue
                
            # Check 24h USD Quote Volume
            quote_volume = ticker.get('quoteVolume', 0) or 0
            if quote_volume < MIN_24H_VOLUME_USD:
                continue

            # Fetch Open Interest for candidates meeting volume requirements
            try:
                oi_data = exchange.fetch_open_interest(symbol)
                # Open interest value in USD (openInterestAmount * lastPrice or oiValue)
                open_interest_usd = oi_data.get('openInterestValue')
                if open_interest_usd is None:
                    oi_contracts = oi_data.get('openInterestAmount', 0) or 0
                    last_price = ticker.get('last', 0) or 0
                    open_interest_usd = oi_contracts * last_price
                
                if open_interest_usd >= MIN_OPEN_INTEREST_USD:
                    logger.info(
                        f"✅ Qualified: {symbol} | "
                        f"24h Vol: ${quote_volume/1e6:.1f}M | "
                        f"OI: ${open_interest_usd/1e6:.1f}M"
                    )
                    qualified_symbols.append(symbol)
                    
            except Exception as e:
                logger.warning(f"Could not fetch Open Interest for {symbol}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error fetching market tickers: {e}")
        
    logger.info(f"Market scan complete. Found {len(qualified_symbols)} qualified pair(s).")
    return qualified_symbols

def fetch_ohlcv_data(exchange, symbol: str, timeframe: str) -> pd.DataFrame:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=CANDLE_LIMIT)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()
