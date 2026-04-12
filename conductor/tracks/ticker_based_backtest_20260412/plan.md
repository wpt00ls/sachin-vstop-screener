# Implementation Plan: VStop Historical Backtester

This plan outlines the steps for implementing the historical backtesting and visualization module.

## Phase 1: Logic Consolidation

- [x] Task: Refactor `vstop_screener.py` for modularity (5f9d8be)
    - [x] Write failing test cases to ensure `calculate_master_logic` can be imported and executed independently
    - [x] Implement/Refactor `calculate_master_logic` in `vstop_screener.py` (if needed) for clean import
    - [x] Verify test passes and check coverage
- [x] Task: Set up `backtester.py` scaffolding (8a5c550)
    - [x] Create `backtester.py` with basic `argparse` CLI setup
    - [x] Write failing test cases for CLI argument parsing (ticker, timespan)
    - [x] Implement CLI argument parsing in `backtester.py`
    - [x] Verify test passes and check coverage
- [x] Task: Conductor - User Manual Verification 'Phase 1: Logic Consolidation' (Protocol in workflow.md) [checkpoint: 55695c2]

## Phase 2: Signal Generation & Backtesting Logic

- [x] Task: Implement historical data fetching (83eefec)
    - [x] Write failing test cases for fetching historical data via `yfinance` over a specified timespan
    - [x] Implement data fetching logic in `backtester.py` (handle missing data edge case)
    - [x] Verify test passes and check coverage
- [x] Task: Implement Entry (BUY) logic (05bb859)
    - [x] Write failing test cases for BUY conditions (DIAMOND LAUNCH)
    - [x] Implement chronological iteration and BUY signal generation in `backtester.py`
    - [x] Verify test passes and check coverage
- [x] Task: Implement Exit (SELL) logic (557032c)
    - [x] Write failing test cases for SELL conditions (VStop red or close < 50 EMA)
    - [x] Implement SELL signal generation and trade matching in `backtester.py`
    - [x] Verify test passes and check coverage
- [x] Task: Implement PnL calculation (2f671ff)
    - [x] Write failing test cases for Trade PnL calculations
    - [x] Implement calculation of win/loss percentages and overall performance for executed trades
    - [x] Verify test passes and check coverage
- [x] Task: Conductor - User Manual Verification 'Phase 2: Signal Generation & Backtesting Logic' (Protocol in workflow.md) [checkpoint: c6f1ecc]

## Phase 3: Reporting & CLI

- [x] Task: Implement terminal reporting (65cc574)
    - [x] Write failing test cases for terminal output formatting (trade log and summary metrics)
    - [x] Implement summary calculation (Win Rate, Avg Win/Loss %, Max Drawdown) and terminal printing in `backtester.py`
    - [x] Verify test passes and check coverage (handle "0 trades" edge case)
- [x] Task: Integration and Final Polish (4a9061d)
    - [x] Run full test suite and verify >80% code coverage for `backtester.py` and `vstop_screener.py`
    - [x] Fix any remaining linting or static analysis errors
- [x] Task: Conductor - User Manual Verification 'Phase 3: Reporting & CLI' (Protocol in workflow.md) [checkpoint: 762ace9]

## Phase 4: Visualization (TradingView-style)

- [x] Task: Implement interactive charting (6f74388)
    - [x] Install `lightweight-charts` and update `requirements.txt`
    - [x] Write failing test cases for chart generation (ensuring HTML file creation)
    - [x] Implement multi-pane layout: Price/VStop/EMAs in main pane, Volume and Squeeze in secondary panes
    - [x] Implement Buy/Sell marker overlay logic
    - [x] Verify test passes and check coverage
- [x] Task: Conductor - User Manual Verification 'Phase 4: Visualization (TradingView-style)' (Protocol in workflow.md) [checkpoint: 682910f]