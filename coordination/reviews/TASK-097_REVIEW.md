# TASK-097 Review

## Findings

- Blocking: `tests/datahub/test_akshare_a_share_adjustment_factors_live.py:57-65` relies on `AkshareAShareAdjustmentFactorsAdapter._is_adjustment_factors_network_unavailable()` to downgrade live exceptions into environment `SKIP`, but the classifier in [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:3877) treats any message containing `"sina"` / `"finance.sina.com.cn"` / `"stock_zh_a_daily"` as network-unavailable. A direct review repro returned `True` for `ValueError("sina hfq factor not available")`. That is a real route/data failure, not a network outage, so future live failures can be reported as false `SKIP`. This violates the handoff and AGENTS live-truthfulness requirement. Current classifier tests only cover connection-refused and a generic value error, so this regression path is untested.

## Decision

Rework required before Controller closure.

## Closure Readiness

- Controller closure: No.
- Default tests offline-safe: Yes. Review reruns confirmed the default suite stayed offline-safe, and the live smoke file still skips by default when `QUANT_SYSTEM_LIVE_TESTS` is unset.
- Live-enabled result: PASS on review rerun (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py`), but rework is still required because the skip classifier can misclassify non-network source failures as environment `SKIP`.
- Phase/scope/contract/test blockers: No phase-scope violation found. Blocking test/live-classification issue remains in the new adjustment-factor adapter path and must be fixed with regression coverage.

## Verification

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_akshare_a_share_adjustment_factors_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
