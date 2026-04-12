import pytest
import pandas as pd
from vstop_screener import calculate_master_logic

def test_calculate_master_logic_custom_params():
    # Create a 30-day dummy dataset
    dates = pd.date_range(start="2023-01-01", periods=30)
    data = {
        'high': [100] * 30,
        'low': [90] * 30,
        'close': [100 + i for i in range(30)],
        'volume': [1000] * 30
    }
    df = pd.DataFrame(data, index=dates)
    
    # Dummy benchmark data
    bench_data = {'close': [100] * 30}
    bench_df = pd.DataFrame(bench_data, index=dates)
    
    # This should fail if calculate_master_logic doesn't accept these arguments
    try:
        result_df = calculate_master_logic(
            df.copy(), 
            bench_df, 
            vstop_mult=2.0, 
            atr_period=10, 
            ema_periods=[20, 50], 
            box_lookback=3, 
            rsi_period=7
        )
        # If it passes, check if they were actually used (e.g. ema20 should exist)
        assert 'ema20' in result_df.columns
        assert 'ema50' in result_df.columns
        assert 'ema200' not in result_df.columns # Since we passed [20, 50]
    except TypeError as e:
        pytest.fail(f"calculate_master_logic does not accept custom parameters: {e}")

if __name__ == "__main__":
    test_calculate_master_logic_custom_params()
