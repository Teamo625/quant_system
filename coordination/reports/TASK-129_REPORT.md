# TASK-129 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/policy.py`
- `quant/datahub/adapters/hkex.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_china_macro_adapter.py`
- `tests/datahub/test_akshare_china_macro_live.py`
- `tests/datahub/test_policy_documents_adapter.py`
- `tests/datahub/test_hkex_company_announcements_adapter.py`
- `tests/datahub/test_hkex_company_announcements_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## implementation summary
- Selected readiness batch id: `macro_policy__datahub_hardening__macro_policy__batch_01`
- Included follow-up ids: `macro_policy__macro_policy_capability_readiness__macro_observations`, `macro_policy__macro_policy_capability_readiness__macro_indicator_definitions`, `macro_policy__macro_policy_capability_readiness__macro_release_metadata`, `macro_policy__macro_policy_capability_readiness__policy_documents`, `macro_policy__macro_policy_capability_readiness__company_announcements_cross_market`
- Expanded bounded macro indicator support from the original 3-CN slice to a caller-selected CN/US/EU set while keeping `symbols=None` observations conservative and bounded.
- Hardened policy-document live fetch parameter handling by inspecting callable signatures instead of swallowing `TypeError`, and pushed requested date windows down to gov.cn query params.
- Added explicit HK announcement `source_route="predefineddoc.xhtml"` so HK and A-share announcements now share first-class route provenance under the common contract.
- Updated capability/catalog truth to match the stronger bounded macro set, per-observation release-date truth, gov.cn date-window semantics, and cross-market announcement route truth. No capability was promoted.

## macro route/source-family investigation result
- Local `akshare` route inspection found many callable macro routes. This round only adopted routes whose payloads mapped cleanly to the existing contracts without schema expansion:
- Adopted routes: CN `macro_china_cpi_yearly`, `macro_china_ppi_yearly`, `macro_china_gdp_yearly`, `macro_china_m2_yearly`, `macro_china_pmi_yearly`, `macro_china_exports_yoy`, `macro_china_imports_yoy`; US/EU `macro_usa_cpi_yoy`, `macro_usa_ppi`, `macro_euro_cpi_yoy`, `macro_euro_gdp_yoy`
- Observed payload variations now covered: `日期`/`时间`, `今值`/`现值`, and `发布日期`.
- Not adopted this round: broader route families with unclear unit semantics or higher normalization risk; those remain future work, not silently covered.

## policy route/source-family investigation result
- Retained official gov.cn selectors `zhengcelibrary_gw` and `zhengcelibrary_bm`.
- Hardening added deterministic `min_time` / `max_time` propagation to the live search route and strict callable-signature handling.
- No broader official selector family was proven stable enough this round inside the existing contract; policy breadth remains conservative.

## A-share/HK announcement route/source-family investigation result
- A-share path unchanged in scope: primary `stock_individual_notice_report`, fallback `stock_notice_report`, bounded symbol/date windows, explicit `source_route`, and existing whole-window fallback truth.
- HK path hardened for parity: `predefineddoc.xhtml` now emits explicit `source_route`.
- Cross-market capability truth now references the actual public families in use: `akshare_cn_hk_public_family` + `hkex_disclosure_and_calendar_family`.

## supported behavior
- Macro indicators now support bounded explicit selection for `CPI_CN_YOY`, `PPI_CN_YOY`, `GDP_CN_YOY`, `M2_CN_YOY`, `PMI_CN`, `EXPORTS_CN_YOY`, `IMPORTS_CN_YOY`, `CPI_US_YOY`, `PPI_US_YOY`, `CPI_EU_YOY`, `GDP_EU_YOY`
- Policy selectors remain `ZHENGCELIBRARY_GW`, `ZHENGCELIBRARY_BM`
- Announcement markets/symbols: A-share existing canonical SH/SZ/BJ stock symbols only; HK existing HK stock symbols only, now with explicit route truth
- Date-window behavior:
  - macro observations: invalid inverted windows fail; requested windows filter deterministically
  - policy documents: invalid inverted windows fail at request validation; bounded windows now also propagate to gov.cn query params
  - announcements: existing bounded filtering preserved
- Deduplication behavior:
  - macro: same `indicator_id + observation_date`, prefer latest `source_ts`, conflict hard-fails
  - policy: same `policy_id`, prefer latest `source_ts`, conflict hard-fails
  - announcements: existing id-based conflict rules preserved; HK parity now includes `source_route`

## macro release/revision metadata source truth and known limitations
- Source-backed truth strengthened: `MACRO_OBSERVATIONS.release_date` is now preserved for supported routes that expose `发布日期` / `release_date`.
- `macro_release_metadata` remains `partial`: no first-class release calendar dataset, no revision-history contract, and no complete revision/preliminary taxonomy beyond explicit per-row facts.

## policy document pagination/authority/history source truth and known limitations
- Source truth strengthened only to deterministic bounded date-window querying on the accepted gov.cn routes.
- Still limited: only selected official routes are proven; broader authority families are unproven; pagination depth/history completeness are still incomplete; no first-class per-record `source_route` field was added to the dataset contract in this execution window

## cross-market announcement source truth and known limitations
- Shared `COMPANY_ANNOUNCEMENTS` records now carry explicit route truth on both public families actually used in this cluster:
  - A-share: AKShare route names
  - HK: `predefineddoc.xhtml`
- `company_announcements_cross_market` remains `partial`: HK latest-feed coverage is still stronger, A-share category breadth/history continuity remain incomplete, and broader A/H parity is not proven.

## tests run
- `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS (`Ran 45 tests`)
- `python3 -m unittest tests.datahub.test_source_catalog` -> PASS (`Ran 9 tests`)
- `python3 -m unittest tests.datahub.test_akshare_china_macro_adapter` -> PASS (`Ran 30 tests`)
- `python3 -m unittest tests.datahub.test_policy_documents_adapter` -> PASS (`Ran 19 tests`)
- `python3 -m unittest tests.datahub.test_akshare_a_share_company_announcements_adapter` -> PASS (`Ran 19 tests`)
- `python3 -m unittest tests.datahub.test_hkex_company_announcements_adapter` -> PASS (`Ran 19 tests`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_china_macro_live` -> PASS (`OK`, live smoke skipped by default)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_policy_documents_live` -> PASS (`OK`, live smoke skipped by default)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_company_announcements_live` -> PASS (`OK`, live smoke skipped by default)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_hkex_company_announcements_live` -> PASS (`OK`, live smoke skipped by default)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_china_macro_live` -> PASS (`Ran 3 tests in 3.352s`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_policy_documents_live` -> PASS (`Ran 3 tests in 0.441s`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_hkex_company_announcements_live` -> PASS (`Ran 3 tests in 3.695s`)

## default network behavior
- Default adapter and metadata tests remained offline-safe.
- All live files still require explicit `QUANT_SYSTEM_LIVE_TESTS=1`; `env -u QUANT_SYSTEM_LIVE_TESTS ...` verified default skip behavior.
- No hidden default live network path was introduced.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Macro live smoke: PASS
  - Evidence: explicit live request for `CPI_CN_YOY` + newly supported `CPI_US_YOY` completed `OK`
- Policy live smoke: PASS
  - Evidence: explicit live request on `zhengcelibrary_gw` completed `OK` after the new bounded-date query path
- HK announcement live smoke: PASS
  - Evidence: explicit HKEX live smoke completed `OK` and now asserts `source_route="predefineddoc.xhtml"`

## capability truth changed
- No status promotion. All five targeted capabilities remain `partial`.
- Truth wording/linkage changed for `macro_observations`, `macro_indicator_definitions`, `macro_release_metadata`, `policy_documents`, and `company_announcements_cross_market`; the changes reflect broader bounded macro support, per-observation release-date truth, deterministic gov.cn date-window query truth, and actual public A-share/HK source-family parity.

## deviations
- None.

## risks/follow-up
- Macro remains bounded and selector-driven; broader public macro families, revision history, and a first-class release calendar still need future work.
- Policy documents still lack proven broader authority selectors, deeper pagination/history proof, and first-class route provenance in the dataset schema.
- Cross-market announcements remain conservative because HK feed depth and A-share route/category breadth are still asymmetric.
