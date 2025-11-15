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
    parser.add_argument("tickers", nargs='+', help="One or more ticker symbols on Yahoo Finance (e.g., AAPL BTC-USD)")
    parser.add_argument("-s", "--start", default=None, help="Historical start date (YYYY-MM-DD format)")
    parser.add_argument("-e", "--end", default=None, help="Historical end date (YYYY-MM-DD format)")
    parser.add_argument("-i", "--interval", default='1d', help="Historical data frequency (default: 1d)")
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of concurrent threads to use when fetching multiple tickers (default: 1)")
    parser.add_argument("-o", "--out-dir", default=None, help="Output directory for CSV files (default: parent directory)")
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
        
        # Validate ticker(s) are provided when not showing markets
        if not getattr(args, 'tickers', None):
            logger.error("Ticker symbol(s) are required. Use -m to show available markets or provide ticker symbol(s).")
            return 1
        
        # Validate date formats if provided
        if args.start and not validate_date_format(args.start):
            logger.error(f"Invalid start date format: {args.start}. Use YYYY-MM-DD format.")
            return 1
        
        if args.end and not validate_date_format(args.end):
            logger.error(f"Invalid end date format: {args.end}. Use YYYY-MM-DD format.")
            return 1
        
        # Validate interval
        if not validate_interval(args.interval):
            logger.error(f"Invalid interval: {args.interval}. Supported intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
            return 1
        
        # Initialize data fetcher
        fetcher = YfData()

        # Iterate over all provided tickers and fetch data for each (potentially in parallel)
        from pathlib import Path
        from datetime import datetime
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Prepare kwargs common to all ticker fetches
        if args.start and args.end:
            fetch_kwargs = {'start': args.start, 'end': args.end}
        elif args.start:
            fetch_kwargs = {'start': args.start}
        else:
            fetch_kwargs = {'interval': args.interval}

        any_success = False

        # Determine output directory for CSVs
        parent_dir = None
        if getattr(args, 'out_dir', None):
            parent_dir = Path(args.out_dir)
        else:
            parent_dir = Path(__file__).parent.parent
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create out-dir {parent_dir}: {e}")

        max_workers = max(1, int(args.threads))
        logger.debug(f"Starting ThreadPoolExecutor with max_workers={max_workers}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {executor.submit(fetcher.get_data, ticker, **fetch_kwargs): ticker for ticker in args.tickers}

            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    df = future.result()
                    if df is not None and not df.empty:
                        any_success = True
                        print(f"\nData for {ticker}:")
                        print(df.head())
                        print(f"\nShape: {df.shape}")
                        try:
                            date_min = df.index.min()
                            date_max = df.index.max()
                            print(f"Date range: {date_min} to {date_max}")
                        except Exception:
                            pass

                        # Save DataFrame as CSV to parent directory (or --out-dir)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{ticker}_{timestamp}.csv"
                        csv_path = parent_dir / filename

                        try:
                            df.to_csv(csv_path)
                            print(f"\nData saved to: {csv_path}")
                            logger.info(f"Data successfully saved to {csv_path}")
                        except Exception as e:
                            logger.error(f"Failed to save CSV file for {ticker}: {e}")
                            print(f"Warning: Could not save CSV file for {ticker}: {e}")
                    else:
                        logger.error(f"Failed to fetch data for {ticker}")
                except Exception as e:
                    logger.error(f"Unhandled error fetching data for {ticker}: {e}")

        if not any_success:
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