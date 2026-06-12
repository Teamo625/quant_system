# TASK-132 Report

- batch: `a_share__datahub_hardening__a_share__batch_02`
- follow-up ids:
  - `a_share__a_share_capability_readiness__a_share_capital_flow`
  - `a_share__a_share_capability_readiness__a_share_northbound_flow`
  - `a_share__a_share_capability_readiness__a_share_turnover_liquidity`
  - `a_share__a_share_capability_readiness__a_share_limit_up_down`
  - `a_share__a_share_capability_readiness__a_share_margin_financing_and_lending`
  - `a_share__a_share_capability_readiness__a_share_financial_statements`

## files changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_northbound_flow_adapter.py`
- `tests/datahub/test_akshare_a_share_northbound_flow_live.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- `tests/datahub/test_akshare_a_share_financial_data_adapter.py`
- `tests/datahub/test_akshare_a_share_financial_data_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## implementation summary

- Northbound flow: added bounded fallback route support from `stock_hsgt_individual_em` to `stock_hsgt_individual_detail_em`, preserved route-distinct `source_route`, aggregated detail rows by trade date, and hardened fallback shape-error handling so a broken detail route does not false-fail a primary-route fetch.
- Limit-up/down: added optional breadth routes `stock_zt_pool_strong_em` and `stock_zt_pool_sub_new_em`, emitted route truth in records/schema, kept route-distinct dedupe, inferred board-specific limit ratios when explicit prices exist, and skipped optional malformed rows whose upstream change-percent cannot produce usable limit prices.
- Financial statements: added THS statement-backed secondary routes `stock_financial_debt_new_ths`, `stock_financial_benefit_new_ths`, and `stock_financial_cash_new_ths`, kept route-distinct statement records, and prioritized `parent_holder_net_profit` over weaker `net_profit` when both appear for the same THS period.
- Capability/catalog truth: tightened `source_capabilities` and `source_catalog` wording so unresolved continuity/reconciliation gaps remain explicit for capital flow, northbound flow, turnover/liquidity, limit-up/down, margin financing/lending, and financial statements.

## route / capability investigation result

- `a_share_capital_flow`: no new public route added in this handoff; existing truth remains conservative around dated symbol-level and fallback breadth limits.
- `a_share_northbound_flow`: primary symbol history is still `stock_hsgt_individual_em`; bounded redundancy now attempts `stock_hsgt_individual_detail_em` and keeps route-local truth instead of overclaiming market-level quota or buy/sell decomposition.
- `a_share_turnover_liquidity`: no adapter code change; capability wording now explicitly keeps semantics at daily volume/amount/turnover facts rather than inferred float/share-base liquidity claims.
- `a_share_limit_up_down`: breadth expanded to previous-day, strong, sub-new, and broken-board route families with route-distinct truth; optional-route malformed rows are discarded rather than poisoning the full bounded batch.
- `a_share_margin_financing_and_lending`: no adapter code change; capability wording now keeps SSE/SZSE exchange-summary routes explicitly non-symbol-compatible.
- `a_share_financial_statements`: primary Sina statement family remains active; THS debt/benefit/cash routes now provide secondary statement-backed redundancy with per-route provenance.

## symbol / window / dedupe behavior

- Supported symbol class remains bounded A-share stock symbols only; ETF/fund/HK/index-like symbols remain rejected by adapter-side validation.
- Northbound, limit-up/down, and financial statements continue to honor bounded date/report windows and filter wider upstream history to the requested window.
- Route-distinct facts stay distinguishable by `source_route`; dedupe keys now preserve route separation for northbound fallback rows, optional limit-up/down pools, and THS statement rows.

## tests run

- PASS: `python3 -m unittest tests.datahub.test_source_capabilities tests.datahub.test_source_catalog tests.datahub.test_datasets tests.datahub.test_akshare_a_share_capital_flow_snapshot_adapter tests.datahub.test_akshare_a_share_northbound_flow_adapter tests.datahub.test_akshare_a_share_turnover_liquidity_adapter tests.datahub.test_akshare_a_share_limit_up_down_adapter tests.datahub.test_akshare_a_share_margin_financing_lending_adapter tests.datahub.test_akshare_a_share_financial_data_adapter`
- PASS: `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest tests.datahub.test_akshare_a_share_capital_flow_snapshot_live tests.datahub.test_akshare_a_share_northbound_flow_live tests.datahub.test_akshare_a_share_turnover_liquidity_live tests.datahub.test_akshare_a_share_limit_up_down_live tests.datahub.test_akshare_a_share_margin_financing_lending_live tests.datahub.test_akshare_a_share_financial_data_live`
- PASS: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_limit_up_down_live`
- PASS: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_financial_data_live`
- SKIP: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_northbound_flow_live`

## default network behavior

- Default/offline adapter tests stayed network-safe.
- Default live modules remained explicitly gated by `QUANT_SYSTEM_LIVE_TESTS`; with the env var unset they skipped live smoke paths and did not perform real network calls.

## live-enabled result and root-cause evidence

- `northbound_flow`: SKIP. Live diagnosis showed `stock_hsgt_individual_em(symbol=600000/000001)` currently tops out at `持股日期=2024-08-16`, so the requested recent bounded window yields no usable rows. The bounded fallback route `stock_hsgt_individual_detail_em(symbol=..., start_date=..., end_date=...)` currently fails upstream with `TypeError: 'NoneType' object is not subscriptable`. Code was hardened so this upstream shape failure no longer hard-fails the smoke.
- `limit_up_down`: PASS. Live smoke succeeded after adding strong/sub-new route support and skipping optional malformed rows such as recent `stock_zt_pool_sub_new_em` rows with extreme non-daily `涨跌幅` values and no limit-price fields.
- `financial_statements`: PASS. Live smoke succeeded after adding THS statement-backed routes and resolving same-period THS metric precedence for `parent_holder_net_profit` vs `net_profit`.

## deviations

- None from allowed-write scope.
- No new capital-flow, turnover/liquidity, or margin-financing source code path was changed in this handoff; those capabilities were tightened through capability/catalog truth only.

## risks / follow-up

- AKShare northbound public routes remain materially limited for recent bounded history: primary symbol history appears stale through `2024-08-16`, and the bounded detail route is currently upstream-broken. Controller should treat northbound continuity as unresolved public-source risk, not as closed completeness.
- Optional limit-up/down routes can expose non-daily or route-specific `涨跌幅` semantics for certain rows; current handling safely skips unusable rows, but exact upstream field semantics remain a public-source documentation risk.
- THS secondary financial-statement routes improve redundancy but do not solve full cross-route reconciliation or long-history completeness; capability wording remains intentionally conservative.
