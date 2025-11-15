#! /usr/bin/env python
# fetcher.py: Script to scrape historical data from Yahoo Finance

import time
import threading
from typing import Optional, Dict, Any
from datetime import datetime
import pandas as pd
import yfinance as yf
from set_logs import setup_logger
from cache import Caches

logger = setup_logger(__name__)

class YfData:
    """
    A thread-safe data fetcher for Yahoo Finance with caching and retry logic.
    """
    def __init__(self, max_retries: int = 3, base_delay: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.cache = Caches()
        self._lock = threading.Lock()

    def _flatten_multiindex_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Flatten MultiIndex columns to a single level."""
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
        return df

    def get_data(
        self,
        ticker: str,
        **kwargs: Any
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a ticker with specified parameters.

        Args:
            ticker (str): The stock ticker symbol.
            **kwargs: Arbitrary keyword arguments passed to yfinance.download().
                      Examples: start, end, period, interval.

        Returns:
            A DataFrame with historical data, or None if fetching fails.
        """
        # Generate a cache key based on the request parameters
        cache_key = self.cache._get_cache_key(ticker, kwargs)

        # Thread-safe cache check
        with self._lock:
            cached_df = self.cache.load_from_cache(cache_key)
            if cached_df is not None:
                return cached_df.copy(deep=True)

        # If not in cache, fetch from yfinance
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.base_delay * (2 ** attempt))  # Exponential backoff
                logger.debug(f"Fetching data for {ticker} (attempt {attempt + 1}) with params: {kwargs}")

                df = yf.download(
                    ticker,
                    **kwargs,
                    auto_adjust=True,
                    prepost=False,
                    progress=False
                )

                if not df.empty:
                    # yfinance can return a single-ticker DF or a multi-ticker DF
                    # If it's multi-ticker, it will have a MultiIndex
                    if isinstance(df.columns, pd.MultiIndex):
                        # Extract the data for our specific ticker
                        df = df.xs(ticker, level=1, axis=1)

                    df_clean = self._flatten_multiindex_columns(df)

                    # Thread-safe cache save
                    with self._lock:
                        self.cache.save_to_cache(df_clean, cache_key)
                    
                    logger.debug(f"Successfully fetched {len(df_clean)} rows for {ticker}")
                    return df_clean

                elif attempt == self.max_retries - 1:
                    logger.warning(f"Empty DataFrame for {ticker} after {self.max_retries} attempts")
                    return None

            except Exception as e:
                logger.error(f"Failed to fetch data for {ticker} on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    return None
        return None


