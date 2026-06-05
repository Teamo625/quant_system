# TASK-091 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/policy.py`
- `quant/datahub/adapters/__init__.py`
- `tests/datahub/test_akshare_china_macro_adapter.py`
- `tests/datahub/test_akshare_china_macro_live.py`
- `tests/datahub/test_policy_documents_adapter.py`
- `tests/datahub/test_policy_documents_live.py`
- `coordination/reports/TASK-091_REPORT.md`

## tests run
- `python3 -m unittest tests/datahub/test_akshare_china_macro_adapter.py`
- `python3 -m unittest tests/datahub/test_policy_documents_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
- `python3 -m unittest -v tests/datahub/test_policy_documents_live.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_policy_documents_live.py`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_policy_documents_live.py`

## default network behavior
- Offline adapter/catalog/capability tests stayed local-only.
- Live test files remain env-gated and skip when `QUANT_SYSTEM_LIVE_TESTS` is unset.
- This shell had `QUANT_SYSTEM_LIVE_TESTS=1` exported globally, so I additionally ran the two `env -u QUANT_SYSTEM_LIVE_TESTS ...` commands to verify default skip behavior explicitly.

## live-enabled result
- Macro live smoke: `PASS`
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
  - Result: `Ran 3 tests in 4.940s` / `OK`
  - Verified bounded live access for two explicit indicator identifiers: `CPI_CN_YOY`, `PPI_CN_YOY`
- Policy live smoke: `PASS`
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_policy_documents_live.py`
  - Result: `Ran 3 tests in 0.453s` / `OK`
  - Verified bounded live access for explicit policy route selector `zhengcelibrary_gw` with schema-valid policy-document metadata

## capability truth changed
- No capability status change.
- `macro_observations`, `macro_indicator_definitions`, `macro_release_metadata`, and `policy_documents` remain conservatively `partial`.
- `quant/datahub/source_capabilities.py` and `quant/datahub/source_catalog.py` were not changed.

## source coverage and limitations
- Macro route coverage hardened for caller-parameterized access to locally supported public routes:
  - `CPI_CN_YOY` -> `macro_china_cpi_yearly`
  - `PPI_CN_YOY` -> `macro_china_ppi_yearly`
  - `GDP_CN_YOY` -> `macro_china_gdp_yearly`
- No-symbol macro requests still return all locally supported indicators.
- Requested macro batches now fail clearly on blank/duplicate/unsupported/policy-like/stock-like/HK-like selectors and on requested indicators that yield no usable rows after normalization/date filtering.
- Policy route coverage hardened for explicit selector use within the existing contract:
  - `zhengcelibrary_gw`
  - `zhengcelibrary_bm`
- Macro optional metadata is preserved only when upstream rows expose it: `release_date`, `source_ts`, `is_preliminary`.
- Policy optional metadata is preserved only when upstream rows expose it: `source_ts`, `summary`, `url`.
- Remaining limits are unchanged: bounded public macro breadth only, no first-class revision-history/release-calendar completeness, no broader policy authority coverage, no pagination/history completeness guarantees beyond the current bounded routes.

## deviations
- No code-scope deviations from the handoff.
- Operational note only: because `QUANT_SYSTEM_LIVE_TESTS=1` was already exported in the shell, explicit `env -u` verification was added to prove default skip behavior.

## risks/follow-up
- Macro selector support is intentionally limited to the three locally mapped identifiers; broader public macro families still need future handoffs.
- Requested macro batches now hard-fail when any requested indicator has no usable rows in the bounded window; callers need to handle that explicit failure mode.
- Policy route selectors are limited to the two currently supported gov.cn routes; wider authority families and deeper pagination/history remain future work.
