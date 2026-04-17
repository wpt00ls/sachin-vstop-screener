# Implementation Plan: The KeyMaker Pine Script (v6)

## Phase 1: Core Indicator Implementation
- [x] Task: Implement Recursive VStop logic (3.0 ATR multiplier) in Pine Script v6. [ccb350d]
- [x] Task: Implement Squeeze Pro logic (Standard, Tight, Extra Tight) using BB and Keltner Channels. [ccb350d]
- [x] Task: Implement EMA 200 Slope (20-day % change) and EMA 50/200 plots. [ccb350d]
- [x] Task: Implement RS Ratio (vs. Benchmark) and RS vs. Avg indicators. [ccb350d]
- [x] Task: Implement Darvas Box / Box Breakout lookback logic. [ccb350d]
- [x] Task: Implement 7-day Volume Spike lookback condition. [ccb350d]
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Core Indicator Implementation' (Protocol in workflow.md)

## Phase 2: Strategy Logic & MTF Support
- [ ] Task: Implement MTF inputs for D/W/M for all core indicators.
- [ ] Task: Implement Signal Confluence logic (DIAMOND LAUNCH, SQUEEZE FIRE, etc.).
- [ ] Task: Implement Strategy Execution (buy/sell) using Pine Script `strategy.*` functions.
- [ ] Task: Implement Emergency Slope Stop and VStop Red exit logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Strategy Logic & MTF Support' (Protocol in workflow.md)

## Phase 3: Visualization & Dashboard
- [ ] Task: Implement Bar/Background coloring based on market states.
- [ ] Task: Create an on-chart Dashboard (Table) showing status, slope, and RS metrics.
- [ ] Task: Finalize documentation and user inputs for the script.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Visualization & Dashboard' (Protocol in workflow.md)
