import argparse
import sys
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_data(ticker, years=5):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365 + 100) # Buffer for indicators
    
    print(f"📡 Downloading {ticker} data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)
    
    if df.empty:
        raise ValueError(f"No data found for ticker: {ticker}")
        
    # Standardize columns to lowercase
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).lower() for c in df.columns]
    
    return df

def main():
    parser = argparse.ArgumentParser(description='VStop Historical Backtester')
    parser.add_argument('ticker', type=str, help='Ticker symbol (e.g., RELIANCE.NS)')
    parser.add_argument('--years', type=int, default=5, help='Number of years for historical data (default: 5)')
    
    args = parser.parse_args()
    
    print(f"Backtesting ticker: {args.ticker} over {args.years} years...")
    # Logic for data fetching and backtesting will be added in subsequent tasks

if __name__ == "__main__":
    main()
