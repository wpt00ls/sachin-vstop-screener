import pytest
from backtester import calculate_metrics

def test_calculate_metrics_success():
    trades = [
        {'pnl_pct': 10.0},
        {'pnl_pct': -5.0},
        {'pnl_pct': 20.0},
        {'pnl_pct': -10.0}
    ]
    
    metrics = calculate_metrics(trades)
    
    assert metrics['total_trades'] == 4
    assert metrics['win_rate'] == 50.0
    assert metrics['total_pnl'] == 15.0 # Simple sum for now, or compounded?
    # Spec says win/loss percentages
    assert metrics['avg_win'] == 15.0
    assert metrics['avg_loss'] == -7.5

def test_calculate_metrics_empty():
    metrics = calculate_metrics([])
    assert metrics['total_trades'] == 0
    assert metrics['win_rate'] == 0.0
    assert metrics['total_pnl'] == 0.0
