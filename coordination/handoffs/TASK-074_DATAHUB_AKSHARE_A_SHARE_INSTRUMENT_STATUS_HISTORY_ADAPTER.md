# TASK-074 DataHub AKShare A-share Instrument Status History Adapter

## Role

5.3 Execution Window.

## Context

TASK-073 added the canonical `DatasetName.INSTRUMENT_STATUS_HISTORY` contract and mapped `a_share_listing_delisting_st_status` to it. Review accepted the contract-only work and required the next handoff to implement bounded A-share adapter coverage with gated live smoke evidence before the capability can move above `partial`.

This task stays inside Phase 2.5 DataHub Trading-Usable Hardening. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Implement bounded public AKShare-backed A-share `INSTRUMENT_STATUS_HISTORY` adapter coverage for listing, delisting, ST/*ST/risk-warning, normal, and source-provided lifecycle/status deltas where reliable no-credential public routes exist.

The adapter must normalize records to `DatasetName.INSTRUMENT_STATUS_HISTORY`, keep default tests offline-safe, and include a gated live smoke that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-074_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
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

Do not use credentials or private account data.

Do not implement downstream feature calculation, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Add or extend an AKShare adapter class for `DatasetName.INSTRUMENT_STATUS_HISTORY`.
- Accept caller-provided A-share symbols through `SourceRequest.symbols`; reject `symbols=None` or an empty symbol list clearly.
- Validate and normalize A-share symbols consistently with existing A-share AKShare adapter behavior.
- Discover and use no-credential public AKShare routes that can provide status/lifecycle evidence. Prefer source truth over synthetic inference.
- Normalize available source rows into the TASK-073 schema:
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
- Represent ST/*ST/risk-warning and normal-status evidence conservatively. Do not invent historical continuity when the public route only proves current status or a bounded date slice.
- Support delisted/listing lifecycle evidence when a public route exposes it; otherwise document the source limitation in the report and capability gap text.
- Deduplicate deterministically by at least `(symbol, effective_start_date, status_type, status, source)`.
- Sort normalized output deterministically by symbol, effective date, status type, and status.
- Validate normalized records with `DatasetRegistry.validate_record(DatasetName.INSTRUMENT_STATUS_HISTORY, ...)`.
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures, following the existing DataHub live-failure classification policy.
- Update only `a_share_listing_delisting_st_status` capability truth if implementation and live evidence justify it. Keep it `partial` unless the adapter demonstrably covers the full required breadth; otherwise refine the gap text conservatively.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py`

The live-enabled smoke should validate at least one active normal A-share symbol and, if a stable public-source sample is available, one ST/risk-warning or lifecycle-status symbol. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-074_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- capability truth changes
- source route coverage and known limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- `DatasetName.INSTRUMENT_STATUS_HISTORY` can be fetched through the AKShare adapter for caller-provided A-share symbols
- normalized records pass the dataset registry contract
- offline tests cover success, invalid symbol/input, deterministic sorting/deduplication, and source limitation behavior
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects the actual proven source breadth
