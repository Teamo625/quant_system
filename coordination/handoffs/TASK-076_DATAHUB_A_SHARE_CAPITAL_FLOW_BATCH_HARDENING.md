# TASK-076 DataHub A-share Capital Flow Batch Hardening

## Role

5.3 Execution Window.

## Context

TASK-071 audited DataHub against the trading-usable completion standard and found that most real-source capabilities remain narrow slices. TASK-072 closed the A-share daily-bars batch gap. TASK-073 and TASK-074 added contract and bounded adapter coverage for A-share listing/delisting/ST/status history. TASK-075 proved caller-provided multi-symbol bounded A-share valuation access, but kept `a_share_valuation_history` conservative because broader history/pagination remains incomplete.

Phase 2.5 remains open because A-share medium/long-term and flow-oriented research inputs are still not trading-usable enough. `a_share_capital_flow` and `a_share_northbound_flow` remain `partial`; the existing `AkshareAShareCapitalFlowSnapshotAdapter` has accepted one-symbol live evidence but still rejects multi-symbol requests and does not yet prove practical batch/date-window behavior.

This task is the next current-phase hardening slice. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden AKShare-backed A-share `CAPITAL_FLOW_SNAPSHOT` access from a one-symbol slice into deterministic, caller-provided multi-symbol access with bounded date-window filtering where the public routes provide dated capital-flow or northbound rows.

The adapter should preserve existing one-symbol behavior, reject invalid symbols clearly, normalize records to `DatasetName.CAPITAL_FLOW_SNAPSHOT`, keep default tests offline-safe, and include a gated live smoke that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

This task does not require full-market collection, full-history backfill, a dedicated northbound-flow dataset contract, or changes to the existing `CAPITAL_FLOW_SNAPSHOT` schema.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-076_REPORT.md`

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

Do not use credentials, cookies, tokens, browser session state, or private account data.

Do not implement downstream feature calculation, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Extend `AkshareAShareCapitalFlowSnapshotAdapter` for multiple requested A-share symbols through the existing `SourceRequest.symbols` path.
- Preserve support for exactly one symbol.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently fetch a full-market capital-flow table.
- Validate and normalize A-share symbol formats consistently with existing A-share AKShare adapter behavior.
- Reject HK, ETF/fund, index-like, malformed, ambiguous, missing, and unsupported symbols clearly.
- Fetch each requested symbol through bounded no-credential public AKShare capital-flow routes and combine normalized records.
- Preserve the existing fallback route behavior only where it is already source-truthful and bounded; do not hide route-name-bearing AKShare argument/signature compatibility errors as soft skips.
- Honor `start_date` and `end_date` for every symbol using normalized `trade_date`; if a source route only provides latest or limited history, apply the bounds deterministically and document that limitation.
- Normalize northbound values into the existing optional `northbound_net_buy` field only when public source rows provide source-truth values. Do not invent or backfill northbound values.
- Preserve source-truth optionality for fields not reliably exposed by public routes. Do not invent capital-flow metrics.
- Keep records compatible with `DatasetRegistry.validate_record(DatasetName.CAPITAL_FLOW_SNAPSHOT, ...)`.
- Deduplicate deterministically by at least `(symbol, trade_date, source)`.
- Sort output deterministically by symbol and trade date.
- If one symbol fails due to invalid input or adapter/schema/normalization behavior, fail clearly rather than returning a partial successful batch.
- Do not change `DatasetName.CAPITAL_FLOW_SNAPSHOT` schema in this task.
- Update only `a_share_capital_flow` and/or `a_share_northbound_flow` capability truth if implementation and live evidence justify it. Keep them `partial` unless the adapter demonstrably satisfies the full trading-usable breadth/history standard; otherwise refine the gap text conservatively.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

The live-enabled smoke should validate at least two A-share symbols if the upstream source is available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-076_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `a_share_capital_flow` or `a_share_northbound_flow` capability truth changed
- source route coverage and known capital-flow/northbound limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- multi-symbol A-share capital-flow requests work through the adapter contract in offline tests
- normalized records validate against `DatasetName.CAPITAL_FLOW_SNAPSHOT`
- date-window behavior is deterministic and tested
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects the actual proven source breadth
