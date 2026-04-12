import pytest
import pandas as pd
from unittest.mock import patch
from backtester import fetch_data

def test_fetch_data_success():
    # Mock yfinance.download
    with patch('yfinance.download') as mock_yf:
        mock_df = pd.DataFrame({'Close': [100, 101]}, index=pd.date_range('2023-01-01', periods=2))
        mock_yf.return_value = mock_df
        
        df = fetch_data('RELIANCE.NS', years=1)
        assert not df.empty
        assert 'close' in df.columns # Check lowercase conversion
        assert mock_yf.called

def test_fetch_data_empty():
    # Mock yfinance.download returning empty df
    with patch('yfinance.download') as mock_yf:
        mock_yf.return_value = pd.DataFrame()
        
        with pytest.raises(ValueError, match="No data found for ticker"):
            fetch_data('INVALID.NS', years=1)
