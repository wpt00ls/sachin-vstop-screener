# Specification: Strategy Update & Signal Export

## Overview
This track introduces a refinement to the volume confluence logic and a new feature to export historical trading signals from the backtester to an Excel file with normalized indicators for easier analysis.

## Functional Requirements
1. **Volume Confluence Refinement**:
   - Update the volume check logic. Instead of requiring a volume spike exactly on the signal day, the condition should pass if a volume spike (Volume > Volume Average * Multiplier) occurred at any point within the **last 7 trading days**.
   - This applies to status calculations in both `vstop_screener.py` and `backtester.py`.

2. **Historical Signal Export (Backtester)**:
   - Enhance the backtester to export the full historical signal/indicator series for a ticker to an Excel file.
   - **File Naming**: `<TICKER>_Signals_<TIMESTAMP>.xlsx`.
   - **New Normalized Columns**:
     - **VStop Distance %**: `((Close - VStop) / Close) * 100` (normalized measure of trend buffer).
     - **Volume Multiple**: `Volume / Volume_Avg` (normalized measure of relative volume).
   - **Standard Data Columns**: Date, Close, Status, Squeeze Status, Trend, EMA 50/200, RSI, RS Ratio, RS MA, EMA 200 Slope.

## Acceptance Criteria
- Screener and Backtester both reflect the updated "last 7 days" volume logic.
- Running a backtest generates an Excel file containing the full indicator history with normalized VStop and Volume metrics.
- The Excel file is correctly formatted.
- Unit tests verify the new volume lookback logic and the normalization calculations.

## Out of Scope
- Real-time data streaming.
- Exporting data for the entire NSE 500 in a single Excel file from the backtester.