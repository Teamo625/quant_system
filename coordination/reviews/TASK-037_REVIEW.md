# TASK-037 Review

## Task
- Task ID: `TASK-037`
- Handoff: `coordination/handoffs/TASK-037_DATAHUB_HKEX_HK_TRADING_CALENDAR_ADAPTER.md`
- Review Role: Review Agent

## Scope Checked
- `quant/datahub/adapters/hkex.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_hkex_hk_trading_calendar_adapter.py`
- `tests/datahub/test_hkex_hk_trading_calendar_live.py`
- `coordination/reports/TASK-037_REPORT.md`

## Workspace Baseline Note
- The worktree was dirty before TASK-037 execution (per provided baseline evidence).
- Controller-owned file diffs (`coordination/PROJECT_STATE.md`, `coordination/ROADMAP.md`, `coordination/TASK_BOARD.md`, `coordination/CONTEXT_SNAPSHOT.md`) and TASK-036 catalog diffs were already present in baseline context and are not treated as TASK-037 execution-scope violations in this review.

## Findings (ordered by severity)
- No blocking findings.
- No phase-boundary violation found for TASK-037 implementation scope (DataHub + tests only).
- No hidden default-path live network call found; live smoke remains env-gated and default-skipped.

## Requirement-by-Requirement Verification
- HKEX adapter exists and is narrow to `DatasetName.TRADING_CALENDAR`:
  - `HkexHKTradingCalendarAdapter` implemented in `quant/datahub/adapters/hkex.py`.
  - Exported via `quant/datahub/adapters/__init__.py` and `quant/datahub/__init__.py`.
- Contract behavior checks:
  - rejects unsupported dataset with explicit `ValueError`.
  - rejects non-`None` `symbols` with explicit `ValueError`.
  - validates date range and malformed payload/date/session/source_ts errors with explicit failures.
  - sets `market="HK"` and `source="hkex_disclosure_and_calendar_family"`.
  - stamps `schema_version` from `DatasetRegistry`.
  - stamps deterministic `ingested_at` via injectable `now_fn`.
  - supports ICS string, DataFrame-like (`to_dict(orient="records")`), list-of-mapping, and list-of-date-like payloads.
  - sorts by `trade_date`, deduplicates duplicate dates, and derives `previous_trade_date`/`next_trade_date` deterministically.
- Offline deterministic coverage exists in `tests/datahub/test_hkex_hk_trading_calendar_adapter.py`:
  - protocol compatibility
  - dataset contract validation via `DatasetRegistry.validate_record(...)`
  - payload-shape coverage and error-boundary coverage
  - filtering/sorting/dedup/linkage coverage
- Mandatory live smoke exists in `tests/datahub/test_hkex_hk_trading_calendar_live.py`:
  - default skipped unless `QUANT_SYSTEM_LIVE_TESTS=1`
  - verifies at least one record (or explicit skip when environment/source unavailable)
  - validates schema and asserts source/market fields
  - distinguishes environment/network availability from contract failures

## Report Compliance Check
- Execution report exists at `coordination/reports/TASK-037_REPORT.md`.
- Report includes required sections: files changed, tests run, default network behavior, live-enabled result, deviations, and risks/follow-up.
- Mandatory live-enabled result is recorded as PASS and is reproducible in reviewer run.

## Validation Runs (Reviewer)
- `python3 -m unittest tests/datahub/test_hkex_hk_trading_calendar_adapter.py`
  - PASS (`Ran 15 tests`)
- `python3 -m unittest -v tests/datahub/test_hkex_hk_trading_calendar_live.py`
  - PASS (`Ran 3 tests`, `skipped=1` default gate)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_hkex_hk_trading_calendar_live.py`
  - PASS (`Ran 3 tests`)
- `python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py tests/datahub/test_hkex_company_announcements_adapter.py tests/datahub/test_source.py`
  - PASS (`Ran 50 tests`)
- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
  - PASS (`Ran 598 tests`, `skipped=24`)

## Decision
- PASS (Accepted for integration)

## Follow-up Requirements
- Integration Agent may proceed with TASK-037 integration.
- Residual non-blocking risk: half-day classification relies on HKEX ICS summary token matching; if HKEX wording changes, session typing may degrade to `full` while schema validation still passes.
