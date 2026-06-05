# TASK-089 DataHub Index Constituents Batch/Rebalance Hardening

## Role

5.3 Execution Window.

## Context

TASK-088 is closed after accepted Review Agent verification. It hardened bounded public AKShare-backed `INDEX_DAILY_BARS` access from a one-index source slice to caller-provided multi-index bounded benchmark daily-bar access with default offline-safe tests and gated live smoke PASS evidence.

Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`: index constituent/rebalance metadata, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver.

This task continues the TASK-071 index queue. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden public AKShare-backed `DatasetName.INDEX_CONSTITUENTS` access from a one-index source slice into practical, caller-provided multi-index bounded constituent access for core China index research, while improving explicit rebalance/effective-date metadata where public source truth permits.

The adapter should support multiple requested index identifiers, normalize records to the existing `INDEX_CONSTITUENTS` contract, keep default tests offline-safe, and include gated live smoke evidence that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

This task does not require credentialed Tushare index weights, full index weight history, a new dataset contract, downstream benchmark-relative features, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_index_constituents_adapter.py`
- `tests/datahub/test_akshare_index_constituents_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-089_REPORT.md`

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

Do not implement index weight history, Tushare credential handling, downstream factor/features, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Extend `AkshareIndexConstituentsAdapter` to support `SourceRequest.symbols` with caller-provided multiple index identifiers.
- Preserve support for the existing accepted one-index request path.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently return broad or full-market constituent tables.
- Accept canonical forms such as `000300.CN_INDEX` and supported source-native or bare forms already used locally, such as `000300`, `000905`, `399001`, or equivalent route-supported identifiers.
- Reject A-share stock-like, ETF/fund, Hong Kong stock, malformed, ambiguous, missing, and unsupported index identifiers clearly before returning records.
- Normalize records to `DatasetName.INDEX_CONSTITUENTS` with the existing contract fields, preserving source truth for optional weight, effective date, end date, source timestamp, or rebalance-like fields only when the source provides them.
- Improve rebalance/effective-date metadata extraction within the existing `INDEX_CONSTITUENTS` contract when public AKShare rows expose such fields. If the public route does not provide explicit dates, preserve conservative null/omitted source truth and document the limitation.
- Validate normalized records with `DatasetRegistry.validate_record(DatasetName.INDEX_CONSTITUENTS, ...)`.
- Deduplicate deterministically by at least `(index_code, symbol, effective_date, source)` or the nearest contract-compatible key if effective date is absent.
- Sort output deterministically by `index_code`, then effective date if present, then constituent symbol.
- If one requested index is invalid or unsupported, fail clearly rather than returning a partial successful batch.
- If one valid requested index yields no usable rows while another succeeds, fail clearly rather than returning a partial successful batch, unless the adapter can classify a source-wide route outage.
- Keep route-name-bearing AKShare argument/signature incompatibility as a hard failure, not a live-unavailable skip.
- Add or update route-unavailability classification narrowly for network/proxy/DNS/TLS/upstream/public-source availability conditions.
- Update source catalog metadata only if needed to reflect actual public route coverage for `INDEX_CONSTITUENTS`.
- Update `index_constituent_history` and `index_rebalance_effective_dates` capability truth only if implementation and live evidence justify it. Keep them `partial` unless the adapter demonstrably satisfies the full trading-usable breadth/history/rebalance standard; otherwise refine gap text conservatively.
- Do not promote `index_weight_history`; the paid Tushare credentialed path remains blocked unless the owner supplies credentials or waives the limitation.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py`

The live-enabled smoke should validate at least two supported benchmark/index identifiers if upstream public routes are available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-089_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `index_constituent_history` or `index_rebalance_effective_dates` capability truth changed
- source route coverage and known constituent/rebalance metadata limitations
- confirmation that `index_weight_history` remains blocked/planned unless credentialed live evidence was explicitly in scope, which it is not for this task
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- index `INDEX_CONSTITUENTS` requests work through the adapter contract in offline tests for multiple caller-provided identifiers
- normalized records validate against `DatasetName.INDEX_CONSTITUENTS`
- invalid, unsupported, or no-row identifiers fail clearly before returning partial batch success
- deterministic dedupe/sorting behavior is covered
- rebalance/effective-date source truth is preserved or the absence of public fields is explicitly documented
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects actual proven source breadth
