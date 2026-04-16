# Implementation Plan: Strategy Update & Signal Export

## Phase 1: Core Strategy & Indicator Refinement [checkpoint: a9af5ba]
- [x] Task: Update `calculate_master_logic` in `vstop_screener.py` to calculate `vol_spike_last_7d` (lookback volume condition). 32efb77
- [x] Task: Update `calculate_master_logic` in `vstop_screener.py` to include `vstop_dist_pct` and `vol_multiple` indicators. 32efb77
- [x] Task: Update `calculate_status` in `vstop_screener.py` to use `vol_spike_last_7d` for "💎 DIAMOND LAUNCH" confluence. 32efb77
- [x] Task: Write tests in `tests/test_strategy_update.py` to verify the 7-day volume lookback and normalized metrics. 32efb77
- [x] Task: Conductor - User Manual Verification 'Phase 1: Core Strategy & Indicator Refinement' (Protocol in workflow.md) a9af5ba

## Phase 2: Backtester Excel Export Feature [checkpoint: a32489b]
- [x] Task: Enhance `backtester.py` to capture full indicator history for each row during the signal generation loop. 945af15
- [x] Task: Implement `export_to_excel` functionality in `backtester.py` using `xlsxwriter`. 0651d98
- [x] Task: Update `backtester.py` CLI to include an `--export` flag (or enable it by default). 0651d98
- [x] Task: Update `tests/test_backtester_signals.py` to verify that the export functionality works and contains the correct columns. 0651d98
- [x] Task: Conductor - User Manual Verification 'Phase 2: Backtester Excel Export Feature' (Protocol in workflow.md) a32489b

## Phase 3: Final Integration & Regression
- [ ] Task: Run full regression tests on `vstop_screener.py` and `backtester.py`.
- [ ] Task: Verify the Excel output format and data accuracy for a sample ticker (e.g., RELIANCE.NS).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Integration & Regression' (Protocol in workflow.md)
