# Specification: Pine Script Strategy Implementation (v6)

## Overview
Implement the "Four Pillars" multi-bagger trading strategy in TradingView using Pine Script version 6. The script will be named "**The KeyMaker**" and saved at `scripts/pinescript/the_keymaker.pinescript`.

## Functional Requirements
1. **Core Indicators**:
   - **Recursive VStop**: Implemented with a 3.0 ATR multiplier for trend detection and trailing stops.
   - **Squeeze Pro**: Detection of Standard, Tight, and Extra Tight squeezes using Bollinger Bands and Keltner Channels.
   - **EMA 200 Slope**: Calculation of 20-day % change in the 200 EMA.
   - **Relative Strength (RS)**:
     - **RS Ratio**: Stock price vs. Benchmark (e.g., Nifty 50) relative to its 50-day MA.
     - **RS vs. Avg**: Relative strength compared to the stock's own average performance.
   - **Darvas Box / Box Breakout**: High/Low lookback for consolidation zones.
   - **Volume Confluence**: Detection of volume spikes within a 7-day lookback window.

2. **Multi-Timeframe (MTF) Support**:
   - Provide input parameters to allow calculations/visualizations based on Daily, Weekly, and Monthly data.
   - Specific indicator settings (like ATR periods or multipliers) should be configurable per timeframe if required.

3. **Signals & Execution**:
   - **Buy Signals**: Trigger "DIAMOND LAUNCH" and "SQUEEZE FIRE" entries based on confluence logic (Squeeze fired + Volume + RS + Trend).
   - **Sell Signals**: Trigger exits on "VStop Red" or "Emergency Slope Stop" (5-day negative slope).

4. **Visualization**:
   - **Indicator Plots**: Plot VStop line and EMAs (50, 200).
   - **Coloring**: Bar colors or background highlights for different market states (Coiling, Trending, Squeeze).
   - **Status Table**: A dashboard on the chart showing current status, slope, and RS metrics.

## Acceptance Criteria
- The Pine Script v6 compiles without errors in TradingView.
- Visual plots match the Python screener's logic for VStop and Squeeze.
- Backtest entries/exits trigger correctly according to the "Four Pillars" logic.
- MTF inputs correctly adjust indicator calculations.

## Out of Scope
- Integration with external brokers for live trading.
