# TASK-102 Review

## Findings

- Blocking: [tests/datahub/test_akshare_a_share_northbound_flow_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_a_share_northbound_flow_live.py:31) classifies any exception message containing `eastmoney`, `stock_hsgt_individual_em`, or `em_hsgt` as environment-unavailable, and [the live smoke](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_a_share_northbound_flow_live.py:117) converts that classification into `SKIP`. That would incorrectly downgrade route-signature/call-compatibility failures such as `unexpected keyword argument` on `stock_hsgt_individual_em`, violating the handoff rule that route-name-bearing AKShare argument/signature defects must fail rather than skip.

## Decision

Rework required before Controller closure.

Independent verification:
- `python3 -m unittest tests/datahub/test_datasets.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py` -> PASS
- `python3 -m unittest tests/datahub/test_akshare_a_share_northbound_flow_adapter.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` -> PASS (`skipped=1`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_northbound_flow_live.py` -> PASS (`skipped=1`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` -> PASS
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_northbound_flow_live.py` -> PASS

## Closure Readiness

- Controller closure allowed: No
- Default tests offline-safe: Yes
- Live-enabled result: PASS in the current environment; rework still required because the new northbound live classifier can mask repository-side route/signature regressions as `SKIP`
- Phase/scope/contract/test blockers: Yes; test-classifier blocker in the dedicated northbound live smoke

## Required Follow-up

- Narrow the new northbound live-environment classifier so network/proxy/DNS/TLS/upstream unavailability may skip, but route-signature and request/contract defects on `stock_hsgt_individual_em` fail.
