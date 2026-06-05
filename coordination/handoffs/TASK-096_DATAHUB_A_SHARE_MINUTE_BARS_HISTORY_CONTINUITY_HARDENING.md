# TASK-096 DataHub A-share Minute Bars History Continuity Hardening

## Role

5.3 Execution Window.

## Context

TASK-095 is closed after accepted Review Agent verification. It fixed duplicate logical A-share suspension/resumption events across overlapping Eastmoney and Baidu public routes, added offline regression coverage, kept default tests offline-safe, and provided live-enabled PASS evidence.

Phase 2.5-P remains open under the Personal Trading Perfection Standard. The accepted TASK-093 readiness gate still reports non-pass follow-up items, and `index_weight_history` remains an owner credential blocker that must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.

The next executable `datahub_hardening` item in the TASK-093 structured queue is:

- `a_share__a_share_capability_readiness__a_share_minute_bars`
- theme: expand A-share minute-bars history continuity and broader public-source breadth beyond bounded date-window coverage
- reason: TASK-078 proved caller-provided multi-symbol bounded minute-bar access, but broader intraday history continuity and public-source breadth remain incomplete

## Objective

Harden A-share `DatasetName.MINUTE_BARS` public-source coverage by extending the existing AKShare-backed minute-bars adapter and tests toward stronger historical continuity evidence and broader no-credential public route coverage where stable source truth supports it.

This task should preserve existing multi-symbol bounded date-window behavior. It must not introduce full-market minute-bar collection, unbounded history backfill, credentialed Tushare routes, downstream FeatureHub calculations, scanner ranking, strategy/backtest logic, signal/risk/portfolio behavior, AI reports, notifications, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `tests/datahub/test_akshare_a_share_minute_bars_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-096_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-096_REPORT.md`
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

Do not use credentials, cookies, tokens, browser session state, paid APIs, or private account data.

## Implementation Requirements

- Reuse `AkshareAShareMinuteBarsAdapter` and the existing `DatasetName.MINUTE_BARS` schema.
- Investigate stable no-credential AKShare A-share minute-bar routes already available in the local dependency, especially whether current `stock_zh_a_hist_min_em` / `stock_zh_a_minute` behavior can provide stronger historical continuity, longer bounded windows, alternate intervals, or resilient route fallback without changing the dataset contract.
- Add only source-backed behavior that the public route actually exposes. Do not synthesize intraday bars, missing sessions, historical continuity, liquidity fields, or adjusted values.
- Preserve caller-provided symbol access. Do not allow `symbols=None`, empty symbol lists, or broad full-market requests.
- Keep requests bounded. If stronger history support requires a practical max-window guard, implement it with a clear error and offline coverage.
- Preserve validation of A-share symbol formats and clear rejection of HK, ETF/fund, index-like, malformed, ambiguous, missing, or unsupported symbols.
- Preserve deterministic sorting and duplicate handling by at least `(symbol, bar_time, interval, source)`.
- Keep normalized records compatible with `DatasetRegistry.validate_record(DatasetName.MINUTE_BARS, ...)`.
- If public routes expose only recent/latest bars in the local environment, document that limitation truthfully and strengthen tests/report around the conservative behavior rather than over-promoting capability truth.
- Update `a_share_minute_bars` capability truth only if implementation and live evidence justify it. Keep it conservative unless full personal trading breadth and history continuity are actually proven.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`

The live-enabled smoke should validate at least one stable no-credential public historical minute-bar sample beyond a trivial latest-only path when such a sample is available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-096_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- source routes investigated and which route is used
- historical continuity, bounded-window, interval, and fallback limitations
- whether `a_share_minute_bars` capability truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- any feasible no-credential public-source A-share minute-bar history continuity or route-breadth improvement is implemented and tested, or infeasibility is evidenced in code/tests/report without over-promoting capability truth
- default tests remain offline-safe and live tests remain skipped by default
- live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects actual proven public-source breadth
- no downstream or inactive module behavior is introduced
