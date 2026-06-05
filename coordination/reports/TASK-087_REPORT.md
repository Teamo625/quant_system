# TASK-087 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_fund_premium_discount_adapter.py`
- `tests/datahub/test_akshare_fund_premium_discount_live.py`
- `tests/datahub/test_source_capabilities.py`

## tests run
- `python3 -m unittest tests/datahub/test_akshare_fund_premium_discount_adapter.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
- `python3 -m unittest -v tests/datahub/test_akshare_fund_premium_discount_live.py` -> PASS in current shell because `QUANT_SYSTEM_LIVE_TESTS=1` was already set
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_fund_premium_discount_live.py` -> PASS with live smoke SKIP (`skipped=1`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_premium_discount_live.py` -> PASS

## default network behavior
- Default adapter/unit tests are offline-safe and use injected fixtures only.
- The live smoke file is environment-gated and skips when `QUANT_SYSTEM_LIVE_TESTS` is unset.
- Current operator shell had `QUANT_SYSTEM_LIVE_TESTS=1`, so the plain live-file command executed live; explicit unset verification confirmed the default skip boundary still works.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_premium_discount_live.py`
- Evidence:
  - Returned `record_count=2`
  - `159915.ETF_CN 2026-06-04 fund_etf_fund_daily_em market_price=4.1 nav=4.1046 premium_discount_rate=0.11`
  - `510300.ETF_CN 2026-06-04 fund_etf_fund_daily_em market_price=4.926 nav=4.9284 premium_discount_rate=0.05`
- No network/proxy/DNS/TLS/upstream failure occurred in the live-enabled run.

## capability truth
- `fund_premium_discount` status remains `partial`.
- Gap text was updated from “implementation pending” to bounded latest-available public AKShare coverage with remaining breadth/history limitations.

## source route coverage and known limitations
- Implemented adapter: `AkshareETFFundPremiumDiscountAdapter`
- Primary route: `fund_etf_fund_daily_em`
  - Proven fields: `fund_code`, `trade_date`, `market_price`, `nav`, `premium_discount_rate`, computed `premium_discount_amount`, `source_route`, `source_category`
  - Behavior: caller-provided multi-symbol filtering over one latest-available public exchange snapshot, then bounded date-window filtering
- Fallback route on primary network unavailability: `fund_etf_spot_em`
  - Proven fields: `market_price`, `iopv`, `premium_discount_rate`, `source_ts`
- Known limitations:
  - No broader historical premium-discount series; current public proof is latest-available exchange snapshot coverage
  - Coverage is still limited to requested exchange-traded ETF/fund codes accepted by current adapter normalization
  - No non-exchange fund premium-discount path or broader route redundancy was added
  - Source catalog metadata did not need changes

## deviations
- None

## risks/follow-up
- If future work needs longer premium-discount history, a different public route or a multi-day historical premium-discount source will be required.
- Some 1-prefix exchange fund codes may still be source-limited by upstream table membership; current behavior is to fail clearly on partial batch success instead of silently degrading.
- Current live proof used `fund_etf_fund_daily_em`; fallback `fund_etf_spot_em` is covered offline but was not the route used in the passing live run.
