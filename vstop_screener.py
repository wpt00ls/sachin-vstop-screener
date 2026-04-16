import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import concurrent.futures

# ==========================================
# 1. CONFIGURATION
# ==========================================
VSTOP_MULT = 3.0   # Structural trend setting for multi-baggers
ATR_PERIOD = 20
EMA_PERIODS = [50, 200] 
VOL_MULT   = 1.5   
BOX_LOOKBACK = 5   
RSI_PERIOD = 14
BENCHMARK  = "^NSEI" 
DATA_LOOKBACK = 450 

def get_nifty500():
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    try:
        df = pd.read_csv(url)
        return [f"{s}.NS" for s in df['Symbol'].tolist()]
    except Exception:
        # Fallback list if NSE URL is unreachable
        return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "TATASTEEL.NS"]

def calculate_master_logic(df, bench_df, vstop_mult=VSTOP_MULT, atr_period=ATR_PERIOD, ema_periods=EMA_PERIODS, box_lookback=BOX_LOOKBACK, rsi_period=RSI_PERIOD):
    df.columns = [str(c).lower() for c in df.columns]
    
    # --- 1. RSI & EMAs ---
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    df['rsi'] = 100 - (100 / (1 + (gain / loss)))

    for p in ema_periods:
        df[f'ema{p}'] = df['close'].ewm(span=p, adjust=False).mean()
    
    # EMA 200 Slope (Performance over last 20 trading days)
    # Note: We use 200 explicitly here as per original logic, but we could make it dynamic if needed.
    # For parity, we'll keep it as is or check if 200 is in ema_periods.
    if 200 in ema_periods:
        df['ema200_slope'] = (df['ema200'] - df['ema200'].shift(20)) / df['ema200'].shift(20) * 100
        
    df['vol_avg'] = df['volume'].rolling(20).mean()
    df['rs_ratio'] = df['close'] / bench_df['close'].reindex(df.index).ffill()
    df['rs_ma'] = df['rs_ratio'].rolling(50).mean()
    
    # --- 2. Squeeze Pro Logic (Bollinger Bands vs Keltner Channels) ---
    sma = df['close'].rolling(window=20).mean()
    std = df['close'].rolling(window=20).std()
    df['bb_up'] = sma + (2.0 * std)
    df['bb_low'] = sma - (2.0 * std)
    
    tr = pd.concat([df['high']-df['low'], abs(df['high']-df['close'].shift(1)), abs(df['low']-df['close'].shift(1))], axis=1).max(axis=1)
    atr_val = tr.rolling(20).mean() # Using 20 as period for ATR in squeeze
    
    # Standard (1.5x), Tight (1.2x), Extra Tight (1.0x ATR)
    df['sqz_std'] = (df['bb_up'] < (sma + (1.5 * atr_val))) & (df['bb_low'] > (sma - (1.5 * atr_val)))
    df['sqz_tight'] = (df['bb_up'] < (sma + (1.2 * atr_val))) & (df['bb_low'] > (sma - (1.2 * atr_val)))
    df['sqz_xtra'] = (df['bb_up'] < (sma + (1.0 * atr_val))) & (df['bb_low'] > (sma - (1.0 * atr_val)))

    # --- 3. Box & 52-Week Metrics ---
    df['box_high'] = df['high'].shift(1).rolling(window=box_lookback).max()
    df['box_low'] = df['low'].shift(1).rolling(window=box_lookback).min()
    df['box_width_pct'] = ((df['box_high'] - df['box_low']) / df['box_low']) * 100
    df['hi_52w'] = df['high'].rolling(window=252).max()
    df['lo_52w'] = df['low'].rolling(window=252).min()
    
    # --- 4. Recursive Vstop ---
    # We use the provided atr_period for VStop
    atr_vstop = tr.rolling(atr_period).mean()
    closes, highs, lows, atrs = df['close'].values, df['high'].values, df['low'].values, atr_vstop.values
    stops, trends = [np.nan]*len(df), [True]*len(df)
    
    # Initialize with first valid ATR index
    start_idx = atr_period
    if len(df) <= start_idx:
        df['vstop'], df['trend'] = stops, trends
        return df
        
    uptrend, max_val, stop = True, highs[start_idx], lows[start_idx]
    
    for i in range(start_idx, len(df)):
        src, atr_m = closes[i], atrs[i] * vstop_mult
        if np.isnan(atr_m):
            continue
        if uptrend:
            max_val = max(max_val, highs[i])
            stop = max(stop, max_val - atr_m)
            if src < stop:
                uptrend, stop = False, lows[i] + atr_m
        else:
            stop = min(stop, lows[i] + atr_m)
            if src > stop:
                uptrend, max_val, stop = True, highs[i], highs[i] - atr_m
        stops[i], trends[i] = stop, uptrend
        
    df['vstop'], df['trend'] = stops, trends
    return df

def calculate_status(row, prev_row, vol_mult=VOL_MULT, ema_periods=EMA_PERIODS):
    # Squeeze Label Assignment
    sqz_label = "None"
    if row['sqz_xtra']:
        sqz_label = "EXTRA TIGHT"
    elif row['sqz_tight']:
        sqz_label = "TIGHT"
    elif row['sqz_std']:
        sqz_label = "Standard"
    elif prev_row is not None and prev_row['sqz_std'] and not row['sqz_std']:
        sqz_label = "FIRED 🚀"

    # Confluence Check Results
    c1 = row['trend']
    c3 = row['close'] > row['box_high']
    c4 = row['volume'] > (row['vol_avg'] * vol_mult)
    ema_check = all(row['close'] > row[f'ema{p}'] for p in ema_periods)
    rs_check = (row['rs_ratio'] > row['rs_ma'])
    # Check if ema200_slope exists in row
    slope_up = row.get('ema200_slope', 0) > 0 if 'ema200_slope' in row else False

    # --- STATUS LOGIC (LIFECYCLE RANKING) ---
    if sqz_label == "FIRED 🚀" and c3 and c4 and ema_check and rs_check and slope_up:
        status = "💎 DIAMOND LAUNCH"
    elif sqz_label == "FIRED 🚀":
        status = "🚀 SQUEEZE FIRE"
    elif (sqz_label in ["TIGHT", "EXTRA TIGHT"]) and row['box_width_pct'] < 5:
        status = "🌀 COILING"
    elif c1 and rs_check and slope_up:
        status = "📈 TRENDING"
    else:
        status = "Consolidating"
        
    return status, sqz_label

def audit_stock(ticker, full_data, bench_df):
    try:
        if ticker not in full_data.columns.get_level_values(0): return None
        df = full_data[ticker].copy().dropna(subset=['Close'])
        if len(df) < 252: return None
        df = calculate_master_logic(df, bench_df)
        
        today, yesterday = df.iloc[-1], df.iloc[-2]
        week_ago = df.iloc[-5] if len(df) > 5 else df.iloc[0]
        month_ago = df.iloc[-21] if len(df) > 21 else df.iloc[0]
        
        status, sqz_label = calculate_status(today, yesterday)

        # Confluence results for display
        c1 = today['trend']
        c2 = today['low'] > yesterday['low']
        c3 = today['close'] > today['box_high']
        c4 = today['volume'] > (today['vol_avg'] * VOL_MULT)
        ema_check = all(today['close'] > today[f'ema{p}'] for p in EMA_PERIODS)
        
        return {
            "Ticker": ticker.replace(".NS", ""),
            "LTP": round(today['close'], 2),
            "Status": status,
            "Squeeze Status": sqz_label,
            "1. Vstop Green": "Yes" if c1 else "No",
            "2. Higher Low": "Yes" if c2 else "No",
            "3. Box Breakout": "Yes" if c3 else "No",
            "4. Heavy Volume": "Yes" if c4 else "No",
            "5. EMA Filters Met": "Yes" if ema_check else "No",
            "Box High (Ceiling)": round(today['box_high'], 2),
            "Box Width %": round(today['box_width_pct'], 2),
            "RSI (14)": round(today['rsi'], 2),
            "1D %": round(((today['close']/yesterday['close'])-1)*100, 2),
            "1W %": round(((today['close']/week_ago['close'])-1)*100, 2),
            "1M %": round(((today['close']/month_ago['close'])-1)*100, 2),
            "52W High": round(today['hi_52w'], 2),
            "52W Low": round(today['lo_52w'], 2),
            "EMA 200 Slope": round(today.get('ema200_slope', 0), 3),
            "Chart Link": f"https://www.tradingview.com/chart/?symbol=NSE:{ticker.replace('.NS', '')}"
        }
    except Exception:
        return None

# ==========================================
# 2. EXECUTION
# ==========================================
def main():
    tickers = get_nifty500()
    start_pt = (datetime.now() - timedelta(days=DATA_LOOKBACK)).strftime("%Y-%m-%d")

    print("📡 Downloading Nifty 500 Data and Benchmark...")
    bench = yf.download(BENCHMARK, start=start_pt, auto_adjust=False, progress=False)
    if isinstance(bench.columns, pd.MultiIndex): bench.columns = bench.columns.get_level_values(0)
    bench.columns = [str(c).lower() for c in bench.columns]

    data = yf.download(tickers, start=start_pt, auto_adjust=False, group_by='ticker', progress=True)

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(audit_stock, t, data, bench) for t in tickers]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res: results.append(res)

    if results:
        fname = f"NSE500_Master_Audit_{datetime.now().strftime('%d%b')}.xlsx"

        # Sort logic: Diamond > Squeeze Fire > Coiling > Trending > Consolidating
        status_order = {"💎 DIAMOND LAUNCH": 0, "🚀 SQUEEZE FIRE": 1, "🌀 COILING": 2, "📈 TRENDING": 3, "Consolidating": 4}
        df_audit = pd.DataFrame(results)
        df_audit['rank'] = df_audit['Status'].map(status_order)
        df_audit = df_audit.sort_values("rank").drop(columns=['rank'])

        with pd.ExcelWriter(fname, engine='xlsxwriter') as writer:
            df_audit.to_excel(writer, index=False, sheet_name='NSE500_Audit')

            workbook = writer.book
            ws = writer.sheets['NSE500_Audit']

            # Formatting Styles
            green_fmt = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
            red_fmt   = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})

            # Conditional Formatting for Yes/No columns (E to I)
            ws.conditional_format('E2:I600', {'type': 'cell', 'criteria': 'equal to', 'value': '"Yes"', 'format': green_fmt})
            ws.conditional_format('E2:I600', {'type': 'cell', 'criteria': 'equal to', 'value': '"No"', 'format': red_fmt})

            ws.set_column('A:T', 18)

        print(f"✅ Audit Complete! Saved to {fname}")

if __name__ == "__main__":
    main()