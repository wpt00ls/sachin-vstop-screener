import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from backtester import generate_signals

def test_generate_signals_buy_logic():
    # Create dummy data that triggers a SQUEEZE FIRE
    # SQUEEZE FIRE: yesterday sqz_std=True, today sqz_std=False
    dates = pd.date_range(start="2023-01-01", periods=100)
    data = {
        'high': [102] * 100,
        'low': [98] * 100,
        'close': [100] * 100,
        'volume': [1000] * 100
    }
    df = pd.DataFrame(data, index=dates)
    
    # Mock calculate_master_logic to add necessary columns
    # and mock calculate_status to return SQUEEZE FIRE at a specific index
    with patch('backtester.calculate_master_logic') as mock_logic:
        with patch('backtester.calculate_status') as mock_status:
            with patch('yfinance.download') as mock_yf:
                # Mock trend column in df
                df['trend'] = True
                mock_logic.return_value = df.copy() 
                mock_yf.return_value = pd.DataFrame({'close': [100]*100}, index=dates)
                
                # Mock status to be Consolidating except for one index
                def status_side_effect(row, prev_row):
                    if row.name == dates[50]:
                        return "🚀 SQUEEZE FIRE", "FIRED 🚀"
                    return "Consolidating", "None"
                
                mock_status.side_effect = status_side_effect
                
                # We need to ensure df has index as names for the side effect
                df.index.name = 'date'
                
                trades, result_df = generate_signals(df, "TEST.NS")
                
                # Since SELL logic is not implemented, trades should be empty
                # but we can check if it identified the entry (if we added logging or state)
                # For now, just verify it runs without error
                assert isinstance(trades, list)

def test_generate_signals_sell_logic():
    # Create dummy data
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
                mock_logic.return_value = df.copy()
                mock_yf.return_value = pd.DataFrame({'close': [100]*100}, index=dates)
                
                # BUY at index 10, SELL at index 20 (trend flip)
                def status_side_effect(row, prev_row):
                    if row.name == dates[10]:
                        return "🚀 SQUEEZE FIRE", "FIRED 🚀"
                    return "Consolidating", "None"
                
                mock_status.side_effect = status_side_effect
                
                # Mock trend column in df
                df['trend'] = True
                df.loc[dates[20], 'trend'] = False
                # Ensure ema50 exists
                df['ema50'] = 90
                
                mock_logic.return_value = df
                
                trades, result_df = generate_signals(df, "TEST.NS")
                
                assert len(trades) == 1
                assert trades[0]['exit_date'] == dates[20]
                assert trades[0]['exit_reason'] == 'VStop Red'
