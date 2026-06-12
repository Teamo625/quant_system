# TASK-144 Report

## files changed

- `quant/scanner/contracts.py`
- `quant/scanner/universe.py`
- `quant/scanner/runner.py`
- `quant/scanner/personal_readiness.py`
- `quant/scanner/__init__.py`
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_universe.py`
- `tests/scanner/test_runner.py`
- `tests/scanner/test_personal_readiness.py`

## implemented universe-family and exclusion-list capabilities

- Added first-class Scanner universe family support for `a_share`, `hong_kong_stock`, `etf_fund`, `sector`, `index`, and `custom_watchlist`.
- Added supported preset labels and strict family/preset-to-market validation for the hardened path.
- Added `UniverseExclusionInput` and `compose_universe_membership(...)` to trim caller-provided membership snapshots deterministically without mutating the original snapshot.
- Added symbol-level exclusion trace records with deterministic reason codes and details.

## implemented missing/stale feature and market-constraint capabilities

- Added `ScanConstraintPolicies` with explicit `missing_feature_policy` and `stale_feature_policy`.
- Added `FeatureValueSnapshot` with caller-provided `as_of_date` support for local stale checks only.
- Added `SymbolMarketState` for caller-provided suspension, limit-up, limit-down, and market-specific constraint flags.
- Added `run_scan_with_diagnostics(...)` to return candidate output plus symbol-level exclusion/ineligibility decisions while keeping `run_scan(...)` backward-compatible.
- Preserved default fail-fast behavior unless callers explicitly choose exclusion policies.

## readiness-gate updates

- Updated Scanner readiness so:
  - `universe_definition_and_validation` -> `pass`
  - `market_constraints_and_missing_data_handling` -> `pass`
  - `offline_scan_workflow_regression_coverage` remains `warn` because ranking regressions are still pending
- Updated follow-up truth by removing completed `SCN-UNI-001`, `SCN-UNI-002`, `SCN-CONSTRAINT-001`, and `SCN-CONSTRAINT-002`.
- Next recommended batch is now `scanner_ranking_workflow_batch_01`.

## tests run

- `python3 -m unittest tests.scanner.test_universe`
  - `PASS` (`Ran 9 tests`)
- `python3 -m unittest tests.scanner.test_matching`
  - `PASS` (`Ran 6 tests`)
- `python3 -m unittest tests.scanner.test_runner`
  - `PASS` (`Ran 12 tests`)
- `python3 -m unittest tests.scanner.test_personal_readiness`
  - `PASS` (`Ran 4 tests`)
- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`
  - `PASS` (`Ran 44 tests`)

## default network behavior

- Offline-safe only.
- No live calls, source adapters, DataHub reads, FeatureHub reads, warehouse reads, credentials, or hidden network behavior were added.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks

- `SKIP`
- TASK-144 is local Scanner hardening only.
- The handoff forbids live tests, and this execution added no live-capable code path.

## deviations

- None.

## risks/follow-up

- Ranking/scoring, tie-break ordering, and ranking workflow regressions remain open and should move to `scanner_ranking_workflow_batch_01`.
- Candidate artifact provenance and downstream handoff metadata remain intentionally isolated in `scanner_artifact_contract_repair_batch_01`.
- Current universe family support is validation/composition only; it does not fetch members from DataHub and stays within the current offline Scanner phase boundary.
