import pytest
import pandas as pd
from backtester import print_report

def test_print_report_with_trades(capsys):
    ticker = "TEST.NS"
    trades = [{
        'entry_date': pd.Timestamp('2023-01-01'),
        'exit_date': pd.Timestamp('2023-01-10'),
        'entry_price': 100.0,
        'exit_price': 110.0,
        'pnl_pct': 10.0,
        'exit_reason': 'Target Hit'
    }]
    metrics = {
        'total_trades': 1,
        'win_rate': 100.0,
        'total_pnl': 10.0,
        'avg_win': 10.0,
        'avg_loss': 0.0,
        'max_drawdown': 0.0
    }
    
    print_report(ticker, trades, metrics)
    captured = capsys.readouterr()
    
    assert "BACKTEST RESULTS: TEST.NS" in captured.out
    assert "2023-01-01" in captured.out
    assert "10.00%" in captured.out

def test_print_report_no_trades(capsys):
    metrics = {
        'total_trades': 0,
        'win_rate': 0.0,
        'total_pnl': 0.0,
        'avg_win': 0.0,
        'avg_loss': 0.0,
        'max_drawdown': 0.0
    }
    print_report("EMPTY.NS", [], metrics)
    captured = capsys.readouterr()
    assert "No trades executed" in captured.out
