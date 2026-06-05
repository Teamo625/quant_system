# TASK-090 DataHub Sector Membership Batch/History Hardening

## Role

5.3 Execution Window.

## Context

TASK-089 is closed after accepted Review Agent verification. It hardened bounded public AKShare-backed `INDEX_CONSTITUENTS` access from a one-index source slice to caller-provided multi-index bounded constituent access, kept capability truth conservative, and provided default offline-safe tests plus gated live smoke PASS evidence.

Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`: sector membership/history, macro/policy depth, source-health metadata, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver.

This task continues the TASK-071 DataHub hardening queue in the sector/concept domain. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden public AKShare-backed `DatasetName.SECTOR_MEMBERSHIP` access from a one-sector source slice into practical, caller-provided multi-sector bounded membership access for industry/concept research, while preserving explicit membership date/history source truth where public routes expose it.

The adapter should support multiple requested typed sector identifiers, normalize records to the existing `SECTOR_MEMBERSHIP` contract, keep default tests offline-safe, and include gated live smoke evidence that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

This task does not require a new dataset contract, full sector taxonomy history, an index-level or sector-level rebalance calendar, downstream sector-relative features, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_sector_membership_adapter.py`
- `tests/datahub/test_akshare_sector_membership_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-090_REPORT.md`

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

Do not implement derived sector features, scanner universes/ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Extend `AkshareSectorMembershipAdapter` to support `SourceRequest.symbols` with multiple caller-provided sector identifiers.
- Preserve support for the existing accepted one-sector request path.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently return all sector membership tables.
- Accept typed sector identifiers already used locally, such as `INDUSTRY:小金属` and `CONCEPT:绿色电力`, with deterministic whitespace/case normalization for the type prefix.
- Reject malformed, blank, duplicate ambiguous, unsupported, stock-like, ETF/fund-like, Hong Kong stock-like, and untyped sector identifiers clearly before returning records.
- Normalize records to `DatasetName.SECTOR_MEMBERSHIP` with the existing contract fields, preserving source truth for optional `in_date`, `out_date`, and `source_ts` fields when public rows expose them.
- If the public route does not provide membership date fields, preserve the existing conservative fallback behavior and document the limitation; do not invent historical change events.
- Validate normalized records with `DatasetRegistry.validate_record(DatasetName.SECTOR_MEMBERSHIP, ...)`.
- Deduplicate deterministically by at least `(sector_id, symbol)` plus contract-compatible membership dates when present, and keep conflicting duplicate rows as hard failures.
- Sort output deterministically by `sector_id`, then `in_date`, then constituent symbol.
- If one requested sector identifier is invalid or unsupported, fail clearly rather than returning a partial successful batch.
- If one valid requested sector yields no usable rows while another succeeds, fail clearly rather than returning a partial successful batch, unless the adapter can classify a source-wide route outage.
- Keep route-name-bearing AKShare argument/signature incompatibility as a hard failure, not a live-unavailable skip.
- Add or update route-unavailability classification narrowly for network/proxy/DNS/TLS/upstream/public-source availability conditions.
- Update source catalog metadata only if needed to reflect actual public route coverage for `SECTOR_MEMBERSHIP`.
- Update `sector_membership` and `sector_historical_changes` capability truth only if implementation and live evidence justify it. Keep them `partial` unless the adapter demonstrably satisfies the full trading-usable breadth/history/classification-version standard; otherwise refine gap text conservatively.
- Do not promote `sector_classification_master`; it is already `covered` and this task is not a sector-master expansion task.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_sector_membership_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`

The live-enabled smoke should validate at least two supported sector identifiers, preferably one `INDUSTRY:*` and one `CONCEPT:*`, if upstream public routes are available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-090_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `sector_membership` or `sector_historical_changes` capability truth changed
- source route coverage and known sector membership/history/version metadata limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- sector `SECTOR_MEMBERSHIP` requests work through the adapter contract in offline tests for multiple caller-provided identifiers
- normalized records validate against `DatasetName.SECTOR_MEMBERSHIP`
- invalid, unsupported, or no-row identifiers fail clearly before returning partial batch success
- deterministic dedupe/sorting behavior is covered
- membership date/history source truth is preserved or the absence of public fields is explicitly documented
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects actual proven source breadth
