# TASK-129 DataHub Macro/Policy Capability Cluster Hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-128 is closed after accepted Review Agent verification. It hardened the sector/concept capability cluster and completed the focused sector daily-bar live-classifier rework. Default tests remained offline-safe, and Review independently reproduced live-enabled PASS for the sector daily-bar smoke.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked` and `phase_closure_ready=False`. `index_weight_history` remains an owner paid-credential blocker, optional `hk_minute_bars` remains owner-waiver-required, and macro/policy plus quality-report gaps still require accepted hardening or owner-accepted disposition.

Controller read DataHub readiness `follow_up_batches`. TASK-128 covered batch `sector_concept__datahub_hardening__sector_concept__batch_01`. The next executable current-phase capability cluster is:

- batch id: `macro_policy__datahub_hardening__macro_policy__batch_01`
- disposition: `datahub_hardening`
- recommended theme: `cluster harden DataHub capabilities: macro_observations, macro_indicator_definitions, macro_release_metadata, policy_documents, company_announcements_cross_market`

Included follow-up items:

- `macro_policy__macro_policy_capability_readiness__macro_observations`
- `macro_policy__macro_policy_capability_readiness__macro_indicator_definitions`
- `macro_policy__macro_policy_capability_readiness__macro_release_metadata`
- `macro_policy__macro_policy_capability_readiness__policy_documents`
- `macro_policy__macro_policy_capability_readiness__company_announcements_cross_market`

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden the public-source macro/policy/news/announcement capability cluster for practical personal quant research:

- `macro_observations`: strengthen or truthfully constrain macro indicator breadth, bounded request behavior, revision history, release-date truth, and public-route redundancy beyond the current bounded CPI/PPI/GDP slice.
- `macro_indicator_definitions`: strengthen or truthfully constrain macro indicator dictionary breadth, source-route truth, metadata richness, and unsupported indicator handling.
- `macro_release_metadata`: add source-backed release-calendar/revision metadata where stable public routes expose it, or preserve conservative capability truth with tests preventing overclaiming.
- `policy_documents`: strengthen or truthfully constrain policy-document source breadth, authority coverage, pagination depth, bounded history behavior, route provenance, and document identity stability.
- `company_announcements_cross_market`: strengthen or truthfully constrain A-share/HK announcement parity, source-route truth, date-window behavior, cross-market normalization, and known public-source gaps.

Execution should add stable no-credential public-source support where feasible. If stronger public routes are not feasible, execution must tighten capability/catalog wording and tests so macro breadth, release/revision metadata, policy authority/history depth, or cross-market announcement parity gaps are not silently treated as complete.

Keep all included capabilities conservative unless implementation, tests, and gated live evidence genuinely satisfy the practical public-source personal trading completeness standard.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-129_DATAHUB_MACRO_POLICY_CLUSTER_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-024_REPORT.md`
- `coordination/reviews/TASK-024_REVIEW.md`
- `coordination/reports/TASK-030_REPORT.md`
- `coordination/reviews/TASK-030_REVIEW.md`
- `coordination/reports/TASK-046_REPORT.md`
- `coordination/reviews/TASK-046_REVIEW.md`
- `coordination/reports/TASK-054_REPORT.md`
- `coordination/reviews/TASK-054_REVIEW.md`
- `coordination/reports/TASK-091_REPORT.md`
- `coordination/reviews/TASK-091_REVIEW.md`
- `coordination/reports/TASK-108_REPORT.md`
- `coordination/reviews/TASK-108_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/policy.py`
- `quant/datahub/adapters/hkex.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_china_macro_adapter.py`
- `tests/datahub/test_akshare_china_macro_live.py`
- `tests/datahub/test_policy_documents_adapter.py`
- `tests/datahub/test_policy_documents_live.py`
- `tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `tests/datahub/test_akshare_a_share_company_announcements_live.py`
- `tests/datahub/test_hkex_company_announcements_adapter.py`
- `tests/datahub/test_hkex_company_announcements_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- related macro/policy/announcement DataHub tests only as needed to preserve compatibility

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/policy.py`
- `quant/datahub/adapters/hkex.py`
- `quant/datahub/adapters/__init__.py` only if an adapter export needs a minimal compatibility update
- `quant/datahub/__init__.py` only if an adapter export needs a minimal compatibility update
- `quant/datahub/datasets.py` only if a minimal schema-compatible macro/policy/announcement source-fact clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_china_macro_adapter.py`
- `tests/datahub/test_akshare_china_macro_live.py`
- `tests/datahub/test_policy_documents_adapter.py`
- `tests/datahub/test_policy_documents_live.py`
- `tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `tests/datahub/test_akshare_a_share_company_announcements_live.py`
- `tests/datahub/test_hkex_company_announcements_adapter.py`
- `tests/datahub/test_hkex_company_announcements_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_*macro*.py`, `tests/datahub/test_*policy*.py`, or `tests/datahub/test_*announcement*.py` file needed for this handoff
- `coordination/reports/TASK-129_REPORT.md`

If a tightly related macro/policy/announcement test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-129_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- unrelated DataHub adapters or tests
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not use credentials, tokens, cookies, browser session state, private account data, paid sources, or hidden default live network behavior.

Do not implement macro features, sector-relative features, Scanner universes/ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Preserve TASK-091 accepted macro/policy route-selector behavior and bounded request semantics unless a stricter compatible behavior is needed for source truth.
- Preserve TASK-108 accepted A-share announcement date-window/fallback truth and TASK-023/TASK-030/TASK-046 accepted source behavior.
- Prefer caller-provided, bounded macro indicators, route selectors, document windows, symbols, markets, and date windows. Keep unbounded full-table fetches as clear errors unless a route is explicitly designed and tested as a bounded catalog/list operation.
- Investigate stable no-credential public routes within repository-supported source families for:
  - broader China/global macro observations and indicator dictionaries;
  - source-backed release calendar, release date, revision, preliminary/final, or period metadata;
  - broader policy authority/source coverage, pagination depth, route provenance, and stable document identifiers;
  - A-share and Hong Kong announcement parity, cross-market field normalization, date-window behavior, and source-route truth.
- Emit only source-backed facts. Do not invent macro release dates, revision markers, policy authorities, document identifiers, announcement categories, source timestamps, or source-route values when a verified route does not provide them.
- Route-distinct facts must remain distinguishable when values can differ.
- Honor `start_date` and `end_date` deterministically for macro observations, policy documents, and company announcements. If a route returns wider history, filter to the requested window.
- Reject malformed, ambiguous, unsupported, duplicate-normalized, stock-like macro symbols, macro-like stock symbols, invalid policy route selectors, and unsupported market/symbol forms clearly.
- If a batch includes one invalid requested item or one repository-side schema/normalization defect, fail clearly rather than returning partial successful output.
- If a valid requested item yields no usable rows while another succeeds for the same bounded request, fail clearly unless execution can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, route-signature, call-compatibility, unbounded-fetch, or date-window defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `macro_observations`, `macro_indicator_definitions`, `macro_release_metadata`, `policy_documents`, and `company_announcements_cross_market` conservative unless full practical public-source breadth, history/revision/release truth, cross-market parity, and redundancy are genuinely proven.
- If no stable broader no-credential route is feasible for a capability, record attempted route names and observed limitations in the report, add or preserve tests that prevent overclaiming, and leave capability truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_china_macro_adapter`
- `python3 -m unittest tests.datahub.test_policy_documents_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_company_announcements_adapter`
- `python3 -m unittest tests.datahub.test_hkex_company_announcements_adapter`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_china_macro_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_policy_documents_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_company_announcements_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_hkex_company_announcements_live`
- focused macro/policy/announcement tests for every changed adapter/test file

Live smoke requirement:

- If any real-source macro path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_china_macro_live`.
- If any real-source policy-document path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_policy_documents_live`.
- If any A-share announcement path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_company_announcements_live`.
- If any Hong Kong announcement path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_hkex_company_announcements_live`.
- Live smokes must be explicitly gated and skipped by default.
- Live-enabled smokes should validate at least one newly supported or materially changed route/indicator/selector/symbol when upstream routes are available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If a live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-129_REPORT.md` with:

- files changed
- implementation summary
- selected readiness batch id and included follow-up ids
- macro route/source-family investigation result
- policy route/source-family investigation result
- A-share/HK announcement route/source-family investigation result
- supported indicator, policy selector, market/symbol, date-window, source-route, and deduplication behavior
- macro release/revision metadata source truth and known limitations
- policy document pagination/authority/history source truth and known limitations
- cross-market announcement source truth and known limitations
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for each materially changed real-source path
- whether any of the five capability truths changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- The macro/policy cluster has stronger public-source proof or stricter capability/catalog truth for all included follow-up items.
- Any emitted `MACRO_INDICATOR_MASTER`, `MACRO_OBSERVATIONS`, `POLICY_DOCUMENTS`, or `COMPANY_ANNOUNCEMENTS` records validate against their dataset contracts.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
