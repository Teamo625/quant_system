# TASK-026 Execution Report (DataHub AKShare A-share Instrument Master Adapter)

## Task

- Task ID: `TASK-026`
- Active Handoff: `coordination/handoffs/TASK-026_DATAHUB_AKSHARE_A_SHARE_INSTRUMENT_MASTER_ADAPTER.md`
- Dataset Scope: `DatasetName.INSTRUMENT_MASTER` (A-share active instrument master slice)
- Module Scope: DataHub only

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_a_share_instrument_master_adapter.py`
- `tests/datahub/test_akshare_a_share_instrument_master_live.py`
- `coordination/reports/TASK-026_REPORT.md`

## Implementation Summary

Implemented `AkshareAShareInstrumentMasterAdapter` under source `akshare_cn_hk_public_family` with narrow `INSTRUMENT_MASTER` support only.

1. Added bounded AKShare route coverage (explicit order):
   - `stock_info_sh_name_code("主板A股")`
   - `stock_info_sh_name_code("科创板")`
   - `stock_info_sz_name_code("A股列表")`
   - `stock_info_bj_name_code()`

2. Added strict normalization to contract fields:
   - `symbol`, `raw_symbol`, `name`, `market`, `asset_type`, `currency`, `exchange`
   - `list_date`, `delist_date`, `is_active`
   - `source`, optional `source_ts`, `ingested_at`, `schema_version`
   - fixed values: `market=CN`, `asset_type=stock`, `currency=CNY`, `source=akshare_cn_hk_public_family`
   - active-route defaults: `delist_date=9999-12-31`, `is_active=True`
   - canonical symbol form: `XXXXXX.SH|SZ|BJ`

3. Added bounded validation/normalization behavior:
   - supports DataFrame-like payload and list-of-mapping payload
   - rejects unsupported dataset
   - rejects malformed payload shape, non-mapping rows, missing required fields, invalid required strings
   - rejects invalid code values/prefixes by route boundary
   - rejects invalid list-date/source-ts formats
   - supports optional `symbols` filter after normalization
   - accepts canonical, raw 6-digit, and prefixed (`SH600000`/`SZ000001`/`BJ920000`) forms
   - rejects invalid symbol filter format, type, and invalid market-code combinations

4. Added duplicate boundary handling:
   - benign canonical duplicates are deduplicated deterministically
   - preferred duplicate chooses newer `source_ts` when available
   - conflicting duplicates for same canonical `symbol` hard-fail

5. Added route network-unavailable classification for live diagnostics:
   - network/proxy/DNS/TLS/upstream/source-availability errors are wrapped as route-unavailable runtime errors for explicit live-skip handling
   - contract/normalization errors remain hard failures

6. Exported adapter via:
   - `quant.datahub.adapters.__init__`
   - `quant.datahub.__init__`

## Tests Added or Changed

- Added `tests/datahub/test_akshare_a_share_instrument_master_adapter.py` (offline deterministic):
  - SourceAdapter protocol compatibility
  - `fetch_source_result(...)` normalization + `DatasetRegistry.validate_record(...)`
  - DataFrame-like + list payload conversion
  - SH/SZ/BJ canonical symbol & exchange normalization
  - symbol filter support and invalid-filter rejection
  - required-field/list-date/code/source-ts validation boundaries
  - delist-date and active defaults
  - duplicate dedupe/conflict boundaries
  - malformed payload boundaries
  - route network-classification behavior boundaries

- Added `tests/datahub/test_akshare_a_share_instrument_master_live.py`:
  - default skip gate via `QUANT_SYSTEM_LIVE_TESTS`
  - live smoke fetch + schema validation for `INSTRUMENT_MASTER`
  - environment/source unavailability classified to `skipTest(...)`
  - adapter/schema issues preserved as failures

## Tests Run

1. `python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_adapter.py`
   - Result: PASS (`Ran 21 tests`)

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_master_live.py`
   - Result: PASS (`Ran 3 tests`, `OK (skipped=1)`)

3. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
   - Result: PASS (`Ran 10 tests`)

4. `python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`
   - Result: PASS (`Ran 11 tests`)

5. `python3 -m unittest tests/datahub/test_source.py`
   - Result: PASS (`Ran 20 tests`)

6. `python3 -m unittest tests/datahub/test_quality.py`
   - Result: PASS (`Ran 7 tests`)

7. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - Result: PASS (`Ran 368 tests`, `OK (skipped=14)`)

8. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_master_live.py`
   - Result: PASS (`Ran 3 tests in 6.718s`, `OK`)

## Default Network Behavior

- Default test runs remain offline-safe.
- New offline adapter tests use injected fixtures/functions only and do not require network.
- Live smoke test is explicitly gated and skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`.

## Live-Enabled Result (Mandatory)

- Live-enabled status: `PASS`
- Evidence:
  - command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_master_live.py`
  - output tail: `Ran 3 tests in 6.718s`, `OK`

## Deviations From Handoff

- None.

## Risks / Follow-Up

1. Upstream AKShare route payload columns or endpoint behavior may change; if field names drift, adapter field-picking keys and tests should be updated together.
2. Route availability is environment-sensitive (proxy/DNS/TLS/upstream); live smoke is currently correctly gated and classified, but operator environment quality still affects live signal cadence.
3. Symbol filter now enforces market-code consistency for canonical/prefixed forms; if future requirements include looser fuzzy matching, that should be introduced explicitly with contract tests.
