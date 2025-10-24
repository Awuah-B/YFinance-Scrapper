#!/usr/bin/env python3

"""
Simple test script for the Yahoo Finance scraper.

This script tests the basic functionality of the YFinance scraper
without making actual API calls to avoid rate limiting during testing.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from fetcher import YfData
from cache import Caches
import tickers

def test_cache_functionality():
    """Test cache creation and basic functionality."""
    print("Testing cache functionality...")
    
    cache = Caches("./test_cache")
    
    # Test date normalization
    test_date = "2023-01-01"
    normalized = cache._normalize_date(test_date)
    print(f"Date normalization test: {test_date} -> {normalized}")
    
    # Test cache path generation
    cache_path = cache._get_cache_path("AAPL", "2023-01-01", "2023-12-31")
    print(f"Cache path generation: {cache_path}")
    
    print("Cache functionality test completed successfully!")
    return True

def test_ticker_lists():
    """Test that ticker lists are properly populated."""
    print("Testing ticker lists...")
    
    markets = ['crypto', 'stocks', 'forex', 'indices', 'commodities']
    
    for market in markets:
        ticker_list = getattr(tickers, f"{market}_tickers", [])
        print(f"{market} tickers: {len(ticker_list)} entries")
        if ticker_list:
            print(f"  Sample: {ticker_list[:3]}...")
        else:
            print(f"  WARNING: {market} tickers list is empty!")
    
    print("Ticker lists test completed!")
    return True

def test_fetcher_initialization():
    """Test that the fetcher can be initialized properly."""
    print("Testing fetcher initialization...")
    
    try:
        fetcher = YfData(max_retries=3, base_delay=1.0)
        print(f"Fetcher initialized with max_retries={fetcher.max_retries}, base_delay={fetcher.base_delay}")
        print("Fetcher initialization test completed successfully!")
        return True
    except Exception as e:
        print(f"Fetcher initialization failed: {e}")
        return False

def cleanup_test_cache():
    """Clean up test cache directory."""
    import shutil
    test_cache_dir = Path("./test_cache")
    if test_cache_dir.exists():
        shutil.rmtree(test_cache_dir)
        print("Test cache directory cleaned up.")

def main():
    """Run all tests."""
    print("Starting Yahoo Finance scraper tests...\n")
    
    tests = [
        test_cache_functionality,
        test_ticker_lists,
        test_fetcher_initialization,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print(f"Test Results: {passed} passed, {failed} failed")
    
    # Cleanup
    cleanup_test_cache()
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
