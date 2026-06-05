# TASK-092 Report

## files changed
- `quant/datahub/source.py`
- `tests/datahub/test_source.py`
- `tests/datahub/test_refresh.py`

## tests run
- `python3 -m unittest tests/datahub/test_source.py` -> PASS (`Ran 24 tests`)
- `python3 -m unittest tests/datahub/test_refresh.py` -> PASS (`Ran 10 tests`)
- `python3 -m unittest tests/datahub/test_quality.py` -> PASS (`Ran 8 tests`)
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 34 tests`)
- `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 7 tests`)
- `python3 -m unittest discover tests/datahub` -> attempted as optional broader check only; it entered broader long-running DataHub paths, emitted partial progress including an `E`, and did not produce a final summary during this handoff, so it was not used as the acceptance gate

## default network behavior
- Default tests remained offline-safe.
- No live flag was enabled.
- `QUANT_SYSTEM_LIVE_TESTS` was not set.
- No credentials, tokens, cookies, or live network access were introduced.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
- `SKIP`
- This handoff is local-only and explicitly forbids live tests.

## classification behavior after rework
- Clear request/signature/contract mismatches still classify as:
  - `failure_category=unsupported_request`
  - `availability_status=unsupported`
  - `request_or_configuration_like=true`
- Internal fetch-stage `TypeError` now classifies as:
  - `failure_category=fetch_failed`
  - `availability_status=degraded`
  - `request_or_configuration_like=false`
- Implementation detail:
  - `fetch_source_result()` now converts only direct `adapter.fetch(...)` call-signature `TypeError` failures into `SourceAdapterContractError`.
  - `_is_unsupported_request_error()` now treats raw `TypeError` as non-unsupported; unsupported classification comes from `SourceAdapterContractError` or other non-`TypeError` unsupported-request hints.
- Regression coverage now proves an internal `fetch()` `TypeError` with signature-like text (`"got an unexpected keyword argument 'symbols'"`) still remains `fetch_failed`.

## deviations
- No scope deviations.
- `quant/datahub/refresh.py` was allowed but did not require changes.
- The optional broader `discover` run did not yield a final result in this handoff and was not used for closure.

## risks/follow-up
- If `python3 -m unittest discover tests/datahub` is intended to be a reliable gate, its broader non-required paths need separate diagnosis because this attempt emitted partial error/progress output without a final usable summary.
