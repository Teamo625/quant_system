# TASK-091 DataHub Macro/Policy Depth Hardening

## Role

5.3 Execution Window.

## Context

TASK-090 is closed after accepted Review Agent verification. It hardened bounded public AKShare-backed `SECTOR_MEMBERSHIP` access from a one-sector slice to caller-provided multi-sector bounded membership access, kept sector membership/history capability truth conservative, preserved default offline-safe tests, and provided gated live smoke PASS evidence.

Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`: macro/policy depth, source-health metadata, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver.

This task continues the TASK-071 DataHub hardening queue in the macro and policy/news/announcement domain. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden the existing public macro/policy source family from bounded representative coverage into more practical caller-parameterized depth for macro observations, macro indicator definitions, and policy-document metadata.

The implementation should make the current public adapters easier to use for real short-term and medium/long-term research by supporting explicit requested macro indicators/routes where public AKShare routes are already represented locally, preserving release/revision metadata where source rows expose it, and strengthening bounded policy-document retrieval/filtering without inventing missing full-history or authority coverage.

This task does not require a new dataset contract, full global macro source coverage, full policy-document historical backfill, paid/private sources, downstream features, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/policy.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_china_macro_adapter.py`
- `tests/datahub/test_akshare_china_macro_live.py`
- `tests/datahub/test_policy_documents_adapter.py`
- `tests/datahub/test_policy_documents_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-091_REPORT.md`

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

Do not implement derived macro features, news summarization, scanner universes/ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Extend `AkshareChinaMacroAdapter` so `SourceRequest.symbols` can be used as explicit macro indicator identifiers for the locally supported public macro routes, such as `CPI_CN_YOY`, `PPI_CN_YOY`, and `GDP_CN_YOY`.
- Preserve the existing no-symbol request path as "all locally supported macro indicators."
- Reject malformed, blank, duplicate-normalized, unsupported, stock-like, ETF/fund-like, Hong Kong stock-like, and policy-document-like symbols clearly before returning records.
- For `DatasetName.MACRO_INDICATOR_MASTER`, return only the requested indicator definitions when symbols are supplied.
- For `DatasetName.MACRO_OBSERVATIONS`, fetch only requested supported indicators when symbols are supplied, apply `start_date` / `end_date` filtering, and fail clearly rather than returning partial successful batches when a requested indicator is unsupported or yields no usable rows while another succeeds.
- Preserve source truth for optional macro fields such as `release_date`, `source_ts`, and `is_preliminary` when public rows expose them. Do not invent revision history, release calendars, or preliminary/final states.
- Keep route-name-bearing AKShare argument/signature incompatibility as a hard failure, not a live-unavailable skip.
- Add or update route-unavailability classification narrowly for network/proxy/DNS/TLS/upstream/public-source availability conditions only.
- Harden `MacroPolicyDocumentsAdapter` within the existing `POLICY_DOCUMENTS` contract by preserving bounded date-window behavior, deterministic ordering, route provenance, duplicate handling, and optional `source_ts` / `url` / `summary` fields where source rows expose them.
- If feasible within the existing `SourceRequest` contract, let policy-document `symbols` act as explicit public route selectors for supported policy routes, such as `zhengcelibrary_gw` and `zhengcelibrary_bm`; otherwise preserve the current no-symbol route behavior and document why route selectors need a future contract extension.
- Validate normalized records with `DatasetRegistry.validate_record(...)` for `MACRO_INDICATOR_MASTER`, `MACRO_OBSERVATIONS`, and `POLICY_DOCUMENTS`.
- Update source catalog metadata only if needed to reflect actual public route coverage.
- Update `macro_observations`, `macro_indicator_definitions`, `macro_release_metadata`, and `policy_documents` capability truth only if implementation and live evidence justify it. Keep them `partial` unless the adapter demonstrably satisfies full trading-usable breadth/history/release-metadata standards; otherwise refine gap text conservatively.
- Do not promote `news_events` or `company_announcements_cross_market`; this task is not a news or company-announcement expansion task.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_china_macro_adapter.py`
- `python3 -m unittest tests/datahub/test_policy_documents_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
- `python3 -m unittest -v tests/datahub/test_policy_documents_live.py`

The live smoke files must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smokes:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_policy_documents_live.py`

The live-enabled macro smoke should validate at least two supported macro indicator identifiers when upstream public routes are available. The live-enabled policy smoke should validate at least one supported public policy route and schema-valid policy-document metadata when upstream public routes are available.

If a live-enabled smoke fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-091_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for both macro and policy live smokes
- whether macro/policy capability truth changed
- source route coverage and known macro release/revision/policy history limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- macro indicator definitions and macro observations support clear caller-parameterized access for supported public indicator identifiers
- policy-document handling is hardened or its current route-selector limitation is documented with conservative capability truth
- normalized records validate against their existing DataHub contracts
- invalid, unsupported, or no-row requested macro identifiers fail clearly before returning partial batch success
- deterministic dedupe/sorting behavior remains covered
- release/revision/source timestamp truth is preserved or the absence of public fields is explicitly documented
- default live tests remain offline-safe and skipped by default
- both live-enabled smokes are attempted and truthfully reported
- capability metadata remains conservative and reflects actual proven source breadth
