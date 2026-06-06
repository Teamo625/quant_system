# TASK-120 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_fund_nav_adapter.py`
  - `tests/datahub/test_akshare_fund_nav_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary
  - Hardened `AkshareETFFundNavSnapshotAdapter` from ETF-only symbol truth to mixed `ETF_CN` / `FUND_CN` NAV support with clear namespace disambiguation.
  - Preserved accepted exchange ETF behavior for `510300.ETF_CN` and similar listed ETF families through bounded `fund_etf_fund_info_em`.
  - Added explicit `FUND_CN` support for public fund NAV history via `fund_open_fund_info_em`, including merged unit/accumulated NAV rows and bounded local date filtering.
  - Added same-family fallback from bounded ETF NAV windows to open-fund history when `fund_etf_fund_info_em` returns the source-side empty-window failure `ValueError: No objects to concatenate`.
  - Bare `0*` codes now fail clearly as ambiguous and require explicit `.FUND_CN`; mismatched suffixes such as `510300.FUND_CN` fail clearly.
  - Corrected normalized market truth for listed/open funds such as `161725.FUND_CN`, `501018.FUND_CN`, and `000001.FUND_CN`; `fund_nav` remains conservative at `partial`.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py` -> PASS (`OK`, `skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py` -> PASS

- default network behavior
  - Default adapter/capability/catalog tests remain offline-safe and use injected fixtures only.
  - `tests/datahub/test_akshare_fund_nav_live.py` still skips before any live source call unless `QUANT_SYSTEM_LIVE_TESTS=1` is explicitly set.
  - No hidden default live-network path was added.

- live-enabled result and root-cause evidence
  - Result: PASS
  - Evidence:
    - Gated live smoke passed for recent bounded mixed-symbol request `510300.ETF_CN` + `000001.FUND_CN`.
    - The same live smoke also passed a historical bounded request for `000001.FUND_CN` and asserted first returned trade date `2001-12-18`.
    - Additional direct adapter probes in this environment confirmed:
      - `510300.ETF_CN` over `2012-05-01..2012-05-10` -> PASS, first record `2012-05-04`, proving the open-route fallback recovers an earlier ETF history window where the bounded route is empty.
      - `161725.FUND_CN` over `2024-01-02..2024-01-10` -> PASS.
      - `501018.FUND_CN` over `2024-01-02..2024-01-10` -> PASS.

- ETF/fund NAV route/source-family investigation result
  - Investigated AKShare public NAV routes in this environment:
    - `fund_etf_fund_info_em` returned bounded dated NAV rows not only for exchange ETFs (`510300`, `159915`) but also for several fund codes (`161725`, `000051`, `000001`, `501018`).
    - `fund_open_fund_info_em` returned much longer same-family history for `000001`, `000051`, `161725`, `501018`, and also for ETF codes such as `510300`.
    - `fund_etf_fund_info_em` raised `ValueError: No objects to concatenate` for some earlier ETF windows (`510300` 2012-05 bounded window), while `fund_open_fund_info_em` still returned usable history.
    - `150001.FUND_CN` remained unproven here: `fund_open_fund_info_em` failed with `JSParseException ... Unexpected token '<'`, so split/legacy/other fund classes remain incomplete.

- supported symbol classes, granularity, identity, deduplication, limitations
  - Supported now:
    - Bare listed ETF codes in proven ETF families -> normalized to `.ETF_CN`.
    - Explicit `.FUND_CN` public fund codes such as `000001.FUND_CN`.
    - Non-ETF listed fund codes such as `161725` / `501018` -> normalized to `.FUND_CN`.
  - Rejected clearly:
    - bare ambiguous `0*` codes like `000001`
    - suffix mismatches like `510300.FUND_CN`
    - malformed, stock-like, index-like bare, missing, and unsupported codes
  - Granularity remains caller-provided bounded symbol/date-window NAV series under `DatasetName.FUND_NAV_SNAPSHOT`.
  - Deduplication remains deterministic by `(fund_code, trade_date, source)` with conflict checks when duplicate rows disagree.
  - Known limitations:
    - schema has no `source_route`, so route-level provenance cannot yet be emitted in normalized NAV rows
    - some fund classes still fail upstream (`150001.FUND_CN` probe)
    - full no-credential breadth and independent public-route redundancy are still unproven

- capability truth
  - `fund_nav` status remains `partial`.
  - Truth changed: capability/catalog wording now reflects bounded exchange ETF NAV plus explicit `FUND_CN` public-fund history and ETF empty-window fallback, instead of implying only generic exchange ETF/fund coverage.

- compatibility confirmation
  - Existing accepted ETF compatibility was preserved for `510300.ETF_CN`.
  - `DatasetName.FUND_NAV_SNAPSHOT` schema compatibility was preserved; no schema file change was required.

- deviations
  - No scope deviations.
  - Added direct adapter probes beyond the required test list to document route behavior and limitations precisely in this report.

- risks/follow-up
  - `fund_nav` must not be promoted beyond `partial`; unsupported or unstable fund classes still exist, and route-level provenance is not yet first-class in the dataset contract.
  - A future follow-up should decide whether NAV contracts need explicit `source_route` before combining more route families.
  - Broader off-exchange fund breadth, split/legacy fund handling, and stronger no-credential redundancy remain open.
