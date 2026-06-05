# TASK-095 DataHub A-share Suspension/Resumption Breadth and Taxonomy Hardening

## Role

5.3 Execution Window.

## Context

TASK-094 is closed after accepted Review Agent verification. It improved A-share `DatasetName.INSTRUMENT_STATUS_HISTORY` lifecycle evidence where public routes expose source truth, kept `a_share_listing_delisting_st_status` conservative at `partial`, and provided gated live PASS evidence without hidden default live-network behavior.

Phase 2.5-P remains open under the Personal Trading Perfection Standard. The accepted TASK-093 readiness gate still reports non-pass follow-up items, and `index_weight_history` remains an owner credential blocker that must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.

The next executable `datahub_hardening` item in the TASK-093 structured queue is:

- `a_share__a_share_capability_readiness__a_share_suspension_resumption`
- theme: expand A-share suspension/resumption breadth and confirm resumption taxonomy coverage
- reason: public AKShare bounded suspension-table coverage is validated, but trading-grade breadth, exact resumption confirmation, and taxonomy depth remain incomplete

This task stays inside Phase 2.5-P DataHub Personal Trading Perfection Re-Review. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden A-share `DatasetName.SUSPENSION_RESUMPTION_EVENTS` coverage by extending the existing public AKShare-backed adapter and tests toward broader suspension/resumption source breadth and more explicit source-truth event taxonomy where stable no-credential public routes expose it.

The task should preserve existing bounded suspension-table behavior. It must not infer a resumption event, exact end date, or event taxonomy from source text that does not actually provide it.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-095_REPORT.md`

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

- Reuse the existing AKShare A-share suspension/resumption adapter and `DatasetName.SUSPENSION_RESUMPTION_EVENTS` schema.
- Keep source access caller-bounded by explicit request parameters already supported by the adapter. Do not add broad universe collection, full-history backfill, scheduler logic, or cross-source orchestration.
- Preserve deterministic symbol validation, date validation, deduplication, sorting, injectable clock behavior, and schema validation behavior from TASK-053.
- Investigate stable no-credential AKShare routes already available in the dependency for A-share suspension, resumption, temporary suspension, continued suspension, suspension reason, suspension date, resumption date, or source-provided status taxonomy.
- Add source-backed normalization only for rows that expose reliable event dates/status truth. Do not synthesize resumption from the absence of a suspension row, latest trading status, stock name, or generic board membership.
- If a route provides current-only or ambiguous suspension text, keep it as current-only or ambiguous source evidence and document the limitation rather than promoting it to full continuity coverage.
- Normalize any new source-backed events into the existing schema fields:
  - `symbol`
  - `market`
  - `event_date`
  - `event_type`
  - optional `start_date`
  - optional `end_date`
  - optional `reason`
  - optional `raw_status`
  - optional `exchange`
  - optional `board`
  - optional `source_ts`
  - `source`
  - `ingested_at`
  - `schema_version`
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures under the existing DataHub live-failure classification policy.
- Update only `a_share_suspension_resumption` capability truth if implementation and live evidence justify it. Keep it conservative unless full trading-grade breadth and taxonomy are actually proven.
- If no additional stable public route can improve the capability, make the smallest code/test/report change that records the proven infeasibility explicitly and keeps the readiness truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py`

The live-enabled smoke should validate at least one stable no-credential public suspension/resumption source sample when such a sample is available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-095_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- source routes investigated and route-level findings
- any capability truth changes
- remaining public-source limitations for suspension/resumption breadth, exact resumption confirmation, and taxonomy depth
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- any feasible no-credential source-backed suspension/resumption breadth or taxonomy improvement is implemented and tested, or infeasibility is explicitly evidenced in code/tests/report without over-promoting capability truth
- normalized records still validate against `DatasetName.SUSPENSION_RESUMPTION_EVENTS`
- offline tests cover new source-backed taxonomy cases or explicit limitation behavior
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- `a_share_suspension_resumption` remains conservative unless full personal trading breadth is proven
