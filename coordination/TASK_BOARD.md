# Task Board

## Status Enum

Allowed task statuses:

- Ready
- In Progress
- In Review
- Ready to Integrate
- Done
- Rejected
- Blocked

This board structure uses the lifecycle:

`handoff -> execution report -> review file -> integration file -> controller state update`

## Active

| Task | Title | Status | Owner | Handoff | Report | Review | Integration | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-040 | FeatureHub foundation contracts | Ready | 5.3 execution window | `coordination/handoffs/TASK-040_FEATUREHUB_FOUNDATION_CONTRACTS.md` | `coordination/reports/TASK-040_REPORT.md` | `coordination/reviews/TASK-040_REVIEW.md` | `coordination/integrations/TASK-040_INTEGRATION.md` | Open Phase 3 with importable FeatureHub contract primitives and offline-only validation tests; no real feature calculations |

## Backlog

| Task | Title | Status | Phase | Handoff | Report | Review | Integration |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | First technical feature calculation slice | Blocked | Phase 3 | TBD | TBD | TBD | TBD |
| TBD | Valuation and capital-flow feature slices | Blocked | Phase 3 | TBD | TBD | TBD | TBD |
| TBD | Feature output local persistence/versioning | Blocked | Phase 3 | TBD | TBD | TBD | TBD |
| TBD | DataHub source expansion beyond current approved Phase 2 coverage | Blocked | Future DataHub extension | TBD | TBD | TBD | TBD |

## Done

| Task | Title | Status | Completed In | Handoff | Report | Review | Integration |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PHASE-0-INIT | Governance and blueprint initialization | Done | Phase 0 | N/A | N/A | N/A | N/A |
| TASK-001 | DataHub foundation skeleton | Done | Phase 1 | `coordination/handoffs/TASK-001_DATAHUB_FOUNDATION.md` | `coordination/reports/TASK-001_REPORT.md` | `coordination/reviews/TASK-001_REVIEW.md` | `coordination/integrations/TASK-001_INTEGRATION.md` |
| TASK-002 | DataHub schema contracts | Done | Phase 1 | `coordination/handoffs/TASK-002_DATAHUB_SCHEMA_CONTRACTS.md` | `coordination/reports/TASK-002_REPORT.md` | `coordination/reviews/TASK-002_REVIEW.md` | `coordination/integrations/TASK-002_INTEGRATION.md` |
| TASK-003 | DataHub local storage IO | Done | Phase 1 | `coordination/handoffs/TASK-003_DATAHUB_LOCAL_STORAGE_IO.md` | `coordination/reports/TASK-003_REPORT.md` | `coordination/reviews/TASK-003_REVIEW.md` | `coordination/integrations/TASK-003_INTEGRATION.md` |
| TASK-004 | DataHub offline fixture validation | Done | Phase 1 | `coordination/handoffs/TASK-004_DATAHUB_OFFLINE_FIXTURE_VALIDATION.md` | `coordination/reports/TASK-004_REPORT.md` | `coordination/reviews/TASK-004_REVIEW.md` | `coordination/integrations/TASK-004_INTEGRATION.md` |
| TASK-005 | DataHub schema type validation | Done | Phase 1 | `coordination/handoffs/TASK-005_DATAHUB_SCHEMA_TYPE_VALIDATION.md` | `coordination/reports/TASK-005_REPORT.md` | `coordination/reviews/TASK-005_REVIEW.md` | `coordination/integrations/TASK-005_INTEGRATION.md` |
| TASK-006 | DataHub comprehensive source catalog | Done | Phase 2 | `coordination/handoffs/TASK-006_DATAHUB_ALL_SOURCE_CATALOG.md` | `coordination/reports/TASK-006_REPORT.md` | `coordination/reviews/TASK-006_REVIEW.md` | `coordination/integrations/TASK-006_INTEGRATION.md` |
| TASK-007 | DataHub expanded domain schema contracts | Done | Phase 2 | `coordination/handoffs/TASK-007_DATAHUB_EXPANDED_DOMAIN_SCHEMA_CONTRACTS.md` | `coordination/reports/TASK-007_REPORT.md` | `coordination/reviews/TASK-007_REVIEW.md` | `coordination/integrations/TASK-007_INTEGRATION.md` |
| TASK-008 | DataHub expanded contract semantic validation | Done | Phase 2 | `coordination/handoffs/TASK-008_DATAHUB_EXPANDED_CONTRACT_SEMANTIC_VALIDATION.md` | `coordination/reports/TASK-008_REPORT.md` | `coordination/reviews/TASK-008_REVIEW.md` | `coordination/integrations/TASK-008_INTEGRATION.md` |
| TASK-009 | DataHub explicit semantic validation rules | Done | Phase 2 | `coordination/handoffs/TASK-009_DATAHUB_EXPLICIT_SEMANTIC_VALIDATION_RULES.md` | `coordination/reports/TASK-009_REPORT.md` | `coordination/reviews/TASK-009_REVIEW.md` | `coordination/integrations/TASK-009_INTEGRATION.md` |
| TASK-010 | DataHub semantic rule integrity checks | Done | Phase 2 | `coordination/handoffs/TASK-010_DATAHUB_SEMANTIC_RULE_INTEGRITY_CHECKS.md` | `coordination/reports/TASK-010_REPORT.md` | `coordination/reviews/TASK-010_REVIEW.md` | `coordination/integrations/TASK-010_INTEGRATION.md` |
| TASK-011 | DataHub source adapter contract foundation | Done | Phase 2 | `coordination/handoffs/TASK-011_DATAHUB_SOURCE_ADAPTER_CONTRACT_FOUNDATION.md` | `coordination/reports/TASK-011_REPORT.md` | `coordination/reviews/TASK-011_REVIEW.md` | `coordination/integrations/TASK-011_INTEGRATION.md` |
| TASK-012 | DataHub AKShare A-share daily bar adapter | Done | Phase 2 | `coordination/handoffs/TASK-012_DATAHUB_AKSHARE_A_SHARE_DAILY_BAR_ADAPTER.md`; `coordination/handoffs/TASK-012_DATAHUB_AKSHARE_LIVE_SMOKE_REWORK.md`; `coordination/handoffs/TASK-012_DATAHUB_AKSHARE_LIVE_REPORT_CORRECTION.md` | `coordination/reports/TASK-012_REPORT.md` | `coordination/reviews/TASK-012_REVIEW.md` | `coordination/integrations/TASK-012_INTEGRATION.md` |
| TASK-013 | DataHub AKShare A-share trading calendar adapter | Done | Phase 2 | `coordination/handoffs/TASK-013_DATAHUB_AKSHARE_A_SHARE_TRADING_CALENDAR_ADAPTER.md` | `coordination/reports/TASK-013_REPORT.md` | `coordination/reviews/TASK-013_REVIEW.md` | `coordination/integrations/TASK-013_INTEGRATION.md` |
| TASK-014 | DataHub AKShare Hong Kong daily bar adapter | Done | Phase 2 | `coordination/handoffs/TASK-014_DATAHUB_AKSHARE_HK_DAILY_BAR_ADAPTER.md`; `coordination/handoffs/TASK-014_DATAHUB_HK_LIVE_NETWORK_EVIDENCE_REWORK.md` | `coordination/reports/TASK-014_REPORT.md` | `coordination/reviews/TASK-014_REVIEW.md` | `coordination/integrations/TASK-014_INTEGRATION.md` |
| TASK-015 | DataHub AKShare ETF/fund NAV snapshot adapter | Done | Phase 2 | `coordination/handoffs/TASK-015_DATAHUB_AKSHARE_ETF_FUND_NAV_ADAPTER.md` | `coordination/reports/TASK-015_REPORT.md` | `coordination/reviews/TASK-015_REVIEW.md` | `coordination/integrations/TASK-015_INTEGRATION.md` |
| TASK-016 | DataHub AKShare index daily bar adapter | Done | Phase 2 | `coordination/handoffs/TASK-016_DATAHUB_AKSHARE_INDEX_DAILY_BAR_ADAPTER.md` | `coordination/reports/TASK-016_REPORT.md` | `coordination/reviews/TASK-016_REVIEW.md` | `coordination/integrations/TASK-016_INTEGRATION.md` |
| TASK-017 | DataHub AKShare sector daily bar adapter (including live rework closure) | Done | Phase 2 | `coordination/handoffs/TASK-017_DATAHUB_AKSHARE_SECTOR_DAILY_BAR_ADAPTER.md`; `coordination/handoffs/TASK-017_DATAHUB_SECTOR_LIVE_NETWORK_EVIDENCE_REWORK.md`; `coordination/handoffs/TASK-017_DATAHUB_SECTOR_LIVE_PASS_REWORK.md` | `coordination/reports/TASK-017_REPORT.md` | `coordination/reviews/TASK-017_REVIEW.md` | `coordination/integrations/TASK-017_INTEGRATION.md` |
| TASK-018 | DataHub AKShare sector master adapter (including live duplicate rework closure) | Done | Phase 2 | `coordination/handoffs/TASK-018_DATAHUB_AKSHARE_SECTOR_MASTER_ADAPTER.md`; `coordination/handoffs/TASK-018_DATAHUB_SECTOR_MASTER_LIVE_DUPLICATE_REWORK.md` | `coordination/reports/TASK-018_REPORT.md` | `coordination/reviews/TASK-018_REVIEW.md` | `coordination/integrations/TASK-018_INTEGRATION.md` |
| TASK-019 | DataHub AKShare sector membership adapter (including live evidence/PASS rework closure) | Done | Phase 2 | `coordination/handoffs/TASK-019_DATAHUB_AKSHARE_SECTOR_MEMBERSHIP_ADAPTER.md`; `coordination/handoffs/TASK-019_DATAHUB_SECTOR_MEMBERSHIP_LIVE_EVIDENCE_REWORK.md`; `coordination/handoffs/TASK-019_DATAHUB_SECTOR_MEMBERSHIP_LIVE_PASS_REWORK.md` | `coordination/reports/TASK-019_REPORT.md` | `coordination/reviews/TASK-019_REVIEW.md` | `coordination/integrations/TASK-019_INTEGRATION.md` |
| TASK-020 | DataHub AKShare index constituents adapter | Done | Phase 2 | `coordination/handoffs/TASK-020_DATAHUB_AKSHARE_INDEX_CONSTITUENTS_ADAPTER.md` | `coordination/reports/TASK-020_REPORT.md` | `coordination/reviews/TASK-020_REVIEW.md` | `coordination/integrations/TASK-020_INTEGRATION.md` |
| TASK-021 | DataHub AKShare global equity snapshot adapter (including live-route rework closure) | Done | Phase 2 | `coordination/handoffs/TASK-021_DATAHUB_AKSHARE_GLOBAL_EQUITY_SNAPSHOT_ADAPTER.md`; `coordination/handoffs/TASK-021_DATAHUB_GLOBAL_EQUITY_LIVE_NETWORK_REWORK.md`; `coordination/handoffs/TASK-021_DATAHUB_GLOBAL_EQUITY_SINA_KEYERROR_REWORK.md` | `coordination/reports/TASK-021_REPORT.md` | `coordination/reviews/TASK-021_REVIEW.md` | `coordination/integrations/TASK-021_INTEGRATION.md` |
| TASK-022 | DataHub AKShare news events adapter | Done | Phase 2 | `coordination/handoffs/TASK-022_DATAHUB_AKSHARE_NEWS_EVENTS_ADAPTER.md` | `coordination/reports/TASK-022_REPORT.md` | `coordination/reviews/TASK-022_REVIEW.md` | `coordination/integrations/TASK-022_INTEGRATION.md` |
| TASK-023 | DataHub HKEX company announcements adapter (including symbol-filter rework closure) | Done | Phase 2 | `coordination/handoffs/TASK-023_DATAHUB_HKEX_COMPANY_ANNOUNCEMENTS_ADAPTER.md`; `coordination/handoffs/TASK-023_DATAHUB_HKEX_SYMBOL_FILTER_REWORK.md` | `coordination/reports/TASK-023_REPORT.md` | `coordination/reviews/TASK-023_REVIEW.md` | `coordination/integrations/TASK-023_INTEGRATION.md` |
| TASK-024 | DataHub AKShare China macro adapter (including `is_preliminary` rework closure) | Done | Phase 2 | `coordination/handoffs/TASK-024_DATAHUB_AKSHARE_CHINA_MACRO_ADAPTER.md`; `coordination/handoffs/TASK-024_DATAHUB_CHINA_MACRO_PRELIMINARY_REWORK.md` | `coordination/reports/TASK-024_REPORT.md` | `coordination/reviews/TASK-024_REVIEW.md` | `coordination/integrations/TASK-024_INTEGRATION.md` |
| TASK-025 | DataHub local refresh metadata and quality baseline | Done | Phase 2 | `coordination/handoffs/TASK-025_DATAHUB_LOCAL_REFRESH_QUALITY_BASELINE.md` | `coordination/reports/TASK-025_REPORT.md` | `coordination/reviews/TASK-025_REVIEW.md` | `coordination/integrations/TASK-025_INTEGRATION.md` |
| TASK-026 | DataHub AKShare A-share instrument master adapter | Done | Phase 2 | `coordination/handoffs/TASK-026_DATAHUB_AKSHARE_A_SHARE_INSTRUMENT_MASTER_ADAPTER.md` | `coordination/reports/TASK-026_REPORT.md` | `coordination/reviews/TASK-026_REVIEW.md` | `coordination/integrations/TASK-026_INTEGRATION.md` |
| TASK-027 | DataHub AKShare A-share corporate actions adapter | Done | Phase 2 | `coordination/handoffs/TASK-027_DATAHUB_AKSHARE_A_SHARE_CORPORATE_ACTIONS_ADAPTER.md` | `coordination/reports/TASK-027_REPORT.md` | `coordination/reviews/TASK-027_REVIEW.md` | `coordination/integrations/TASK-027_INTEGRATION.md` |
| TASK-028 | DataHub AKShare A-share valuation snapshot adapter (including live-network rework closure) | Done | Phase 2 | `coordination/handoffs/TASK-028_DATAHUB_AKSHARE_A_SHARE_VALUATION_SNAPSHOT_ADAPTER.md`; `coordination/handoffs/TASK-028_DATAHUB_AKSHARE_A_SHARE_VALUATION_LIVE_NETWORK_REWORK.md` | `coordination/reports/TASK-028_REPORT.md` | `coordination/reviews/TASK-028_REVIEW.md` | `coordination/integrations/TASK-028_INTEGRATION.md` |
| TASK-029 | DataHub AKShare A-share capital flow snapshot adapter (including live-network rework closure) | Done | Phase 2 | `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_SNAPSHOT_ADAPTER.md`; `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_LIVE_NETWORK_REWORK.md` | `coordination/reports/TASK-029_REPORT.md` | `coordination/reviews/TASK-029_REVIEW.md` | `coordination/integrations/TASK-029_INTEGRATION.md` |
| TASK-030 | DataHub policy documents adapter | Done | Phase 2 | `coordination/handoffs/TASK-030_DATAHUB_POLICY_DOCUMENTS_ADAPTER.md` | `coordination/reports/TASK-030_REPORT.md` | `coordination/reviews/TASK-030_REVIEW.md` | `coordination/integrations/TASK-030_INTEGRATION.md` |
| TASK-031 | DataHub AKShare ETF/fund holdings adapter (including classifier rework closure) | Done | Phase 2 | `coordination/handoffs/TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_ADAPTER.md`; `coordination/handoffs/TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_CLASSIFIER_REWORK.md` | `coordination/reports/TASK-031_REPORT.md` | `coordination/reviews/TASK-031_REVIEW.md` | `coordination/integrations/TASK-031_INTEGRATION.md` |
| TASK-032 | DataHub AKShare Hong Kong instrument master adapter | Done | Phase 2 | `coordination/handoffs/TASK-032_DATAHUB_AKSHARE_HK_INSTRUMENT_MASTER_ADAPTER.md` | `coordination/reports/TASK-032_REPORT.md` | `coordination/reviews/TASK-032_REVIEW.md` | `coordination/integrations/TASK-032_INTEGRATION.md` |
| TASK-033 | DataHub AKShare Hong Kong corporate actions adapter | Done | Phase 2 | `coordination/handoffs/TASK-033_DATAHUB_AKSHARE_HK_CORPORATE_ACTIONS_ADAPTER.md` | `coordination/reports/TASK-033_REPORT.md` | `coordination/reviews/TASK-033_REVIEW.md` | `coordination/integrations/TASK-033_INTEGRATION.md` |
| TASK-034 | DataHub AKShare Hong Kong valuation snapshot adapter | Done | Phase 2 | `coordination/handoffs/TASK-034_DATAHUB_AKSHARE_HK_VALUATION_SNAPSHOT_ADAPTER.md` | `coordination/reports/TASK-034_REPORT.md` | `coordination/reviews/TASK-034_REVIEW.md` | `coordination/integrations/TASK-034_INTEGRATION.md` |
| TASK-035 | DataHub AKShare fund profile adapter | Done | Phase 2 | `coordination/handoffs/TASK-035_DATAHUB_AKSHARE_FUND_PROFILE_ADAPTER.md` | `coordination/reports/TASK-035_REPORT.md` | `coordination/reviews/TASK-035_REVIEW.md` | `coordination/integrations/TASK-035_INTEGRATION.md` |
| TASK-036 | DataHub source catalog implementation reconciliation | Done | Phase 2 | `coordination/handoffs/TASK-036_DATAHUB_SOURCE_CATALOG_RECONCILIATION.md` | `coordination/reports/TASK-036_REPORT.md` | `coordination/reviews/TASK-036_REVIEW.md` | `coordination/integrations/TASK-036_INTEGRATION.md` |
| TASK-037 | DataHub HKEX Hong Kong trading calendar adapter | Done | Phase 2 | `coordination/handoffs/TASK-037_DATAHUB_HKEX_HK_TRADING_CALENDAR_ADAPTER.md` | `coordination/reports/TASK-037_REPORT.md` | `coordination/reviews/TASK-037_REVIEW.md` | `coordination/integrations/TASK-037_INTEGRATION.md` |
| TASK-038 | DataHub AKShare ETF daily bar adapter (including live-network rework closure) | Done | Phase 2 | `coordination/handoffs/TASK-038_DATAHUB_AKSHARE_ETF_DAILY_BAR_ADAPTER.md`; `coordination/handoffs/TASK-038_DATAHUB_AKSHARE_ETF_DAILY_BAR_LIVE_NETWORK_REWORK.md` | `coordination/reports/TASK-038_REPORT.md` | `coordination/reviews/TASK-038_REVIEW.md` | `coordination/integrations/TASK-038_INTEGRATION.md` |
| TASK-039 | DataHub local warehouse refresh runner | Done | Phase 2 | `coordination/handoffs/TASK-039_DATAHUB_LOCAL_WAREHOUSE_REFRESH_RUNNER.md` | `coordination/reports/TASK-039_REPORT.md` | `coordination/reviews/TASK-039_REVIEW.md` | `coordination/integrations/TASK-039_INTEGRATION.md` |
