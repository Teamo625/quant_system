# TASK-117 Review

## Findings

1. Blocking: HK financial live-failure classification still downgrades route-signature/schema/payload defects into environment `SKIP`, so the reported live `PASS` is not a reliable closure gate. In [tests/datahub/test_akshare_hk_financial_data_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_hk_financial_data_live.py:31), `_is_live_environment_unavailable()` treats any exception message containing `stock_financial_hk_report_em` or `stock_financial_hk_analysis_indicator_em` as environment-unavailable, and the live tests use that classifier in the skip path at [tests/datahub/test_akshare_hk_financial_data_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_hk_financial_data_live.py:124) and [tests/datahub/test_akshare_hk_financial_data_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_hk_financial_data_live.py:216). The adapter-side classifier in [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:17869) has the same problem. Independent repro in review:
   - signature error `RuntimeError("... route=stock_financial_hk_report_em ...")` -> `True`
   - payload/schema error `ValueError("... route=stock_financial_hk_analysis_indicator_em ...")` -> `True`
   This violates the handoff requirement that route-name-bearing argument/signature/schema/payload/normalization defects remain hard failures.

## Decision

REWORK REQUIRED.

No phase-scope violation was found in the modified files. Default/offline tests are still offline-safe, and the current live-enabled run did pass locally, but controller closure is still blocked by the defect-classification issue above.

## Closure Readiness

- Controller closure allowed: No.
- Default tests offline-safe: Yes. Independent rerun passed for adapter, capability, catalog, and default-gated live tests; live smokes still skip by default when `QUANT_SYSTEM_LIVE_TESTS` is unset.
- Live-enabled result: PASS in this review run, but rework is required because repository-side route defects can still be downgraded to `SKIP`.
- Phase/scope/contract/test blockers: Yes. The HK financial live classifier path does not satisfy the handoff's hard-failure requirement for route-signature/schema/payload defects.

## Required Follow-up

- Narrow both HK financial unavailability classifiers to genuine network/proxy/DNS/TLS/upstream availability failures only.
- Add regression coverage proving route-name-bearing signature/argument/schema/payload/normalization defects fail rather than skip.
- Re-run the TASK-117 default and live-enabled HK financial test suite after the classifier fix.
