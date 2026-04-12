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

## Execution Model
- **Concurrent.futures (ThreadPoolExecutor)**: Used to speed up the data fetching and auditing process by running ticker-level scans in parallel.