# Yahoo Finance Data Scraper

A Python tool for fetching historical financial data from Yahoo Finance with built-in caching, rate limiting, and comprehensive error handling.

## Features

- **Multiple Asset Classes**: Support for stocks, crypto, forex, indices, and commodities
- **Flexible Data Retrieval**: Fetch data by time period or specific date range
- **Built-in Caching**: Local caching to reduce API calls and improve performance
- **Rate Limiting**: Exponential backoff retry logic to handle API throttling
- **Comprehensive Error Handling**: Robust error handling with detailed logging
- **CLI Interface**: Easy-to-use command-line interface with validation

## Installation

1. Clone or download the project files
2. Install dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Get Apple stock data
python main.py AAPL

# Get Bitcoin data with hourly intervals
python main.py BTC-USD -i 1h

# Get Microsoft data for 2023
python main.py MSFT -s 2023-01-01 -e 2023-12- closing price of the stock on that day.
- **Volume**: Number of shares traded on that day.

### Command Line Options

- `ticker`: Stock/crypto ticker symbol (required unless using -m option)
- `-s, --start`: Start date in YYYY-MM-DD format
- `-e, --end`: End date in YYYY-MM-DD format  
- `-i, --interval`: Data interval (1m, 5m, 1h, 1d, 1wk, 1mo, etc.)
- `-m, --market`: Show available tickers for a market (crypto, stocks, forex, indices, commodities)
 - `-o, --out-dir`: Output directory to save CSV files. If not provided, CSVs are saved to the parent directory of the project.

You can use `-o` to write output files to a custom folder (it will be created if it doesn't exist):

```bash
python main.py AAPL MSFT -o ./data/output
```

### Supported Intervals

- **Intraday**: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h
- **Daily/Weekly**: 1d, 5d, 1wk, 1mo, 3mo

### Supported Markets

- **crypto**: Cryptocurrencies (BTC-USD, ETH-USD, etc.)
- **stocks**: Popular stocks (AAPL, MSFT, GOOGL, etc.)
- **forex**: Currency pairs (EURUSD=X, GBPUSD=X, etc.)
- **indices**: Market indices (^DJI, ^GSPC, ^IXIC, etc.)
- **commodities**: Commodity futures (GC=F, SI=F, etc.)

## Examples

```bash
# Show available crypto tickers
python main.py -m crypto

# Get Tesla stock data with daily intervals
python main.py TSLA -i 1d

# Get S&P 500 data for the last 6 months
python main.py ^GSPC -i 1d

# Get Bitcoin data for a specific date range
python main.py BTC-USD -s 2023-01-01 -e 2023-06-30 -i 1h
```

## Data Output

The tool outputs:
- First 5 rows of the dataset
- Total number of rows and columns
- Date range of the data

Example output:
```
Data for AAPL:
                   Open        High         Low       Close   Adj Close    Volume
Date                                                                             
2023-01-03  130.279999  130.899994  124.169998  125.070000  124.617943  112117500
2023-01-04  126.889999  128.660004  125.080002  126.360001  125.902451   89113600
...

Shape: (251, 6)
Date range: 2023-01-03 00:00:00 to 2023-12-29 00:00:00
```

## Caching

The tool automatically caches downloaded data in the `./cache/yfinance/` directory to:
- Reduce API calls
- Improve performance on repeated requests
- Handle network interruptions gracefully

Cache files are automatically cleaned up when new data is fetched for the same ticker and time period.

## Testing

Run the test suite to verify functionality:

```bash
python test_yf_scraper.py
```

## Project Structure

```
yf/
├── main.py              # Main CLI application
├── fetcher.py           # Data fetching logic with rate limiting
├── cache.py             # Caching functionality
├── tickers.py           # Ticker symbol lists for different markets
├── set_logs.py          # Logging configuration
├── test_yf_scraper.py   # Test suite
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Dependencies

- `yfinance`: Yahoo Finance data API
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computing (pandas dependency)

## Error Handling

The tool includes comprehensive error handling for:
- Network connectivity issues
- Invalid ticker symbols
- Invalid date formats
- API rate limiting
- Corrupted cache files

## Logging

All operations are logged with timestamps and detailed error messages. Log levels can be adjusted in the code if needed.

## License

This project is open source and available under the MIT License.
