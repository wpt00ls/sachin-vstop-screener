# Product Guidelines

## Development Philosophy
- **Modular and Extensible**: Ensure technical indicators are implemented as reusable functions or classes to facilitate the addition of new screening criteria.
- **Reliability First**: The script must handle network failures (e.g., during data fetching) gracefully without crashing.
- **Performance Optimized**: Utilize concurrency (e.g., `ThreadPoolExecutor`) where appropriate to ensure the NSE 500 can be processed in a reasonable timeframe.

## User Experience (Output)
- **Visual Clarity**: Use conditional formatting in Excel to highlight key "Yes/No" metrics and high-priority statuses.
- **Actionable Insights**: Prioritize the "Status" column to allow users to quickly filter for high-conviction setups.
- **Traceability**: Provide direct links (e.g., TradingView) for each ticker to bridge the gap between screening and chart analysis.

## Coding Style
- **Pythonic Code**: Adhere to PEP 8 standards for readability.
- **Type Hinting**: Use Python type hints to improve code clarity and tool support.
- **Documentation**: Maintain clear docstrings and comments explaining the mathematical logic behind technical indicators.
- **Configuration Management**: Centralize parameters (e.g., periods, multipliers) to allow for easy tuning of the screener.

## Testing & Quality
- **Unit Testing**: Implement unit tests for core indicator logic to ensure mathematical correctness.
- **Functional Testing**: Verify the integrity of the generated Excel report (e.g., correct column headers, accurate values).