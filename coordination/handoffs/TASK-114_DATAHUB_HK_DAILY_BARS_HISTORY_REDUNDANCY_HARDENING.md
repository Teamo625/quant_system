# TASK-114 DataHub Hong Kong Daily Bars History/Redundancy Hardening

## Role

5.3 Execution Window.

## Context

TASK-113 is closed after accepted Review Agent verification. It kept Hong Kong universe reference truth conservative by proving that current no-credential HK instrument-master routes are stock-only and do not expose reusable non-stock taxonomy or trustworthy dated delist/inactive lifecycle metadata.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still has unresolved non-pass follow-up queue items and `phase_closure_ready=False`. The next unclosed executable queue item is:

- follow-up id: `hong_kong__hong_kong_capability_readiness__hk_daily_bars`
- capability: `hk_daily_bars`
- disposition: `datahub_hardening`
- theme: expand HK daily-bars history continuity and broader public-source redundancy beyond bounded batch coverage

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden Hong Kong `DatasetName.DAILY_BARS` source truth beyond the current caller-provided multi-symbol bounded batch path by doing one of the following:

1. Prove and implement stronger stable no-credential public-source coverage for HK daily bars, focused on longer history continuity and/or route redundancy; or
2. If no stable no-credential route can prove stronger coverage, truthfully constrain DataHub source-capability and source-catalog wording without promoting `hk_daily_bars`.

The result must keep `hk_daily_bars` conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source personal trading completeness for HK daily bars.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_adapter.py`
- `tests/datahub/test_akshare_hk_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-114_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than the TASK-114 report
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/datasets.py`
- unrelated DataHub adapters or tests
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, private account data, paid sources, or hidden default live network behavior.

## Implementation Requirements

- Read `AGENTS.md` and this handoff before editing.
- Preserve the existing `AkshareHKDailyBarAdapter` contract for caller-provided HK stock symbols.
- Preserve clear rejection for `symbols=None`, empty symbols, malformed HK symbols, A-share symbols, ETF/fund symbols, index-like symbols, or ambiguous values.
- Preserve full batch validation before source calls; invalid input must not produce partial successful batches.
- Investigate stable no-credential public AKShare/local routes available in this repository environment for HK daily bars, including the existing `stock_hk_hist` primary route and `stock_hk_daily` fallback.
- If a stronger stable route or route combination is implemented:
  - keep route-name-bearing AKShare argument/signature/schema/payload/normalization defects as hard failures;
  - classify only genuine network/proxy/DNS/TLS/upstream/public-source availability failures as live unavailability;
  - preserve date-window filtering for every returned record;
  - make source route/fallback truth explicit in normalized records or source metadata only if compatible with existing schemas;
  - keep records valid for `DatasetName.DAILY_BARS`;
  - deduplicate deterministically by at least symbol, trade date, source, and price-adjustment truth;
  - sort deterministically by symbol and `trade_date`.
- If no stronger stable no-credential route is feasible:
  - do not add speculative adapter behavior;
  - update `hk_daily_bars` source-capability and/or source-catalog wording to state the proven public-source limits precisely;
  - keep `hk_daily_bars` at `partial`.
- Do not change `DatasetName.DAILY_BARS` schema.
- Do not implement HK minute bars in this task.
- Do not perform full-market local collection or full-history backfill.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`

The live-enabled smoke should attempt to prove the strongest feasible no-credential HK daily-bar truth for at least two liquid HK stock symbols over a bounded historical window. If route availability, proxy, DNS, TLS, upstream behavior, or public-source limits prevent stronger proof, record PASS, SKIP, or FAIL truthfully with root-cause evidence and keep capability truth conservative.

## Completion Report

Write `coordination/reports/TASK-114_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `hk_daily_bars` capability truth changed
- source route coverage, date-window behavior, fallback behavior, history-continuity evidence, and known HK daily-bar limitations
- whether stronger public-source redundancy was implemented, constrained, or unsupported
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- HK daily-bar source truth is either strengthened with deterministic implementation/tests/live evidence or explicitly constrained without promotion;
- default tests remain offline-safe;
- live-enabled evidence is attempted and truthfully reported;
- source-capability/source-catalog wording cannot silently imply closure-grade HK daily-bar breadth when only bounded coverage is proven;
- no downstream modules or paid/private scopes are touched.
