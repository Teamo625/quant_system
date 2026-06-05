# TASK-089 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_index_constituents_adapter.py`
- `tests/datahub/test_akshare_index_constituents_live.py`
- `tests/datahub/test_source_capabilities.py`

## tests run
- `python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py` -> PASS (`Ran 27 tests`)
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 33 tests`)
- `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 7 tests`)
- `python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py` -> PASS in this shell because inherited `QUANT_SYSTEM_LIVE_TESTS=1`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py` -> PASS with live smoke `SKIP` (`skipped=1`), confirming default gating when env is unset
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py` -> PASS

## default network behavior
- Default offline adapter/capability/catalog tests do not perform real network calls.
- The live smoke file remains env-gated by `QUANT_SYSTEM_LIVE_TESTS`.
- In the current shell, `QUANT_SYSTEM_LIVE_TESTS=1` was already set, so the bare `-v tests/datahub/test_akshare_index_constituents_live.py` command executed live.
- Explicit `env -u QUANT_SYSTEM_LIVE_TESTS ...` verification confirmed the intended default skip path.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Live-enabled result: PASS.
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py`
- Evidence:
  - batch request `("000300.CN_INDEX", "399001.CN_INDEX")` normalized successfully
  - returned `718` records total
  - per-index counts: `000300.CN_INDEX=300`, `399001.CN_INDEX=418`
  - `000300.CN_INDEX` sample preserved date-bearing/weight-bearing source truth: `in_date=2026-05-29`, `weight=0.397`
  - `399001.CN_INDEX` sample preserved dated membership truth from public fallback coverage: `in_date` range observed `2003-05-26 .. 2026-05-11`
- No live network rework was required.

## capability truth change
- `index_constituent_history`: status unchanged, remains `partial`
- `index_rebalance_effective_dates`: status unchanged, remains `partial`
- Only conservative gap text was refined to reflect proven bounded multi-index constituent access and limited effective-date-like metadata preservation.

## source route coverage and known limitations
- Adapter now supports caller-provided multi-index requests for the bounded core China slice: `000001.CN_INDEX`, `000300`, `000852`, `000905`, `000906`, `399001`, `399006`, plus validated source-native forms such as `sh000300`, `sh000905`, `sz399001`.
- Bare ambiguous `000001` is rejected; canonical `000001.CN_INDEX` and `sh000001` are accepted.
- Route preference is now:
  - `index_stock_cons_weight_csindex`
  - `index_stock_cons_csindex`
  - `index_stock_cons`
  - `index_stock_cons_sina`
- Metadata preservation:
  - `日期` / `生效日期` / `调整日期` / `纳入日期` map into `INDEX_CONSTITUENTS.in_date`
  - `剔除日期` / `结束日期`-like fields map into `out_date`
  - `权重` is preserved when available
  - `source_ts` remains null unless the route exposes a parseable timestamp
- Known limitation:
  - public AKShare does not guarantee an explicit index-level rebalance calendar/history in the current `INDEX_CONSTITUENTS` contract
  - snapshot fallback (`index_stock_cons_sina`) has no dated membership fields; adapter conservatively falls back to `in_date=1900-01-01`
  - broader benchmark breadth and long-history continuity remain incomplete

## index_weight_history status
- `index_weight_history` remains blocked/planned for credentialed Tushare live proof.
- This task did not change Tushare credential handling and did not promote `index_weight_history`.

## deviations
- No scope deviations.
- `quant/datahub/source_catalog.py`, `quant/datahub/adapters/__init__.py`, and `tests/datahub/test_source_catalog.py` required no code changes.

## risks/follow-up
- `399001`/`399006` public coverage can depend on fallback routes because CSIndex weight routes may not expose stable dated payloads for every index family.
- A future handoff is still needed if the controller wants explicit rebalance-calendar truth, broader benchmark breadth, or stronger historical continuity guarantees across more index families.
