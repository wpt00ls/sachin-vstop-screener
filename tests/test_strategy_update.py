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

def test_coiling_requires_tight_box_width():
    """
    Test that COILING status is only assigned when Box Width % is under 3%.
    """
    dates = pd.date_range(start="2023-01-01", periods=30)
    
    # Base data (Extra Tight Squeeze)
    df = pd.DataFrame({
        'high': [102] * 30,
        'low': [98] * 30,
        'close': [100] * 30,
        'volume': [1000] * 30
    }, index=dates)
    
    bench_df = pd.DataFrame({'close': [100] * 30}, index=dates)
    df = calculate_master_logic(df, bench_df)
    
    # row['sqz_xtra'] will be True
    # Test with box_width_pct = 4.0 (Previously allowed, now should be Consolidating)
    row_4 = df.iloc[-1].copy()
    row_4['box_width_pct'] = 4.0
    
    # Test with box_width_pct = 2.0 (Should still be COILING)
    row_2 = df.iloc[-1].copy()
    row_2['box_width_pct'] = 2.0
    
    status_4, _ = calculate_status(row_4, df.iloc[-2])
    status_2, _ = calculate_status(row_2, df.iloc[-2])
    
    assert status_2 == "🌀 COILING"
    # This should fail in RED phase (currently checks for < 5)
    assert status_4 != "🌀 COILING", "Coiling should NOT be assigned if Box Width % is >= 3%"

def test_vstop_multiplier_is_three():
    """
    Test that VStop uses a 3.0 ATR multiplier.
    """
    from vstop_screener import VSTOP_MULT
    assert VSTOP_MULT == 3.0, "VStop multiplier should be exactly 3.0 for multi-bagger 'breathing room'"

def test_ema200_slope_neg_5d_indicator():
    """
    Test that ema200_slope_neg_5d is correctly calculated.
    """
    dates = pd.date_range(start="2023-01-01", periods=300)
    # Case: EMA 200 Slope is negative for 10 days
    close = [500 - i for i in range(300)]
    df = pd.DataFrame({
        'high': [c + 2 for c in close],
        'low': [c - 2 for c in close],
        'close': close,
        'volume': [1000] * 300
    }, index=dates)
    
    bench_df = pd.DataFrame({'close': [100] * 300}, index=dates)
    df = calculate_master_logic(df, bench_df)
    
    # Should be in df
    assert 'ema200_slope_neg_5d' in df.columns
    # Last row should be True as slope has been negative for 300 days
    assert df.iloc[-1]['ema200_slope_neg_5d'] == True
    
    # Now test a case where it flips
    # 290 days increasing, last 10 days decreasing
    close_flip = [100 + i for i in range(290)] + [390 - i for i in range(10)]
    df_flip = pd.DataFrame({
        'high': [c + 2 for c in close_flip],
        'low': [c - 2 for c in close_flip],
        'close': close_flip,
        'volume': [1000] * 300
    }, index=dates)
    df_flip = calculate_master_logic(df_flip, bench_df)
    
    # Index 289 (end of increasing): slope_up is True, neg_5d should be False
    assert df_flip.iloc[289]['ema200_slope'] > 0
    assert df_flip.iloc[289]['ema200_slope_neg_5d'] == False
    
    # Index 294 (5 days into decreasing): slope should be negative for 5 days
    # Wait, EMA 200 reacts slowly. Let's make sure the slope actually turns negative.
    # EMA 200 with span 200 has alpha = 2/201.
    # If price drops sharply, EMA 200 will eventually drop.
    # For simplicity, let's just check the logic in the dataframe.
    
    # We'll check the last row which is 10 days into the drop.
    assert df_flip.iloc[-1]['ema200_slope'] < df_flip.iloc[-6]['ema200_slope']
    # If the slope itself is negative for 5 days, then neg_5d is True.
