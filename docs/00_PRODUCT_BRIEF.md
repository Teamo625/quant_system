# Product Brief

## Project Name

`quant_system`

## Vision

Build a personal quantitative research and signal system for A-shares, Hong Kong stocks, and ETFs.

The long-term system should support:

- local market data acquisition and storage
- technical, capital-flow, valuation, and macro features
- full-market scanning
- strategy research and backtesting
- watchlist and portfolio monitoring
- signal triggering and risk checks
- mobile notifications
- external AI interpretation
- local Web UI

This is a full research platform, not a single data-source script.

## Current Phase Boundary

The current stage is project governance and system blueprint initialization.

No business implementation is allowed in Phase 0.

After Phase 0, Phase 1 may implement only the DataHub foundation. The purpose of DataHub is to provide reliable, local, versioned market data for later modules.

## Explicitly Out of Scope Now

- trading strategies
- AI reports
- push notifications
- automated trading
- complex UI
- feature engineering beyond DataHub output contracts
- backtesting logic
- scanner logic

## Success Criteria for Phase 0

Phase 0 is complete when:

- repository governance rules exist
- system architecture is documented
- module boundaries are explicit
- DataHub output contracts are defined
- task protocol is documented
- testing policy prevents accidental live network access
- project coordination files exist
- placeholder module directories exist
- the first DataHub execution handoff is ready
