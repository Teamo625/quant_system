# TASK-033 Integration

## Task
- `TASK-033_DATAHUB_AKSHARE_HK_CORPORATE_ACTIONS_ADAPTER`

## Inputs Read
- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-033_DATAHUB_AKSHARE_HK_CORPORATE_ACTIONS_ADAPTER.md`
- `coordination/reports/TASK-033_REPORT.md`
- `coordination/reviews/TASK-033_REVIEW.md`
- current worktree changes

## Review Decision
- Review result: ACCEPTED
- Blocking findings: none
- Follow-up requirements: none blocking for integration

## Integration Result
- Integrated accepted TASK-033 work by recording this integration pass.
- The reviewed implementation is present in the worktree and remains within the DataHub phase boundary.
- No architectural direction change was made by integration.
- No controller-owned project state files were edited by this Integration Agent.

## Files Touched By TASK-033 Implementation
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_hk_corporate_actions_live.py`
- `coordination/reports/TASK-033_REPORT.md`
- `coordination/reviews/TASK-033_REVIEW.md`
- `coordination/integrations/TASK-033_INTEGRATION.md`

## Integrated Behavior Summary
- Added `AkshareHKCorporateActionsAdapter` for `DatasetName.CORPORATE_ACTIONS` under source id `akshare_cn_hk_public_family`.
- Scope is limited to one requested Hong Kong stock symbol and dividend/corporate-action records.
- Accepts canonical HK symbols such as `00700.HK` and source-native numeric symbols such as `00700`, then normalizes output to canonical HK symbol form.
- Uses bounded routes only:
  - primary: `stock_hk_dividend_payout_em(symbol=<5-digit-code>)`
  - fallback: `stock_hk_fhpx_detail_ths(symbol=<source-native-code>)`, only when the primary route is unavailable for network/source-availability reasons.
- Normalizes records to the existing `CORPORATE_ACTIONS` contract with `symbol`, `market=HK`, `event_date`, `event_type=dividend`, structured `value`, deterministic `raw_payload_ref`, source id, optional `source_ts`, deterministic `ingested_at`, and registry schema version.
- Preserves source-truth text and dates; cash dividend amount/currency are parsed only when the source plan text has a safe explicit pattern.
- Applies deterministic event-date fallback order and client-side `start_date` / `end_date` filtering on normalized `event_date`.
- Includes deterministic duplicate handling, malformed payload checks, required-field checks, serializability checks, and live-source unavailability classification.
- Includes mandatory gated live smoke coverage, skipped by default and enabled only by `QUANT_SYSTEM_LIVE_TESTS=1`.

## Verification Performed During Integration
- `python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
  - PASS, 19 tests
- `python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`
  - PASS, 3 tests, 1 live smoke skipped by default
- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
  - PASS, 535 tests, 21 skipped

## Live Smoke Evidence From Report And Review
- Execution report records:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`
  - PASS, 3 tests, live smoke PASS
- Review independently reran the enabled live smoke and recorded PASS.
- No live-network rework gate is required for TASK-033 because the accepted review records live-enabled PASS.

## Conflicts Or Gaps
- No TASK-033 integration conflicts found.
- No blocking gaps remain for TASK-033.
- Workspace note: the worktree contains pre-existing modified controller-owned coordination files and prior TASK-031/TASK-032 coordination or test artifacts. They were not modified by this Integration Agent and are outside this TASK-033 integration action.

## State Update Recommendations For Controller
- Mark `TASK-033` as Done / integrated in `coordination/TASK_BOARD.md`.
- Add `TASK-033` to completed Phase 2 work in `coordination/PROJECT_STATE.md` and `coordination/CONTEXT_SNAPSHOT.md`.
- Keep Phase 2 open unless `coordination/PHASE_GATE.md` indicates all required Phase 2 coverage is complete.
- If Phase 2 remains open, dispatch the next executable DataHub source-coverage task according to `coordination/PHASE_GATE.md` and the roadmap.
- Record that TASK-033 had default offline PASS and live-enabled PASS evidence for the HK corporate-actions one-symbol dividend adapter.
