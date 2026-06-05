# TASK-092 DataHub Source Health TypeError Classification Rework

## Role

5.3 Execution Window.

## Context

TASK-092 implemented local source-health metadata and standardized failure-state records. Review rejected the result because fetch-stage `TypeError` handling is too broad:

- `quant/datahub/source.py` currently classifies every fetch-stage `TypeError` as `unsupported_request`.
- The original handoff required clear route/signature/request mismatch errors to avoid being treated as upstream unavailability.
- Internal adapter bugs that raise `TypeError` inside `fetch()` must not be recorded as `availability_status=unsupported` or `request_or_configuration_like=true`.

This rework must stay inside Phase 2.5 DataHub Trading-Usable Hardening and address only the Review finding. Do not perform a broader source-health redesign.

## Objective

Narrow source-health failure classification so only clear request/contract/signature mismatches map to `unsupported_request`, while internal adapter `TypeError` failures remain non-unsupported fetch/implementation failures with truthful standardized health metadata.

Add focused offline regression coverage proving an adapter whose `fetch()` raises an unrelated internal `TypeError` is not classified as `unsupported_request`.

## Allowed Writes

Only:

- `quant/datahub/source.py`
- `quant/datahub/refresh.py`
- `tests/datahub/test_source.py`
- `tests/datahub/test_refresh.py`
- `coordination/reports/TASK-092_REPORT.md`

Use the smallest necessary subset of these files.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `coordination/reviews/**`
- `coordination/integrations/**`
- real-source adapters under `quant/datahub/adapters/`
- live test files
- dataset contracts
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/quality.py` unless the controller explicitly reopens the scope
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, private account data, or live network access.

## Required Rework

- Inspect the existing request/signature mismatch classifier in `quant/datahub/source.py`.
- Ensure only clear adapter request/contract/signature mismatches become:
  - `failure_category=unsupported_request`
  - `availability_status=unsupported`
  - `request_or_configuration_like=true`
- Ensure unrelated/internal fetch-stage `TypeError` remains a non-unsupported failure classification, preferably `fetch_failed` unless the existing standardized taxonomy has a more precise non-unsupported category.
- Keep route-name-bearing adapter argument/signature compatibility errors out of upstream/network-like classifications.
- Preserve existing standardized categories and successful TASK-092 behavior for success, empty result, schema validation failure, metadata-write failure, and persistence failure.
- Avoid broad exception swallowing. If a path raised before this rework, it may still raise after standardized metadata/quality evidence is recorded.

## Required Tests

Add or update focused offline tests for:

- a clear request/signature mismatch still maps to `unsupported_request`
- an adapter whose `fetch()` raises an internal/unrelated `TypeError` does not map to `unsupported_request`

Run:

- `python3 -m unittest tests/datahub/test_source.py`
- `python3 -m unittest tests/datahub/test_refresh.py`
- `python3 -m unittest tests/datahub/test_quality.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`

Recommended if focused tests pass:

- `python3 -m unittest discover tests/datahub`

Do not run live-enabled tests and do not set `QUANT_SYSTEM_LIVE_TESTS=1`.

## Completion Report

Update `coordination/reports/TASK-092_REPORT.md` with:

- files changed by this rework
- tests run and results
- default network behavior
- live-enabled result, which must remain `SKIP` because this task is local-only and live tests are not permitted
- exact classification behavior after rework for request/signature mismatch versus internal fetch `TypeError`
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete when:

- Review's blocking classification bug is fixed
- offline regression coverage proves internal fetch `TypeError` is not classified as `unsupported_request`
- default tests remain offline-safe
- no live network access or credential usage is introduced
- no phase-boundary or forbidden-file changes are made
