import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='VStop Historical Backtester')
    parser.add_argument('ticker', type=str, help='Ticker symbol (e.g., RELIANCE.NS)')
    parser.add_argument('--years', type=int, default=5, help='Number of years for historical data (default: 5)')
    
    args = parser.parse_args()
    
    print(f"Backtesting ticker: {args.ticker} over {args.years} years...")
    # Logic for data fetching and backtesting will be added in subsequent tasks

if __name__ == "__main__":
    main()
