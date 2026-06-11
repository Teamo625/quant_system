# TASK-128 Report

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_sector_adapter.py`
  - `tests/datahub/test_akshare_sector_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary:
  - Hardened `AkshareSectorDailyBarAdapter` from one-sector fetches to caller-provided bounded multi-sector industry/concept batches.
  - Added daily-bar identifier normalization/rejection parity with sector-membership rules: reject untyped, duplicate-normalized, stock-like, ETF/fund-like, HK-like, malformed, and unsupported-prefix sector identifiers.
  - Added per-sector zero-row failure handling so mixed-success bounded batches fail clearly instead of returning partial success.
  - Added deterministic same-day sector-bar dedupe with conflict hard-fail when duplicate rows disagree on OHLCV/amount facts.
  - Tightened `source_capabilities` and `source_catalog` wording so latest membership snapshots, optional dated fields, change-event timelines, classification-version metadata, and sector daily-bar redundancy are no longer overclaimed.

- selected readiness batch id and follow-up ids:
  - batch id: `sector_concept__datahub_hardening__sector_concept__batch_01`
  - follow-up ids:
    - `sector_concept__sector_concept_capability_readiness__sector_membership`
    - `sector_concept__sector_concept_capability_readiness__sector_historical_changes`
    - `sector_concept__sector_concept_capability_readiness__sector_daily_bars`

- sector/concept route/source-family investigation result:
  - Confirmed current no-credential proof remains inside `akshare_cn_hk_public_family`.
  - Membership truth: `stock_board_industry_cons_em` / `stock_board_concept_cons_em` primary, THS detail-page fallback for public-network Eastmoney failures.
  - Daily-bar truth: `stock_board_industry_hist_em` / `stock_board_concept_hist_em` primary, `stock_board_industry_index_ths` / `stock_board_concept_index_ths` fallback, then local requested-window filtering.
  - No independent non-AKShare public redundancy was proven in this handoff, so all three sector/concept capabilities remain conservative.

- supported sector identifier classes, taxonomy families, date behavior, source truth, deduplication behavior:
  - Supported identifiers: caller-provided typed `INDUSTRY:<name>` and `CONCEPT:<name>` only; daily bars now accept bounded multi-sector batches.
  - Rejected clearly: blank, untyped, duplicate-normalized, unsupported-prefix, stock-like, ETF/fund-like, HK-like, and malformed identifiers.
  - Taxonomy families proven in code/tests: industry and concept.
  - Daily-bar date behavior: pass bounded `start_date` / `end_date` to routes when supported and always filter locally to the requested window.
  - Source truth is adapter-level/catalog-level only; this handoff did not add per-record `source_route` fields because the dataset contract does not currently carry them.
  - Daily-bar dedupe: same `sector_id` + `trade_date` rows are deduped only when compatible; conflicting OHLCV/amount duplicates now hard-fail.

- membership/effective-date/change-event/classification-version truth and known limitations:
  - `sector_membership` remains bounded batch membership proof, not full taxonomy history proof.
  - Source-backed `in_date` / `out_date` are preserved only when upstream rows expose them.
  - THS fallback still proves latest-membership snapshots and therefore does not establish explicit reclassification event timelines.
  - `sector_historical_changes` remains `partial`: explicit change-event timelines, full taxonomy history, and classification-version metadata are still unproven.

- sector daily-bar source truth and known limitations:
  - `sector_daily_bars` now proves bounded multi-sector daily-bar batches for industry and concept sectors, not only one-sector samples.
  - Eastmoney primary plus THS fallback is proven in current environment; requested-window filtering is deterministic even when upstream returns wider history.
  - Capability remains `partial` because broader taxonomy continuity, stronger long-history proof, and independent public-route redundancy remain unresolved.

- tests run:
  - `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS
  - `python3 -m unittest tests.datahub.test_source_catalog` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_sector_adapter` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_sector_membership_adapter` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_sector_live` -> PASS (`skipped=1`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_sector_membership_live` -> PASS (`skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_sector_live` -> PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_sector_membership_live` -> PASS

- default network behavior:
  - Default tests remain offline-safe.
  - Live tests remain explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - `env -u QUANT_SYSTEM_LIVE_TESTS ...` confirmed the repository default skip path for both sector live suites.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks:
  - sector daily bars: PASS
    - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_sector_live` -> `Ran 1 test in 20.907s`, `OK`.
    - The live smoke validated a bounded batch containing one industry sector and one concept sector, with both sector IDs present in normalized output.
  - sector membership/history: PASS
    - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_sector_membership_live` -> `Ran 3 tests in 18.530s`, `OK`.
    - The live smoke validated a bounded mixed industry/concept membership batch with contract-valid normalized records.

- whether any capability truths changed:
  - `sector_membership`: status unchanged (`partial`), wording tightened to distinguish bounded dated rows from latest snapshot fallback and to keep redundancy/version gaps explicit.
  - `sector_historical_changes`: status unchanged (`partial`), wording tightened to reject treating snapshots as explicit change-event timelines.
  - `sector_daily_bars`: status unchanged (`partial`), wording updated from narrow sample wording to bounded batch proof with explicit Eastmoney/THS same-family limits.

- deviations:
  - No deviations from allowed scope or testing policy.
  - `tests/datahub/test_akshare_sector_membership_live.py` and `tests/datahub/test_akshare_sector_membership_adapter.py` were not changed because the existing membership tests already matched the preserved adapter behavior and truth boundary.

- risks/follow-up:
  - Sector datasets still rely on one public source family; independent non-AKShare redundancy remains open.
  - Membership fallback still does not create explicit reclassification events or classification-version metadata.
  - Sector daily-bar long-history continuity across the full sector taxonomy remains unproven and should not be promoted from this task alone.
