import pytest
import pandas as pd
from unittest.mock import patch
from backtester import generate_signals

def test_backtester_new_exit_logic():
    """
    Test that backtester uses new exit logic:
    1. Removes EMA 50 exit.
    2. Adds 5-day negative EMA 200 slope emergency stop.
    3. Keeps VStop Red exit.
    """
    dates = pd.date_range(start="2023-01-01", periods=100)
    data = {
        'high': [102] * 100,
        'low': [98] * 100,
        'close': [100] * 100,
        'volume': [1000] * 100
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = 'date'
    
    with patch('backtester.calculate_master_logic') as mock_logic:
        with patch('backtester.calculate_status') as mock_status:
            with patch('yfinance.download') as mock_yf:
                # Mock components
                mock_yf.return_value = pd.DataFrame({'close': [100]*100}, index=dates)
                
                # Signal at index 10
                def status_side_effect(row, prev_row):
                    if row.name == dates[10]:
                        return "💎 DIAMOND LAUNCH", "None"
                    return "Consolidating", "None"
                mock_status.side_effect = status_side_effect
                
                # Case 1: EMA 50 should NOT trigger exit anymore
                df1 = df.copy()
                df1['trend'] = True
                df1['ema50'] = 110 # Close (100) is below EMA 50 (110)
                df1['ema200_slope_neg_5d'] = False
                mock_logic.return_value = df1
                
                trades1, _ = generate_signals(df1, "TEST1.NS")
                # Currently, it WILL exit because the code hasn't been updated.
                # In RED phase, this assertion should FAIL if we want it NOT to exit.
                assert len(trades1) == 0, "Should NOT exit on EMA 50 anymore"

                # Case 2: VStop Red SHOULD still trigger exit
                df2 = df.copy()
                df2['trend'] = True
                df2.loc[dates[20], 'trend'] = False
                df2['ema50'] = 90
                df2['ema200_slope_neg_5d'] = False
                mock_logic.return_value = df2
                
                trades2, _ = generate_signals(df2, "TEST2.NS")
                assert len(trades2) == 1
                assert trades2[0]['exit_reason'] == "VStop Red"

                # Case 3: 5-day negative slope SHOULD trigger exit
                df3 = df.copy()
                df3['trend'] = True
                df3['ema50'] = 90
                df3['ema200_slope_neg_5d'] = False
                df3.loc[dates[30], 'ema200_slope_neg_5d'] = True
                mock_logic.return_value = df3
                
                trades3, _ = generate_signals(df3, "TEST3.NS")
                # Currently, it WON'T exit because the code hasn't been updated.
                # In RED phase, this assertion should FAIL.
                assert len(trades3) == 1
                assert trades3[0]['exit_reason'] == "Emergency Slope Stop"
