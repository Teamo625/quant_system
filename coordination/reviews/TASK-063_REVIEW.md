# TASK-063 Review

## Findings

- `quant/features/storage.py:104` writes the JSONL output before it validates whether `manifest_path` is writable. If `manifest_path` already exists and `overwrite=False`, `write_feature_records_jsonl(...)` raises `FileExistsError` only after the records file has already been replaced at `quant/features/storage.py:117-135`. I reproduced this locally: the call failed on the manifest path while leaving a newly written JSONL file behind. That violates the expected clear/consistent file-exists behavior for this helper and makes the optional manifest path a partial-write footgun.
- `tests/features/test_storage.py` does not cover the combined `write_feature_records_jsonl(..., manifest_path=...)` conflict path, so this regression is currently undetected by the added offline suite.
- No phase-scope violation was found. The changes stay inside allowed FeatureHub paths, and the independently rerun default suites stayed offline-safe.

## Decision

REWORK REQUIRED.

## Closure Readiness

- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required from live result: NO; TASK-063 is offline-only and the handoff forbids live tests.
- Phase/scope/contract/test blockers: YES; the persistence helper has a blocking partial-write behavior when `manifest_path` already exists, and there is no test covering that path.

## Required Follow-up

- Preflight both output targets before any write in `write_feature_records_jsonl(...)`, or otherwise make the combined records-plus-manifest write path deterministic and non-partial when `overwrite=False`.
- Add a focused offline test covering `manifest_path` already existing during `write_feature_records_jsonl(...)`.
- Re-run:
  - `python3 -m unittest discover -s tests/features -p 'test_*.py'`
  - `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
