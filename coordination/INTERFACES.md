# Interfaces

This file records stable cross-module interfaces.

Only the 5.5 controller may update this file.

## Current Stable Interfaces

### DataHub Dataset Contracts

DataHub exposes versioned dataset contracts through `quant.datahub.datasets.DatasetName`, `DatasetRegistry`, and `DatasetSchema`.

Schema version impact:

- all current contracts are `v1`
- TASK-007 added new `v1` contracts for expanded Phase 2 domains
- TASK-028 kept `valuation_snapshot` at `v1` but changed `float_market_cap` to optional because the bounded no-credential one-symbol valuation source could not reliably provide it without depending on a supplemental route; the field remains part of the schema and should be emitted when truthfully available
- no migration is required yet because no downstream implementation phase is open

Affected future consumers:

- FeatureHub
- Scanner
- StrategyLab
- BacktestEngine
- PortfolioMonitor
- SignalEngine
- RiskEngine
- Notification
- AIReport
- Local Web UI

Current stable dataset contracts:

- `instrument_master`
- `trading_calendar`
- `daily_bars`
- `corporate_actions`
- `valuation_snapshot`
- `capital_flow_snapshot`
- `data_quality_report`
- `index_daily_bars`
- `index_constituents`
- `fund_profile`
- `fund_nav_snapshot`
- `fund_holdings`
- `sector_master`
- `sector_membership`
- `sector_daily_bars`
- `macro_indicator_master`
- `macro_observations`
- `policy_documents`
- `news_events`
- `company_announcements`
- `global_equity_snapshot`

Reason for latest change:

- TASK-028 completed A-share valuation adapter live-network rework and recorded source-truth optionality for `valuation_snapshot.float_market_cap`.

Migration notes:

- downstream modules are still placeholders, so no consumer migration is required
- source adapter tasks must emit records compatible with these contracts
- future DataHub work may revisit `float_market_cap` requiredness if a stable, bounded, no-credential source reliably provides it across target symbols and environments
- future schema changes must record version impact here and in controller state

## Interface Change Rule

Any change to a stable cross-module contract must include:

- reason for change
- affected consumers
- migration notes
- schema version impact
