#! /usr/bin/env python
# fetcher.py: Script to scrape historical data from Yahoo Finance

"""
Yahoo Finance Data Fetcher

This module provides functionality to fetch historical financial data from Yahoo Finance
with built-in rate limiting, retry logic, and caching capabilities.

Features:
- Rate limiting to avoid API throttling
- Exponential backoff retry logic
- Local caching to reduce API calls
- Support for different time intervals and date ranges
- Comprehensive error handling and logging
"""


import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import pickle

import pandas as pd
import yfinance as yf

from set_logs import setup_logger
from cache import Caches

logger = setup_logger(__name__)

class YfData:
    """
    Handles Yahoo Finance data fetching with rate limiting and caching.
    
    This class provides methods to fetch historical financial data from Yahoo Finance
    with built-in rate limiting, retry logic, and caching to ensure reliable data retrieval.
    
    Attributes:
        max_retries (int): Maximum number of retry attempts for failed requests
        base_delay (float): Base delay in seconds between retry attempts
        cached_data (Caches): Cache handler for storing and retrieving data
    """
    
    def __init__(self, max_retries: int = 5, base_delay: float = 3.0):
        """
        Initialize the YfData fetcher.
        
        Args:
            max_retries (int): Maximum number of retry attempts (default: 5)
            base_delay (float): Base delay in seconds between retries (default: 3.0)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.cached_data = Caches()
    
    def get_yf_for_timeframe(
        self,
        ticker: str,
        interval: str,
        period: str = 'max',
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a ticker with specified interval and period.
        
        Args:
            ticker (str): Stock/crypto ticker symbol (e.g., 'AAPL', 'BTC-USD')
            interval (str): Data interval ('1m', '5m', '1h', '1d', '1wk', '1mo', etc.)
            period (str): Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            
        Returns:
            Optional[pd.DataFrame]: Historical data as DataFrame or None if failed
            
        Raises:
            ValueError: If DataFrame is empty after all retries
        """
        cached_df = self.cached_data._load_from_cache(ticker, interval)
        if cached_df is not None:
            return cached_df

        for attempt in range(self.max_retries):
            try:
                time.sleep(self.base_delay * (2 ** attempt))
                df = yf.download(
                    ticker,
                    period=period,
                    interval=interval,
                    auto_adjust=True,
                    prepost=False
                )

                if not df.empty:
                    self.cached_data._save_to_cache(df, ticker, interval)
                    return df
                elif attempt == self.max_retries - 1:
                    raise ValueError("Empty DataFrame after retries")
            except Exception as e:
                logger.error(f"{interval} data attempt {attempt+1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    return None
    
    def get_data_for_range(
            self,
            ticker: str,
            start: str,
            end: str,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a ticker within a specific date range.
        
        Args:
            ticker (str): Stock/crypto ticker symbol (e.g., 'AAPL', 'BTC-USD')
            start (str): Start date in YYYY-MM-DD format
            end (str): End date in YYYY-MM-DD format
            
        Returns:
            Optional[pd.DataFrame]: Historical data as DataFrame or None if failed
            
        Raises:
            ValueError: If DataFrame is empty after all retries
        """
        cache_path = self.cached_data._get_cache_path(ticker, start, end)
        cached_df = self.cached_data._load_from_cache_range(cache_path)
        if cached_df is not None:
            return cached_df

        for attempt in range(self.max_retries):
            try:
                time.sleep(self.base_delay * (2 ** attempt))
                df = yf.download(
                    ticker,
                    start=start,
                    end=end,
                    interval='1d',
                    auto_adjust=True,
                    prepost=False
                )
                
                if not df.empty:
                    self.cached_data._save_to_cache_range(df, cache_path, ticker, start)
                    return df
                elif attempt == self.max_retries - 1:
                    raise ValueError("Empty DataFrame after retries")
            
            except Exception as e:
                logger.error(f"Data range attempt {attempt+1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    return None




    



