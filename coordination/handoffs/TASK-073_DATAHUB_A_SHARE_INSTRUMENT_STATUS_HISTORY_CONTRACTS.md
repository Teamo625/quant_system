# TASK-073 DataHub A-share Instrument Status History Contracts

## Role

5.3 Execution Window.

## Context

TASK-071 found `a_share_listing_delisting_st_status` remains `partial` because ST history and lifecycle deltas are not standardized in DataHub contracts. TASK-072 closed the A-share daily-bars batch-access gap and promoted `a_share_daily_bars` to `covered`.

Before implementing a source adapter for listing/delisting/ST history, DataHub needs a stable event-style contract that downstream FeatureHub, Scanner, and later StrategyLab/BacktestEngine can consume without overloading static `INSTRUMENT_MASTER` snapshots.

The owner asked to stop after TASK-072 closure. Because pipeline closure includes dispatching the next handoff, this task is dispatched but must not be executed until the owner resumes the pipeline.

## Objective

Add a dedicated DataHub dataset contract for instrument status/lifecycle history events, focused on A-share listing, delisting, ST/*ST status, normal status, and other exchange/public-source status deltas.

This is a contract-only task. Do not implement a live source adapter in this handoff.

## Allowed Writes

Only:

- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-073_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `quant/datahub/adapters/`
- `tests/datahub/*live.py`
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not add live network calls, use credentials, or implement source fetching.

## Contract Requirements

Add a new canonical dataset contract with a clear name such as `INSTRUMENT_STATUS_HISTORY`.

The schema should support event/source-fact records with fields sufficient for:

- canonical symbol
- market/region
- event date or effective start date
- optional effective end date
- status type, for example listing, delisting, ST, *ST, normal, paused, or other source-provided lifecycle status
- status value or normalized status
- optional raw status/source label
- optional status reason
- source
- ingested timestamp
- schema version

Keep the contract generic enough for future HK or ETF/fund reuse if appropriate, but this task's capability update should target only the A-share status-history gap.

Update source catalog/capability metadata narrowly:

- Include the new dataset in relevant public/credentialed source family coverage where source families plausibly cover A-share status/lifecycle data.
- Update `a_share_listing_delisting_st_status` to map to the new dataset.
- Keep `a_share_listing_delisting_st_status` no higher than `partial` because this task is contract-only.
- Do not change unrelated capability statuses.

## Tests

Run only offline tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

No live-enabled smoke is required or allowed because this is contract-only.

## Completion Report

Write `coordination/reports/TASK-073_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result
- capability truth changes
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- the new dataset exists in the registry and schema map
- schema and semantic validation tests cover valid and invalid status-history examples
- source catalog and capability metadata reference the new contract consistently
- default tests pass offline
- the report clearly recommends the next adapter/source hardening task
