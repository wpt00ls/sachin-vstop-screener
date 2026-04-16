import pytest
import pandas as pd
import numpy as np
from vstop_screener import calculate_master_logic, calculate_status

def test_diamond_launch_requires_positive_slope():
    """
    Test that DIAMOND LAUNCH status is only assigned when EMA 200 slope is positive.
    """
    dates = pd.date_range(start="2023-01-01", periods=300)
    
    # Case 1: EMA 200 Slope is POSITIVE
    # Close prices steadily increasing to ensure positive slope
    close_pos = [100 + i for i in range(300)]
    df_pos = pd.DataFrame({
        'high': [c + 2 for c in close_pos],
        'low': [c - 2 for c in close_pos],
        'close': close_pos,
        'volume': [2000] * 300 # High volume for c4
    }, index=dates)
    
    # Case 2: EMA 200 Slope is NEGATIVE
    # Close prices steadily decreasing to ensure negative slope
    close_neg = [500 - i for i in range(300)]
    df_neg = pd.DataFrame({
        'high': [c + 2 for c in close_neg],
        'low': [c - 2 for c in close_neg],
        'close': close_neg,
        'volume': [2000] * 300 # High volume for c4
    }, index=dates)
    
    bench_df = pd.DataFrame({'close': [100] * 300}, index=dates)
    
    # Process both
    df_pos = calculate_master_logic(df_pos, bench_df)
    df_neg = calculate_master_logic(df_neg, bench_df)
    
    # Mocking conditions for DIAMOND LAUNCH:
    # sqz_label == "FIRED 🚀" (previous sqz_std=True, current sqz_std=False)
    # c3 (close > box_high)
    # c4 (volume > vol_avg * vol_mult)
    # ema_check (close > ema50 and close > ema200)
    # rs_check (rs_ratio > rs_ma)
    
    # We'll manually force the "FIRED 🚀" condition for the test
    # by overriding the squeeze columns for the last two rows.
    for df in [df_pos, df_neg]:
        df.loc[dates[-2], 'sqz_std'] = True
        df.loc[dates[-1], 'sqz_std'] = False
        # Ensure c3: close > box_high
        df.loc[dates[-1], 'box_high'] = df.loc[dates[-1], 'close'] - 1
        # Ensure c4: volume > vol_avg * 1.5
        df.loc[dates[-1], 'volume'] = df.loc[dates[-1], 'vol_avg'] * 2
        # Ensure ema_check: close > ema50 and close > ema200
        df.loc[dates[-1], 'ema50'] = df.loc[dates[-1], 'close'] - 1
        df.loc[dates[-1], 'ema200'] = df.loc[dates[-1], 'close'] - 1
        # Ensure rs_check: rs_ratio > rs_ma
        df.loc[dates[-1], 'rs_ratio'] = 1.1
        df.loc[dates[-1], 'rs_ma'] = 1.0

    # Verify slopes
    assert df_pos.iloc[-1]['ema200_slope'] > 0
    assert df_neg.iloc[-1]['ema200_slope'] < 0
    
    status_pos, _ = calculate_status(df_pos.iloc[-1], df_pos.iloc[-2])
    status_neg, _ = calculate_status(df_neg.iloc[-1], df_neg.iloc[-2])
    
    assert status_pos == "💎 DIAMOND LAUNCH"
    # This is the failing assertion for the RED phase
    assert status_neg != "💎 DIAMOND LAUNCH", "Diamond Launch should NOT be assigned if EMA 200 slope is negative"
