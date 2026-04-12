import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from backtester import create_chart

def test_create_chart_execution():
    # Create dummy data
    dates = pd.date_range(start="2023-01-01", periods=100)
    df = pd.DataFrame({
        'open': [100]*100,
        'high': [102]*100,
        'low': [98]*100,
        'close': [101]*100,
        'volume': [1000]*100,
        'vstop': [95]*100,
        'trend': [True]*100,
        'ema50': [90]*100,
        'ema200': [80]*100,
        'sqz_std': [False]*100,
        'sqz_tight': [False]*100,
        'sqz_xtra': [False]*100
    }, index=dates)
    
    trades = [{
        'entry_date': dates[10],
        'entry_price': 100.0,
        'exit_date': dates[20],
        'exit_price': 110.0,
        'pnl_pct': 10.0,
        'exit_reason': 'VStop Red'
    }]
    
    with patch('backtester.Chart') as mock_chart_class:
        mock_chart_instance = MagicMock()
        mock_chart_class.return_value = mock_chart_instance
        
        # We also need to mock create_subchart to return a mock
        mock_subchart = MagicMock()
        mock_chart_instance.create_subchart.return_value = mock_subchart
        
        res = create_chart(df, trades, "TEST.NS")
        
        assert res is True
        assert mock_chart_instance.show.called
        assert mock_chart_instance.set.called
        assert mock_chart_instance.create_line.called
