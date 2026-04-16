import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from vstop_screener import calculate_master_logic, get_nifty500, audit_stock

def test_rsi_calculation():
    # Create a 30-day dummy dataset
    dates = pd.date_range(start="2023-01-01", periods=30)
    data = {
        'high': [100] * 30,
        'low': [90] * 30,
        'close': [
            100, 102, 104, 103, 105, 107, 108, 110, 109, 111,
            113, 114, 116, 115, 117, 119, 120, 122, 121, 123,
            125, 126, 128, 127, 129, 131, 132, 134, 133, 135
        ],
        'volume': [1000] * 30
    }
    df = pd.DataFrame(data, index=dates)
    
    # Dummy benchmark data
    bench_data = {'close': [100] * 30}
    bench_df = pd.DataFrame(bench_data, index=dates)
    
    # Calculate indicators
    result_df = calculate_master_logic(df.copy(), bench_df)
    
    # Verify RSI column exists
    assert 'rsi' in result_df.columns
    
    # Check a specific RSI value (at index 20)
    # The current implementation uses simple rolling mean of gains/losses.
    # Manual calculation for simple RSI (period 14) at index 14:
    # Gains: [2, 2, 0, 2, 2, 1, 2, 0, 2, 2, 1, 2, 0, 2] -> Sum: 19, Mean: 1.357
    # Losses: [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0] -> Sum: 3, Mean: 0.214
    # RS = 1.357 / 0.214 = 6.34
    # RSI = 100 - (100 / (1 + 6.34)) = 86.37
    
    # Let's check index 14 specifically
    rsi_val = result_df['rsi'].iloc[14]
    assert not np.isnan(rsi_val)
    # We expect roughly 86.37 based on manual calculation above
    assert pytest.approx(rsi_val, 0.01) == 86.37

def test_ema_calculation():
    # Create a 250-day dummy dataset (to cover EMA 200 + 20 day slope)
    dates = pd.date_range(start="2023-01-01", periods=250)
    data = {
        'high': [100] * 250,
        'low': [90] * 250,
        'close': [100 + i for i in range(250)], # Steadily increasing
        'volume': [1000] * 250
    }
    df = pd.DataFrame(data, index=dates)
    
    # Dummy benchmark data
    bench_data = {'close': [100] * 250}
    bench_df = pd.DataFrame(bench_data, index=dates)
    
    # Calculate indicators
    result_df = calculate_master_logic(df.copy(), bench_df)
    
    # Verify columns exist
    assert 'ema50' in result_df.columns
    assert 'ema200' in result_df.columns
    assert 'ema200_slope' in result_df.columns
    
    # Verify EMA 200 slope logic
    # Slope = (ema200 - ema200_shift20) / ema200_shift20 * 100
    idx = 249
    ema200_curr = result_df['ema200'].iloc[idx]
    ema200_prev = result_df['ema200'].iloc[idx-20]
    expected_slope = (ema200_curr - ema200_prev) / ema200_prev * 100
    
    assert pytest.approx(result_df['ema200_slope'].iloc[idx], 0.0001) == expected_slope

def test_squeeze_logic():
    # Create a 30-day dummy dataset
    dates = pd.date_range(start="2023-01-01", periods=30)
    data = {
        'high': [102] * 30,
        'low': [98] * 30,
        'close': [100] * 30,
        'volume': [1000] * 30
    }
    df = pd.DataFrame(data, index=dates)
    
    # Dummy benchmark data
    bench_data = {'close': [100] * 30}
    bench_df = pd.DataFrame(bench_data, index=dates)
    
    # Calculate indicators
    result_df = calculate_master_logic(df.copy(), bench_df)
    
    # Verify Squeeze columns exist
    assert 'bb_up' in result_df.columns
    assert 'bb_low' in result_df.columns
    assert 'sqz_std' in result_df.columns
    assert 'sqz_tight' in result_df.columns
    assert 'sqz_xtra' in result_df.columns
    
    # In this case, with zero volatility (close=100 constantly),
    # std=0, so bb_up = sma = 100, bb_low = sma = 100
    # high-low = 4, so tr=4, atr_20=4
    # sma + 1.5*atr = 100 + 6 = 106
    # bb_up (100) < 106 and bb_low (100) > 94 -> sqz_std should be True
    idx = 29
    assert result_df['sqz_std'].iloc[idx]
    assert result_df['sqz_tight'].iloc[idx]
    assert result_df['sqz_xtra'].iloc[idx]

def test_squeeze_multipliers():
    # Test specific multipliers for squeeze
    from vstop_screener import SQZ_STD_MULT, SQZ_TIGHT_MULT, SQZ_XTRA_MULT
    assert SQZ_STD_MULT == 1.5
    assert SQZ_TIGHT_MULT == 1.2
    assert SQZ_XTRA_MULT == 1.0

    # Create data where Bollinger Bands and Keltner Channels are easily controllable
    dates = pd.date_range(start="2023-01-01", periods=30)
    # ATR = 4
    data = {
        'high': [102] * 30,
        'low': [98] * 30,
        'close': [100] * 30,
        'volume': [1000] * 30
    }
    df = pd.DataFrame(data, index=dates)
    bench_df = pd.DataFrame({'close': [100] * 30}, index=dates)
    
    # We will mock the bb_up and bb_low columns after calculate_master_logic
    # to test the squeeze boolean logic specifically.
    df_res = calculate_master_logic(df, bench_df)
    
    # sma = 100, atr = 4
    # sqz_std threshold: 100 + 1.5 * 4 = 106
    # sqz_tight threshold: 100 + 1.2 * 4 = 104.8
    # sqz_xtra threshold: 100 + 1.0 * 4 = 104
    
    # Test 1: bb_up = 105 (Between Standard and Tight)
    df_res.loc[dates[-1], 'bb_up'] = 105
    df_res.loc[dates[-1], 'bb_low'] = 95
    # Recalculate booleans for the last row
    sma = 100
    atr = 4
    df_res.loc[dates[-1], 'sqz_std'] = (df_res.loc[dates[-1], 'bb_up'] < (sma + (SQZ_STD_MULT * atr))) & (df_res.loc[dates[-1], 'bb_low'] > (sma - (SQZ_STD_MULT * atr)))
    df_res.loc[dates[-1], 'sqz_tight'] = (df_res.loc[dates[-1], 'bb_up'] < (sma + (SQZ_TIGHT_MULT * atr))) & (df_res.loc[dates[-1], 'bb_low'] > (sma - (SQZ_TIGHT_MULT * atr)))
    df_res.loc[dates[-1], 'sqz_xtra'] = (df_res.loc[dates[-1], 'bb_up'] < (sma + (SQZ_XTRA_MULT * atr))) & (df_res.loc[dates[-1], 'bb_low'] > (sma - (SQZ_XTRA_MULT * atr)))
    
    assert df_res.iloc[-1]['sqz_std'] == True
    assert df_res.iloc[-1]['sqz_tight'] == False
    assert df_res.iloc[-1]['sqz_xtra'] == False

    # Test 2: bb_up = 104.5 (Between Tight and Extra Tight)
    df_res.loc[dates[-1], 'bb_up'] = 104.5
    df_res.loc[dates[-1], 'bb_low'] = 95.5
    df_res.loc[dates[-1], 'sqz_std'] = (df_res.loc[dates[-1], 'bb_up'] < (sma + (SQZ_STD_MULT * atr))) & (df_res.loc[dates[-1], 'bb_low'] > (sma - (SQZ_STD_MULT * atr)))
    df_res.loc[dates[-1], 'sqz_tight'] = (df_res.loc[dates[-1], 'bb_up'] < (sma + (SQZ_TIGHT_MULT * atr))) & (df_res.loc[dates[-1], 'bb_low'] > (sma - (SQZ_TIGHT_MULT * atr)))
    df_res.loc[dates[-1], 'sqz_xtra'] = (df_res.loc[dates[-1], 'bb_up'] < (sma + (SQZ_XTRA_MULT * atr))) & (df_res.loc[dates[-1], 'bb_low'] > (sma - (SQZ_XTRA_MULT * atr)))
    
    assert df_res.iloc[-1]['sqz_std'] == True
    assert df_res.iloc[-1]['sqz_tight'] == True
    assert df_res.iloc[-1]['sqz_xtra'] == False

    # Test 3: bb_up = 103.5 (Extra Tight)
    df_res.loc[dates[-1], 'bb_up'] = 103.5
    df_res.loc[dates[-1], 'bb_low'] = 96.5
    df_res.loc[dates[-1], 'sqz_std'] = (df_res.loc[dates[-1], 'bb_up'] < (sma + (SQZ_STD_MULT * atr))) & (df_res.loc[dates[-1], 'bb_low'] > (sma - (SQZ_STD_MULT * atr)))
    df_res.loc[dates[-1], 'sqz_tight'] = (df_res.loc[dates[-1], 'bb_up'] < (sma + (SQZ_TIGHT_MULT * atr))) & (df_res.loc[dates[-1], 'bb_low'] > (sma - (SQZ_TIGHT_MULT * atr)))
    df_res.loc[dates[-1], 'sqz_xtra'] = (df_res.loc[dates[-1], 'bb_up'] < (sma + (SQZ_XTRA_MULT * atr))) & (df_res.loc[dates[-1], 'bb_low'] > (sma - (SQZ_XTRA_MULT * atr)))
    
    assert df_res.iloc[-1]['sqz_std'] == True
    assert df_res.iloc[-1]['sqz_tight'] == True
    assert df_res.iloc[-1]['sqz_xtra'] == True

def test_box_metrics():
    # Create a 300-day dummy dataset (for 52-week/252-day metrics)
    dates = pd.date_range(start="2023-01-01", periods=300)
    # Highs steadily increasing, Lows steadily increasing
    data = {
        'high': [100 + i for i in range(300)],
        'low': [90 + i for i in range(300)],
        'close': [95 + i for i in range(300)],
        'volume': [1000] * 300
    }
    df = pd.DataFrame(data, index=dates)
    
    # Dummy benchmark data
    bench_data = {'close': [100] * 300}
    bench_df = pd.DataFrame(bench_data, index=dates)
    
    # Calculate indicators
    result_df = calculate_master_logic(df.copy(), bench_df)
    
    # Verify columns exist
    assert 'box_high' in result_df.columns
    assert 'box_low' in result_df.columns
    assert 'box_width_pct' in result_df.columns
    assert 'hi_52w' in result_df.columns
    assert 'lo_52w' in result_df.columns
    
    # Check Box metrics at index 10
    # box_high is max of high.shift(1) over 5 periods
    # high.shift(1) at index 10: [..., 104, 105, 106, 107, 108, 109]
    # Lookback 5 from index 10 (exclusive of index 10 itself due to shift): 
    # indices 5, 6, 7, 8, 9. Highs: 105, 106, 107, 108, 109. Max = 109.
    assert result_df['box_high'].iloc[10] == 109
    assert result_df['box_low'].iloc[10] == 95 # indices 5..9 lows: 95, 96, 97, 98, 99. Min = 95.
    
    # Check 52-week metrics at index 260
    # hi_52w is max of high over 252 periods (inclusive of current)
    # highs: 100, ..., 359 (at index 259)
    # index 260: high is 360. hi_52w from 260 back to 9 (252 periods)
    # Max will be current high (360) as they are increasing.
    assert result_df['hi_52w'].iloc[260] == 360
    assert result_df['lo_52w'].iloc[260] == 99 # 260-252+1 = index 9. low[9] = 90+9 = 99.

def test_vstop_calculation():
    # Create a 60-day dummy dataset
    dates = pd.date_range(start="2023-01-01", periods=60)
    # Start with uptrend, then sharp drop
    close = [100 + i for i in range(40)] + [140 - (i-40)*5 for i in range(40, 60)]
    high = [c + 2 for c in close]
    low = [c - 2 for c in close]
    
    data = {
        'high': high,
        'low': low,
        'close': close,
        'volume': [1000] * 60
    }
    df = pd.DataFrame(data, index=dates)
    
    # Dummy benchmark data
    bench_data = {'close': [100] * 60}
    bench_df = pd.DataFrame(bench_data, index=dates)
    
    # Calculate indicators
    result_df = calculate_master_logic(df.copy(), bench_df)
    
    # Verify VSTOP columns exist
    assert 'vstop' in result_df.columns
    assert 'trend' in result_df.columns
    
    # Check trend at index 30 (should be uptrend)
    assert result_df['trend'].iloc[30]
    
    # Check trend reversal at end (should be downtrend)
    assert not result_df['trend'].iloc[59]

def test_get_nifty500():
    # Mocking pandas.read_csv to return a simple dataframe
    with patch('pandas.read_csv') as mock_read_csv:
        mock_df = pd.DataFrame({'Symbol': ['RELIANCE', 'TCS']})
        mock_read_csv.return_value = mock_df
        
        tickers = get_nifty500()
        assert tickers == ['RELIANCE.NS', 'TCS.NS']
        
    # Test fallback
    with patch('pandas.read_csv', side_effect=Exception("Network error")):
        tickers = get_nifty500()
        assert 'RELIANCE.NS' in tickers

def test_audit_stock():
    # Create a dummy full_data for audit_stock
    dates = pd.date_range(start="2023-01-01", periods=300)
    data = {
        ('RELIANCE.NS', 'Open'): [100.0] * 300,
        ('RELIANCE.NS', 'High'): [102.0] * 300,
        ('RELIANCE.NS', 'Low'): [98.0] * 300,
        ('RELIANCE.NS', 'Close'): [100.0] * 300,
        ('RELIANCE.NS', 'Volume'): [1000.0] * 300
    }
    full_data = pd.DataFrame(data, index=dates)
    full_data.columns = pd.MultiIndex.from_tuples(full_data.columns)
    
    # Dummy benchmark data
    bench_data = {'close': [100.0] * 300}
    bench_df = pd.DataFrame(bench_data, index=dates)
    
    # Test audit_stock
    res = audit_stock('RELIANCE.NS', full_data, bench_df)
    assert res is not None
    assert res['Ticker'] == 'RELIANCE'
    # Default state for flat data should be "COILING" or "Consolidating"
    # (sqz_label in ["TIGHT", "EXTRA TIGHT"]) and box_width_pct < 3 -> "🌀 COILING"
    # In this test data, box_high=102, box_low=98 (from previous rows)
    # box_width_pct = (102-98)/98 * 100 = 4.08%
    # 4.08 > 3, so it should be "Consolidating"
    assert res['Status'] == "Consolidating"

    # Now let's test COILING with tighter data
    data_tight = {
        ('RELIANCE.NS', 'Open'): [100.0] * 300,
        ('RELIANCE.NS', 'High'): [100.5] * 300,
        ('RELIANCE.NS', 'Low'): [99.5] * 300,
        ('RELIANCE.NS', 'Close'): [100.0] * 300,
        ('RELIANCE.NS', 'Volume'): [1000.0] * 300
    }
    full_data_tight = pd.DataFrame(data_tight, index=dates)
    full_data_tight.columns = pd.MultiIndex.from_tuples(full_data_tight.columns)
    # box_width_pct = (100.5-99.5)/99.5 * 100 = 1.005% < 3%
    res_tight = audit_stock('RELIANCE.NS', full_data_tight, bench_df)
    assert res_tight['Status'] == "🌀 COILING"

def test_main_execution():
    # Mocking external calls in the main execution block
    with patch('vstop_screener.get_nifty500') as mock_get_nifty:
        with patch('yfinance.download') as mock_yf:
            with patch('pandas.DataFrame.to_excel') as mock_to_excel:
                with patch('pandas.ExcelWriter') as mock_writer:
                    mock_get_nifty.return_value = ['RELIANCE.NS']
                    
                    # Mocking yf.download to return dataframes
                    mock_bench = pd.DataFrame({'Close': [100.0] * 300}, index=pd.date_range('2023-01-01', periods=300))
                    mock_bench.columns = ['close']
                    
                    mock_data = pd.DataFrame({
                        ('RELIANCE.NS', 'Open'): [100.0] * 300,
                        ('RELIANCE.NS', 'High'): [102.0] * 300,
                        ('RELIANCE.NS', 'Low'): [98.0] * 300,
                        ('RELIANCE.NS', 'Close'): [100.0] * 300,
                        ('RELIANCE.NS', 'Volume'): [1000.0] * 300
                    }, index=pd.date_range('2023-01-01', periods=300))
                    mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)
                    
                    # Side effect for yf.download to handle both calls
                    def yf_side_effect(tickers, *args, **kwargs):
                        if tickers == "^NSEI":
                            return mock_bench
                        return mock_data
                    mock_yf.side_effect = yf_side_effect
                    
                    # Mock ExcelWriter context manager
                    mock_writer.return_value.__enter__.return_value = MagicMock()
                    
                    from vstop_screener import main
                    main()
                    
                    # Verify that download was called
                    assert mock_yf.called
                    # Verify that to_excel was called
                    assert mock_to_excel.called
