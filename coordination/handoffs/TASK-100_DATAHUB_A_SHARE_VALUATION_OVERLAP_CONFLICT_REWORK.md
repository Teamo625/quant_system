# TASK-100 DataHub A-share Valuation Overlap Conflict Rework

## Role

5.3 Execution Window.

## Context

TASK-100 initial execution added an Eastmoney dated valuation-history route alongside the existing Baidu route and reported live-enabled PASS evidence. Review rejected closure because the implementation silently dropped every Baidu record on or after the earliest Eastmoney date. That policy hides cross-route disagreements and can also lose Baidu records for dates where Eastmoney has gaps after its first available day.

This is a focused rework for the same TASK-100. Do not treat TASK-100 as closed, do not enter Integration, and do not move to a new domain.

## Objective

Fix the A-share `DatasetName.VALUATION_SNAPSHOT` Baidu/Eastmoney overlap policy so second-source coverage preserves source truth instead of silently preferring Eastmoney from its first available date onward.

The smallest acceptable rework is:

- overlapping dated Baidu/Eastmoney facts must either remain visible as route-distinct source facts with deterministic conflict detection, or be rejected deterministically when they are incompatible and cannot be represented truthfully
- Baidu records must not be dropped solely because their trade date is on or after the earliest Eastmoney date
- dates missing from Eastmoney after its first available date must not be silently lost when Baidu still has source-backed data for those dates

Keep `a_share_valuation_history` conservative unless the rework and live evidence prove materially stronger public-source completeness.

## Allowed Writes

Only:

- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
- `coordination/reports/TASK-100_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-100_REPORT.md`
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

## Required Rework

- Read `AGENTS.md`, this handoff, and `coordination/reviews/TASK-100_REVIEW.md` before editing.
- Inspect the current TASK-100 Baidu/Eastmoney combination logic and remove any first-secondary-date cutover policy that silently discards Baidu records.
- Preserve existing caller-provided symbol requirements and A-share symbol validation.
- Preserve deterministic de-duplication by at least `(symbol, trade_date, source, source_route)`.
- Detect conflicting duplicates within the same route/key and fail rather than silently merging incompatible metrics.
- For same-symbol/same-date cross-route Baidu/Eastmoney disagreements, implement one truthful policy:
  - preserve both records with distinct `source_route` values and deterministic sorting, with explicit regression coverage proving the disagreement remains visible; or
  - reject the incompatible cross-route facts with a clear deterministic error/result classification.
- Add or update offline regression coverage for the two Review-required cases:
  - overlapping same-date cross-route disagreements are not silently hidden
  - secondary-route gaps after its earliest available date do not cause Baidu source-backed records to disappear
- Keep normalized records schema-valid under `DatasetRegistry.validate_record(DatasetName.VALUATION_SNAPSHOT, ...)` for any successful path.
- Do not infer valuation history from prices, financial statements, adjustment factors, latest-only routes, or any non-dated source.
- Update source catalog/capability metadata only if the implemented behavior changes proven public-source truth. Do not promote `a_share_valuation_history` to `covered` from this rework alone.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`

Live smoke requirement:

- Because TASK-100 changed a real-source valuation adapter path, rerun `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`.
- The live smoke must remain explicitly gated and skipped by default.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence.
- If the live smoke skips or fails because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Update `coordination/reports/TASK-100_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- the final Baidu/Eastmoney overlap policy
- evidence for overlapping same-date disagreement handling
- evidence for secondary-route gap handling after the earliest Eastmoney date
- whether normalized records validate against `DatasetName.VALUATION_SNAPSHOT`
- whether `a_share_valuation_history` capability truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

This rework is complete only when:

- the Review blocking first-date cutover behavior is removed or replaced with truthful conflict handling
- offline regressions prove cross-route disagreements and secondary-route gaps are handled without silent data loss
- default tests remain offline-safe and live tests remain skipped by default
- gated live evidence is recorded truthfully
- TASK-100 remains within Phase 2.5-P DataHub scope and does not modify inactive downstream modules
