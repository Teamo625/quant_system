# TASK-090 Report

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_sector_membership_adapter.py`
  - `tests/datahub/test_akshare_sector_membership_live.py`
  - `tests/datahub/test_source_capabilities.py`

- tests run:
  - `python3 -m unittest tests/datahub/test_akshare_sector_membership_adapter.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py` -> PASS (`skipped=1` for live smoke; classifier tests passed)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py` -> PASS

- default network behavior:
  - Default offline-safe behavior is preserved: the live smoke is `skipUnless(QUANT_SYSTEM_LIVE_TESTS=1)`.
  - Local shell state had `QUANT_SYSTEM_LIVE_TESTS=1` preset, so I explicitly used `env -u QUANT_SYSTEM_LIVE_TESTS` to verify the default skipped path without network access.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence:
  - PASS
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py` completed `Ran 3 tests in 25.032s` and `OK`.
  - The live smoke validated a bounded multi-sector batch path with one industry identifier and one concept identifier. The adapter returned normalized `SECTOR_MEMBERSHIP` records whose `sector_id` set matched the requested batch.

- capability truth change:
  - `sector_membership`: remains `partial`
  - `sector_historical_changes`: remains `partial`
  - Change made: gap text was refined to reflect proven bounded multi-sector membership batches and preserved dated fields, while keeping history/classification-version limits conservative.

- source route coverage and known limitations:
  - Proven public coverage in this task: caller-provided bounded batch access for typed `INDUSTRY:*` and `CONCEPT:*` sector membership requests through AKShare-backed routes.
  - Identifier handling now rejects blank, duplicate-normalized, unsupported-prefix, untyped, stock-like, ETF/fund-like, and Hong Kong stock-like inputs before any batch records are returned.
  - Records are normalized to `DatasetName.SECTOR_MEMBERSHIP`, validated through `DatasetRegistry`, deduped by `(sector_id, symbol, in_date, out_date)` identity, checked for conflicting overlapping history windows, and sorted deterministically by `sector_id`, `in_date`, `symbol`.
  - When upstream rows do not expose dated membership fields, the adapter still uses the existing conservative fallback `in_date=1900-01-01`.
  - This task does not prove full sector taxonomy history, explicit change-event timelines, or classification-version metadata completeness.

- deviations:
  - No scope deviations.
  - `quant/datahub/source_catalog.py`, `tests/datahub/test_source_catalog.py`, and `quant/datahub/adapters/__init__.py` were left unchanged because the existing catalog/export truth did not require adjustment for this bounded hardening.

- risks/follow-up:
  - Public AKShare/THS sector membership still does not establish a complete reclassification event timeline; future work is still needed if the controller wants explicit historical change events instead of bounded membership snapshots with optional dates.
  - Sector classification-version metadata remains incomplete and should not be inferred from this task’s PASS.
  - The environment-level preset `QUANT_SYSTEM_LIVE_TESTS=1` can make the plain default live-test command execute network smoke locally; operators should unset it when they specifically want to validate the repository’s default skip path.
