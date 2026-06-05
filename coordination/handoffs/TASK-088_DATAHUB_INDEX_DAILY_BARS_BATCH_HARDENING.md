# TASK-088 DataHub Index Daily-Bars Batch Hardening

## Role

5.3 Execution Window.

## Context

TASK-087 is closed after accepted Review Agent verification. It added bounded public ETF/fund `FUND_PREMIUM_DISCOUNT` adapter/source-fact coverage with default offline-safe tests and gated live smoke PASS evidence.

Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`: index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver.

This task starts the TASK-071 index queue. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden public AKShare-backed `DatasetName.INDEX_DAILY_BARS` access from a one-index source slice into practical, caller-provided multi-index bounded daily-bar access for core China benchmark research.

The adapter should support multiple requested index symbols over bounded date windows, normalize records to the existing `INDEX_DAILY_BARS` contract, keep default tests offline-safe, and include gated live smoke evidence that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

This task does not require full global benchmark coverage, credentialed index routes, index constituent or weight history, index rebalance metadata, local warehouse refresh orchestration, downstream feature calculation, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_index_adapter.py`
- `tests/datahub/test_akshare_index_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-088_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `coordination/reviews/**`
- `coordination/integrations/**`
- dataset contracts unless the controller issues a separate contract handoff
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

Do not implement index constituents, weight history, rebalance/effective-date metadata, downstream benchmark-relative features, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Extend `AkshareIndexDailyBarAdapter` to support `SourceRequest.symbols` with caller-provided multiple index symbols.
- Preserve support for the existing accepted one-index request path.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently return broad or full-market index tables.
- Accept canonical forms such as `000300.CN_INDEX` and supported source-native or bare forms already used locally, such as `sh000300`, `sz399001`, and `000300`.
- Reject A-share stock-like, ETF/fund, Hong Kong stock, malformed, ambiguous, missing, and unsupported index symbols clearly before returning records.
- Require bounded `start_date` and `end_date`; avoid accidental broad history pulls.
- Honor `start_date` and `end_date` deterministically. If the public route returns wider history, filter to the requested bounded window.
- Normalize records to `DatasetName.INDEX_DAILY_BARS` with the existing contract fields, preserving source truth for optional volume, amount, or source timestamp fields only when the source provides them.
- Validate normalized records with `DatasetRegistry.validate_record(DatasetName.INDEX_DAILY_BARS, ...)`.
- Deduplicate deterministically by at least `(index_code, trade_date, source)`.
- Sort output deterministically by `index_code` then `trade_date`.
- If one requested index is invalid or unsupported, fail clearly rather than returning a partial successful batch.
- If one valid requested index yields no usable rows while another succeeds for the same bounded window, fail clearly rather than returning a partial successful batch, unless the adapter can classify a source-wide route outage.
- Keep route-name-bearing AKShare argument/signature incompatibility as a hard failure, not a live-unavailable skip.
- Add or update route-unavailability classification narrowly for network/proxy/DNS/TLS/upstream/public-source availability conditions.
- Update source catalog metadata only if needed to reflect the actual public route coverage for `INDEX_DAILY_BARS`.
- Update `index_daily_bars` capability truth only if implementation and live evidence justify it. Keep it `partial` unless the adapter demonstrably satisfies the full trading-usable index daily-bar and benchmark breadth standard; otherwise refine the gap text conservatively.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_index_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest -v tests/datahub/test_akshare_index_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_live.py`

The live-enabled smoke should validate at least two benchmark index symbols, such as `000300.CN_INDEX` and `399001.CN_INDEX`, if the upstream public routes are available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-088_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `index_daily_bars` capability truth changed
- source route coverage and known benchmark/index daily-bar limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- index `INDEX_DAILY_BARS` requests work through the adapter contract in offline tests for multiple caller-provided symbols
- normalized records validate against `DatasetName.INDEX_DAILY_BARS`
- bounded date-window behavior is deterministic and tested
- invalid, unsupported, or no-row symbols fail clearly before returning partial batch success
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects the actual proven source breadth
