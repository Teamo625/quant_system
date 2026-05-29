# TASK-035 Review

## Decision

ACCEPTED.

The execution satisfies the TASK-035 handoff. The change remains inside the Phase 2 DataHub implementation scope, adds a bounded AKShare `DatasetName.FUND_PROFILE` adapter for one requested China public fund code, keeps default tests offline-safe, and provides a gated live smoke with live-enabled PASS evidence.

## Findings

No blocking findings.

## Scope Review

- Phase scope: PASS. Code changes are limited to `quant/datahub/**`, `tests/datahub/**`, and the required execution report.
- Forbidden files: PASS. No controller-owned project state files, review/integration files, or future-phase modules were modified by the execution change set.
- Adapter scope: PASS. `AkshareFundProfileAdapter` supports only `DatasetName.FUND_PROFILE`, requires exactly one fund code, fetches only the requested code, and does not introduce broad fund-universe ingestion or ETF-specific fallback.
- Source catalog scope: PASS. AKShare `FUND_PROFILE` coverage was added only to the existing `akshare_cn_hk_public_family` catalog entry and `ETF_FUND_FULL_DATA` stable dataset list, matching the handoff's minimal catalog-alignment allowance.

## Contract Review

- `SourceAdapter` compatibility is covered by deterministic offline tests.
- Required `FUND_PROFILE` fields are normalized to the existing schema: `fund_code`, `fund_name`, `market`, `fund_type`, `management_company`, `inception_date`, `currency`, `source`, `ingested_at`, and `schema_version`.
- Optional `benchmark` and `source_ts` are included only when present in source payloads.
- Canonical fund code output uses `*.FUND_CN`; source-native six-digit input is accepted.
- The adapter hard-fails on unsupported datasets, missing/multiple/malformed symbols, malformed payloads, missing required source fields, invalid required values, source-code mismatch, and conflicting duplicates.
- No placeholder fund profile values are synthesized to satisfy schema requiredness. `currency="CNY"` and `market="CN"` are consistent with this bounded China public-fund slice.

## Network and Live Review

- Default tests remain offline-safe. The live smoke in `tests/datahub/test_akshare_fund_profile_live.py` is gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- Offline tests use injected fetch callables and include socket-guard coverage for the main normalization path.
- The live smoke classifies network/source unavailability as `skipTest(...)` while preserving adapter/schema/normalization failures as hard failures.
- The execution report records live-enabled PASS for `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_profile_live.py`, including route and validation evidence.
- Independent review reran the live-enabled smoke successfully in the current environment.

## Tests Rerun by Review

- `python3 -m unittest tests/datahub/test_akshare_fund_profile_adapter.py`
  - PASS: 16 tests.
- `python3 -m unittest -v tests/datahub/test_akshare_fund_profile_live.py`
  - PASS: 3 tests, 1 default-gated live smoke skipped.
- `python3 -m unittest tests/datahub/test_source_catalog.py tests/datahub/test_datasets.py tests/datahub/test_source.py`
  - PASS: 53 tests.
- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
  - PASS: 580 tests, 23 skipped default-gated live tests.
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_profile_live.py`
  - PASS: 3 tests.
- `git diff --check -- quant/datahub tests/datahub coordination/reports/TASK-035_REPORT.md`
  - PASS: no whitespace errors.

## Residual Risks

- The adapter depends on the public AKShare `fund_individual_basic_info_xq` route and its observed vertical profile payload shape. Upstream route or field-shape changes may require future maintenance.
- ETF-like fund profile support remains intentionally out of scope and rejected by this adapter.

## Follow-Up Requirements

None for TASK-035 integration.
