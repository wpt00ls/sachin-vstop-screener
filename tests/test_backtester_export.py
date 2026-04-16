import pytest
import pandas as pd
from unittest.mock import patch
from backtester import generate_signals

def test_generate_signals_history_capture():
    """
    Test that generate_signals captures status and squeeze_status in the returned dataframe.
    """
    dates = pd.date_range(start="2023-01-01", periods=50)
    data = {
        'high': [102] * 50,
        'low': [98] * 50,
        'close': [100] * 50,
        'volume': [1000] * 50
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = 'date'
    
    with patch('backtester.calculate_master_logic') as mock_logic:
        with patch('backtester.calculate_status') as mock_status:
            with patch('yfinance.download') as mock_yf:
                mock_logic.return_value = df.copy()
                mock_yf.return_value = pd.DataFrame({'close': [100]*50}, index=dates)
                
                # Mock status to be something recognizable
                mock_status.return_value = ("TEST_STATUS", "TEST_SQZ")
                
                trades, result_df = generate_signals(df, "TEST.NS")
                
                # Check if history columns exist
                assert 'status' in result_df.columns
                assert 'squeeze_status' in result_df.columns
                assert result_df['status'].iloc[-1] == "TEST_STATUS"
                assert result_df['squeeze_status'].iloc[-1] == "TEST_SQZ"

def test_export_to_excel_functionality():
    """
    Test that backtester has an export_to_excel function and it creates a file with correct columns and sorting.
    """
    import backtester
    import os
    import pandas as pd
    
    # Create dummy data
    dates = pd.date_range(start="2023-01-01", periods=10)
    df = pd.DataFrame({
        'close': [100.123] * 10,
        'status': ['Consolidating'] * 10,
        'squeeze_status': ['None'] * 10,
        'vstop': [90.456] * 10,
        'trend': [True] * 10,
        'vstop_dist_pct': [10.678] * 10,
        'volume': [1000] * 10,
        'vol_avg': [1000] * 10,
        'vol_multiple': [1.0] * 10,
        'vol_spike_last_7d': [False] * 10
    }, index=dates)
    
    fname = backtester.export_to_excel(df, "TEST_EXPORT.NS")
    
    assert os.path.exists(fname)
    assert "results" in fname
    
    # Read back and verify columns and sorting
    df_read = pd.read_excel(fname, sheet_name='Signal History')
    assert 'Date' in df_read.columns
    assert 'Close' in df_read.columns
    
    # Check rounding
    assert df_read['Close'].iloc[0] == 100.12
    assert df_read['VStop Distance %'].iloc[0] == 10.68
    
    # Check descending sort (index 0 should be latest date)
    assert str(df_read['Date'].iloc[0]) == "2023-01-10"
    
    # Cleanup
    os.remove(fname)
