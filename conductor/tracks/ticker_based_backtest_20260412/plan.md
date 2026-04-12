# Implementation Plan: VStop Historical Backtester

This plan outlines the steps for implementing the historical backtesting and visualization module.

## Phase 1: Logic Consolidation

- [ ] Task: Refactor `vstop_screener.py` for modularity
    - [ ] Write failing test cases to ensure `calculate_master_logic` can be imported and executed independently
    - [ ] Implement/Refactor `calculate_master_logic` in `vstop_screener.py` (if needed) for clean import
    - [ ] Verify test passes and check coverage
- [ ] Task: Set up `backtester.py` scaffolding
    - [ ] Create `backtester.py` with basic `argparse` CLI setup
    - [ ] Write failing test cases for CLI argument parsing (ticker, timespan)
    - [ ] Implement CLI argument parsing in `backtester.py`
    - [ ] Verify test passes and check coverage
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Logic Consolidation' (Protocol in workflow.md)

## Phase 2: Signal Generation & Backtesting Logic

- [ ] Task: Implement historical data fetching
    - [ ] Write failing test cases for fetching historical data via `yfinance` over a specified timespan
    - [ ] Implement data fetching logic in `backtester.py` (handle missing data edge case)
    - [ ] Verify test passes and check coverage
- [ ] Task: Implement Entry (BUY) logic
    - [ ] Write failing test cases for BUY conditions (DIAMOND LAUNCH or SQUEEZE FIRE)
    - [ ] Implement chronological iteration and BUY signal generation in `backtester.py`
    - [ ] Verify test passes and check coverage
- [ ] Task: Implement Exit (SELL) logic
    - [ ] Write failing test cases for SELL conditions (VStop red or close < 50 EMA)
    - [ ] Implement SELL signal generation and trade matching in `backtester.py`
    - [ ] Verify test passes and check coverage
- [ ] Task: Implement PnL calculation
    - [ ] Write failing test cases for Trade PnL calculations
    - [ ] Implement calculation of win/loss percentages and overall performance for executed trades
    - [ ] Verify test passes and check coverage
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Signal Generation & Backtesting Logic' (Protocol in workflow.md)

## Phase 3: Reporting & CLI

- [ ] Task: Implement terminal reporting
    - [ ] Write failing test cases for terminal output formatting (trade log and summary metrics)
    - [ ] Implement summary calculation (Win Rate, Avg Win/Loss %, Max Drawdown) and terminal printing in `backtester.py`
    - [ ] Verify test passes and check coverage (handle "0 trades" edge case)
- [ ] Task: Integration and Final Polish
    - [ ] Run full test suite and verify >80% code coverage for `backtester.py` and `vstop_screener.py`
    - [ ] Fix any remaining linting or static analysis errors
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Reporting & CLI' (Protocol in workflow.md)

## Phase 4: Visualization (TradingView-style)

- [ ] Task: Implement interactive charting
    - [ ] Install `lightweight-charts` and update `requirements.txt`
    - [ ] Write failing test cases for chart generation (ensuring HTML file creation)
    - [ ] Implement price and indicator plotting using `lightweight-charts`
    - [ ] Implement Buy/Sell marker overlay logic
    - [ ] Verify test passes and check coverage
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Visualization (TradingView-style)' (Protocol in workflow.md)