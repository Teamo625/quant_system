# TASK-035 Integration

## Task
- `TASK-035_DATAHUB_AKSHARE_FUND_PROFILE_ADAPTER`

## Inputs Read
- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-035_DATAHUB_AKSHARE_FUND_PROFILE_ADAPTER.md`
- `coordination/reports/TASK-035_REPORT.md`
- `coordination/reviews/TASK-035_REVIEW.md`
- current worktree changes

## Review Decision
- Review result: ACCEPTED
- Blocking findings: none
- Follow-up requirements: none for TASK-035 integration

## Integration Result
- Integrated accepted TASK-035 work by recording this integration pass.
- The reviewed implementation is present in the worktree and remains within the DataHub phase boundary.
- The source catalog alignment made by execution is minimal and matches the TASK-035 handoff and accepted review.
- No architectural direction change was made by integration.
- No controller-owned project state files were edited by this Integration Agent.

## Files Touched By TASK-035 Implementation
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_fund_profile_adapter.py`
- `tests/datahub/test_akshare_fund_profile_live.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-035_REPORT.md`
- `coordination/reviews/TASK-035_REVIEW.md`
- `coordination/integrations/TASK-035_INTEGRATION.md`

## Integrated Behavior Summary
- Added `AkshareFundProfileAdapter` for `DatasetName.FUND_PROFILE` under source id `akshare_cn_hk_public_family`.
- Scope is limited to one requested China public fund profile record.
- Accepts canonical fund symbols such as `000001.FUND_CN` and source-native six-digit symbols such as `000001`, then normalizes output to canonical `*.FUND_CN` form.
- Uses the bounded no-credential AKShare `fund_individual_basic_info_xq` route when live.
- Rejects missing, multiple, empty, malformed, unsupported market, A-share stock-like, index-like, and ETF-like symbols for this bounded public-fund profile slice.
- Normalizes records to the existing `FUND_PROFILE` contract with `fund_code`, `fund_name`, `market=CN`, `fund_type`, `management_company`, `inception_date`, `currency=CNY`, optional source-provided `benchmark`, optional source-provided `source_ts`, source id, deterministic `ingested_at`, and registry schema version.
- Does not fabricate placeholder fund names, companies, fund types, dates, or optional profile values.
- Supports DataFrame-like payloads, horizontal list-of-mapping payloads, and observed vertical `item`/`value` profile payloads.
- Preserves duplicate boundaries: benign exact duplicates are deduplicated, while conflicting duplicates hard-fail.
- Includes deterministic offline tests and a mandatory gated live smoke, skipped by default and enabled only by `QUANT_SYSTEM_LIVE_TESTS=1`.
- Source catalog stable ETF/fund full-data coverage now includes `DatasetName.FUND_PROFILE` for `akshare_cn_hk_public_family`, as allowed by the TASK-035 handoff.

## Verification Performed During Integration
- `python3 -m unittest tests/datahub/test_akshare_fund_profile_adapter.py tests/datahub/test_source_catalog.py`
  - PASS, 22 tests
- `git diff --check -- quant/datahub tests/datahub coordination/reports/TASK-035_REPORT.md coordination/reviews/TASK-035_REVIEW.md`
  - PASS, no whitespace errors

## Live Smoke Evidence From Report And Review
- Execution report records:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_profile_live.py`
  - PASS, 3 tests, live smoke PASS
- Review independently reran the enabled live smoke and recorded PASS.
- No live-network rework gate is required for TASK-035 because the accepted review records live-enabled PASS.

## Conflicts Or Gaps
- No TASK-035 integration conflicts found.
- No blocking gaps remain for TASK-035.
- ETF-like fund profile support remains intentionally out of scope and rejected by this adapter.
- Workspace note: `coordination/agent_runs/*` files are dirty in the local worktree from the pipeline context. They were not modified by this Integration Agent and are outside this TASK-035 integration action.

## State Update Recommendations For Controller
- Mark `TASK-035` as Done / integrated in `coordination/TASK_BOARD.md`.
- Add `TASK-035` to completed Phase 2 work in `coordination/PROJECT_STATE.md` and `coordination/CONTEXT_SNAPSHOT.md`.
- Record that AKShare now has bounded no-credential `FUND_PROFILE` coverage for one requested China public fund record under `akshare_cn_hk_public_family`.
- Record that TASK-035 had default offline PASS and live-enabled PASS evidence for the fund profile adapter.
- Keep Phase 2 open unless `coordination/PHASE_GATE.md` indicates all required Phase 2 coverage is complete.
- If Phase 2 remains open, dispatch the next executable DataHub source-coverage task according to `coordination/PHASE_GATE.md` and the roadmap.
