# TASK-102 Report

- files changed
  - `tests/datahub/test_akshare_a_share_northbound_flow_live.py`
  - `coordination/reports/TASK-102_REPORT.md`

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_northbound_flow_live.py` -> PASS (`Ran 6 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_northbound_flow_live.py` -> PASS (`OK`, `skipped=1`)
  - `python3 -m unittest tests/datahub/test_akshare_a_share_northbound_flow_adapter.py` -> PASS (`Ran 7 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 37 tests`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_northbound_flow_live.py` -> PASS (`Ran 6 tests`)

- default network behavior
  - Default execution remains offline-safe.
  - `tests/datahub/test_akshare_a_share_northbound_flow_live.py` still gates the real-source smoke behind `QUANT_SYSTEM_LIVE_TESTS=1`.
  - With the env var unset, the live smoke is skipped by default and only classifier regression cases run.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS
  - The explicit live command completed with `OK` under `QUANT_SYSTEM_LIVE_TESTS=1`; no environment skip path was taken.
  - Because the smoke test passed, its runtime assertions held for the current source response: schema validation succeeded, `source_route == 'stock_hsgt_individual_em'`, records were available for at least two requested symbols, and the normalized records remained date-valid and sorted.

- narrowed classifier policy
  - Removed route-name-only skip behavior for `eastmoney`, `stock_hsgt_individual_em`, and `em_hsgt`.
  - The classifier now uses a two-pass check:
    first, any chained `TypeError` or explicit call-signature text such as `unexpected keyword argument`, `missing required positional argument`, or `got multiple values for argument` forces a non-environment result;
    second, only network/upstream availability signals such as proxy/DNS/TLS/timeout/connection failures or `service unavailable`-style messages may classify as environment `SKIP`.

- regression evidence
  - Added offline regression coverage proving `stock_hsgt_individual_em() got an unexpected keyword argument 'market'` stays non-environment even when wrapped by a higher-level runtime error.
  - Added offline regression coverage proving a message that only mentions `stock_hsgt_individual_em` does not become `SKIP`.
  - Preserved positive coverage for genuine availability cases via `ProxyError` and `503 Service Unavailable` examples.

- contract/source-capability truth
  - No DataHub adapter, dataset, source-catalog, or source-capability files changed in this rework.
  - `a_share_northbound_flow` was not promoted or broadened; TASK-102 contract and capability truth remain unchanged from the prior execution.

- deviations
  - None.

- risks/follow-up
  - The dedicated northbound live smoke is now truthful about route-signature defects, but the broader adapter-side capital-flow network classifier still contains route-name tokens and was out of scope for this handoff.
  - The only proven dedicated public northbound route remains `stock_hsgt_individual_em`; redundancy and freshness limits remain follow-up work outside this rework.
