# TASK-049 Execution Report

## Task
- Task ID: `TASK-049`
- Handoff: `coordination/handoffs/TASK-049_DATAHUB_AKSHARE_A_SHARE_MAJOR_ACTIVITY_EVENTS_ADAPTER.md`
- Role: 5.3 Execution

## Summary
Implemented a narrow AKShare A-share major activity events adapter slice for `DatasetName.MAJOR_ACTIVITY_EVENTS` using public route `stock_dzjy_mrmx` with bounded single-trade-date requests, deterministic normalization, symbol filtering/validation, sorting, deduplication, and gated live smoke coverage.

## Files Changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_adapter.py` (new)
- `tests/datahub/test_akshare_a_share_major_activity_events_live.py` (new)
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## Implementation Details
- Added `AkshareAShareMajorActivityEventsAdapter` under source family `akshare_cn_hk_public_family`.
- Supported dataset: `DatasetName.MAJOR_ACTIVITY_EVENTS` only.
- Bounded request rules:
  - requires both `start_date` and `end_date`
  - requires `start_date == end_date` (single trade date)
  - rejects unbounded and multi-day ranges.
- Route handling:
  - selected bounded public AKShare route `stock_dzjy_mrmx`
  - callable-argument inspection and strict required-arg compatibility checks
  - route signature incompatibility remains hard failure.
- Symbol handling:
  - accepts canonical/prefixed/bare A-share symbols (`600000.SH`, `SH600000`, `600000`, etc.)
  - rejects HK/ETF/index/malformed symbols when symbol filter is requested
  - normalizes output to canonical exchange-qualified symbols.
- Normalization:
  - sets `market=A_SHARE`, `source=akshare_cn_hk_public_family`
  - sets `schema_version` from `DatasetRegistry`
  - sets `ingested_at` from injectable clock
  - supports DataFrame-like and list-of-mapping payloads
  - maps route rows to truthful `MAJOR_ACTIVITY_EVENTS` fields (`event_type=block_trade`)
  - deterministic sort key: `event_date`, `symbol`, `event_type`, `event_id`
  - deterministic dedup on generated stable `event_id`, with conflict detection.
- Error boundaries:
  - malformed payload/missing required fields/date/numeric/symbol errors fail clearly
  - live/source-unavailable classifier includes network/proxy/DNS/TLS/upstream tokens and AKShare route-shape empty/JSON/`NoneType`-subscriptable failures.

## Source-Capability/Catalog Truth Updates
- `a_share_major_activity_events` updated from `PLANNED` to `PARTIAL` in `source_capabilities.py`.
- `source_family_ids` updated to include public AKShare + Tushare family.
- `source_catalog.py` updated to include `DatasetName.MAJOR_ACTIVITY_EVENTS` under AKShare dataset coverage and A-share full-data stable datasets.

## Tests Run
1. `python3 -m unittest tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- PASS (`Ran 15 tests ... OK`)

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- PASS with default live gating (`Ran 4 tests ... OK (skipped=1)`)

3. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- PASS (`Ran 10 tests ... OK`)

4. `python3 -m unittest tests/datahub/test_source.py`
- PASS (`Ran 20 tests ... OK`)

5. `python3 -m unittest tests/datahub/test_datasets.py`
- PASS (`Ran 31 tests ... OK`)

6. `python3 -m unittest tests/datahub/test_source_capabilities.py`
- PASS (`Ran 13 tests ... OK`)

7. `python3 -m unittest tests/datahub/test_source_catalog.py`
- PASS (`Ran 6 tests ... OK`)

8. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- PASS (`Ran 756 tests ... OK (skipped=33)`)

9. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- PASS with live smoke SKIP (`Ran 4 tests ... OK (skipped=1)`)

## Default Network Behavior
- Default test mode remains offline-safe.
- New adapter offline tests use injected fixtures/functions and do not require live network.
- Live test remains explicitly environment-gated via `QUANT_SYSTEM_LIVE_TESTS=1`.

## Live-Enabled Result (Mandatory)
- Status: `SKIP` (environment/source unavailable)
- Evidence:
  - live run encountered AKShare upstream route-shape failure:
  - `RuntimeError: AKShare A-share major-activity route unavailable: stock_dzjy_mrmx(start_date=20260531, end_date=20260531) -> TypeError: 'NoneType' object is not subscriptable`
  - root cause chain points to AKShare route internals (`stock_dzjy_mrmx` JSON path resolving to `None` payload branch).

## Feasible Fix Attempted in Repository
- Implemented/strengthened unavailable-classification for this adapter so AKShare route-shape upstream unavailability (`empty_payload`, JSON decode, `NoneType` subscriptable) is classified as live-source unavailable and reported as gated SKIP rather than masking as contract success.
- Kept adapter/schema/argument compatibility errors as hard failures (validated by tests).

## Deviations from Handoff
- None in scope/files/tests.
- Note: live-enabled result is `SKIP` (not `PASS`) due upstream/source availability behavior for the queried route/date.

## Risks / Follow-up
- Controller should treat this as live-unavailable evidence, not closure-by-live-pass.
- Per `AGENTS.md` live-network rule, closure requires controller review of SKIP evidence and, if deemed necessary, a rework/review/integration cycle for further feasible mitigations (e.g., bounded fallback strategy or additional route slice) before closure.

---

## Rework Cycle: TASK-049 Live Route Rework (current execution)

### Handoff
- `coordination/handoffs/TASK-049_DATAHUB_AKSHARE_A_SHARE_MAJOR_ACTIVITY_EVENTS_LIVE_ROUTE_REWORK.md`

### Files Changed (this rework only)
- `tests/datahub/test_akshare_a_share_major_activity_events_live.py`

### Root-Cause Diagnosis Evidence
- Baseline reproduction before edits:
  - Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`
  - Result: `SKIP`
  - Evidence: `RuntimeError: AKShare A-share major-activity route unavailable: stock_dzjy_mrmx(start_date=20260531, end_date=20260531) -> TypeError: 'NoneType' object is not subscriptable`
- Route/date probe evidence (local AKShare live probing):
  - `stock_dzjy_mrmx` and `stock_dzjy_mrtj` failed on non-trading/unsupported dates such as `20260531` and `20260530` with the same `NoneType`-subscriptable upstream shape.
  - The same route succeeded for recent valid trade dates (for example `20260529`, `20260528`, `20260527`) and returned non-empty rows.
- Conclusion:
  - Primary blocker was live smoke date-selection behavior (first attempted date unavailable) and test control flow (immediate `skipTest` on first unavailable date), not adapter contract logic.

### Repository-Level Fix Applied
- Reworked live smoke to probe a bounded recent window (`1..30` days back) and continue past environment/source-unavailable dates instead of skipping on the first unavailable date.
- Preserved hard-fail boundaries:
  - schema/normalization/contract errors still fail
  - AKShare route argument/signature compatibility errors still fail
  - only true environment/source-unavailable cases are treated as skip candidates
- Added deterministic unit tests for the new probing behavior:
  - continue after unavailable date and succeed later
  - return last unavailable error when all attempts are unavailable
  - keep non-unavailable errors as hard failures

### Tests Run (this rework execution)
1. `python3 -m unittest tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- PASS (`Ran 15 tests ... OK`)

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- PASS with default live gate (`Ran 7 tests ... OK (skipped=1)`)

3. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- PASS (`Ran 10 tests ... OK`)

4. `python3 -m unittest tests/datahub/test_source.py`
- PASS (`Ran 20 tests ... OK`)

5. `python3 -m unittest tests/datahub/test_datasets.py`
- PASS (`Ran 31 tests ... OK`)

6. `python3 -m unittest tests/datahub/test_source_capabilities.py`
- PASS (`Ran 13 tests ... OK`)

7. `python3 -m unittest tests/datahub/test_source_catalog.py`
- PASS (`Ran 6 tests ... OK`)

8. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- PASS (`Ran 759 tests ... OK (skipped=33)`)

9. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- PASS (`Ran 7 tests ... OK`)

### Default Network Behavior
- Default mode remains offline-safe.
- Live network remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.

### Live-Enabled PASS/SKIP/FAIL Truth
- Status after rework: `PASS`
- Evidence:
  - Live smoke passed after bounded recent-date probing located a usable trade date and validated source-fact output through `DatasetRegistry.validate_record(...)`.

### Deviations from Handoff
- None.

### Residual Risks / Operator Action
- Public AKShare route behavior can still vary by day/upstream availability.
- If all bounded recent dates are unavailable in a future environment run, test will truthfully `SKIP` with the last unavailable root-cause error.
