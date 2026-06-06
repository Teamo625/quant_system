# TASK-123 Review

## Findings

1. Blocking: `AkshareETFFundFlowAdapter` now unconditionally pulls Sina full-table latest snapshot routes for every `FUND_SCALE_SHARE_SNAPSHOT` request, including bounded ETF-only batches that already have exchange-history routes. See `quant/datahub/adapters/akshare.py:24139-24154` and `quant/datahub/adapters/akshare.py:24730-24758`. That conflicts with the handoff requirement to prefer caller-bounded requests and not silently fetch unbounded full-market ETF/fund data (`coordination/handoffs/TASK-123_DATAHUB_ETF_FUND_SCALE_SHARE_SOURCE_BREADTH_HARDENING.md:108`). The report acknowledges the routes are not caller-parameterized, so this is not just a wording issue; it is current runtime behavior and needs execution rework before Controller closure.

2. Non-blocking but scope-noisy: duplicate scale/share dedupe helpers were also added under the unrelated `AkshareETFFundNavSnapshotAdapter` (`quant/datahub/adapters/akshare.py:23753-23829`). They are not needed for TASK-123 behavior and push the change outside the focused adapter surface the handoff asked for.

## Decision

- Result: REWORK REQUIRED
- Independent verification:
  - `python3 -m unittest tests.datahub.test_datasets tests.datahub.test_source_capabilities tests.datahub.test_source_catalog tests.datahub.test_akshare_fund_flow_adapter tests.datahub.test_akshare_fund_nav_adapter tests.datahub.test_akshare_fund_scale_share_adapter` -> PASS (`Ran 154 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live tests.datahub.test_akshare_fund_scale_share_live` -> PASS default skip (`Ran 3 tests`, `skipped=3`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live` -> PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_scale_share_live` -> PASS

## Closure Readiness

- Controller closure allowed: No
- Default tests offline-safe: Yes
- Live-enabled result: PASS, but rework is still required
- Phase/scope/contract/test blockers: Yes
  - Scope/implementation blocker: current adapter behavior silently fetches unbounded full-table Sina snapshot data, which violates the TASK-123 bounded-request requirement.

## Required Follow-up

- Rework the scale/share path so unbounded snapshot routes are not fetched by default for every bounded request. Either restrict their use to an explicitly justified, request-scoped fallback that does not violate the handoff boundary, or revert to capability/catalog truth tightening without adapter-backed snapshot expansion.
- Remove the unrelated duplicate helper insertion from the NAV adapter unless a separate handoff explicitly requires it.
