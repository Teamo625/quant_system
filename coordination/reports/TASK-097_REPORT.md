# TASK-097 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
  - `coordination/reports/TASK-097_REPORT.md`

- classifier behavior before and after
  - Before: `_is_adjustment_factors_network_unavailable()` treated `sina`, `finance.sina.com.cn`, and `stock_zh_a_daily` as standalone skip tokens, so route/data failures mentioning those strings could be downgraded to live `SKIP`.
  - After: the classifier only treats clear environment/source availability signals as unavailable, including proxy/DNS/timeout/connection/TLS/upstream-service wording plus network exception types and relevant `OSError.errno` values.
  - Result: `ValueError("sina hfq factor not available")`, domain-only messages, and route-name-only messages no longer classify as environment-unavailable.

- regression tests added
  - Added offline classifier coverage proving these stay hard failures:
    - `ValueError("sina hfq factor not available")`
    - `RuntimeError("finance.sina.com.cn")`
    - `RuntimeError("stock_zh_a_daily")`
  - Added positive coverage proving clear availability wording still classifies as environment-unavailable:
    - `RuntimeError("... stock_zh_a_daily -> service unavailable from finance.sina.com.cn")`
    - existing `OSError(111, "connection refused ...")` case retained

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_adjustment_factors_adapter.py`
    - PASS (`Ran 5 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
    - PASS (`Ran 7 tests`, live smoke skipped by default)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
    - PASS (`Ran 7 tests`, including live smoke)

- default network behavior
  - Default tests remain offline-safe.
  - The live smoke still runs only when `QUANT_SYSTEM_LIVE_TESTS=1` is set.
  - Verified default gating with `env -u QUANT_SYSTEM_LIVE_TESTS ...`, where classifier tests ran offline and the real-source smoke skipped.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
  - PASS.
  - `QUANT_SYSTEM_LIVE_TESTS=1 ...test_akshare_a_share_adjustment_factors_live.py` completed successfully in the current environment.
  - Evidence: the live smoke no longer misclassified non-network review examples, and the real AKShare adjustment-factor fetch for `600000.SH` / `000001.SZ` returned schema-valid bounded records with both `qfq` and `hfq` bases.

- deviations
  - None.

- risks/follow-up
  - This rework intentionally narrows only the live skip classifier. It does not revisit broader adjustment-factor contract breadth or continuity limits from the initial TASK-097 work.
  - If future live failures surface new upstream availability wording not covered by the current token set, add a focused regression before broadening the classifier again.
