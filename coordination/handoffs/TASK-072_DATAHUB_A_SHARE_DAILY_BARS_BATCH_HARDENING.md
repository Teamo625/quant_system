# TASK-072 DataHub A-share Daily Bars Batch Hardening

## Role

5.3 Execution Window.

## Context

TASK-071 audited DataHub against the trading-usable completion standard and found that the largest systemic gap is batch-capable and parameterized real-source access. A-share daily bars are the highest-priority dependency because price/volume data feeds FeatureHub technical features, Scanner universes, liquidity/turnover analysis, strategy research, and later backtest replay.

The current `AkshareAShareDailyBarAdapter` has accepted one-symbol source evidence, but it rejects multi-symbol requests. This task hardens that capability without reopening downstream phases.

## Objective

Expand A-share daily bar fetching from one-symbol-only behavior to practical, deterministic, parameterized multi-symbol access over caller-provided A-share symbols and bounded date ranges.

The adapter should still use public AKShare routes, preserve existing one-symbol behavior, reject invalid symbols clearly, normalize records to `DatasetName.DAILY_BARS`, and keep default tests offline-safe.

If implementation and live evidence justify it, update only the `a_share_daily_bars` capability truth from `partial` to `covered` or update its gap reason conservatively. Do not promote any unrelated capability.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_adapter.py`
- `tests/datahub/test_akshare_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-072_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`
- unrelated DataHub datasets, adapters, or tests

Do not implement FeatureHub indicators, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI, notification, UI, or automated trading.

Do not use credentials.

## Implementation Requirements

- Support multiple requested A-share symbols through the existing `SourceRequest.symbols` path.
- Preserve support for exactly one symbol.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently fetch the full market in this task.
- Validate and normalize A-share symbol formats consistently with existing single-symbol behavior.
- Fetch each requested symbol through the public AKShare daily bar route and combine normalized records.
- Keep date bounds honored for every symbol.
- Ensure records are deterministic and deduplicated by at least `(symbol, trade_date, source)`.
- Sort output deterministically by symbol and trade date.
- Preserve existing price-adjustment behavior.
- Keep source/schema fields compatible with `DatasetRegistry.validate_record(DatasetName.DAILY_BARS, ...)`.
- If one symbol fails due to invalid input, fail clearly rather than returning a partial successful batch.
- Do not add hidden live network calls to default tests.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_live.py`

The live-enabled smoke should validate at least two A-share symbols if the upstream source is available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-072_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `a_share_daily_bars` capability truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- multi-symbol A-share daily bar requests work through the adapter contract in offline tests
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- any capability metadata update is narrow and justified by implementation plus evidence
