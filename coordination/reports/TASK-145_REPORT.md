# TASK-145 Report

## files changed

- `quant/scanner/runner.py`
- `tests/scanner/test_runner.py`
- `coordination/reports/TASK-145_REPORT.md`

## ranking normalization behavior

- Chosen behavior: accept mixed mapping-plus-dataclass ranking payloads.
- `_normalize_ranking_config(...)` now normalizes each `criteria` item through the same dataclass-or-mapping path before reading `feature_ref`, `direction`, and `weight`.
- `run_scan(..., ranking={"criteria": (RankingCriterion(...),)})` no longer escapes a raw `TypeError`; it normalizes into `ScanRankingConfig` and preserves existing ranking score/order semantics.
- Malformed mapping criteria still go through `validate_scan_ranking_config(...)` and raise `InvalidScanRankingConfigError` rather than uncontrolled exceptions.

## regression coverage added

- Added a default offline runner regression for mixed mapping-plus-dataclass input:
  `ranking={"criteria": (RankingCriterion(...),)}`
- The regression proves the reviewed defect path now produces a ranked candidate list with deterministic ordering and ranks instead of a raw `TypeError`.

## tests run

- `python3 -m unittest tests.scanner.test_runner` -> `PASS` (`Ran 19 tests`)
- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'` -> `PASS` (`Ran 56 tests`)

## default network behavior

- Offline-safe only.
- No live calls, source adapters, DataHub reads, FeatureHub reads, warehouse reads, credentials, or hidden network behavior were added.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks

- `SKIP`
- This is local Scanner work only, and the handoff forbids live tests.

## deviations

- None.

## risks/follow-up

- This rework is intentionally narrow and does not address the separate pending Scanner artifact contract/provenance batch.
- Review should confirm mixed ranking payload normalization is now covered and that invalid mapping criteria still fail in a controlled way.
