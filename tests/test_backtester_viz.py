import pytest
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from backtester import create_chart

def test_create_chart_execution():
    # Create dummy data
    dates = pd.date_range(start="2023-01-01", periods=300)
    df = pd.DataFrame({
        'open': [100.0]*300,
        'high': [102.0]*300,
        'low': [98.0]*300,
        'close': [101.0]*300,
        'volume': [1000.0]*300,
        'vstop': [95.0]*300,
        'trend': [True]*300,
        'ema50': [90.0]*300,
        'ema200': [80.0]*300,
        'rsi': [50.0]*300,
        'sqz_std': [False]*300,
        'sqz_tight': [False]*300,
        'sqz_xtra': [False]*300
    }, index=dates)
    
    trades = [{
        'ticker': 'TEST.NS',
        'entry_date': dates[100],
        'entry_price': 100.0,
        'exit_date': dates[120],
        'exit_price': 110.0,
        'pnl_pct': 10.0,
        'exit_reason': 'VStop Red'
    }]
    
    with patch('plotly.graph_objects.Figure.write_html') as mock_write:
        res = create_chart(df, trades, "TEST.NS")
        assert res is True
        assert mock_write.called
        # Check if the path passed to write_html starts with results/
        args, kwargs = mock_write.call_args
        assert args[0].startswith('results/backtest_TEST_')
