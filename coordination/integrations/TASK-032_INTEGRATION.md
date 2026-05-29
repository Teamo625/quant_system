# TASK-032 Integration

## Task
- `TASK-032_DATAHUB_AKSHARE_HK_INSTRUMENT_MASTER_ADAPTER`

## Inputs Read
- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-032_DATAHUB_AKSHARE_HK_INSTRUMENT_MASTER_ADAPTER.md`
- `coordination/reports/TASK-032_REPORT.md`
- `coordination/reviews/TASK-032_REVIEW.md`
- current worktree changes

## Review Decision
- Review result: ACCEPTED
- Blocking findings: none
- Follow-up requirements: none blocking for integration

## Integration Result
- Integrated accepted TASK-032 work by recording this integration pass.
- The reviewed implementation is present in the worktree and remains within the DataHub phase boundary.
- No architectural direction change was made by integration.
- No controller-owned project state files were edited by this Integration Agent.

## Files Touched By TASK-032 Implementation
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_akshare_hk_instrument_master_live.py`
- `coordination/reports/TASK-032_REPORT.md`
- `coordination/reviews/TASK-032_REVIEW.md`
- `coordination/integrations/TASK-032_INTEGRATION.md`

## Integrated Behavior Summary
- Added `AkshareHKInstrumentMasterAdapter` for `DatasetName.INSTRUMENT_MASTER` under source id `akshare_cn_hk_public_family`.
- Scope is limited to a one-symbol Hong Kong stock profile fetch using the bounded AKShare route `stock_hk_security_profile_em(symbol=<single_code>)`.
- Accepts canonical HK symbols such as `00700.HK` and source-native numeric symbols such as `00700`.
- Normalizes records to the existing `INSTRUMENT_MASTER` contract with `market=HK`, `asset_type=stock`, `currency=HKD`, `exchange=HKEX`, source id `akshare_cn_hk_public_family`, registry schema version, deterministic `ingested_at`, source-truth `list_date`, and default active current-security fields where source delisting data is absent.
- Includes deterministic offline coverage for payload shapes, symbol validation, required fields, date parsing, duplicate boundaries, malformed payloads, non-stock rejection, default delist date, optional `source_ts`, and source-result validation.
- Includes mandatory gated live smoke coverage, skipped by default and enabled only by `QUANT_SYSTEM_LIVE_TESTS=1`.

## Verification Performed During Integration
- `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`
  - PASS, 20 tests
- `python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`
  - PASS, 3 tests, 1 live smoke skipped by default
- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
  - PASS, 513 tests, 20 skipped

## Live Smoke Evidence From Report And Review
- Execution report records:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`
  - PASS, 3 tests, live smoke PASS
- Review independently reran the enabled live smoke and recorded PASS.
- No live-network rework gate is required for TASK-032 because the accepted review records live-enabled PASS.

## Conflicts Or Gaps
- No TASK-032 integration conflicts found.
- No blocking gaps remain for TASK-032.
- Workspace note: the worktree contains pre-existing modified controller-owned coordination files and TASK-031 coordination/test files. They were not modified by this Integration Agent and are outside this TASK-032 integration action.

## State Update Recommendations For Controller
- Mark `TASK-032` as Done / integrated in `coordination/TASK_BOARD.md`.
- Add `TASK-032` to completed Phase 2 work in `coordination/PROJECT_STATE.md` and `coordination/CONTEXT_SNAPSHOT.md`.
- Keep Phase 2 open unless `coordination/PHASE_GATE.md` indicates all required Phase 2 coverage is complete.
- If Phase 2 remains open, dispatch the next executable DataHub source-coverage task according to `coordination/PHASE_GATE.md` and the roadmap.
- Record that TASK-032 had default offline PASS and live-enabled PASS evidence for the HK instrument master one-symbol adapter.
