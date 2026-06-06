# TASK-121 REPORT

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_fund_holdings_adapter.py`
  - `tests/datahub/test_akshare_fund_holdings_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary
  - Hardened `AkshareETFFundHoldingsAdapter` symbol truth from ETF-only suffix handling to mixed ETF/fund namespace handling under the existing `fund_portfolio_hold_em` route.
  - Added explicit `.FUND_CN` support for public fund codes, including ambiguous bare `0*` codes only when explicitly disambiguated as funds.
  - Canonicalized bare non-ETF `1*`/`5*` fund codes such as `161725` to `FUND_CN`, while preserving accepted exchange ETF behavior for `510300.ETF_CN` / `159915.ETF_CN`.
  - Added clear failure for requested funds whose holdings payload contains non-A-share/BJ constituent codes; this prevents silently mis-normalizing QDII/global-asset style funds.
  - Kept `DatasetName.FUND_HOLDINGS` schema compatibility unchanged and kept `fund_holdings_composition` conservative at `partial`.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_fund_holdings_adapter.py` -> PASS (`Ran 36 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 42 tests`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 9 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py` -> PASS (`OK`, `skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py` -> PASS (`Ran 3 tests`)

- default network behavior
  - Default adapter/capability/catalog tests remain offline-safe and use injected fixtures only.
  - `tests/datahub/test_akshare_fund_holdings_live.py` still skips before any real source call unless `QUANT_SYSTEM_LIVE_TESTS=1` is explicitly set.
  - No hidden default live-network path was added.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS
  - Required gated live smoke passed with mixed request `symbols=("510300.ETF_CN", "000001.FUND_CN")`, `start_date=2025-01-01`, `end_date=2025-03-31`.
  - Returned fund identities were exactly `{"510300.ETF_CN", "000001.FUND_CN"}` and records validated under `DatasetName.FUND_HOLDINGS`.
  - Direct post-test probes in this environment confirmed:
    - `510300.ETF_CN` -> PASS, `record_count=20`, first record `510300.ETF_CN / 000001.SZ / 2025-03-31 / weight=0.53`
    - `000001.FUND_CN` -> PASS, `record_count=10`, first record `000001.FUND_CN / 002025.SZ / 2025-03-31 / weight=5.55`
    - `162411.FUND_CN` -> clear FAIL-by-design on normalization with `ValueError` because the route returned non-A-share holding symbol `AR`

- ETF/fund holdings route/source-family investigation result
  - Investigated AKShare no-credential holdings routes locally.
  - `fund_portfolio_hold_em` returned usable holdings for:
    - exchange ETFs: `510300`, `159915`
    - listed/open funds with domestic equity holdings: `161725`, `160706`, `000051`, `000001`
  - `fund_portfolio_hold_em` returned `rows=0` for `501018` in this environment, so broader listed-fund breadth is still not proven.
  - `fund_portfolio_hold_em` returned non-A-share constituents for `162411` (for example `AR`, `HES`), so cross-market/QDII-style holdings are not safe to normalize under the current `FUND_HOLDINGS` contract.
  - `stock_report_fund_hold_detail` and `fund_report_stock_cninfo` were investigated but not adopted:
    - `stock_report_fund_hold_detail` lacks normalized weight fields required by `DatasetName.FUND_HOLDINGS`
    - `fund_report_stock_cninfo` is aggregate-by-stock and lacks per-fund identity

- supported symbol classes, report-period granularity, identity, deduplication, known limitations
  - Supported now:
    - exchange ETF codes in proven ETF families -> canonical `.ETF_CN`
    - explicit `.FUND_CN` public fund codes, including ambiguous `0*` codes such as `000001.FUND_CN`
    - bare non-ETF `1*`/`5*` fund codes such as `161725` -> canonical `.FUND_CN`
  - Rejected clearly:
    - bare ambiguous `0*` codes
    - explicit `.FUND_CN` on proven ETF codes such as `510300.FUND_CN`
    - explicit `.ETF_CN` on non-ETF fund codes such as `161725.ETF_CN`
    - stock-like, HK-like, malformed, and index-like requests
    - fund payloads whose constituent symbols are not A-share/BJ equity codes
  - Granularity remains caller-provided bounded report-period holdings under `DatasetName.FUND_HOLDINGS`.
  - Identity/deduplication remains deterministic by `(fund_code, symbol, report_date, source)` with conflict failure on disagreeing duplicates and `source_ts` preference for exact duplicates.

- capability truth changed
  - `fund_holdings_composition` status remains `partial`.
  - Truth was narrowed and clarified, not promoted: capability/catalog wording now states that current public proof covers exchange ETFs plus explicit `FUND_CN` domestic-equity funds via `fund_portfolio_hold_em`, while non-A-share fund classes, broader breadth, longer continuity, and route redundancy remain incomplete.

- compatibility confirmation
  - Existing accepted ETF batch/report-period behavior for `510300.ETF_CN` / `159915.ETF_CN` was preserved.
  - `DatasetName.FUND_HOLDINGS` schema compatibility was preserved; `quant/datahub/datasets.py` was not changed.

- deviations
  - None.

- risks/follow-up
  - `fund_holdings_composition` must not be promoted beyond `partial`; `501018` remained empty here and QDII/global-asset funds can emit non-A-share constituents.
  - If future work needs cross-market fund holdings, the contract likely needs first-class holding-market/route truth before mixing A-share and overseas constituents.
  - Independent no-credential route redundancy for per-fund holdings remains unproven.
