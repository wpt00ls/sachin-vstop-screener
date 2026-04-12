# Specification: Implement unit tests for core technical indicators

## Goal
The goal of this track is to implement a robust unit testing suite for the core technical indicators used in the stock screener. This ensures the mathematical correctness of the screening logic and provides a safety net for future refactoring.

## Scope
- Technical Indicators to be tested:
  - Relative Strength Index (RSI)
  - Exponential Moving Averages (EMA 50, 200)
  - Squeeze Pro Logic (Bollinger Bands vs. Keltner Channels)
  - Recursive VSTOP (Volatility Stop)
  - Box Breakout and 52-Week metrics
- Mocking data for unit tests using `pytest` and `pandas`.

## Requirements
1. **Mathematical Accuracy**: Tests must verify that calculations for each indicator match expected values for a given set of input data.
2. **Edge Case Handling**: Handle cases with missing data (`NaN`), insufficient data points (e.g., fewer than the lookback period), and extreme volatility.
3. **Reproducibility**: Use fixed, deterministic data sets for tests to ensure they are repeatable.
4. **Code Coverage**: Aim for >80% code coverage for the logic being tested.

## Technical Approach
- Framework: `pytest`
- Tools: `pytest-cov` for coverage reports.
- Data: Create synthetic `pandas.DataFrame` objects with known values to test specific indicator behavior.
- Structure: Create a `tests/` directory with a corresponding test file for `vstop_screener.py`.