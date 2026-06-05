# TASK-078 DataHub A-share Minute Bars Batch/Window Hardening

## Role

5.3 Execution Window.

## Context

TASK-071 audited DataHub against the trading-usable completion standard and found that most real-source capabilities remain narrow slices. TASK-072 through TASK-077 closed the first A-share batch-hardening queue items for daily bars, status history, valuation, capital flow, and financial-history access.

Phase 2.5 remains open because short-term A-share research still needs more practical intraday source access. `a_share_minute_bars` remains `partial`; the existing `AkshareAShareMinuteBarsAdapter` has accepted one-symbol bounded-date live evidence but still rejects multi-symbol requests and only proves one trade date per request.

This task is the next current-phase hardening slice. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden AKShare-backed A-share `MINUTE_BARS` access from a one-symbol/one-date slice into deterministic, caller-provided multi-symbol access with bounded date-window behavior where public routes can support it.

The adapter should preserve existing one-symbol behavior, reject invalid symbols clearly before partial batch success, normalize records to the existing `MINUTE_BARS` dataset, keep default tests offline-safe, and include gated live smoke evidence that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

This task does not require full-market collection, full-history backfill, new minute-bar dataset contracts, credentialed Tushare routes, feature calculation, local warehouse refresh orchestration, or downstream short-term strategy logic.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `tests/datahub/test_akshare_a_share_minute_bars_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-078_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `coordination/reviews/**`
- `coordination/integrations/**`
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

- Extend `AkshareAShareMinuteBarsAdapter` for multiple requested A-share symbols through the existing `SourceRequest.symbols` path.
- Preserve support for exactly one symbol.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently fetch full-market minute bars.
- Validate and normalize A-share symbol formats consistently with existing A-share AKShare adapter behavior.
- Reject HK, ETF/fund, index-like, malformed, ambiguous, missing, and unsupported symbols clearly.
- Validate the full requested symbol batch before making source calls so invalid inputs do not produce partial successful batches.
- Support `DatasetName.MINUTE_BARS` for every requested valid A-share symbol where the selected public route provides rows.
- Honor bounded `start_date` and `end_date` deterministically. If the primary route supports a date window, use it for a bounded multi-day request. If a fallback route exposes only latest/recent bars, filter by normalized `bar_time` and document the fallback limitation.
- Keep requests bounded. Do not introduce unbounded full-history or full-market fetch behavior. If a practical max date-window guard is needed to protect public-source usage and test runtime, implement it with a clear error message and test it.
- Preserve source-truth optionality for fields not reliably exposed by public routes. Do not invent minute-bar values.
- Keep records compatible with `DatasetRegistry.validate_record(DatasetName.MINUTE_BARS, ...)`.
- Deduplicate deterministically by at least `(symbol, bar_time, interval, source)`.
- Sort output deterministically by symbol and `bar_time`.
- If one symbol fails due to invalid input or adapter/schema/normalization behavior, fail clearly rather than returning a partial successful batch.
- Do not change the `DatasetName.MINUTE_BARS` schema in this task.
- Update `a_share_minute_bars` capability truth only if implementation and live evidence justify it. Keep it `partial` unless the adapter demonstrably satisfies the full trading-usable breadth/history standard; otherwise refine the gap text conservatively.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`

The live-enabled smoke should validate at least two A-share symbols for `MINUTE_BARS` over a bounded recent trade-date or date window if the upstream public routes are available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-078_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `a_share_minute_bars` capability truth changed
- source route coverage, date-window behavior, and known intraday-history limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- multi-symbol A-share minute-bar requests work through the adapter contract in offline tests
- bounded date-window behavior is deterministic and tested
- normalized records validate against `DatasetName.MINUTE_BARS`
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects the actual proven source breadth
