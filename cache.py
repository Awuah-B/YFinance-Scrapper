#!/usr/bin/env python3

"""
Cache Management for Yahoo Finance Data

This module provides caching functionality to store and retrieve Yahoo Finance data
locally to reduce API calls and improve performance.

Features:
- Local file-based caching using pickle
- Automatic cache directory creation
- Cache file naming based on ticker, interval, and date ranges
- Automatic cleanup of old cache files
- Error handling for corrupted cache files
"""

from pathlib import Path
import pickle
from typing import Optional

import pandas as pd
from set_logs import setup_logger

class Caches:
    """
    Handles local caching of Yahoo Finance data.
    
    This class provides methods to store and retrieve financial data locally
    to reduce API calls and improve performance. It supports both interval-based
    and date range-based caching strategies.
    
    Attributes:
        cache_dir (Path): Directory where cache files are stored
        logger: Logger instance for debugging and error reporting
    """
    
    def __init__(self, cache_dir: str = "./cache/yfinance"):
        """
        Initialize the cache handler.
        
        Args:
            cache_dir (str): Directory path for storing cache files (default: "./cache/yfinance")
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = setup_logger(__name__)

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format."""
        try:
            dt = pd.to_datetime(date_str).normalize()
            return dt.strftime("%Y-%m-%d")
        except Exception as e:
            self.logger.warning(f"Date normalization failed for {date_str}: {e}")
            return date_str 

    def _get_cache_path(self, ticker: str, start: str, end: str) -> Path:
        """Generate cache file path based on ticker, start, and end date (YYYY-MM-DD)."""
        start_norm = self._normalize_date(start)
        end_norm = self._normalize_date(end)
        return self.cache_dir / f"{ticker}_{start_norm}_{end_norm}.pkl"

    def _find_existing_cache_files(self, ticker: str, start: str) -> list:
        """Find all cache files for a ticker with the same start date (any end date)."""
        start_norm = self._normalize_date(start)
        pattern = f"{ticker}_{start_norm}_*.pkl"
        return list(self.cache_dir.glob(pattern))
    
    def _delete_old_caches(self, ticker: str, start: str, keep_path: Path):
        """Delete all cache files for ticker/start except the one to keep."""
        for file in self._find_existing_cache_files(ticker, start):
            if file != keep_path:
                try:
                    file.unlink()
                    self.logger.info(f"Deleted old cache file: {file}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete cache file {file}: {e}")

    def _load_from_cache(self, ticker: str, interval: str) -> Optional[pd.DataFrame]:
        cache_path = self.cache_dir / f"{ticker}{interval}.pkl"
        if not cache_path.exists():
            return None
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
                if isinstance(data, pd.DataFrame) and not data.empty:
                    self.logger.debug(f"Loaded cached data from {cache_path}")
                    return data
        except (pickle.PickleError, EOFError, AttributeError) as e:
            self.logger.warning(f"Cache load failed for {cache_path}: {e}")
            try:
                cache_path.unlink()
                self.logger.info(f"Removed corrupted cache file {cache_path}")
            except OSError:
                pass
        return None
    
    def _save_to_cache(self, df: pd.DataFrame, ticker: str, interval: str):
        if df.empty:
            return False
        # Normalize index to date only (no hours/minutes)
        df.index = pd.to_datetime(df.index).normalize()
        # Delete all old caches for this ticker/interval except the one we're about to write
        cache_path = self.cache_dir / f"{ticker}_{interval}.pkl"
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)
            self.logger.debug(f"Saved data to cache: {cache_path}")
            return True
        except (pickle.PickleError, OSError) as e:
            self.logger.warning(f"Cache save failed for {cache_path}: {e}")
            return False
    
    def _load_from_cache_range(self, cache_path: Path) -> Optional[pd.DataFrame]:
        """Load cached data from a specific cache path."""
        if not cache_path.exists():
            return None
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
                if isinstance(data, pd.DataFrame) and not data.empty:
                    self.logger.debug(f"Loaded cached data from {cache_path}")
                    return data
        except (pickle.PickleError, EOFError, AttributeError) as e:
            self.logger.warning(f"Cache load failed for {cache_path}: {e}")
            try:
                cache_path.unlink()
                self.logger.info(f"Removed corrupted cache file {cache_path}")
            except OSError:
                pass
        return None
    
    def _save_to_cache_range(self, df: pd.DataFrame, cache_path: Path, ticker: str, start: str):
        """Save data to cache for a specific range."""
        if df.empty:
            return False
        # Normalize index to date only (no hours/minutes)
        df.index = pd.to_datetime(df.index).normalize()
        # Delete all old caches for this ticker/start except the one we're about to write
        self._delete_old_caches(ticker, start, cache_path)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)
            self.logger.debug(f"Saved data to cache: {cache_path}")
            return True
        except (pickle.PickleError, OSError) as e:
            self.logger.warning(f"Cache save failed for {cache_path}: {e}")
            return False
