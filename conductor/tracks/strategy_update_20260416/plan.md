# Implementation Plan: Strategy Update

## Phase 1: Screener Status Logic Updates
- [x] Task: Update `calculate_status` in `vstop_screener.py` to require `slope_up` (EMA 200) for "💎 DIAMOND LAUNCH" cfa8e3c
- [x] Task: Update `calculate_status` in `vstop_screener.py` to change the Box Width threshold for "🌀 COILING" from 5 to 3. 12fa8f6
- [x] Task: Verify and configure `calculate_master_logic` to use ATR multipliers 1.0, 1.2, and 1.5 specifically for Squeeze logic (buy precursor). 0a6c485
- [x] Task: Verify and configure `vstop_mult` to use a 3.0 ATR multiplier specifically for the VStop logic (sell/stop). f4926b7
- [x] Task: Update `calculate_master_logic` in `vstop_screener.py` to include a rolling 5-day negative EMA 200 slope indicator. c00f603
- [ ] Task: Update tests in `tests/test_vstop_screener.py` to verify the new status logic and different ATR multiples.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Screener Status Logic Updates' (Protocol in workflow.md)

## Phase 2: Backtester Exit Logic Updates
- [ ] Task: Update `generate_signals` in `backtester.py` to remove the EMA 50 exit condition.
- [ ] Task: Update `generate_signals` in `backtester.py` to implement the 5-day negative EMA 200 slope emergency stop condition.
- [ ] Task: Ensure the backtester correctly applies the 3.0 ATR trailing stop via the `row['trend']` (VStop Red) condition for sell signals.
- [ ] Task: Update tests in `tests/test_backtester_signals.py` to cover the new exit conditions.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Backtester Exit Logic Updates' (Protocol in workflow.md)