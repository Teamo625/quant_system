# TASK-023: DataHub HKEX Symbol Filter Rework

## Task ID

TASK-023

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-023 remains open.

The initial HKEX `COMPANY_ANNOUNCEMENTS` adapter implementation submitted `coordination/reports/TASK-023_REPORT.md`, and review reproduced offline/default/live test success, including live-enabled PASS evidence.

However, `coordination/reviews/TASK-023_REVIEW.md` records:

- decision: `REWORK REQUIRED (NOT CLOSURE-READY)`
- blocking issue: requested `symbols` input validation is too permissive
- reproduced invalid filters:
  - `symbols=("foo700",)` was accepted as `00700.HK`
  - `symbols=("A700.HK",)` was accepted as `00700.HK`

`coordination/integrations/TASK-023_INTEGRATION.md` records:

- decision: `Not Integrated (Blocked)`
- reason: integration cannot proceed until review is accepted

Per `AGENTS.md` and `coordination/PHASE_GATE.md`, the controller cannot close TASK-023 until this rework is completed, freshly reviewed, and integrated.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-023_DATAHUB_HKEX_COMPANY_ANNOUNCEMENTS_ADAPTER.md`
- `coordination/handoffs/TASK-023_DATAHUB_HKEX_SYMBOL_FILTER_REWORK.md`
- `coordination/reports/TASK-023_REPORT.md`
- `coordination/reviews/TASK-023_REVIEW.md`
- `coordination/integrations/TASK-023_INTEGRATION.md`

## Goal

Fix the review-blocking invalid symbol filter boundary while preserving the HKEX source-row parser tolerance needed for real HKEX HTML payloads.

The preferred closure outcome remains live-enabled `PASS`:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-023_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/hkex.py`
- `tests/datahub/test_hkex_company_announcements_adapter.py`
- `tests/datahub/test_hkex_company_announcements_live.py`

Only touch exports or catalog files if a real implementation change requires it:

- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_source_catalog.py`

## Forbidden Files

The execution window must not modify:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Rework Requirements

### 1. Make requested `symbols` validation strict

Requested symbols must only accept canonical HK input forms:

- `700`
- `00700`
- `00700.HK`

Equivalent valid numeric HK codes with 1 to 5 digits are acceptable and should normalize to five-digit `.HK` form.

Invalid request filters must hard-fail clearly before they can silently change query semantics. At minimum reject:

- `foo700`
- `A700.HK`
- `00700HK`
- wrong market suffixes such as `00700.US`
- empty or non-string symbols

Do not infer a requested symbol from arbitrary trailing digits.

### 2. Preserve source-row parsing tolerance separately

Do not remove the source-row tolerance needed for HKEX HTML cells such as:

- `Stock Code: 00700`
- `Release Time: 22/05/2026 22:57`

If the implementation needs trailing-code extraction for source rows, keep that behavior in a source-payload parsing helper rather than in the request filter validation path.

The adapter may continue to skip HKEX non-company rows with no usable symbol, but malformed matched company rows and DataHub contract failures must remain hard failures.

### 3. Add deterministic offline coverage

Update offline tests to prove:

- valid requested filters still normalize and filter correctly
- invalid requested filters reject at least:
  - `foo700`
  - `A700.HK`
  - `00700HK`
- HKEX source rows with label-prefixed stock-code text still normalize successfully
- default tests do not perform live network calls

Keep the test surface deterministic and fixture-based.

### 4. Update the execution report

Update `coordination/reports/TASK-023_REPORT.md` so it records this rework as the active result, including:

- files changed in the rework
- the exact symbol-filter bug fixed
- tests added or changed
- default network behavior
- live-enabled `PASS`/`SKIP`/`FAIL` result with evidence
- deviations, risks, and follow-up needs

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py`

`python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run related regressions if shared DataHub adapter behavior or exports are touched:

`python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py tests/datahub/test_akshare_global_equity_snapshot_adapter.py tests/datahub/test_akshare_hk_adapter.py tests/datahub/test_source.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run the live-enabled smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`

## Acceptance Criteria

The rework is acceptable for review when:

- TASK-023 remains scoped to `DatasetName.COMPANY_ANNOUNCEMENTS`
- requested symbol filters reject prefix-polluted or suffix-less invalid forms clearly
- source-row label tolerance is preserved without leaking into request input validation
- deterministic offline tests cover the fixed invalid-filter boundary
- default tests remain offline-safe
- live-enabled result is recorded truthfully
- no future-phase module contains new logic
- `coordination/reports/TASK-023_REPORT.md` is updated with this rework result

## Report Path

`coordination/reports/TASK-023_REPORT.md`

## Review Path

`coordination/reviews/TASK-023_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-023_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub `COMPANY_ANNOUNCEMENTS` symbol-filter rework and tests is out of scope.
