# Data Contracts

DataHub must eventually provide stable, documented datasets to downstream modules.

This document defines target contracts, not Phase 0 implementation.

## Contract Principles

- DataHub owns raw acquisition, normalization, validation, and local persistence.
- Downstream modules must consume DataHub outputs instead of fetching their own market data.
- Every dataset should have a schema version.
- Every dataset should include source and update metadata.
- Default tests must validate contracts using local fixtures.

## Common Fields

All tabular DataHub outputs should include or be joinable to:

| Field | Meaning |
| --- | --- |
| `symbol` | normalized instrument code |
| `market` | market identifier, such as `CN`, `HK`, or `ETF_CN` |
| `asset_type` | instrument type, such as stock, ETF, index, or fund |
| `trade_date` | local trading date |
| `source` | upstream data source identifier |
| `source_ts` | upstream timestamp when available |
| `ingested_at` | local ingestion timestamp |
| `schema_version` | DataHub schema version |

## Instrument Master

Purpose:

Provide canonical instrument metadata to all modules.

Target consumers:

- FeatureHub
- Scanner
- BacktestEngine
- PortfolioMonitor
- AIReport
- UI

Expected fields:

| Field | Meaning |
| --- | --- |
| `symbol` | normalized symbol |
| `raw_symbol` | source-native symbol |
| `name` | display name |
| `market` | market identifier |
| `asset_type` | stock, ETF, index, fund |
| `currency` | trading currency |
| `exchange` | exchange code |
| `list_date` | listing date when available |
| `delist_date` | delisting date when available |
| `is_active` | current activity flag |

## Trading Calendar

Purpose:

Provide market trading sessions and holiday awareness.

Target consumers:

- DataHub validators
- FeatureHub
- Scanner
- BacktestEngine
- UI

Expected fields:

| Field | Meaning |
| --- | --- |
| `market` | market identifier |
| `trade_date` | trading date |
| `is_open` | whether market is open |
| `session_type` | full, half-day, holiday, special |
| `previous_trade_date` | previous open date |
| `next_trade_date` | next open date |

## Daily Bars

Purpose:

Provide normalized daily OHLCV data.

Target consumers:

- FeatureHub
- Scanner
- BacktestEngine
- AIReport
- UI

Expected fields:

| Field | Meaning |
| --- | --- |
| `symbol` | normalized symbol |
| `market` | market identifier |
| `trade_date` | trading date |
| `open` | adjusted or raw open, according to adjustment flag |
| `high` | adjusted or raw high |
| `low` | adjusted or raw low |
| `close` | adjusted or raw close |
| `volume` | traded volume |
| `amount` | traded amount |
| `adj_factor` | adjustment factor when available |
| `price_adjustment` | raw, qfq, hfq, or source-specific |

## Corporate Actions

Purpose:

Support price adjustment, historical interpretation, and backtest correctness.

Target consumers:

- DataHub
- FeatureHub
- BacktestEngine
- AIReport

Expected fields:

| Field | Meaning |
| --- | --- |
| `symbol` | normalized symbol |
| `market` | market identifier |
| `event_date` | effective date |
| `event_type` | dividend, split, rights issue, name change, suspension |
| `value` | event-specific value |
| `raw_payload_ref` | pointer to raw source payload when stored |

## Valuation Snapshot

Purpose:

Provide basic valuation data for features, scanner filters, and explanations.

Target consumers:

- FeatureHub
- Scanner
- AIReport
- UI

Expected fields:

| Field | Meaning |
| --- | --- |
| `symbol` | normalized symbol |
| `market` | market identifier |
| `trade_date` | trading date |
| `pe_ttm` | trailing PE |
| `pb` | price-to-book |
| `ps_ttm` | trailing PS |
| `dividend_yield` | dividend yield |
| `market_cap` | market capitalization |
| `float_market_cap` | float market capitalization |

## Capital Flow Snapshot

Purpose:

Provide money-flow and participation data when sources are available.

Target consumers:

- FeatureHub
- Scanner
- AIReport

Expected fields:

| Field | Meaning |
| --- | --- |
| `symbol` | normalized symbol |
| `market` | market identifier |
| `trade_date` | trading date |
| `net_inflow` | net capital inflow |
| `main_net_inflow` | main-force inflow when available |
| `northbound_net_buy` | northbound net buy when applicable |
| `turnover_rate` | turnover rate |

## Data Quality Report

Purpose:

Expose DataHub confidence and known gaps to downstream modules.

Target consumers:

- FeatureHub
- Scanner
- BacktestEngine
- AIReport
- UI

Expected fields:

| Field | Meaning |
| --- | --- |
| `dataset` | dataset name |
| `market` | market identifier |
| `trade_date` | relevant date |
| `check_name` | validation check |
| `status` | pass, warn, fail |
| `severity` | low, medium, high |
| `details` | structured detail or message |
| `created_at` | validation timestamp |

## Downstream Contract Summary

| Consumer | DataHub Inputs Needed |
| --- | --- |
| FeatureHub | instrument master, calendar, daily bars, corporate actions, valuation, capital flow |
| Scanner | instrument master, calendar, daily bars, valuation, capital flow, quality reports |
| BacktestEngine | instrument master, calendar, daily bars, corporate actions, quality reports |
| AIReport | instrument master, daily bars, valuation, capital flow, quality reports |
| UI | status, metadata, datasets, quality reports |
