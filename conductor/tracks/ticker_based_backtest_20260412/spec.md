# Specification: VStop Historical Backtester

**Overview**: 
Create a historical backtesting and visualization module that allows the user to input a specific ticker symbol and run the `calculate_master_logic` from `vstop_screener.py` across historical data. The tool will simulate hypothetical Buy/Sell signals based on the exact same indicator states and compute the performance of those decisions over time.

**Objectives**:
- Decouple `calculate_master_logic` from `vstop_screener.py` into a shared utilities module, or import it safely, ensuring 100% logic parity.
- Accept a user-provided ticker (e.g., `RELIANCE.NS`) and a historical timespan (defaulting to 5 years).
- Define explicit Entry (Buy) and Exit (Sell) signals derived from the screener’s existing metrics.
- Output a trade log containing entry dates, exit dates, win/loss percentages, and total overall performance to the terminal.
- **Interactive Visualization**: Generate a TradingView-style interactive HTML chart (using `lightweight-charts`) that displays the price action, indicators (VStop, EMAs, Squeeze), and clear Buy/Sell markers for every backtested trade.

**Technical Constraints**:
- **Languages/Frameworks**: Python 3.8+, `pandas`, `numpy`, `yfinance`, `lightweight-charts`.
- **Tools**: Command Line interface (`argparse`).
- **File Paths**:
  - `backtester.py` (New script to execute the isolated test).
  - Modify `vstop_screener.py` only if necessary to extract modular logic without breaking existing Excel audit.

**Workflow Steps (Tracks)**:

> **Track 1:** Logic Consolidation
> **Input:** `vstop_screener.py`
> **Logic:** Refactor `calculate_master_logic` if needed so it can be imported cleanly without running the full Nifty500 loop.
> **Output:** Modular, importable indicator generation function.

> **Track 2:** Signal Generation
> **Input:** Clean historical DataFrame with all indicators attached.
> **Logic:** 
> 1. Iterate chronologically over the DataFrame.
> 2. **BUY Condition (Aggressive Breakout)**: Execute entry when status hits `💎 DIAMOND LAUNCH` or `🚀 SQUEEZE FIRE`.
> 3. **SELL Condition (Trend Failure)**: Execute exit when the VStop turns red (`trend == False`) or the close drops below the 50 EMA.
> 4. Record Trade PnL.
> **Output:** A list/DataFrame of executed hypothetical trades.

> **Track 3:** Reporting
> **Input:** Trade List
> **Logic:** Print out total number of trades, Win Rate, Average Win %, Average Loss %, and Maximum Drawdown to a clean terminal table format.
> **Output:** Terminal readout outputting the simulation.

> **Track 4:** Visualization
> **Input:** Clean historical DataFrame + Trade List
> **Logic:** 
> 1. Use `lightweight-charts` to create a multi-pane chart.
> 2. **Main Pane**: Plot Candlestick price action, VStop line (color-coded for trend), EMA 50, and EMA 200.
> 3. **Secondary Pane(s)**: Plot Volume bars and Squeeze indicators (visualizing Standard, Tight, and Extra Tight states).
> 4. Overlay Buy (Green Up Arrow) and Sell (Red Down Arrow) markers at trade execution points on the main pane.
> 5. Export the result to a standalone HTML file for browser viewing.

**Edge Case Mapping**:
- **Missing Data**: If `yfinance` returns empty data for a ticker over the specified time range, exit gracefully with a warning.
- **No Trades Fired**: If the conditions were never met over the last 5 years, still print the success message with `0 trades recorded`.

**Success Criteria**:
- [ ] Running `python backtester.py TICKER.NS` produces a report of historical trades based on the agreed-upon triggers.
- [ ] Indicators match *exactly* with the values seen in the daily `vstop_screener.py` excel output.
- [ ] No regression or slowdown of the existing daily `NSE500_Audit` functionality.