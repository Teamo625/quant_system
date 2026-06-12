# TASK-145 Report

## files changed

- `quant/scanner/__init__.py`
- `quant/scanner/contracts.py`
- `quant/scanner/personal_readiness.py`
- `quant/scanner/runner.py`
- `quant/scanner/storage.py`
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_personal_readiness.py`
- `tests/scanner/test_runner.py`
- `tests/scanner/test_storage.py`

## ranking/scoring and ordering semantics

- Added explicit ranking contracts: `RankingDirection`, `RankingCriterion`, `ScanRankingConfig`, plus validation for malformed config, unsupported directions, duplicate criteria, and invalid weights.
- Extended `ScanCandidateRecord` with optional `score` / `rank` fields while preserving unranked default behavior.
- `run_scan(...)` and `run_scan_with_diagnostics(...)` now accept optional `ranking=...` and keep the previous filter-only `(symbol, market)` ordering when ranking is omitted.
- Ranked scans compute direction-aware weighted scores over caller-provided feature values only, require finite numeric ranking values, emit deterministic 1-based ranks, and break ties by configured criterion values then `(symbol, market)`.
- Missing/stale ranking features reuse existing missing/stale policy handling, so invalid ranking data does not silently promote candidates.

## workflow regression coverage

- Added contract tests for ranking-config validation and ranked candidate ordering invariants.
- Added runner regressions for:
  - descending ranking and stable symbol tie-breaks
  - ascending ranking behavior
  - missing ranking feature under exclusion policy
  - invalid ranking config
  - invalid non-numeric ranking values
- Added storage regression proving ranked candidate rows serialize `score` / `rank` safely.

## readiness updates

- Updated `quant/scanner/personal_readiness.py` so:
  - `scanner_ranking_workflow_batch_01` work is reflected as complete
  - `SCN-RANK-001` and `SCN-TEST-001` are removed from the remaining follow-up queue
  - `ranking_scoring_and_candidate_ordering` and `offline_scan_workflow_regression_coverage` now report `pass`
  - the next recommended handoff is `scanner_artifact_contract_repair_batch_01`
- Phase 4-P closure remains `false`; `candidate_persistence_and_handoff_readiness` stays conservative and pending.

## tests run

- `python3 -m unittest tests.scanner.test_contracts` -> `PASS` (`Ran 10 tests`)
- `python3 -m unittest tests.scanner.test_matching` -> `PASS` (`Ran 6 tests`)
- `python3 -m unittest tests.scanner.test_runner` -> `PASS` (`Ran 18 tests`)
- `python3 -m unittest tests.scanner.test_personal_readiness` -> `PASS` (`Ran 4 tests`)
- `python3 -m unittest tests.scanner.test_storage` -> `PASS` (`Ran 7 tests`)
- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'` -> `PASS` (`Ran 55 tests`)

## default network behavior

- Offline-safe only.
- No live calls, source adapters, DataHub reads, FeatureHub reads, warehouse reads, credentials, or hidden network behavior were added.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks

- `SKIP`
- This is local Scanner work only, and the handoff forbids live tests.

## deviations

- None.

## risks/follow-up

- Ranked candidate rows now carry `score` / `rank`, but persisted artifacts still do not record universe snapshot provenance, ranking-config reproducibility metadata, or downstream handoff metadata.
- The next focused batch should remain `scanner_artifact_contract_repair_batch_01` / `SCN-ART-001`.
