# TASK-130 DataHub Quality Report Coverage KPI Hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-129 is closed after accepted Review Agent verification. It hardened the macro/policy capability cluster, kept default tests offline-safe, recorded live-enabled PASS evidence for the materially changed macro, policy-document, and HK announcement paths, and kept macro/policy capability truth conservative.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches. `index_weight_history` remains an owner paid-credential blocker, and optional `hk_minute_bars` remains owner-waiver-required.

Controller read DataHub readiness `follow_up_batches`. TASK-129 covered batch `macro_policy__datahub_hardening__macro_policy__batch_01`. The next executable current-phase batch is:

- batch id: `quality_reports__datahub_hardening__source__batch_01`
- disposition: `datahub_hardening`
- recommended theme: `enhance quality report with coverage KPIs`

Included follow-up item:

- `quality_reports__quality_reports_source_coverage_metadata__source_coverage_metadata`

This is a single-item handoff because the batch contains one coherent local quality-report capability item. It must not be merged with already closed domain hardening batches, the paid `index_weight_history` credential blocker, or the owner-waiver-required HK minute-bars item.

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, private data, or any hidden live network path.

## Objective

Harden DataHub local quality-report coverage metadata so personal trading readiness gaps are visible through deterministic quality-report KPI records, not only through separate readiness objects.

Execution should add or tighten local-only coverage KPI support for `DatasetName.DATA_QUALITY_REPORT`, including enough structured details for downstream operators to understand:

- source/domain coverage status counts;
- capability status counts;
- blocked/warn/fail follow-up counts;
- follow-up batch counts and identifiers;
- owner-action blockers versus executable DataHub hardening gaps;
- the fact that KPI output is local/readiness metadata, not proof that any source adapter became complete.

Keep all quality-report capability truth conservative unless implementation and tests prove that coverage metadata is materially richer and schema-valid.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-130_DATAHUB_QUALITY_REPORT_COVERAGE_KPI_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-025_REPORT.md`
- `coordination/reviews/TASK-025_REVIEW.md`
- `coordination/reports/TASK-039_REPORT.md`
- `coordination/reviews/TASK-039_REVIEW.md`
- `coordination/reports/TASK-092_REPORT.md`
- `coordination/reviews/TASK-092_REVIEW.md`
- `coordination/reports/TASK-093_REPORT.md`
- `coordination/reviews/TASK-093_REVIEW.md`
- `quant/datahub/quality.py`
- `quant/datahub/personal_readiness.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/datasets.py`
- `tests/datahub/test_quality.py`
- `tests/datahub/test_personal_readiness.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

Read related DataHub local storage, refresh metadata, or dataset tests only if needed to preserve compatibility.

## Allowed Writes

Only:

- `quant/datahub/quality.py`
- `quant/datahub/personal_readiness.py` only if KPI details need a reusable local readiness summary helper
- `quant/datahub/source_capabilities.py` only if the quality-report capability truth must be reconciled after the KPI hardening
- `quant/datahub/source_catalog.py` only if quality-report source/catalog wording becomes inconsistent with the implemented KPI output
- `quant/datahub/datasets.py` only if a minimal schema-compatible `DATA_QUALITY_REPORT` detail clarification is unavoidable
- `tests/datahub/test_quality.py`
- `tests/datahub/test_personal_readiness.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_*quality*.py` file needed for this handoff
- `coordination/reports/TASK-130_REPORT.md`

If a tightly related DataHub local-only test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-130_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- real-source adapters unless required only to fix an import broken by an allowed local helper change
- unrelated DataHub source-domain tests
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not use credentials, tokens, cookies, browser session state, private account data, paid sources, or live network behavior.

Do not implement FeatureHub indicators, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Keep the implementation deterministic and local-only.
- Preserve existing `LocalRefreshQualityHelper.build_quality_report_records(...)` behavior and schema compatibility.
- Add coverage KPI details as structured `DATA_QUALITY_REPORT` records or details in a way that validates through `DatasetRegistry`.
- KPI details should be bounded and stable: no huge raw capability dumps, no nondeterministic ordering, and no reliance on current wall-clock values except the existing injectable quality timestamp behavior.
- KPI details should distinguish `pass`, `warn`, `blocked`, and `fail`.
- KPI details should include enough information to tell owner credential blockers apart from executable DataHub hardening follow-ups and owner-waiver-required items.
- KPI details must not treat `partial`, `warn`, or `blocked` capabilities as complete.
- If quality-report source capability metadata changes, keep wording conservative and explicitly state that KPI hardening improves observability, not real-source completeness.
- Do not add live smoke tests. This is a local quality-report metadata task.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_quality`
- `python3 -m unittest tests.datahub.test_personal_readiness`
- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- focused local-only tests for every changed file

Live smoke requirement:

- None. Live tests are forbidden for this task.
- Report live-enabled result as `SKIP - not applicable; local-only quality-report metadata hardening`.

## Completion Report

Write `coordination/reports/TASK-130_REPORT.md` with:

- files changed
- implementation summary
- selected readiness batch id and included follow-up ids
- exact coverage KPI fields/details added or tightened
- how KPI output distinguishes pass/warn/blocked/fail and executable/owner-action dispositions
- schema validation behavior for `DATA_QUALITY_REPORT`
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as local-only SKIP/not applicable
- whether quality-report capability/source truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- Quality-report records expose deterministic coverage KPI metadata for DataHub personal-readiness gaps.
- KPI records validate under the `DATA_QUALITY_REPORT` contract.
- Default tests remain offline-safe.
- No live network path is introduced.
- Quality-report capability/catalog wording remains conservative and reflects only observability improvements.
- No inactive downstream module behavior is introduced.
