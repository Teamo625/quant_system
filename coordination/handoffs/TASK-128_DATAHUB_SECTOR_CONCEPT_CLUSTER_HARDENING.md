# TASK-128 DataHub Sector/Concept Capability Cluster Hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-127 is closed after accepted Review Agent verification. It hardened the index benchmark capability cluster with curated global daily-bar support and broader China constituent proof, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept all index capabilities conservative because global long history, HK/global constituent history, explicit rebalance calendars, and public-route redundancy remain incomplete.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches. `index_weight_history` remains an owner paid-credential blocker, and optional `hk_minute_bars` remains owner-waiver-required.

Controller read DataHub readiness `follow_up_batches`. TASK-127 covered batch `index__datahub_hardening__index__batch_01`; the next batch is the owner credential blocker for `index_weight_history`, which is not executable without paid token scope. The next executable current-phase capability cluster is:

- batch id: `sector_concept__datahub_hardening__sector_concept__batch_01`
- disposition: `datahub_hardening`
- recommended theme: `cluster harden DataHub capabilities: sector_membership, sector_historical_changes, sector_daily_bars`

Included follow-up items:

- `sector_concept__sector_concept_capability_readiness__sector_membership`
- `sector_concept__sector_concept_capability_readiness__sector_historical_changes`
- `sector_concept__sector_concept_capability_readiness__sector_daily_bars`

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden the public-source sector/concept capability cluster for practical personal quant research:

- `sector_membership`: strengthen or truthfully constrain multi-sector industry/concept membership breadth, source-route truth, membership date fields, full taxonomy coverage, and public-route redundancy after TASK-090's bounded batch support.
- `sector_historical_changes`: strengthen or truthfully constrain explicit membership-change timelines, in/out-date continuity, classification-version metadata, and the difference between source-backed history and latest membership snapshots.
- `sector_daily_bars`: strengthen or truthfully constrain industry/concept sector daily-bar breadth, date-window continuity, route/source truth, and public-route redundancy beyond narrow sample coverage.

Execution should add stable no-credential public-source support where feasible. If stronger public routes are not feasible, execution must tighten capability/catalog wording and tests so full taxonomy history, change-event timelines, classification versions, sector daily-bar continuity, or route redundancy gaps are not silently treated as complete.

Keep all sector/concept capabilities conservative unless implementation, tests, and gated live evidence genuinely satisfy the practical public-source personal trading completeness standard.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-128_DATAHUB_SECTOR_CONCEPT_CLUSTER_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-017_REPORT.md`
- `coordination/reviews/TASK-017_REVIEW.md`
- `coordination/reports/TASK-018_REPORT.md`
- `coordination/reviews/TASK-018_REVIEW.md`
- `coordination/reports/TASK-019_REPORT.md`
- `coordination/reviews/TASK-019_REVIEW.md`
- `coordination/reports/TASK-090_REPORT.md`
- `coordination/reviews/TASK-090_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_sector_adapter.py`
- `tests/datahub/test_akshare_sector_live.py`
- `tests/datahub/test_akshare_sector_membership_adapter.py`
- `tests/datahub/test_akshare_sector_membership_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- related sector/concept DataHub tests only as needed to preserve compatibility

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py` only if an adapter export needs a minimal compatibility update
- `quant/datahub/datasets.py` only if a minimal schema-compatible sector/concept source-fact clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_sector_adapter.py`
- `tests/datahub/test_akshare_sector_live.py`
- `tests/datahub/test_akshare_sector_membership_adapter.py`
- `tests/datahub/test_akshare_sector_membership_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_akshare_sector*.py` file needed for this handoff
- `coordination/reports/TASK-128_REPORT.md`

If a tightly related sector/concept test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-128_REPORT.md`
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

Do not implement sector-relative features, Scanner universes/ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Preserve TASK-090 accepted `SECTOR_MEMBERSHIP` behavior for caller-provided bounded multi-sector industry/concept requests.
- Preserve accepted sector-master behavior unless a minimal compatibility change is needed to prove membership/daily-bar truth.
- Prefer caller-provided, bounded sector identifiers and date windows. Keep `symbols=None`, empty symbols, or unbounded full-table fetches as clear errors unless a route is explicitly designed and tested as a bounded catalog/list operation.
- Investigate stable no-credential public routes within repository-supported source families for:
  - broader industry/concept membership breadth;
  - stronger historical membership in/out-date continuity;
  - explicit sector membership-change event timelines;
  - classification-version or taxonomy-version metadata;
  - broader sector daily-bar route/date-window continuity;
  - independent public-route redundancy.
- Emit only source-backed facts. Do not invent OHLCV, amount, constituent membership dates, out dates, change events, classification versions, source timestamps, or source-route values when a verified route does not provide them.
- Preserve route/source truth with `source`, `source_route` where supported by the dataset contract, normalized typed sector identifiers, source-backed date fields, and any available provenance fields.
- Route-distinct facts must remain distinguishable when values can differ.
- Honor `start_date` and `end_date` deterministically as bounded windows for sector daily bars and any dated membership/history route. If a route returns wider history, filter to the requested window.
- Reject malformed, ambiguous, unsupported, stock-like, ETF/fund-like, Hong Kong stock-like, untyped, and duplicate-normalized sector identifiers clearly.
- If a batch includes one invalid sector identifier or one repository-side schema/normalization defect, fail clearly rather than returning partial successful output.
- If a valid requested sector yields no usable rows while another succeeds for the same bounded request, fail clearly unless execution can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, route-signature, call-compatibility, unbounded-fetch, or date-window defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `sector_membership`, `sector_historical_changes`, and `sector_daily_bars` conservative unless full practical public-source breadth, history continuity, classification-version truth, and redundancy are genuinely proven.
- If no stable broader no-credential route is feasible for a capability, record attempted route names and observed limitations in the report, add or preserve tests that prevent overclaiming, and leave capability truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_sector_adapter`
- `python3 -m unittest tests.datahub.test_akshare_sector_membership_adapter`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_sector_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_sector_membership_live`
- focused sector/concept tests for every changed adapter/test file

Live smoke requirement:

- If any real-source sector daily-bar path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_sector_live`.
- If any real-source sector membership/history path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_sector_membership_live`.
- Live smokes must be explicitly gated and skipped by default.
- Live-enabled smoke should validate at least one newly supported or materially changed industry sector and one concept sector when upstream routes are available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If a live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-128_REPORT.md` with:

- files changed
- implementation summary
- selected readiness batch id and included follow-up ids
- sector/concept route/source-family investigation result
- supported sector identifier classes, taxonomy families, date behavior, source-route truth, and deduplication behavior
- membership/effective-date/change-event/classification-version source truth and known limitations
- sector daily-bar source truth and known limitations
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for daily-bar and membership/history smokes as applicable
- whether any of the three sector/concept capability truths changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- The sector/concept cluster has stronger public-source proof or stricter capability/catalog truth for all included follow-up items.
- Any emitted `SECTOR_MEMBERSHIP` or `SECTOR_DAILY_BARS` records validate against their dataset contracts.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
