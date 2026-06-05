# TASK-079 DataHub Hong Kong Daily Bars Batch/Resilience Hardening

## Role

5.3 Execution Window.

## Context

TASK-071 audited DataHub against the trading-usable completion standard and found that most real-source capabilities remain narrow slices. TASK-072 through TASK-078 closed the first A-share batch-hardening queue for daily bars, lifecycle/status, valuation, capital flow, financial history, and minute bars.

Phase 2.5 remains open because Hong Kong market research inputs are still not trading-usable enough. `hk_daily_bars` remains `partial`; the existing `AkshareHKDailyBarAdapter` has accepted one-symbol live evidence but still rejects multi-symbol requests. `hk_universe_reference` also remains `partial`, with reference coverage validated only on narrow symbol slices.

This task is the next current-phase DataHub hardening slice. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden AKShare-backed Hong Kong `DAILY_BARS` access from a one-symbol slice into deterministic, caller-provided multi-symbol access with bounded date-window behavior and explicit source-resilience handling.

Where narrowly necessary for reliable HK symbol validation or capability truth, also harden the existing AKShare HK `INSTRUMENT_MASTER` reference path without turning this into full-market local collection.

The adapters should preserve existing one-symbol behavior, reject invalid HK symbols clearly before partial batch success, normalize records to existing DataHub datasets, keep default tests offline-safe, and include gated live smoke evidence that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

This task does not require HK minute-bar contracts, full-market collection, full-history backfill, local warehouse orchestration, FeatureHub calculations, scanner workflows, strategy/backtest logic, or private/credentialed sources.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_hk_adapter.py`
- `tests/datahub/test_akshare_hk_live.py`
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-079_REPORT.md`

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

- Extend `AkshareHKDailyBarAdapter` for multiple requested Hong Kong stock symbols through the existing `SourceRequest.symbols` path.
- Preserve support for exactly one HK symbol.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently fetch the full HK market in this task.
- Validate and normalize HK stock symbol formats consistently, accepting canonical `00700.HK`-style symbols and rejecting A-share, ETF/fund, index-like, malformed, ambiguous, missing, or unsupported symbols clearly.
- Validate the full requested symbol batch before making source calls so invalid inputs do not produce partial successful batches.
- Fetch each requested valid HK symbol through bounded no-credential public AKShare daily-bar routes and combine normalized records.
- Preserve the current `stock_hk_hist` primary route and `stock_hk_daily` fallback behavior where source-truthful. Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures; only treat actual network/proxy/DNS/TLS/upstream availability failures as route-unavailable conditions.
- Honor `start_date` and `end_date` for every symbol. If a fallback route does not accept date parameters, filter rows locally by normalized `trade_date` and document the limitation.
- Preserve source-truth optionality for fields not reliably exposed by public routes. Do not invent OHLCV, amount, or adjustment values beyond existing schema-compatible behavior.
- Keep records compatible with `DatasetRegistry.validate_record(DatasetName.DAILY_BARS, ...)`.
- Deduplicate deterministically by at least `(symbol, trade_date, source, price_adjustment)`.
- Sort output deterministically by symbol and `trade_date`.
- If one symbol fails due to invalid input or adapter/schema/normalization behavior, fail clearly rather than returning a partial successful batch.
- Do not change the `DatasetName.DAILY_BARS` or `DatasetName.INSTRUMENT_MASTER` schema in this task.
- If HK instrument reference code is changed, keep it limited to caller-provided HK stock symbols and/or validated public-source breadth needed by this task; do not introduce unbounded collection by default.
- Update only `hk_daily_bars` and, if directly justified by implementation plus tests, `hk_universe_reference` capability truth. Keep each `partial` unless the implementation and live evidence demonstrably satisfy the full trading-usable breadth/history standard; otherwise refine gap text conservatively.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`
- `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`

The live-enabled smoke should validate at least two Hong Kong stock symbols for `DAILY_BARS` over a bounded date window if the upstream public routes are available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-079_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `hk_daily_bars` or `hk_universe_reference` capability truth changed
- source route coverage, date-window behavior, fallback behavior, and known HK source limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- multi-symbol HK daily-bar requests work through the adapter contract in offline tests
- bounded date-window behavior is deterministic and tested
- normalized records validate against `DatasetName.DAILY_BARS`
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects the actual proven source breadth
