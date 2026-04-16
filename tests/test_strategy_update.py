import pytest
import pandas as pd
import numpy as np
from vstop_screener import calculate_master_logic, calculate_status, VOL_MULT

def test_normalized_indicators():
    """
    Test that vol_multiple and vstop_dist_pct are correctly calculated.
    """
    dates = pd.date_range(start="2023-01-01", periods=100)
    data = {
        'high': [102] * 100,
        'low': [98] * 100,
        'close': [100] * 100,
        'volume': [1000] * 100
    }
    df = pd.DataFrame(data, index=dates)
    bench_df = pd.DataFrame({'close': [100] * 100}, index=dates)
    
    # We manually set some values for predictable output
    # Close = 100, vol_avg will be 1000, current volume = 1000 -> vol_multiple = 1.0
    # Let's say vstop = 95 -> vstop_dist_pct = (100 - 95) / 100 * 100 = 5.0%
    
    result_df = calculate_master_logic(df, bench_df)
    
    # Check if columns exist
    assert 'vol_multiple' in result_df.columns
    assert 'vstop_dist_pct' in result_df.columns
    
    # Verify values at the end
    last_row = result_df.iloc[-1]
    assert last_row['vol_multiple'] == pytest.approx(1.0)
    
    # vstop calculation depends on Recursive Vstop logic. 
    # With constant price 100 and ATR=4 (from 102-98), vstop mult 3.0
    # ATR_m = 4 * 3.0 = 12.
    # Uptown: stop = max(stop, max_val - 12) = max(98, 102 - 12) = 98.
    # vstop_dist_pct = (100 - 98) / 100 * 100 = 2.0%
    assert last_row['vstop_dist_pct'] == pytest.approx(2.0)

def test_volume_lookback_indicator():
    """
    Test that vol_spike_last_7d correctly identifies spikes in the lookback window.
    """
    dates = pd.date_range(start="2023-01-01", periods=50)
    # volume avg will be 1000 (rolling 20)
    # VOL_MULT is 1.5
    # Spike threshold = 1500
    volume = [1000] * 50
    
    # Case 1: Spike on current day (index -1)
    volume1 = volume.copy()
    volume1[-1] = 2000
    df1 = pd.DataFrame({'high': [102]*50, 'low': [98]*50, 'close': [100]*50, 'volume': volume1}, index=dates)
    bench_df = pd.DataFrame({'close': [100]*50}, index=dates)
    
    res1 = calculate_master_logic(df1, bench_df)
    assert 'vol_spike_last_7d' in res1.columns
    assert res1.iloc[-1]['vol_spike_last_7d'] == True
    
    # Case 2: Spike 5 days ago (index -6)
    volume2 = volume.copy()
    volume2[-6] = 2000
    df2 = pd.DataFrame({'high': [102]*50, 'low': [98]*50, 'close': [100]*50, 'volume': volume2}, index=dates)
    res2 = calculate_master_logic(df2, bench_df)
    assert res2.iloc[-1]['vol_spike_last_7d'] == True
    
    # Case 3: Spike 8 days ago (index -9) - should be FALSE
    volume3 = volume.copy()
    volume3[-9] = 2000
    df3 = pd.DataFrame({'high': [102]*50, 'low': [98]*50, 'close': [100]*50, 'volume': volume3}, index=dates)
    res3 = calculate_master_logic(df3, bench_df)
    assert res3.iloc[-1]['vol_spike_last_7d'] == False

def test_diamond_launch_confluence_update():
    """
    Test that DIAMOND LAUNCH uses vol_spike_last_7d instead of same-day volume spike.
    """
    # Mock row and prev_row for calculate_status
    row = pd.Series({
        'trend': True,
        'close': 110,
        'box_high': 105,
        'volume': 1000, # NOT a spike today (vol_avg=1000)
        'vol_avg': 1000,
        'ema50': 100,
        'ema200': 90,
        'rs_ratio': 1.1,
        'rs_ma': 1.0,
        'ema200_slope': 1.0,
        'sqz_xtra': False,
        'sqz_tight': False,
        'sqz_std': False,
        'vol_spike_last_7d': True # SPIKE OCCURRED RECENTLY
    })
    
    prev_row = pd.Series({
        'sqz_std': True # SQUEEZE FIRED TODAY
    })
    
    # Squeeze fired today + Recent volume spike + Breakout + EMA + RS + Slope up
    status, _ = calculate_status(row, prev_row)
    assert status == "💎 DIAMOND LAUNCH"
