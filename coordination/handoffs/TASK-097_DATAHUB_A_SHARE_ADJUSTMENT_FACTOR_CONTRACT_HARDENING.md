# TASK-097 DataHub A-share Adjustment-Factor Contract Hardening

## Role

5.3 Execution Window.

## Context

TASK-096 is closed after accepted Review Agent verification. It added the owner-authorized BaoStock no-credential A-share minute-bars history path, then fixed the BaoStock live-smoke classifier so BaoStock-specific contract/data failures no longer downgrade to environment-unavailable `SKIP`. Default tests remain offline-safe and the gated BaoStock live smoke has PASS evidence.

Phase 2.5-P remains open under the Personal Trading Perfection Standard. The accepted TASK-093 readiness gate still reports non-pass follow-up items, and `index_weight_history` remains an owner credential blocker that must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.

The next unclosed executable `datahub_hardening` item in the TASK-093 structured queue is:

- `a_share__a_share_capability_readiness__a_share_adjustment_factors`
- theme: separate adjustment-factor contract fields or dedicated dataset
- reason: A-share adjustment-factor semantics are currently merged into generic `DatasetName.CORPORATE_ACTIONS`, so downstream personal research cannot rely on a first-class symbol x date adjustment-factor source fact.

## Objective

Harden A-share adjustment-factor DataHub semantics so the capability is no longer only an implicit field inside generic corporate actions.

Execution should create the smallest stable DataHub contract/source truth needed for A-share symbol x date adjustment-factor records, then implement no-credential public-source adapter coverage only where a stable public route exposes source truth. If no stable no-credential public adjustment-factor route is feasible, record that truth explicitly and keep capability metadata conservative.

This task must not implement FeatureHub factor calculations. It is DataHub source-fact/contract/source-capability hardening only.

## Allowed Writes

Only:

- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_live.py`
- `tests/datahub/test_akshare_a_share_adjustment_factors_adapter.py`
- `tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
- `coordination/reports/TASK-097_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-097_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
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

- Add a first-class adjustment-factor contract path. Prefer a dedicated dataset if that is cleaner than overloading `DatasetName.CORPORATE_ACTIONS`; otherwise add an explicit contract profile that makes adjustment-factor fields unambiguous.
- Required source-fact semantics must include at least:
  - canonical A-share symbol
  - market
  - effective trade date or factor date
  - numeric adjustment factor
  - adjustment basis/source mode where the public source exposes it
  - source id
  - deterministic raw payload reference
  - ingestion/source timestamp fields consistent with existing DataHub patterns
- Keep source truth explicit. Do not infer adjustment factors from adjusted prices unless the source route itself exposes a defensible adjustment-factor series or the report records the inference as rejected/infeasible.
- Investigate stable no-credential public AKShare routes already available in the local dependency that may expose A-share adjustment-factor data. If a route is implemented, keep requests caller-provided and bounded; do not add full-market collection or unbounded backfill.
- Preserve strict symbol validation. Reject HK, ETF/fund, index-like, malformed, ambiguous, missing, or unsupported symbols.
- Preserve deterministic sorting and duplicate handling by at least `(symbol, date, source, adjustment_basis)`.
- Update `source_catalog` and `source_capabilities` only to reflect proven source truth. Keep `a_share_adjustment_factors` conservative unless implementation and live evidence justify promotion.
- If the task remains contract-only because no stable public route is feasible, record route investigation evidence in the report and do not add live tests.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`

If adapter/source code is added or changed, also run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_adjustment_factors_adapter.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py`

If the implementation reuses or extends the existing corporate-actions adapter instead of adding a dedicated adapter, also run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`

Live smoke requirement:

- If any real-source adjustment-factor adapter path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1` for the relevant live smoke file.
- The live smoke must be explicitly gated and skipped by default.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-097_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` because no real-source adapter path was added
- contract/profile chosen for adjustment factors and why
- public-route investigation result
- whether `a_share_adjustment_factors` capability truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- A-share adjustment-factor semantics are first-class and test-covered in DataHub rather than silently merged into generic corporate actions.
- Source catalog/capability truth reflects the new contract path and any proven public-source adapter coverage.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- No inactive downstream module behavior is introduced.
