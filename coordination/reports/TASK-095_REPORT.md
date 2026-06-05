# TASK-095 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_live.py`
- `coordination/reports/TASK-095_REPORT.md`

## review findings addressed
- Fixed the reviewed duplicate case: when Eastmoney primary and Baidu supplemental rows describe the same logical resumption, the adapter now keeps one normalized `resumption` event.
- Added offline regression coverage for primary-plus-supplemental overlap.
- Strengthened live smoke so a runtime Baidu exact-resumption sample must map to exactly one normalized `resumption` record.

## duplicate identity used
- Resumption overlap suppression key: `symbol + start_date + resume_date`.
- Implementation behavior: if a primary Eastmoney row already normalized to `event_type="resumption"` for that logical key, the Baidu supplemental `resumption` record is suppressed.
- Rationale: this fixes the reviewed duplicate case while keeping source truth conservative and primary-route precedence explicit.

## offline regression evidence
- Added `test_overlapping_primary_and_supplemental_resumption_rows_deduplicate_to_one_event`.
- Fixture: one Eastmoney row and one Baidu row both describe `000001.SZ` with `start_date=2026-05-29` and `resume_date=2026-05-30`.
- Result: adapter returns exactly one normalized `resumption` record, keeps the primary row, and the record still validates against `DatasetName.SUSPENSION_RESUMPTION_EVENTS`.

## tests run
- `python3 -m unittest tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py` -> PASS (`Ran 16 tests`)
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 34 tests`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py` -> PASS with live test `SKIP` by default (`Ran 4 tests`, `skipped=1`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py` -> PASS (`Ran 4 tests in 3.261s`)

## default network behavior
- Default tests remain offline-safe.
- No hidden network calls were added to default adapter or capability tests.
- The live test file still requires explicit `QUANT_SYSTEM_LIVE_TESTS=1`; without it, the live smoke skips.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py`
- Evidence:
  - test runner output: `Ran 4 tests in 3.261s` and `OK`
  - read-only post-run probe found `first_success=('2026-06-04', 15)`
  - the same 30-day window also found a Baidu exact-resumption sample on `2026-06-02`: `first_baidu=('2026-06-02', 27, 4, (('000736.SZ', '2026-06-02', '2026-06-03'), ('002200.SZ', '2026-06-02', '2026-06-03'), ('000668.SZ', '2026-06-02', '2026-06-03'), ('300175.SZ', '2026-06-02', '2026-06-03')))`

## live smoke assertion added
- The live smoke now scans the same 30-day bounded window for a sample date that includes Baidu rows with exact `复牌时间`.
- When such a sample exists, every Baidu logical resumption key found on that date must correspond to exactly one normalized `resumption` record in adapter output.
- In this execution, that stronger assertion path was exercised on the `2026-06-02` sample above.

## capability truth changes
- None.
- `a_share_suspension_resumption` remains conservative and unchanged in metadata.

## deviations
- None from the allowed write scope or test policy.

## risks/follow-up
- The overlap suppression is intentionally narrow to reviewed resumption duplicates; it does not broaden capability claims.
- Live overlap proof still depends on whatever public sample appears in the bounded window; if future public data stops exposing Baidu exact-resumption rows in that window, the test falls back to basic smoke instead of inventing unstable assumptions.
