# TASK-051 Report

## files changed

- `quant/datahub/adapters/akshare.py`
  - added `AkshareETFFundFlowAdapter` for narrow one-code, one-date ETF/fund scale/share source-fact slices
  - implemented SSE route `fund_etf_scale_sse(date=...)` and SZSE route `fund_scale_daily_szse(start_date=..., end_date=..., symbol="ETF")`
  - added bounded request checks, ETF/fund code validation, payload normalization, numeric/date parsing, exact duplicate dedupe, and route-unavailable classifier
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
  - exported `AkshareETFFundFlowAdapter`
- `quant/datahub/datasets.py`
  - made `FUND_FLOW.net_inflow` optional because verified public exchange scale routes do not provide net inflow
- `quant/datahub/source_capabilities.py`
  - moved `fund_flow` from `planned` to conservative `partial`
  - added `akshare_cn_hk_public_family` while preserving remaining breadth/metric gaps
- `quant/datahub/source_catalog.py`
  - added `FUND_FLOW` to AKShare ETF/fund coverage
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- `tests/datahub/test_datasets.py`
  - updated required-field expectation for optional `net_inflow`

## tests run

- `python3 -m unittest tests/datahub/test_akshare_fund_flow_adapter.py`
  - PASS, `Ran 14 tests`
- `python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py`
  - PASS default gated behavior, `Ran 1 test`, `skipped=1`
- `python3 -m unittest tests/datahub/test_datasets.py tests/datahub/test_source_capabilities.py tests/datahub/test_source_catalog.py`
  - PASS, `Ran 51 tests`
- `python3 -m unittest tests/datahub/test_akshare_fund_profile_adapter.py tests/datahub/test_akshare_etf_daily_bar_adapter.py tests/datahub/test_akshare_etf_daily_bar_live.py tests/datahub/test_source.py`
  - PASS, `Ran 64 tests`, `skipped=1`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py`
  - PASS, `Ran 1 test`
- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
  - PASS, `Ran 794 tests`, `skipped=35`

## default network behavior

- Default tests remain offline-safe.
- New offline adapter tests inject route callables and patch `socket.create_connection` in the main normalization test.
- New live smoke is skipped unless `QUANT_SYSTEM_LIVE_TESTS=1`.

## live-enabled result

- Result: PASS.
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py`
- Live sample: `DatasetName.FUND_FLOW`, source `akshare_cn_hk_public_family`, symbol `510300.ETF_CN`, date `2024-01-05`.
- Source route evidence:
  - local AKShare signature: `fund_etf_scale_sse(date: str = '20250115') -> pandas.DataFrame`
  - live route probe returned columns `['序号', '基金代码', '基金简称', 'ETF类型', '统计日期', '基金份额']`
  - no `net_inflow`, subscription, or redemption fields were present in the verified SSE ETF scale table
- The live smoke validated at least one normalized record through `DatasetRegistry.validate_record(...)`.

## deviations

- `net_inflow` was made optional for `FUND_FLOW`.
- Reason: verified no-credential AKShare exchange ETF scale/share routes provide source-fact fund share/scale data, not net inflow.
- No credentialed source, broad universe ingestion, full-history backfill, feature calculation, scanner, strategy, portfolio, signal, UI, AI, notification, or trading logic was added.

## risks/follow-up

- `AkshareETFFundFlowAdapter` is a narrow partial capability, not complete fund-flow coverage.
- Public AKShare route currently supports exchange scale/share facts; true fund net inflow and subscription/redemption metrics still need a future source slice if a public or approved credentialed source is opened.
- SZSE route was implemented and covered offline, but live PASS evidence in this report is for the SSE `510300.ETF_CN` sample only.
