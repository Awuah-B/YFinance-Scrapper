#!/usr/bin/env python3

"""
Unit tests for the Yahoo Finance scraper.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from pathlib import Path
import shutil
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from fetcher import YfData
from cache import Caches
import main as cli

class TestCache(unittest.TestCase):
    """Tests for the Caches class."""
    
    def setUp(self):
        self.cache_dir = Path("./test_cache")
        self.cache = Caches(cache_dir=str(self.cache_dir))
        
    def tearDown(self):
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            
    def test_cache_key_generation(self):
        """Test that cache keys are generated consistently."""
        params1 = {"start": "2023-01-01", "interval": "1d"}
        key1 = self.cache._get_cache_key("AAPL", params1)
        self.assertEqual(key1, "ticker=AAPL_interval=1d_start=2023-01-01")
        
        params2 = {"interval": "1d", "start": "2023-01-01"}
        key2 = self.cache._get_cache_key("AAPL", params2)
        self.assertEqual(key1, key2) # Order should not matter
        
    def test_save_and_load_from_cache(self):
        """Test saving to and loading from the cache."""
        df = pd.DataFrame({'Close': [150, 151]}, index=pd.to_datetime(['2023-01-01', '2023-01-02']))
        key = "test_key"
        
        self.cache.save_to_cache(df, key)
        cached_df = self.cache.load_from_cache(key)
        
        self.assertIsNotNone(cached_df)
        pd.testing.assert_frame_equal(df, cached_df)

class TestYfData(unittest.TestCase):
    """Tests for the YfData fetcher class."""
    
    def setUp(self):
        self.fetcher = YfData()

    @patch('yfinance.download')
    def test_get_data_fetches_from_network_if_not_in_cache(self, mock_download):
        """Test that yfinance.download is called when data is not in cache."""
        mock_df = pd.DataFrame({'Close': [150]})
        mock_download.return_value = mock_df
        
        with patch.object(self.fetcher.cache, 'load_from_cache', return_value=None) as mock_load:
            with patch.object(self.fetcher.cache, 'save_to_cache') as mock_save:
                df = self.fetcher.get_data("AAPL", start="2023-01-01")
                
                mock_load.assert_called_once()
                mock_download.assert_called_once_with(
                    "AAPL", start="2023-01-01", auto_adjust=True, prepost=False, progress=False
                )
                mock_save.assert_called_once()
                self.assertIsNotNone(df)

    def test_get_data_returns_from_cache_if_available(self):
        """Test that data is returned from cache if available."""
        mock_df = pd.DataFrame({'Close': [150]})
        
        with patch.object(self.fetcher.cache, 'load_from_cache', return_value=mock_df) as mock_load:
            with patch('yfinance.download') as mock_download:
                df = self.fetcher.get_data("AAPL", start="2023-01-01")
                
                mock_load.assert_called_once()
                mock_download.assert_not_called()
                self.assertIsNotNone(df)

class TestMainCli(unittest.TestCase):
    """Tests for the main CLI script."""

    @patch('main.YfData')
    def test_single_ticker_fetch(self, mock_yf_data):
        """Test the CLI with a single ticker."""
        mock_instance = mock_yf_data.return_value
        mock_instance.get_data.return_value = pd.DataFrame({'Close': [150]})
        
        with patch('sys.argv', ['main.py', 'AAPL']):
            return_code = cli.main()
            
            mock_instance.get_data.assert_called_once_with("AAPL", interval='1d')
            self.assertEqual(return_code, 0)

    @patch('main.YfData')
    def test_multi_ticker_fetch(self, mock_yf_data):
        """Test the CLI with multiple tickers."""
        mock_instance = mock_yf_data.return_value
        mock_instance.get_data.return_value = pd.DataFrame({'Close': [150]})
        
        with patch('sys.argv', ['main.py', 'AAPL', 'MSFT', '-t', '2']):
            return_code = cli.main()
            
            self.assertEqual(mock_instance.get_data.call_count, 2)
            self.assertEqual(return_code, 0)

    def test_input_validation(self):
        """Test input validation for dates and intervals."""
        with patch('sys.argv', ['main.py', 'AAPL', '-s', 'invalid-date']):
            self.assertEqual(cli.main(), 1)
            
        with patch('sys.argv', ['main.py', 'AAPL', '-i', 'invalid-interval']):
            self.assertEqual(cli.main(), 1)

if __name__ == '__main__':
    unittest.main()
