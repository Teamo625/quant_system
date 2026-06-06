# TASK-117 Report

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_hk_financial_data_adapter.py`
  - `tests/datahub/test_akshare_hk_financial_data_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary:
  - Hardened `AkshareHKFinancialDataAdapter` for HK `FINANCIAL_STATEMENTS` / `FINANCIAL_INDICATORS` without leaving DataHub scope.
  - Added explicit `source_route` truth:
    - statements: `stock_financial_hk_report_em`
    - indicators: `stock_financial_hk_analysis_indicator_em`
  - Added deterministic `metric_family` truth for stable indicator groups: `per_share`, `income_scale`, `growth`, `profitability`, `cash_flow`, `leverage_liquidity`.
  - Reworked statement metric extraction from naive alias matching to priority-based alias selection so mixed HK issuer terminology does not create false conflicts:
    - revenue now prefers route-consistent labels such as `营运收入` / `经营收入总额`
    - net profit now prefers shareholder-attributable labels such as `股东应占溢利`
  - Tightened capability/catalog wording so HK financial proof is described as bounded public Eastmoney report-period history, not closure-grade breadth.

- tests run:
  - `python3 -m unittest tests/datahub/test_akshare_hk_financial_data_adapter.py` -> PASS (`Ran 19 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 41 tests`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 9 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py` -> PASS (`Ran 4 tests`, `skipped=2`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py` -> PASS (`Ran 4 tests`)

- default network behavior:
  - Offline adapter/capability/catalog tests remain network-free.
  - `tests/datahub/test_akshare_hk_financial_data_live.py` is still gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skips live smokes by default.
  - No hidden default live network behavior was introduced.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence:
  - PASS.
  - `QUANT_SYSTEM_LIVE_TESTS=1` live smoke passed for both statements and indicators.
  - Direct adapter probe after the change proved:
    - `FINANCIAL_STATEMENTS`, symbols `00700.HK` + `00005.HK`: `443` normalized records total, report periods `95` and `54`, latest periods `2026-03-31` and `2025-12-31`.
    - Latest income-statement extraction:
      - `00700.HK` -> `revenue=196458000000.0`, `net_profit=58093000000.0`, `source_route=stock_financial_hk_report_em`
      - `00005.HK` -> `revenue=452823411200.0`, `net_profit=148321737600.0`, `source_route=stock_financial_hk_report_em`
    - `FINANCIAL_INDICATORS`, same symbols: `404` normalized records total, `9` report periods per symbol, latest period `2026-03-31` for both symbols.
    - Bounded indicator window `2025-01-01..2025-12-31` returned `180` records with periods:
      - `00700.HK`: `2025-03-31`, `2025-06-30`, `2025-09-30`, `2025-12-31`
      - `00005.HK`: `2025-03-31`, `2025-06-30`, `2025-09-30`, `2025-12-31`
  - No proxy/DNS/TLS/upstream skip occurred in this run.

- `hk_financial_data` capability truth changed:
  - Status stayed `PARTIAL`.
  - Gap wording now states the proven public truth more precisely: multi-symbol HK stock report-period history via `stock_financial_hk_report_em` and `stock_financial_hk_analysis_indicator_em`, with explicit `source_route` and bounded `metric_family` truth where stable.

- source route / statement-family / metric-family / date-window / continuity:
  - Source routes proven:
    - `stock_financial_hk_report_em`
    - `stock_financial_hk_analysis_indicator_em`
  - Statement-family coverage remains:
    - `balance_sheet`
    - `income_statement`
    - `cash_flow_statement`
  - Indicator metric-family coverage added for stable groups:
    - `per_share`, `income_scale`, `growth`, `profitability`, `cash_flow`, `leverage_liquidity`
  - Date-window behavior remains deterministic post-normalization filtering on `report_period_end`; invalid ranges are still rejected upstream through the shared source request path.
  - History continuity evidence is stronger than TASK-081:
    - statements now proven across dozens of report periods for both tested issuers
    - indicators now proven across nine report periods per tested issuer
    - bounded 2025 windows return only in-range periods

- stronger public-source HK financial breadth/history outcome:
  - Implemented stronger no-credential HK financial hardening inside the existing public Eastmoney routes.
  - This task improved practical issuer breadth robustness by handling real route terminology differences across at least `00700.HK` and `00005.HK`.
  - No speculative new adapter route was added; `stock_hk_financial_indicator_em` was inspected locally but not integrated because it is latest-indicator shaped rather than report-period history.

- deviations:
  - None.

- risks/follow-up:
  - `hk_financial_data` still must not be treated as closure-grade coverage: broader HK issuer sampling, non-stock support, and independent public-source redundancy remain unproven.
  - Statement extraction is still limited to the schema’s core fields (`revenue`, `net_profit`, `total_assets`, `total_liabilities`, `net_cash_operating`); more HK-specific fundamental breadth would require contract expansion in a future handoff.
  - `00005.HK` statement history is not as deep/current as `00700.HK` on the statement route; longer continuity across more issuer types still needs future evidence.
