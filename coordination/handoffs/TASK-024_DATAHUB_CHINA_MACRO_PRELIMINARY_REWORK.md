# TASK-024: DataHub China Macro `is_preliminary` Rework

## Task ID

TASK-024

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-024 implemented the first AKShare-backed China macro slice for:

- `DatasetName.MACRO_INDICATOR_MASTER`
- `DatasetName.MACRO_OBSERVATIONS`

The first review did not accept the task. `coordination/reviews/TASK-024_REVIEW.md` records a blocking finding: `AkshareChinaMacroAdapter` maps source fields such as `初值` and `预告` into the optional `is_preliminary` field and then parses them as boolean values. This violates the original handoff rule:

> do not infer `is_preliminary` unless the source explicitly provides a reliable boolean-like value

The reported reproduction is:

- source row: `{"日期": "2024-01-10", "今值": "0.2", "初值": "0.1"}`
- current result: `ValueError("Invalid is_preliminary value: '0.1'")`

This rework must fix only that review-blocking field-handling issue and update the report/test evidence.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-024_DATAHUB_CHINA_MACRO_PRELIMINARY_REWORK.md`
- `coordination/reviews/TASK-024_REVIEW.md`
- `coordination/integrations/TASK-024_INTEGRATION.md`

## Goal

Make `AkshareChinaMacroAdapter` preserve numeric upstream fields such as `初值` / `预测值` / `预告` without treating them as `is_preliminary`, while still accepting an explicit reliable boolean-like `is_preliminary` field.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_china_macro_adapter.py`
- `tests/datahub/test_akshare_china_macro_live.py` only if the live test must be aligned with the corrected behavior
- `coordination/reports/TASK-024_REPORT.md`

Do not touch broader DataHub code unless a focused test proves it is required for this rework.

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

## Required Fix

### 1. Tighten `is_preliminary` handling

In `AkshareChinaMacroAdapter`:

- do not map `初值`, `预测值`, `预告`, or other numeric forecast/previous/initial-value fields into `is_preliminary`
- only emit `is_preliminary` when the source row contains an explicit reliable boolean-like field, such as `is_preliminary`
- preserve the existing behavior where explicit boolean-like values are accepted:
  - `True` / `False`
  - `1` / `0`
  - clear string forms such as `true` / `false` if already supported
- preserve the existing behavior where invalid explicit `is_preliminary` values hard-fail

### 2. Add focused offline regression tests

Add or update offline tests proving:

- a row containing numeric `初值` does not fail and does not include `is_preliminary`
- a row containing numeric `预测值` or `预告` does not fail and does not include `is_preliminary`
- a row containing explicit boolean-like `is_preliminary` still includes the normalized boolean
- invalid explicit `is_preliminary` still fails clearly

Keep these tests deterministic and offline. Use injected payloads only.

### 3. Preserve existing boundaries

Do not change:

- dataset scope beyond `MACRO_INDICATOR_MASTER` and `MACRO_OBSERVATIONS`
- selected indicator scope (`CPI_CN_YOY`, `PPI_CN_YOY`, `GDP_CN_YOY`)
- source id `macro_policy_public_sources`
- symbol-filter rejection
- date range filtering
- duplicate handling
- malformed payload and required-field failures
- default live-test skip gate

## Testing Requirements

Run focused tests:

`python3 -m unittest tests/datahub/test_akshare_china_macro_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`

Run related regressions:

`python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

Run full DataHub default tests:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run mandatory gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`

If the live-enabled run fails or skips because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. The task still cannot close until a fresh review accepts the result.

## Acceptance Criteria

This rework is acceptable when:

- the review diagnostic row `{"日期": "2024-01-10", "今值": "0.2", "初值": "0.1"}` no longer fails
- numeric `初值` / `预测值` / `预告` fields are ignored for `is_preliminary`
- explicit reliable boolean-like `is_preliminary` remains supported
- invalid explicit `is_preliminary` still fails clearly
- default tests remain offline-safe
- mandatory gated live smoke is rerun and truthfully reported
- `coordination/reports/TASK-024_REPORT.md` records the fix, tests, live result, deviations, and risks/follow-ups

## Report Path

`coordination/reports/TASK-024_REPORT.md`

## Review Path

`coordination/reviews/TASK-024_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-024_INTEGRATION.md`

## Out of Scope

Everything outside the `is_preliminary` review-blocking fix for `AkshareChinaMacroAdapter` is out of scope.
