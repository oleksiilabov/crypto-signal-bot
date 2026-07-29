"""
Market Data Ingestion Module.
Retrieves and validates market historical OHLCV data.
"""

import logging
import pandas as pd
import yfinance as yf
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


class DataFetcher:
    """Handles data extraction with resilient HTTP sessions."""

    def __init__(self, retries: int = 3, backoff_factor: float = 0.5):
        self.session = Session()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_ohlcv(self, symbol: str, period: str = "5d", interval: str = "15m") -> pd.DataFrame:
        """
        Fetches historical data for a given ticker symbol.
        """
        try:
            logger.info(f"Fetching market data for {symbol} ({interval} / {period})...")
            df = yf.download(
                tickers=symbol,
                period=period,
                interval=interval,
                progress=False,
                session=self.session
            )

            if df.empty or len(df) < 50:
                logger.warning(f"Insufficient OHLCV data returned for ticker: {symbol}")
                return pd.DataFrame()

            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Standardize column naming
            required_cols = {"Open", "High", "Low", "Close", "Volume"}
            if not required_cols.issubset(df.columns):
                logger.error(f"Missing required columns in dataset for {symbol}: {df.columns}")
                return pd.DataFrame()

            return df

        except Exception as e:
            logger.error(f"Unhandled exception fetching data for {symbol}: {e}", exc_info=True)
            return pd.DataFrame()
