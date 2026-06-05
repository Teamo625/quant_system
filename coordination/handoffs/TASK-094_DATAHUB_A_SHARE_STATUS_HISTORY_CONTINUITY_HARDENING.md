# TASK-094 DataHub A-share Status-History Continuity Hardening

## Role

5.3 Execution Window.

## Context

TASK-093 is closed after accepted Review Agent verification of the offline DataHub personal trading perfection re-review gate follow-up queue. The gate reports overall `blocked`, phase closure `false`, domain counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and a deterministic 42-item follow-up queue.

The first executable `datahub_hardening` item in that queue is:

- `a_share__a_share_capability_readiness__a_share_listing_delisting_st_status`
- theme: expand dated ST/*ST continuity and broader lifecycle taxonomy for A-share instrument-status-history coverage
- reason: public AKShare bounded coverage proves listing dates, terminal delisting dates, current normal/ST snapshots, and SZ short-name status deltas for caller-provided symbols, but full dated ST/*ST continuity and broader lifecycle taxonomy remain incomplete

`index_weight_history` remains an owner credential blocker and must not be promoted unless the owner reopens paid Tushare scope and a future credentialed live smoke records a real PASS.

This task stays inside Phase 2.5-P DataHub Personal Trading Perfection Re-Review. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden A-share `DatasetName.INSTRUMENT_STATUS_HISTORY` coverage by extending the existing public AKShare-backed adapter and tests toward dated ST/*ST/risk-warning continuity and lifecycle taxonomy breadth where stable no-credential public routes expose source truth.

The task should preserve existing bounded listing, delisting, current status, and SZ short-name status-delta behavior. It must not invent historical continuity from current snapshots or name heuristics alone.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-094_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination state files
- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- unrelated DataHub adapters or tests
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, browser session state, private account data, or paid/private APIs.

Do not implement downstream feature calculation, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Reuse the existing `AkshareAShareInstrumentStatusHistoryAdapter` and `DatasetName.INSTRUMENT_STATUS_HISTORY` schema.
- Keep `SourceRequest.symbols` caller-provided and bounded; reject `symbols=None` or empty symbols clearly.
- Preserve deterministic symbol validation, deduplication, sorting, and schema validation behavior from TASK-074.
- Investigate stable no-credential AKShare routes already available in the dependency for dated ST/*ST/risk-warning, special-treatment, delisting, listing, suspension-related lifecycle, or other source-provided status events.
- Add source-backed normalization only for rows that expose reliable event dates/status truth. Do not synthesize historical dated ST continuity solely from the latest stock name, current board, or inferred prefix.
- If a route provides current-only data, keep it as current-only evidence and document the limitation rather than promoting it to continuity coverage.
- Normalize any new source-backed events into the existing schema fields:
  - `symbol`
  - `market`
  - `effective_start_date`
  - optional `effective_end_date`
  - `status_type`
  - `status`
  - optional `raw_status`
  - optional `status_reason`
  - optional `exchange`
  - optional `board`
  - `source`
  - `ingested_at`
  - `schema_version`
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures under the existing DataHub live-failure classification policy.
- Update only `a_share_listing_delisting_st_status` capability truth if implementation and live evidence justify it. Keep it conservative unless full dated status-history breadth is actually proven.
- If no additional stable public route can improve the capability, make the smallest code/test/report change that records the proven infeasibility explicitly and keeps the readiness truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py`

The live-enabled smoke should validate at least one active normal A-share symbol and one stable public-source special-status/lifecycle sample when such a sample is available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-094_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- source routes investigated and route-level findings
- any capability truth changes
- remaining public-source limitations for dated ST/*ST continuity and lifecycle taxonomy
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- any feasible no-credential source-backed status-history improvement is implemented and tested, or infeasibility is explicitly evidenced in code/tests/report without over-promoting capability truth
- normalized records still validate against `DatasetName.INSTRUMENT_STATUS_HISTORY`
- offline tests cover new source-backed status cases or explicit limitation behavior
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- `a_share_listing_delisting_st_status` remains conservative unless full personal trading breadth is proven
