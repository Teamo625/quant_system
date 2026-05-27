# TASK-031 Integration

## Task
- TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_ADAPTER

## Integration Result
- NOT INTEGRATED

## Basis For Integration Decision
- Review file: `coordination/reviews/TASK-031_REVIEW.md`
- Review decision: CHANGES_REQUESTED
- Blocking findings: yes

TASK-031 cannot be integrated in this pass because Integration Agent may only integrate reviewed and accepted work. The current review requests changes for a live-network/source-unavailability classification defect.

## Blocking Findings Carried From Review
1. Live network-unavailable classification path can crash with `NameError`.
   - Location: `quant/datahub/adapters/akshare.py`
   - Cause: `AkshareETFFundHoldingsAdapter._is_fund_holdings_network_unavailable(...)` references `ssl.SSLError`, but `ssl` is not imported in `quant/datahub/adapters/akshare.py`.
   - Impact: adapter-side classification for network/proxy/DNS/TLS/upstream failures can fail before producing the required skip/diagnostic boundary.

2. Adapter-side classifier coverage is insufficient.
   - Location: `tests/datahub/test_akshare_fund_holdings_live.py`
   - Current tests use a local duplicate helper rather than directly exercising `AkshareETFFundHoldingsAdapter._is_fund_holdings_network_unavailable(...)`.
   - Impact: defects in the adapter classifier can bypass deterministic test coverage.

## Files Reviewed For This Integration Pass
- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_ADAPTER.md`
- `coordination/reports/TASK-031_REPORT.md`
- `coordination/reviews/TASK-031_REVIEW.md`
- Current TASK-031 code/test changes observed in:
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_fund_holdings_adapter.py`
  - `tests/datahub/test_akshare_fund_holdings_live.py`

## Conflict Check
- No merge-style file conflict was identified by this integration pass.
- The blocker is acceptance state and the review-confirmed defect, not a textual conflict.
- Controller-owned state files were not modified by this Integration Agent pass.

## Required Next Step
- Dispatch or perform a TASK-031 execution rework in allowed TASK-031 files.
- Fix the adapter-side network-unavailable classifier so it cannot raise `NameError` and handles TLS/network exceptions cleanly.
- Add deterministic test coverage that directly exercises `AkshareETFFundHoldingsAdapter._is_fund_holdings_network_unavailable(...)`.
- Update `coordination/reports/TASK-031_REPORT.md` with the rework and verification evidence.
- Require a fresh Review Agent pass.
- Re-run Integration Agent only after the fresh review decision is ACCEPTED.

## State Update Recommendations For Controller
- Do not mark `TASK-031` Done/Closed yet.
- Keep Phase 2 open.
- Keep `TASK-031` active or move it to a rework/changes-requested state according to the local task board convention.
- Do not dispatch the next Phase 2 task until TASK-031 receives accepted review and successful integration, unless the controller explicitly chooses to split/parallelize work.

## Notes
- The reported implementation otherwise appears scoped to DataHub adapter/tests/report files, but it remains unintegrated until the blocking review findings are resolved and accepted.
