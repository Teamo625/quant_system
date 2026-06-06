# TASK-098 Review

## Findings

1. Blocking regression: `DatasetName.CORPORATE_ACTIONS` now globally requires `action_family` and `source_route` in [quant/datahub/datasets.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/datasets.py:424), but the HK corporate-actions adapter still emits records without those top-level fields in [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:8475). Independent verification fails on both `python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_adapter.py` and `python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_live.py`, each reporting missing required fields at [tests/datahub/test_akshare_hk_corporate_actions_adapter.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_hk_corporate_actions_adapter.py:107) and [tests/datahub/test_akshare_hk_corporate_actions_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_hk_corporate_actions_live.py:78).

2. Report gap: [coordination/reports/TASK-098_REPORT.md](/Users/chenziheng/Documents/量化分析代码/quant_system/coordination/reports/TASK-098_REPORT.md:1) is accurate for the targeted A-share suite, but it does not acknowledge that the shared `CORPORATE_ACTIONS` contract change regressed existing HK coverage. Controller should not close the task with an incomplete regression picture.

## Decision

REWORK REQUIRED.

## Closure Readiness

- Controller closure allowed: No.
- Default tests offline-safe: Yes for the TASK-098 targeted suite; no hidden default live-network behavior was observed.
- Live-enabled result: PASS for `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`; rework still required because the shared contract change breaks existing HK corporate-actions validation.
- Phase/scope/contract/test blockers: Yes. This is a shared `CORPORATE_ACTIONS` contract regression, not a downstream-phase scope issue.

## Required Follow-up

- Rework the shared `CORPORATE_ACTIONS` contract rollout so existing HK corporate-actions records also satisfy the new required fields, or narrow the contract change so it does not apply globally.
- Re-run HK corporate-actions offline/live tests after the fix and update the execution report with the cross-suite regression outcome before Controller closure.
