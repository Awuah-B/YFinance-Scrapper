#! /usr/bin/env python3
import argparse

from set_logs import setup_logger
import tickers
from fetcher import YfData

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="YFinance Market Data Scraper - Fetch historical financial data from Yahoo Finance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s AAPL                    # Get Apple stock data
  %(prog)s BTC-USD -i 1h           # Get Bitcoin hourly data
  %(prog)s MSFT -s 2023-01-01 -e 2023-12-31  # Get Microsoft data for 2023
  %(prog)s -m crypto               # Show available crypto tickers
  %(prog)s -m stocks               # Show available stock tickers

Supported intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
Supported markets: crypto, stocks, forex, indices, commodities
        """
    )
    parser.add_argument("ticker", nargs='?', help="Ticker symbol on Yahoo Finance (e.g., AAPL, BTC-USD)")
    parser.add_argument("-s", "--start", default=None, help="Historical start date (YYYY-MM-DD format)")
    parser.add_argument("-e", "--end", default=None, help="Historical end date (YYYY-MM-DD format)")
    parser.add_argument("-i", "--interval", default='1d', help="Historical data frequency (default: 1d)")
    parser.add_argument("-m", "--market", choices=['crypto', 'stocks', 'forex', 'indices', 'commodities'], 
                       help="Show available tickers for a financial asset class")
    return parser.parse_args()

def validate_date_format(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD)."""
    import re
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))

def validate_interval(interval: str) -> bool:
    """Validate interval format."""
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    return interval in valid_intervals

def main():
    args = parse_arguments()
    logger = setup_logger(__name__, level='DEBUG')

    try:
        # Handle market listing
        if args.market:
            market_tickers = getattr(tickers, f"{args.market}_tickers", [])
            if market_tickers:
                print(f"Available {args.market} tickers:")
                for ticker in market_tickers:
                    print(f"  {ticker}")
            else:
                print(f"No tickers found for market: {args.market}")
            return
        
        # Validate ticker is provided when not showing markets
        if not args.ticker:
            logger.error("Ticker symbol is required. Use -m to show available markets or provide a ticker symbol.")
            return
        
        # Validate date formats if provided
        if args.start and not validate_date_format(args.start):
            logger.error(f"Invalid start date format: {args.start}. Use YYYY-MM-DD format.")
            return
        
        if args.end and not validate_date_format(args.end):
            logger.error(f"Invalid end date format: {args.end}. Use YYYY-MM-DD format.")
            return
        
        # Validate interval
        if not validate_interval(args.interval):
            logger.error(f"Invalid interval: {args.interval}. Supported intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
            return
        
        # Initialize data fetcher
        fetcher = YfData()
        
        if args.start and args.end:
            # Fetch data for specific date range
            logger.info(f"Fetching data for {args.ticker} from {args.start} to {args.end}")
            df = fetcher.get_data_for_range(args.ticker, args.start, args.end)
        else:
            # Fetch data for timeframe
            logger.info(f"Fetching {args.interval} data for {args.ticker}")
            df = fetcher.get_yf_for_timeframe(args.ticker, args.interval)
        
        if df is not None and not df.empty:
            print(f"\nData for {args.ticker}:")
            print(df.head())
            print(f"\nShape: {df.shape}")
            print(f"Date range: {df.index.min()} to {df.index.max()}")
            
            # Save DataFrame as CSV to parent directory
            import os
            from pathlib import Path
            
            # Create filename with ticker and timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{args.ticker}_{timestamp}.csv"
            parent_dir = Path(__file__).parent.parent
            csv_path = parent_dir / filename
            
            try:
                df.to_csv(csv_path)
                print(f"\nData saved to: {csv_path}")
                logger.info(f"Data successfully saved to {csv_path}")
            except Exception as e:
                logger.error(f"Failed to save CSV file: {e}")
                print(f"Warning: Could not save CSV file: {e}")
        else:
            logger.error(f"Failed to fetch data for {args.ticker}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())