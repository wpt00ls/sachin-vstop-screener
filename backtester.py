import argparse
import sys
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from vstop_screener import calculate_master_logic, calculate_status, BENCHMARK

def fetch_data(ticker, years=5):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365 + 252) # Increased buffer for indicators
    
    print(f"📡 Downloading {ticker} data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)
    
    if df.empty:
        raise ValueError(f"No data found for ticker: {ticker}")
        
    # Standardize columns to lowercase
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).lower() for c in df.columns]
    
    return df

def generate_signals(df, ticker_name):
    # Fetch benchmark data for calculate_master_logic
    print(f"📡 Downloading benchmark {BENCHMARK} for calculations...")
    bench_df = yf.download(BENCHMARK, start=df.index[0], end=df.index[-1], auto_adjust=False, progress=False)
    if isinstance(bench_df.columns, pd.MultiIndex):
        bench_df.columns = bench_df.columns.get_level_values(0)
    bench_df.columns = [str(c).lower() for c in bench_df.columns]
    
    # Calculate indicators
    df = calculate_master_logic(df, bench_df)
    
    trades = []
    in_position = False
    entry_price = 0
    entry_date = None
    
    print(f"🔍 Analyzing signals for {ticker_name}...")
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        status, _ = calculate_status(row, prev_row)
        
        if not in_position:
            # BUY Condition (Aggressive Breakout)
            if status in ["💎 DIAMOND LAUNCH", "🚀 SQUEEZE FIRE"]:
                in_position = True
                entry_price = row['close']
                entry_date = df.index[i]
                print(f"  🟢 BUY at {entry_price:.2f} on {entry_date.date()} (Status: {status})")
        else:
            # SELL Condition (Trend Failure)
            exit_reason = None
            if row['trend'] == False:
                exit_reason = "VStop Red"
            elif 'ema50' in row and row['close'] < row['ema50']:
                exit_reason = "Below EMA 50"
                
            if exit_reason:
                exit_price = row['close']
                exit_date = df.index[i]
                pnl_pct = (exit_price - entry_price) / entry_price * 100
                
                trades.append({
                    'ticker': ticker_name,
                    'entry_date': entry_date,
                    'entry_price': entry_price,
                    'exit_date': exit_date,
                    'exit_price': exit_price,
                    'pnl_pct': pnl_pct,
                    'exit_reason': exit_reason
                })
                
                print(f"  🔴 SELL at {exit_price:.2f} on {exit_date.date()} (Reason: {exit_reason}) | PnL: {pnl_pct:.2f}%")
                in_position = False
            
    return trades, df

def calculate_metrics(trades):
    if not trades:
        return {
            'total_trades': 0,
            'win_rate': 0.0,
            'total_pnl': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'max_drawdown': 0.0
        }
        
    pnls = [t['pnl_pct'] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    
    total_trades = len(trades)
    win_rate = len(wins) / total_trades * 100
    total_pnl = sum(pnls)
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0
    
    # Simple max drawdown calculation based on trade sequence
    cumulative_pnl = 0
    peak = 0
    max_dd = 0
    for p in pnls:
        cumulative_pnl += p
        if cumulative_pnl > peak:
            peak = cumulative_pnl
        dd = peak - cumulative_pnl
        if dd > max_dd:
            max_dd = dd
            
    return {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'total_pnl': total_pnl,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'max_drawdown': max_dd
    }

def main():
    parser = argparse.ArgumentParser(description='VStop Historical Backtester')
    parser.add_argument('ticker', type=str, help='Ticker symbol (e.g., RELIANCE.NS)')
    parser.add_argument('--years', type=int, default=5, help='Number of years for historical data (default: 5)')
    
    args = parser.parse_args()
    
    print(f"Backtesting ticker: {args.ticker} over {args.years} years...")
    # Logic for data fetching and backtesting will be added in subsequent tasks

if __name__ == "__main__":
    main()
