import argparse
import sys
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from vstop_screener import calculate_master_logic, calculate_status, BENCHMARK
from lightweight_charts import Chart

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
            if status == "💎 DIAMOND LAUNCH":
                in_position = True
                entry_price = row['close']
                entry_date = df.index[i]
                print(f"  🟢 BUY at {entry_price:.2f} on {entry_date.date()} (Status: {status})")

        else:
            # SELL Condition (Trend Failure)
            exit_reason = None
            if not row['trend']:
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

def create_chart(df, trades, ticker):
    chart = Chart(toolbox=True)
    chart.legend(visible=True)
    
    # Standardize df for lightweight-charts
    viz_df = df.copy().reset_index()
    viz_df.columns = [str(c).lower() for c in viz_df.columns]
    if 'date' not in viz_df.columns and 'index' in viz_df.columns:
        viz_df = viz_df.rename(columns={'index': 'date'})
        
    # 1. Main Pane: Price Action
    chart.set(viz_df)
    
    # 2. Indicators on Main Pane
    vstop_line = chart.create_line('VStop', color='#2196F3', width=2)
    vstop_line.set(viz_df[['date', 'vstop']].dropna().rename(columns={'vstop': 'VStop'}))
    
    ema50_line = chart.create_line('EMA 50', color='#FF9800', width=1)
    ema50_line.set(viz_df[['date', 'ema50']].dropna().rename(columns={'ema50': 'EMA 50'}))
    
    ema200_line = chart.create_line('EMA 200', color='#9C27B0', width=1)
    ema200_line.set(viz_df[['date', 'ema200']].dropna().rename(columns={'ema200': 'EMA 200'}))
    
    # 3. Buy/Sell Markers
    for t in trades:
        chart.marker(text='BUY', position='belowBar', shape='arrowUp', color='#26a69a', time=t['entry_date'])
        chart.marker(text=f"SELL ({t['exit_reason']})", position='aboveBar', shape='arrowDown', color='#ef5350', time=t['exit_date'])
        
    # 4. Squeeze Indicators on a Subchart
    try:
        sqz_pane = chart.create_subchart(height=0.2)
        viz_df['sqz_std_val'] = viz_df['sqz_std'].astype(int)
        viz_df['sqz_tight_val'] = viz_df['sqz_tight'].astype(int) * 2
        viz_df['sqz_xtra_val'] = viz_df['sqz_xtra'].astype(int) * 3
        
        sqz_pane.create_line('Standard', color='gray', width=1).set(
            viz_df[['date', 'sqz_std_val']].rename(columns={'sqz_std_val': 'Standard'})
        )
        sqz_pane.create_line('Tight', color='orange', width=1).set(
            viz_df[['date', 'sqz_tight_val']].rename(columns={'sqz_tight_val': 'Tight'})
        )
        sqz_pane.create_line('Extra Tight', color='red', width=1).set(
            viz_df[['date', 'sqz_xtra_val']].rename(columns={'sqz_xtra_val': 'Extra Tight'})
        )
    except Exception as e:
        print(f"⚠️ Could not create squeeze subplot: {e}")

    print("📈 Opening interactive chart...")
    chart.show()
    return True

def print_report(ticker, trades, metrics):
    print("\n" + "="*80)
    print(f"📊 BACKTEST RESULTS: {ticker}")
    print("="*80)
    
    if trades:
        print(f"{'Entry Date':<12} | {'Exit Date':<12} | {'Entry':<8} | {'Exit':<8} | {'PnL %':<8} | {'Reason'}")
        print("-" * 80)
        for t in trades:
            print(f"{t['entry_date'].strftime('%Y-%m-%d'):<12} | "
                  f"{t['exit_date'].strftime('%Y-%m-%d'):<12} | "
                  f"{t['entry_price']:>8.2f} | "
                  f"{t['exit_price']:>8.2f} | "
                  f"{t['pnl_pct']:>7.2f}% | "
                  f"{t['exit_reason']}")
        print("-" * 80)
    else:
        print("No trades executed during this period.")
        print("-" * 80)

    print(f"{'Total Trades:':<20} {metrics['total_trades']}")
    print(f"{'Win Rate:':<20} {metrics['win_rate']:.2f}%")
    print(f"{'Total PnL:':<20} {metrics['total_pnl']:.2f}%")
    print(f"{'Avg Win:':<20} {metrics['avg_win']:.2f}%")
    print(f"{'Avg Loss:':<20} {metrics['avg_loss']:.2f}%")
    print(f"{'Max Drawdown:':<20} {metrics['max_drawdown']:.2f}%")
    print("="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(description='VStop Historical Backtester')
    parser.add_argument('ticker', type=str, help='Ticker symbol (e.g., RELIANCE.NS)')
    parser.add_argument('--years', type=int, default=5, help='Number of years for historical data (default: 5)')
    
    args = parser.parse_args()
    
    try:
        df = fetch_data(args.ticker, args.years)
        trades, df = generate_signals(df, args.ticker)
        metrics = calculate_metrics(trades)
        
        print_report(args.ticker, trades, metrics)
        create_chart(df, trades, args.ticker)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
