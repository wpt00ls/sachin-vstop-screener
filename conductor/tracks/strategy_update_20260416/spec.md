# Specification: Strategy Update 20260416

## Overview
Update the core indicator logic and backtester rules to precisely match the "Four Pillars" multi-bagger strategy. This involves refining the status definitions in the screener, verifying indicator parameters, and adjusting the exit logic in the backtester.

## Functional Requirements
1. **Screener Logic Updates (`vstop_screener.py`)**:
   - `calculate_status`: For the "💎 DIAMOND LAUNCH" status, explicitly require `slope_up` (EMA 200 slope is positive) in addition to existing checks.
   - `calculate_status`: For the "🌀 COILING" status, tighten the box width requirement from `< 5%` to `< 3%`.
   - **VStop Parameter Validation**: Explicitly verify/ensure that the `VSTOP_MULT` used in the Recursive VStop calculation is set to `3.0` (times the ATR) to provide the necessary "breathing room".
2. **Backtester Updates (`backtester.py`)**:
   - Update the exit logic in `generate_signals`.
   - Remove the `row['close'] < row['ema50']` exit condition.
   - Maintain the `VStop Red` exit condition (`not row['trend']`), which is driven by the 3.0 ATR VStop.
   - Add a new "Emergency Stop" condition: Sell if the EMA 200 slope turns negative and stays negative for 5 consecutive days.
3. **Indicator Pre-calculation (`vstop_screener.py`)**:
   - Calculate a rolling 5-day negative slope status for easier backtesting signal generation if necessary.

## Acceptance Criteria
- Diamond Launch status is only assigned when the EMA 200 slope is positive.
- Coiling status is only assigned when the Box Width is under 3%.
- VStop is calculated with a 3.0 multiplier.
- Backtester exits trades strictly on VStop turning Red or EMA 200 slope being negative for 5+ days.
- Existing tests are updated or new tests are added to cover these logical changes.