# Initial Concept
A Python-based technical stock screener for the NSE 500 index that calculates advanced momentum, volatility, and trend indicators to identify high-probability trading setups.

# Product Guide

## Vision
To provide a robust, automated tool for quantitative traders and investors to rapidly scan the Indian equity market (NSE 500) and identify structurally strong stocks exhibiting specific technical patterns such as volatility squeezes, trend alignments, and box breakouts.

## Target Audience
- Quantitative Traders
- Technical Analysts
- Swing Traders and Active Investors in the Indian stock market

## Core Features
1. **Automated Data Fetching**: Retrieves daily historical price and volume data for Nifty 500 constituents and the benchmark (Nifty 50) using `yfinance`.
2. **Advanced Technical Indicators**: Computes a proprietary suite of indicators including:
   - Recursive Volatility Stop (VSTOP)
   - Relative Strength Index (RSI)
   - Exponential Moving Averages (EMA 50, 200)
   - Squeeze Pro Logic (Bollinger Bands within Keltner Channels)
   - Relative Strength compared to a benchmark
   - Box Breakout metrics and 52-week High/Lows
3. **Confluence Logic & Ranking**: Evaluates stocks against multiple conditions (trend, higher lows, volume, moving average alignment) to categorize them into actionable statuses like "DIAMOND LAUNCH", "SQUEEZE FIRE", "COILING", or "TRENDING".
4. **Excel Reporting**: Exports the audited results into a formatted Excel spreadsheet with conditional formatting for easy visual scanning of the daily setups.

## Success Metrics
- Fast, reliable execution over the entire NSE 500 universe within a single run.
- Accurate calculation of technical indicators matching standard charting platforms.
- Clean, readable, and actionable Excel output generated daily.- **Tested Reliability**: Maintenance of high code coverage (>80%) for all core indicator logic.
