# TASK-103 Report

- files changed
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_catalog.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_datasets.py`
  - `tests/datahub/test_source_catalog.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_turnover_liquidity_adapter.py`
  - `tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`

- implementation
  - Added dedicated `DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT` contract/profile for A-share turnover/liquidity source facts.
  - Canonical fields: `symbol`, `market`, `trade_date`, `metric_granularity`, `volume`, `amount`, `turnover_rate`, `source`, `source_route`, optional `source_ts`, `ingested_at`, `schema_version`.
  - Canonical granularity: `daily`.
  - Deterministic identity: `symbol + trade_date + source + source_route + metric_granularity`.
  - AKShare A-share capital-flow adapter now supports the dedicated turnover/liquidity dataset through `stock_zh_a_hist` while preserving existing `CAPITAL_FLOW_SNAPSHOT` and `NORTHBOUND_FLOW_SNAPSHOT` behavior.
  - Existing compatibility preserved: `DAILY_BARS` still owns OHLCV bars; `CAPITAL_FLOW_SNAPSHOT` still validates current capital-flow records and continues to carry optional `turnover_rate` without schema replacement.

- route/source-family investigation
  - Investigated existing A-share liquidity facts already present across `DAILY_BARS`, `CAPITAL_FLOW_SNAPSHOT`, and AKShare routes.
  - Chosen canonical public route: `stock_zh_a_hist` because it directly exposes dated `volume`, `amount`, and `turnover_rate` for caller-bounded A-share symbol/date requests.
  - Existing capital-flow routes remain non-canonical for this slice because `stock_individual_fund_flow` / datacenter fallback focus on fund-flow metrics and only expose `turnover_rate` optionally, not the full turnover/liquidity field set.
  - Source catalog updated conservatively so AKShare public family and Tushare family both advertise coverage; capability truth remains `partial`.

- tests run
  - `python3 -m py_compile quant/datahub/datasets.py quant/datahub/source_catalog.py quant/datahub/source_capabilities.py quant/datahub/adapters/akshare.py tests/datahub/test_datasets.py tests/datahub/test_source_catalog.py tests/datahub/test_source_capabilities.py tests/datahub/test_akshare_a_share_turnover_liquidity_adapter.py tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
  - `python3 -m unittest tests/datahub/test_datasets.py`
  - `python3 -m unittest tests/datahub/test_source_catalog.py`
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - `python3 -m unittest tests/datahub/test_akshare_adapter.py`
  - `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
  - `python3 -m unittest tests/datahub/test_akshare_a_share_turnover_liquidity_adapter.py`
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`

- default network behavior
  - Default/offline tests remain offline-safe.
  - Dedicated live smokes stay explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - New offline turnover/liquidity adapter tests use injected fixtures only and patch socket creation where relevant to guard against hidden network access.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - `SKIP`
  - Live command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
  - Evidence: `ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`
  - Interpretation: upstream/public-route availability failure while reaching AKShare `stock_zh_a_hist`; not a repository-side schema/normalization/signature failure.
  - Feasible repo-side follow-up already covered: live classifier keeps contract failures non-skip and allows environment/unavailability skips only for network/upstream conditions.

- capability truth change
  - `a_share_turnover_liquidity` remains `partial`.
  - Change made: dataset mapping moved from mixed `DAILY_BARS`/`CAPITAL_FLOW_SNAPSHOT` semantics to explicit `TURNOVER_LIQUIDITY_SNAPSHOT`.

- known limitations
  - Only one public no-credential canonical route is currently proven for the dedicated turnover/liquidity slice.
  - No new derived factors were added: no fabricated VWAP, float shares, free-float turnover, market value, liquidity score, spread, or factor outputs.
  - Route-distinct facts are not merged across source routes; the dedicated dataset currently records `stock_zh_a_hist` source truth only.

- deviations
  - None.

- risks/follow-up
  - A future rework is still needed to obtain a real live `PASS` once `stock_zh_a_hist` is reachable from the execution environment.
  - Public-source redundancy for turnover/liquidity remains unproven; a second stable no-credential route would be needed before promoting the capability beyond `partial`.
