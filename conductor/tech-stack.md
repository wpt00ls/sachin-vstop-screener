# Technology Stack

## Core Language
- **Python**: Used for overall script execution, logic calculation, and reporting.

## Data Analysis & Processing
- **Pandas**: Used for data manipulation, cleaning, and preparation of the final audit report.
- **NumPy**: Used for efficient numerical computations of technical indicators.

## Data Fetching
- **yfinance**: Utilized for downloading daily historical price and download data for NSE 500 stocks and the benchmark.

## Reporting & Output
- **XlsxWriter**: Employed as the engine for generating the formatted Excel spreadsheet with conditional formatting.
- **Plotly**: Used for generating interactive HTML charts for the historical backtester.

## Execution Model
- **Concurrent.futures (ThreadPoolExecutor)**: Used to speed up the data fetching and auditing process by running ticker-level scans in parallel.
## Chart Strategy & Scripting
- **Pine Script v6**: Used to implement the "Four Pillars" multi-bagger strategy as a TradingView strategy script (`/scripts/pinescript/`). Enables interactive chart visualization, multi-timeframe analysis, and integrated backtesting within TradingView.
  - *Added: 2026-04-17 — pinescript_implementation_20260416 track*

## Testing Framework
- **Pytest**: Used for unit and integration testing of core indicators and execution logic.
- **Pytest-cov**: Utilized for monitoring and ensuring high code coverage (>80%).
