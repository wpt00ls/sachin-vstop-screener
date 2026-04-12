import subprocess
import sys

def test_backtester_cli_help():
    # Test if backtester.py exists and shows help
    result = subprocess.run([sys.executable, 'backtester.py', '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'usage: backtester.py' in result.stdout

def test_backtester_cli_args():
    # Test if backtester.py accepts ticker and years
    # We use a mock or just check if it fails later in the execution rather than at parsing
    result = subprocess.run([sys.executable, 'backtester.py', 'RELIANCE.NS', '--years', '2'], capture_output=True, text=True)
    # It might fail with error because data fetching is not yet implemented, 
    # but it shouldn't fail with "unrecognized arguments"
    assert 'unrecognized arguments' not in result.stderr

def test_backtester_report_format():
    # Test if the output contains the summary table headers
    result = subprocess.run([sys.executable, 'backtester.py', 'RELIANCE.NS', '--years', '1'], capture_output=True, text=True)
    # Even if 0 trades, it should show the summary block
    assert 'BACKTEST RESULTS' in result.stdout
    assert 'Win Rate' in result.stdout
    assert 'Max Drawdown' in result.stdout
