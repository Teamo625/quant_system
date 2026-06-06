# TASK-103 Report

- files changed
  - `tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
  - `coordination/reports/TASK-103_REPORT.md`

- classifier behavior before and after
  - Before: the dedicated turnover/liquidity live classifier treated route-name-only text such as `stock_zh_a_hist` as environment-unavailable, and the live smoke also reused the broader capital-flow helper in its skip path.
  - After: the dedicated classifier rejects `TypeError` and signature/call-compatibility tokens before any environment classification, no longer treats `stock_zh_a_hist` route-name-only text as unavailable, and the turnover/liquidity live smoke skips only on the narrowed dedicated classifier.

- regression evidence
  - Added offline classifier coverage proving `stock_zh_a_hist() got an unexpected keyword argument 'market'` remains a non-environment failure even when wrapped in a higher-level runtime error.
  - Added offline coverage proving `stock_zh_a_hist returned malformed payload` does not classify as environment `SKIP`.
  - Added offline coverage proving explicit upstream availability text such as `503 Service Unavailable from Eastmoney upstream` still classifies as environment unavailable.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
  - `python3 -m unittest tests/datahub/test_akshare_a_share_turnover_liquidity_adapter.py`
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`

- default network behavior
  - Default/offline tests remain offline-safe.
  - The dedicated turnover/liquidity live smoke remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - No default test performs real network access.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - `SKIP`
  - Live command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
  - Evidence: `ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`
  - Interpretation: current result is still an environment/upstream availability skip, not a repository-side route-signature, request-construction, schema, normalization, or duplicate-conflict failure.

- contract/source-capability truth
  - No dataset contract, source capability, source catalog, or adapter normalization was broadened in this rework.
  - `a_share_turnover_liquidity` remains unchanged and unpromoted.

- deviations
  - None.

- risks/follow-up
  - A future rerun is still required to obtain live `PASS` once `stock_zh_a_hist` is reachable from the execution environment.
  - The shared capital-flow helper in adapter code remains broader than this dedicated turnover/liquidity live classifier, but it is no longer used to classify the dedicated turnover/liquidity smoke skip path.
