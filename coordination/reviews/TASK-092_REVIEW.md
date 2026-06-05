# TASK-092 Review

## Findings

- Blocking: [quant/datahub/source.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/source.py:210) and [quant/datahub/source.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/source.py:412) classify every fetch-stage `TypeError` as `unsupported_request`. The handoff only required route/signature mismatch errors to avoid being treated as upstream unavailability. An internal adapter bug that raises `TypeError` inside `fetch()` would now be recorded as `availability_status=unsupported` and `request_or_configuration_like=true`, which corrupts the new standardized source-health metadata. The added tests only cover signature mismatch in [tests/datahub/test_source.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_source.py:542) and unsupported-request routing in [tests/datahub/test_refresh.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_refresh.py:376); there is no regression proving unrelated internal `TypeError` stays out of `unsupported_request`.

## Decision

- REWORK REQUIRED

## Closure Readiness

- Controller closure allowed: No.
- Default tests offline-safe: Yes. Independent verification passed for `tests/datahub/test_quality.py`, `tests/datahub/test_refresh.py`, `tests/datahub/test_source.py`, `tests/datahub/test_source_capabilities.py`, and `tests/datahub/test_source_catalog.py`.
- Live-enabled result: SKIP. This task is local-only and no live test was permitted. Rework is still required because of the blocking classification bug above.
- Phase/scope blockers: No phase-boundary or forbidden-file violation found.
- Contract/test blockers: Yes. Fetch-stage failure classification is too broad, and coverage is missing for non-signature/internal `TypeError`.

## Required Follow-up

- Narrow fetch-stage `TypeError` handling so only clear request/contract/signature mismatches map to `unsupported_request`; internal adapter `TypeError` should remain a non-unsupported failure classification.
- Add an offline regression test for an adapter whose `fetch()` raises an internal `TypeError` unrelated to request signature.
