# TASK-085 Report

## Files Changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- `tests/datahub/test_source_capabilities.py`

## Tests Run
- `python3 -m unittest tests/datahub/test_akshare_fund_flow_adapter.py` -> PASS (`Ran 17 tests`)
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 30 tests`)
- `python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py` -> PASS in this shell (`QUANT_SYSTEM_LIVE_TESTS=1` was already set)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py` -> PASS with default skip (`OK (skipped=1)`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py` -> PASS (`Ran 1 test in 2.689s`)

## Default Network Behavior
- Default/offline-safe behavior is preserved in code: the live smoke remains gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- This shell had `QUANT_SYSTEM_LIVE_TESTS=1` pre-set, so the bare `python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py` command executed live here.
- I verified the true default skip path explicitly with `env -u QUANT_SYSTEM_LIVE_TESTS ...`, which skipped without network access.

## Live-Enabled Result
- Result: PASS
- Evidence:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py`
  - Output summary: `ok`, `Ran 1 test in 2.689s`, `OK`
- Live assertions covered:
  - multi-symbol request for `510300.ETF_CN` and `159915.ETF_CN`
  - bounded window `2024-01-04` to `2024-01-05`
  - returned symbols exactly matched the requested batch
  - normalized records stayed within requested trade-date bounds
  - records validated against `DatasetName.FUND_FLOW`

## Capability Truth
- `fund_flow` status remains `partial`
- Changed: gap text/recommended handoff theme only
- Reason: bounded caller-provided multi-symbol date-window coverage is now proven for public exchange scale/share routes, but broader flow metrics, non-exchange breadth, and longer history continuity are still incomplete

## Source Route Coverage / Limitations
- Implemented coverage:
  - SSE `fund_etf_scale_sse`: iterate deterministically across each date in the bounded window
  - SZSE `fund_scale_daily_szse`: fetch bounded window once and filter to requested ETF/fund codes
  - mixed SSE/SZSE batches supported through `SourceRequest.symbols`
  - deterministic dedupe/sort by `(fund_code, trade_date, source)`
  - fail-fast on invalid symbols, schema/normalization errors, and partial batch success where one requested symbol has no usable rows while another succeeds
- Known limitations kept explicit:
  - public route still represents exchange scale/share slices, not full trading-usable ETF/fund flow breadth
  - net inflow / subscription / redemption remain source-optional rather than guaranteed
  - non-exchange fund coverage is not added
  - longer history continuity beyond bounded public windows remains unproven

## Deviations
- No scope deviations
- Additional verification beyond handoff:
  - explicit `env -u QUANT_SYSTEM_LIVE_TESTS ...` run to separate true default skip behavior from this shell's pre-set live env

## Risks / Follow-up
- Future hardening still needs richer ETF/fund flow metrics than exchange scale/share slices alone
- Capability should not be promoted above `partial` without broader public-route breadth and longer-history proof
- Route argument/signature incompatibility remains a hard failure by design and should stay that way in review
