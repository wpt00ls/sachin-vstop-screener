import pytest
import pandas as pd
import numpy as np
from vstop_screener import calculate_master_logic

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
