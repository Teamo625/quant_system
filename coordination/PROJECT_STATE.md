# Project State

Last updated by: 5.5 Controller

## Current Phase

Phase 2.5: DataHub Trading-Usable Hardening.

## Current Implementation Scope

DataHub trading-usable hardening is active because the owner replaced foundation-only phase gates with trading-usable completion gates. TASK-087 is closed, and TASK-088 is dispatched as the next handoff.

Current implementation may target only:

- `quant/datahub/`
- `tests/datahub/`

For `TASK-088` specifically, allowed implementation writes are:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_index_adapter.py`
- `tests/datahub/test_akshare_index_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-088_REPORT.md`

## Repository Status

Initialized:

- governance rules
- system architecture documents
- module boundaries
- data contracts
- task protocol
- testing policy
- coordination files
- compressed context snapshot
- placeholder module directories
- first DataHub handoff
- TASK-001 through TASK-005 completed Phase 1 DataHub foundation work
- Phase 1 completed by phase gate decision
- previous pre-rescope TASK-006 through TASK-009 Phase 2 handoffs and related code were removed after owner-directed Phase 2 scope change
- Phase 2 goal changed from selected source adapters to comprehensive full-domain data-source collection coverage
- TASK-006 through TASK-011 completed Phase 2 catalog/schema/validation/source-contract foundations
- TASK-012 through TASK-024 completed the first accepted real-source DataHub slices across A-share, HK, ETF/fund NAV, index, sector, global equity, news, announcements, and China macro domains
- TASK-025 completed the local refresh metadata and `DATA_QUALITY_REPORT` baseline
- TASK-026 completed AKShare A-share `instrument_master`
- TASK-027 completed AKShare A-share `corporate_actions`
- TASK-028 completed AKShare A-share `valuation_snapshot` after live-network rework; `float_market_cap` remains optional to preserve source-truth behavior
- TASK-029 completed AKShare A-share `capital_flow_snapshot` after live-network rework; primary `stock_individual_fund_flow` remains preferred with bounded one-symbol datacenter fallback for `RPT_FUNDFLOW_SECUCODE` only when primary route is unavailable
- TASK-030 completed public policy document metadata coverage for `DatasetName.POLICY_DOCUMENTS` under source id `macro_policy_public_sources`, with accepted live-enabled PASS evidence
- TASK-031 completed AKShare ETF/fund `fund_holdings` one-fund adapter coverage after classifier rework; the previous `ssl.SSLError`/`NameError` live-unavailability blocker is closed with accepted review, integration, and live-enabled PASS evidence
- TASK-032 completed AKShare Hong Kong stock `instrument_master` one-symbol adapter coverage, with accepted review, integration, and live-enabled PASS evidence
- TASK-033 completed AKShare Hong Kong stock `corporate_actions` one-symbol dividend/corporate-action coverage, with accepted review, integration, and live-enabled PASS evidence
- TASK-034 completed AKShare Hong Kong stock `valuation_snapshot` one-symbol coverage, with accepted review, integration, minimal HK source-catalog alignment, and live-enabled PASS evidence
- TASK-035 completed AKShare `fund_profile` one-fund adapter coverage, with accepted review, integration, and live-enabled PASS evidence
- TASK-036 completed DataHub source catalog implementation reconciliation, with accepted review/integration and offline-only PASS evidence
- TASK-037 completed HKEX Hong Kong `trading_calendar` adapter coverage, with accepted review, integration, and live-enabled PASS evidence
- TASK-038 completed AKShare China ETF exchange-traded `daily_bars` coverage after live-network rework, with accepted review, integration, and live-enabled PASS evidence
- TASK-039 completed the local-only DataHub warehouse refresh runner, tying `SourceResult` fetch output to raw JSONL persistence, curated schema-validated persistence, refresh metadata, and `DATA_QUALITY_REPORT` output with accepted review/integration and offline-only PASS evidence
- Phase 2 completed by phase gate decision after TASK-039 controller closure
- Phase 3 was opened for FeatureHub with TASK-040; TASK-040 is now closed after accepted trade-date validation rework
- Owner clarified that the intended next priority is not full local data collection, but completing DataHub source capability so all data needed for short-term and medium/long-term quant research can be accessed on demand
- Phase 3 is paused before execution and Phase 2.5 is opened to close the trading-grade DataHub source-capability gap
- TASK-041 completed the deterministic Phase 2.5 trading-grade source capability audit and gap matrix, with accepted review/integration and offline-only PASS evidence
- TASK-041 identified required no-`DatasetName` capability gaps that needed stable DataHub contracts before adapter implementation could continue
- TASK-042 completed stable DataHub dataset contracts for required TASK-041 no-mapping gaps (`MINUTE_BARS`, `MARGIN_FINANCING_LENDING`, `FINANCIAL_STATEMENTS`, `FINANCIAL_INDICATORS`, `MAJOR_ACTIVITY_EVENTS`, and `FUND_FLOW`), with accepted review/integration and offline-only PASS evidence
- TASK-043 completed a narrow public AKShare Hong Kong `FINANCIAL_STATEMENTS` / `FINANCIAL_INDICATORS` adapter slice, moved `hk_financial_data` to `partial`, and provided accepted review/integration plus live-enabled PASS evidence
- TASK-044 completed a narrow public AKShare A-share `FINANCIAL_STATEMENTS` / `FINANCIAL_INDICATORS` adapter slice, moved `a_share_financial_statements` and `a_share_financial_indicators` to `partial`, and provided accepted review/integration plus live-enabled PASS evidence
- TASK-045 completed AKShare A-share `MARGIN_FINANCING_LENDING` one-symbol/date-slice adapter coverage after live skip/fail classifier rework; route-name-bearing AKShare argument/signature compatibility errors now remain hard failures, default tests remain offline-safe, and live-enabled rework smoke result was PASS
- TASK-046 completed AKShare A-share `COMPANY_ANNOUNCEMENTS` one-symbol public-source adapter coverage, moved `a_share_company_announcements` to `partial`, kept default tests offline-safe, and provided accepted review/integration plus live-enabled PASS evidence
- TASK-047 completed a dedicated DataHub `LIMIT_UP_DOWN_EVENTS` source-fact contract for A-share limit-up/down capability, kept `a_share_limit_up_down` conservatively planned, kept default tests offline-safe, and provided accepted review/integration with no live test requirement because the task was contract-only
- TASK-048 completed bounded public AKShare A-share `LIMIT_UP_DOWN_EVENTS` adapter coverage, moved `a_share_limit_up_down` to `partial`, kept default tests offline-safe, and provided accepted review/integration plus live-enabled PASS evidence
- TASK-049 completed bounded public AKShare A-share `MAJOR_ACTIVITY_EVENTS` adapter coverage after live-route rework; `a_share_major_activity_events` remains `partial`, default tests remain offline-safe, and the reworked live-enabled smoke result was PASS with accepted review/integration
- TASK-050 completed bounded public AKShare A-share `MINUTE_BARS` adapter coverage; `a_share_minute_bars` is now `partial`, default tests remain offline-safe, and the live-enabled smoke result was PASS with accepted review/integration
- TASK-051 completed bounded public AKShare ETF/fund `FUND_FLOW` adapter coverage; `fund_flow` is now `partial`, `FUND_FLOW.net_inflow` is optional to preserve verified public exchange scale/share source truth, default tests remain offline-safe, and the live-enabled smoke result was PASS with accepted review
- TASK-052 completed a dedicated DataHub `SUSPENSION_RESUMPTION_EVENTS` source-fact contract for A-share suspension/resumption capability; `a_share_suspension_resumption` now maps to the dedicated contract and remains `planned`, default tests remain offline-safe, and no live test was required because the task was contract-only
- TASK-053 completed bounded public AKShare A-share `SUSPENSION_RESUMPTION_EVENTS` adapter coverage; `a_share_suspension_resumption` is now `partial`, default tests remain offline-safe, and the live-enabled smoke result was PASS with accepted review/integration
- TASK-054 completed offline macro/policy source-capability reconciliation; `macro_policy_public_sources` now reflects accepted public macro/policy source coverage, and `macro_observations`, `macro_indicator_definitions`, and `policy_documents` now reconcile to conservative `partial` status with accepted review/integration
- TASK-055 completed explicit DataHub `INDEX_WEIGHT_HISTORY` source-fact contracts for index x symbol x effective-date weight history; `index_weight_history` now maps to `DatasetName.INDEX_WEIGHT_HISTORY` and remains conservatively `planned` under credentialed `tushare_pro_cn_core`, with accepted review/integration and offline-only PASS evidence
- TASK-056 completed bounded repository-level Tushare Pro `INDEX_WEIGHT_HISTORY` adapter and gated smoke-test coverage with accepted review/integration; default tests remain offline-safe, but the live-enabled result was `SKIP` because local `TUSHARE_TOKEN` and `tushare` SDK prerequisites were absent, so live source coverage is not proven and `index_weight_history` remains conservatively `planned`
- TASK-057 completed Tushare `INDEX_WEIGHT_HISTORY` live-evidence/prerequisite rework with accepted review/integration; local `tushare` SDK availability is now confirmed, but live-enabled result remains `SKIP` because `TUSHARE_TOKEN` is unset, so live source coverage is still unproven and `index_weight_history` remains conservatively `planned`
- TASK-058 completed offline `index_weight_history` capability metadata reconciliation with accepted review; stale wording was corrected, default tests remained offline-safe, and the capability remains conservatively `planned` pending credentialed Tushare live PASS evidence
- TASK-059 initial credentialed live PASS execution and subsequent retry reworks produced truthful `BLOCKED / SKIP` reports because `TUSHARE_TOKEN` was unset; Review requires another token-required rework because no credentialed live smoke ran and no `INDEX_WEIGHT_HISTORY` live PASS evidence exists
- Owner directed skipping the paid Tushare credentialed live PASS path for now because it requires a paid credential; TASK-059 is retained as a blocked follow-up and does not block reopening Phase 3
- TASK-040 completed FeatureHub foundation contracts after accepted trade-date validation rework; default tests remain offline-safe and no live tests were required
- TASK-060 completed pure offline FeatureHub price technical primitives with accepted review; default tests remain offline-safe and no live tests were required
- TASK-061 completed pure offline FeatureHub valuation primitives with accepted review; default tests remain offline-safe and no live tests were required
- TASK-062 completed pure offline FeatureHub capital-flow primitives with accepted review; default tests remain offline-safe and no live tests were required
- TASK-063 completed FeatureHub output persistence/versioning after accepted rework; `write_feature_records_jsonl(...)` now preflights manifest path conflicts to avoid partially replacing records JSONL when `overwrite=False`, default tests remain offline-safe, and no live tests were required
- Phase 3 completed by phase gate decision after TASK-063 controller closure
- Phase 4 opened for Scanner; TASK-064 is dispatched as the first Scanner foundation contract task
- TASK-064 completed pure offline Scanner foundation contracts with accepted review; default tests remain offline-safe and no live tests were required
- TASK-065 is dispatched for pure offline Scanner universe validation helpers
- TASK-065 completed pure offline Scanner universe validation helpers with accepted review; default tests remain offline-safe and no live tests were required
- TASK-066 is dispatched for pure local Scanner candidate-list persistence of already-built artifacts
- TASK-066 completed pure local Scanner candidate-list persistence with accepted review; default tests remain offline-safe and no live tests were required
- TASK-067 completed pure offline Scanner filter matching primitives over caller-provided feature values with accepted review; default tests remain offline-safe and no live tests were required
- TASK-068 completed pure offline in-memory Scanner scan runner primitives over caller-provided universe, feature values, and filters with accepted review; default tests remain offline-safe and no live tests were required
- Phase 4 completed by phase gate decision after TASK-068 controller closure
- Phase 5 opened for StrategyLab and BacktestEngine; TASK-069 is dispatched as the first foundation contract task
- TASK-069 completed pure offline StrategyLab and BacktestEngine foundation contracts with accepted review; default tests remain offline-safe and no live tests were required
- TASK-070 was dispatched for pure offline BacktestEngine historical replay primitives, then deferred back to Backlog after the owner required trading-usable phase gates
- Previously closed Phase 2/2.5, Phase 3, and Phase 4 work is now treated as foundation-complete but trading-usable incomplete until audited and hardened against `coordination/ROADMAP.md`
- Phase 2.5 DataHub Trading-Usable Hardening is reopened as the earliest incomplete prerequisite phase
- TASK-071 completed the DataHub trading-usable gap audit with accepted review; it found DataHub not closure-ready because most real-source capabilities remain partial, with the biggest systemic gap in batch/parameterized access
- TASK-072 is dispatched to harden A-share daily bars from one-symbol source slices to caller-provided multi-symbol batch access with gated live evidence
- TASK-072 completed A-share daily bars batch hardening with accepted review and live-enabled PASS evidence; `a_share_daily_bars` is now `covered`
- TASK-073 completed A-share instrument status-history contracts with accepted review; `a_share_listing_delisting_st_status` now maps to `DatasetName.INSTRUMENT_STATUS_HISTORY` and remains `partial`
- TASK-074 completed bounded public AKShare A-share instrument status-history adapter coverage with accepted review and live-enabled PASS evidence; `a_share_listing_delisting_st_status` remains conservative rather than over-promoted
- TASK-075 completed A-share valuation batch/date-window hardening with accepted review and live-enabled PASS evidence; `a_share_valuation_history` remains conservative because broader history/pagination remains incomplete
- TASK-076 completed A-share capital-flow/northbound batch/date-window hardening with accepted review and live-enabled PASS evidence; `a_share_capital_flow` and `a_share_northbound_flow` remain conservative because broader history and dedicated northbound coverage remain incomplete
- TASK-077 completed A-share financial statements/indicators batch/report-period hardening with accepted review and live-enabled PASS evidence; `a_share_financial_statements` and `a_share_financial_indicators` remain conservative because broader public-source history/breadth remains unproven
- TASK-078 completed A-share minute-bars batch/date-window hardening with accepted review and live-enabled PASS evidence; `a_share_minute_bars` remains conservative because broader intraday history continuity and full trading-grade breadth remain incomplete
- Phase gate after TASK-078: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; HK daily bars and HK universe breadth remain `partial`, and later ETF/fund, index, sector, macro/policy, source-health, and paid credential gaps still require accepted hardening or explicit owner waiver
- TASK-079 is dispatched for Hong Kong daily-bars batch/resilience hardening with gated live smoke evidence
- TASK-079 completed Hong Kong daily-bars batch/resilience hardening with accepted review and live-enabled PASS evidence; `hk_daily_bars` remains conservative because broader history continuity and public-source redundancy remain incomplete
- Phase gate after TASK-079: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; HK universe reference remains `partial`, and later ETF/fund, index, sector, macro/policy, source-health, and paid credential gaps still require accepted hardening or explicit owner waiver
- TASK-080 completed Hong Kong instrument-master/universe-reference batch hardening with accepted review and live-enabled PASS evidence; `hk_universe_reference` remains conservative because full-market HK universe collection, dated lifecycle reconstruction, and non-stock taxonomy remain incomplete
- Phase gate after TASK-080: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; HK financial data remains `partial`, and later ETF/fund, index, sector, macro/policy, source-health, and paid credential gaps still require accepted hardening or explicit owner waiver
- TASK-081 completed Hong Kong financial statements/indicators batch/report-period hardening with accepted review and live-enabled PASS evidence; `hk_financial_data` remains conservative because broader HK market breadth and long-history continuity remain incomplete
- Phase gate after TASK-081: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; ETF/fund daily/NAV/holdings/flow breadth and history remain partial, and later index, sector, macro/policy, source-health, and paid credential gaps still require accepted hardening or explicit owner waiver
- TASK-082 completed ETF/fund daily-bars batch/date-window hardening with accepted review and live-enabled PASS evidence; `fund_daily_bars` remains conservative because broader fund breadth, longer history continuity, and non-ETF public-route coverage remain incomplete
- Phase gate after TASK-082: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; ETF/fund NAV/holdings/flow breadth and history remain partial, and later index, sector, macro/policy, source-health, and paid credential gaps still require accepted hardening or explicit owner waiver
- TASK-083 completed ETF/fund NAV batch/date-window hardening with accepted review and live-enabled PASS evidence; `fund_nav` remains conservative because broader fund breadth, longer history continuity, and non-exchange public-route coverage remain incomplete
- Phase gate after TASK-083: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; ETF/fund holdings, scale/share, flow, premium/discount, index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver
- TASK-084 completed ETF/fund holdings batch/report-period hardening with accepted review and live-enabled PASS evidence; `fund_holdings_composition` remains conservative because broader fund breadth, longer history continuity, and non-exchange public-route coverage remain incomplete
- Phase gate after TASK-084: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; ETF/fund scale/share, flow, premium/discount, index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver
- TASK-085 completed ETF/fund flow batch/date-window hardening with accepted review and live-enabled PASS evidence; `fund_flow` remains conservative because broader flow metrics, non-exchange breadth, and longer history continuity remain incomplete
- Phase gate after TASK-085: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; ETF/fund premium/discount, index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver
- TASK-086 completed contract-only ETF/fund premium-discount source-fact schema hardening with accepted review; `fund_premium_discount` now maps to `DatasetName.FUND_PREMIUM_DISCOUNT` while remaining conservative
- Phase gate after TASK-086: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; ETF/fund premium-discount still lacks adapter-backed public source evidence, and index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver
- TASK-087 completed bounded public ETF/fund premium-discount adapter/source-fact coverage with accepted review and live-enabled PASS evidence; `fund_premium_discount` remains conservative because latest-available snapshot breadth/history limitations remain
- Phase gate after TASK-087: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver
- TASK-088 is dispatched for bounded public index daily-bars batch/benchmark hardening with gated live smoke evidence

## Active Constraints

- Current phase is DataHub trading-usable hardening only.
- TASK-088 is dispatched as the active DataHub hardening handoff.
- Future DataHub hardening handoffs may target only `quant/datahub/` and `tests/datahub/` unless explicitly expanded by the controller.
- Paid/private credential gaps must be recorded as Blocked unless the owner provides credentials or explicitly waives them.
- Do not implement FeatureHub indicators until DataHub hardening is accepted or explicitly blocked/waived.
- Do not implement scanner ranking, scoring, or stock-picking logic until FeatureHub hardening is accepted or explicitly blocked/waived.
- Do not implement concrete trading strategies or backtest execution until Scanner hardening is accepted or explicitly blocked/waived and Phase 5 is reopened.
- Do not implement portfolio, signal, or risk logic.
- Do not implement AI reports.
- Do not implement notifications.
- Do not implement automated trading.
- Do not implement complex UI.
- Default tests must not use live network access.
- Live tests require explicit handoff permission and environment-variable gating.
- Real source adapter and real data-fetching tasks remain DataHub-owned and require a gated live smoke test when explicitly assigned; default tests must still skip it unless explicitly enabled.
- Live-enabled network/proxy/DNS/TLS/upstream failures must be routed to a 5.3 execution rework for diagnosis and feasible repository fixes, then independently reviewed before integration or controller closure.
- Execution windows must not update project state files.

## Prior Phase Gate Decision

Phase 2 remains complete for its original approved scope, but the owner has opened a new Phase 2.5 before FeatureHub execution.

Reasons:

- Current Phase 2 deliverables are valuable but intentionally narrow in many adapters (`one-symbol`, `one-fund`, selected indicators, and single-request refresh).
- The required product milestone is a complete data-source capability layer, not merely a representative source-slice layer.
- The system should be able to access all data domains required for rigorous short-term and medium/long-term quant research before FeatureHub proceeds.
- At the time of the Phase 2.5 branch, TASK-040 had not produced lifecycle artifacts, so pausing Phase 3 did not require rejecting completed implementation work.

Phase switch: YES, to Phase 2.5.

## TASK-059 Phase Gate Decision

TASK-059 is skipped as an active Phase 2.5 gate and retained as a blocked paid-credential follow-up.

The TASK-059 Review Agent decision is `REWORK REQUIRED`. The blocked execution matched the handoff precondition and did not introduce implementation/test changes, but the task objective remains unmet:

- no credentialed live smoke ran
- no schema-valid `DatasetName.INDEX_WEIGHT_HISTORY` record was validated through the Tushare adapter path
- `index_weight_history` remains conservatively `planned`

The owner directed skipping this paid-token path for now because `TUSHARE_TOKEN` requires a paid credential. The controller does not mark TASK-059 Done and does not promote `index_weight_history`; instead, TASK-059 moves to the blocked backlog as an explicit paid-credential follow-up. Phase 2.5 is complete for the no-paid-credential scope, with the residual limitation recorded.

Phase switch: YES, to Phase 3.

## TASK-040 Closure

TASK-040 is closed after Review Agent acceptance of the trade-date validation rework.

Review result:

- `coordination/reviews/TASK-040_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-040 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-040:

- Phase switch: NO
- Reason: Phase 3 still has incomplete FeatureHub goals for technical feature calculation, valuation/capital-flow feature slices, and feature output persistence/versioning.

## TASK-060 Closure

TASK-060 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-060_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-060 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-060:

- Phase switch: NO
- Reason: Phase 3 still has incomplete FeatureHub goals for valuation/capital-flow feature slices and feature output persistence/versioning.

## TASK-061 Closure

TASK-061 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-061_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-061 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-061:

- Phase switch: NO
- Reason: Phase 3 still has incomplete FeatureHub goals for capital-flow feature primitives and feature output persistence/versioning.

## TASK-062 Closure

TASK-062 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-062_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-062 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-062:

- Phase switch: NO
- Reason: Phase 3 still has incomplete FeatureHub goals for feature output persistence/versioning.

## TASK-063 Closure

TASK-063 is closed after Review Agent acceptance of the output persistence/versioning rework.

Review result:

- `coordination/reviews/TASK-063_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-063 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-063:

- Phase switch: YES, to Phase 4 Scanner
- Reason: Phase 3 goals are complete: FeatureHub contracts, technical primitives, valuation primitives, capital-flow primitives, and feature output persistence/versioning all have accepted reports/reviews and no active Phase 3 blockers remain.

## Next Task

`TASK-064`: Scanner foundation contracts.

Handoff:

- `coordination/handoffs/TASK-064_SCANNER_FOUNDATION_CONTRACTS.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-064_REPORT.md`
- review: `coordination/reviews/TASK-064_REVIEW.md`
- integration: N/A until review acceptance

## TASK-064 Closure

TASK-064 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-064_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-064 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-064:

- Phase switch: NO
- Reason: Phase 4 still has incomplete Scanner goals for universe handling, scan execution/candidate production, and scan artifact persistence.

## Next Task

`TASK-065`: Scanner universe validation helpers.

Handoff:

- `coordination/handoffs/TASK-065_SCANNER_UNIVERSE_VALIDATION_HELPERS.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-065_REPORT.md`
- review: `coordination/reviews/TASK-065_REVIEW.md`
- integration: N/A until review acceptance

## TASK-065 Closure

TASK-065 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-065_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-065 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-065:

- Phase switch: NO
- Reason: Phase 4 still has incomplete Scanner goals for scan artifact persistence and later screening/candidate production.

## Next Task

`TASK-066`: Scanner candidate-list persistence.

Handoff:

- `coordination/handoffs/TASK-066_SCANNER_CANDIDATE_LIST_PERSISTENCE.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-066_REPORT.md`
- review: `coordination/reviews/TASK-066_REVIEW.md`
- integration: N/A until review acceptance

## TASK-066 Closure

TASK-066 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-066_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-066 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-066:

- Phase switch: NO
- Reason: Phase 4 still has incomplete Scanner goals for offline filter matching and later candidate production.

## Next Task

`TASK-067`: Scanner filter matching primitives.

Handoff:

- `coordination/handoffs/TASK-067_SCANNER_FILTER_MATCHING_PRIMITIVES.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-067_REPORT.md`
- review: `coordination/reviews/TASK-067_REVIEW.md`
- integration: N/A until review acceptance

## TASK-067 Closure

TASK-067 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-067_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-067 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-067:

- Phase switch: NO
- Reason: Phase 4 still has incomplete Scanner goals for local scan execution and candidate production; TASK-067 only completed filter matching primitives.

## TASK-068 Dispatch

`TASK-068`: Scanner scan runner primitives.

Handoff:

- `coordination/handoffs/TASK-068_SCANNER_SCAN_RUNNER_PRIMITIVES.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-068_REPORT.md`
- review: `coordination/reviews/TASK-068_REVIEW.md`
- integration: N/A until review acceptance

## TASK-068 Closure

TASK-068 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-068_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-068 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-068:

- Phase switch: YES, to Phase 5 StrategyLab and BacktestEngine
- Reason: Phase 4 foundation/local artifact goals are complete: Scanner contracts, universe helpers, candidate-list persistence, filter matching, and in-memory scan runner primitives all have accepted reports/reviews and no active Phase 4 blockers remain.

## Next Task

`TASK-069`: StrategyLab and BacktestEngine foundation contracts.

Handoff:

- `coordination/handoffs/TASK-069_STRATEGY_BACKTEST_FOUNDATION_CONTRACTS.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-069_REPORT.md`
- review: `coordination/reviews/TASK-069_REVIEW.md`
- integration: N/A until review acceptance

## TASK-069 Closure

TASK-069 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-069_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-069 is not a real-source task and live tests were forbidden

Phase gate decision after TASK-069:

- Phase switch: NO
- Reason: Phase 5 still has incomplete StrategyLab and BacktestEngine goals for historical replay, cost/slippage assumptions beyond foundation configuration, and report generation.

## TASK-070 Dispatch

`TASK-070`: BacktestEngine historical replay primitives.

Handoff:

- `coordination/handoffs/TASK-070_BACKTEST_HISTORICAL_REPLAY_PRIMITIVES.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-070_REPORT.md`
- review: `coordination/reviews/TASK-070_REVIEW.md`
- integration: N/A until review acceptance

## Phase Gate Decision

The owner replaced the prior foundation-only gate interpretation with trading-usable completion gates. Under the updated standard, the earliest incomplete prerequisite phase is DataHub because many Phase 2/2.5 capabilities were representative, narrow, partial, planned, or blocked rather than proven broad enough for practical quant workflows.

Decision:

- Phase switch: REOPENED PRIOR PHASE, to Phase 2.5 DataHub Trading-Usable Hardening
- TASK-070 moved from Active to Backlog as Phase 5 deferred
- TASK-071 is the new Active audit-only handoff
- Phase 5 must not continue until DataHub hardening is accepted or explicitly blocked/waived, then FeatureHub is reopened and hardened, then Scanner is reopened and hardened

Capability audit requirement:

- TASK-071 must classify DataHub capabilities as covered, partial, planned, missing, or blocked
- TASK-071 must identify paid/private credential gaps as Blocked
- TASK-071 must recommend the next executable DataHub hardening handoff
- After TASK-071 Review is accepted, Controller must dispatch a concrete DataHub capability补齐 task and must not jump back to Phase 5

## TASK-071 Closure

TASK-071 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-071_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-071 was audit-only and live tests were forbidden

Phase gate decision after TASK-071:

- Phase switch: NO
- Reason: DataHub remains below the trading-usable completion standard. The TASK-071 audit found 11 covered, 42 partial, 1 planned, and 1 optional missing capability, with a practical paid `TUSHARE_TOKEN` blocker for index weight history.

## TASK-072 Dispatch

`TASK-072`: DataHub A-share daily bars batch hardening.

Handoff:

- `coordination/handoffs/TASK-072_DATAHUB_A_SHARE_DAILY_BARS_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-072_REPORT.md`
- review: `coordination/reviews/TASK-072_REVIEW.md`
- integration: N/A until review acceptance

## TASK-072 Closure

TASK-072 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-072_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_live.py` passed for the multi-symbol A-share daily-bar smoke

Phase gate decision after TASK-072:

- Phase switch: NO
- Reason: `a_share_daily_bars` is now covered, but DataHub still has remaining Phase 2.5 trading-usable gaps from TASK-071. TASK-073 was dispatched as the next contract hardening handoff.

## TASK-073 Dispatch

`TASK-073`: DataHub A-share instrument status history contracts.

Handoff:

- `coordination/handoffs/TASK-073_DATAHUB_A_SHARE_INSTRUMENT_STATUS_HISTORY_CONTRACTS.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-073_REPORT.md`
- review: `coordination/reviews/TASK-073_REVIEW.md`
- integration: N/A until review acceptance

## TASK-073 Closure

TASK-073 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-073_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-073 was contract-only and explicitly forbade live/source-fetch work

Phase gate decision after TASK-073:

- Phase switch: NO
- Reason: `a_share_listing_delisting_st_status` now has a dedicated `INSTRUMENT_STATUS_HISTORY` contract, but DataHub still does not have adapter-backed and live-proven A-share listing/delisting/ST/status-history coverage. Phase 2.5 remains incomplete under `coordination/ROADMAP.md` because TASK-071 found many remaining partial capabilities, and TASK-073 only closed the contract part of this capability.

## TASK-074 Dispatch

`TASK-074`: DataHub AKShare A-share instrument status history adapter.

Handoff:

- `coordination/handoffs/TASK-074_DATAHUB_AKSHARE_A_SHARE_INSTRUMENT_STATUS_HISTORY_ADAPTER.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-074_REPORT.md`
- review: `coordination/reviews/TASK-074_REVIEW.md`
- integration: N/A until review acceptance

## TASK-074 Closure

TASK-074 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-074_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS for the gated A-share instrument status-history smoke
- Rework required: NO

Phase gate decision after TASK-074:

- Phase switch: NO
- Reason: TASK-074 adds bounded adapter-backed and live-proven A-share instrument status-history access, but Phase 2.5 remains incomplete under `coordination/ROADMAP.md`. TASK-071 still identifies remaining partial capabilities, including A-share valuation/capital-flow/financial-history batch and historical-window gaps that feed medium/long-term research.

## TASK-075 Dispatch

`TASK-075`: DataHub A-share valuation batch hardening.

Handoff:

- `coordination/handoffs/TASK-075_DATAHUB_A_SHARE_VALUATION_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-075_REPORT.md`
- review: `coordination/reviews/TASK-075_REVIEW.md`
- integration: N/A until review acceptance

## TASK-075 Closure

TASK-075 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-075_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py` passed for the gated multi-symbol A-share valuation smoke
- Rework required: NO

Phase gate decision after TASK-075:

- Phase switch: NO
- Reason: TASK-075 proves caller-provided multi-symbol bounded near-year A-share valuation access, but `a_share_valuation_history` remains `partial` and Phase 2.5 remains incomplete under `coordination/ROADMAP.md`. TASK-071 still identifies remaining partial capabilities, including A-share capital-flow/northbound and financial-history batch/history gaps that feed medium/long-term research.

## TASK-076 Dispatch

`TASK-076`: DataHub A-share capital-flow batch hardening.

Handoff:

- `coordination/handoffs/TASK-076_DATAHUB_A_SHARE_CAPITAL_FLOW_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-076_REPORT.md`
- review: `coordination/reviews/TASK-076_REVIEW.md`
- integration: N/A until review acceptance

## TASK-076 Closure

TASK-076 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-076_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` passed for the gated multi-symbol A-share capital-flow smoke
- Rework required: NO

Phase gate decision after TASK-076:

- Phase switch: NO
- Reason: TASK-076 proves caller-provided multi-symbol bounded A-share capital-flow access, but `a_share_capital_flow` and `a_share_northbound_flow` remain `partial`, and Phase 2.5 remains incomplete under `coordination/ROADMAP.md`. TASK-071 still identifies remaining partial capabilities, including A-share financial-statement/financial-indicator batch/history gaps, A-share minute-bar expansion, HK/ETF/fund/index/sector breadth and history, macro/policy depth, and source health metadata. No integration is entered for TASK-076 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-077 Dispatch

`TASK-077`: DataHub A-share financial history batch hardening.

Handoff:

- `coordination/handoffs/TASK-077_DATAHUB_A_SHARE_FINANCIAL_HISTORY_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-077_REPORT.md`
- review: `coordination/reviews/TASK-077_REVIEW.md`
- integration: N/A until review acceptance

## TASK-077 Closure

TASK-077 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-077_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py` passed for the gated two-symbol A-share financial statements/indicators smoke
- Rework required: NO

Phase gate decision after TASK-077:

- Phase switch: NO
- Reason: TASK-077 proves caller-provided multi-symbol bounded A-share financial statements/indicators access, but `a_share_financial_statements` and `a_share_financial_indicators` remain `partial`, and Phase 2.5 remains incomplete under `coordination/ROADMAP.md`. TASK-071 still identifies remaining partial capabilities, including A-share minute-bar expansion, HK/ETF/fund/index/sector breadth and history, macro/policy depth, source health metadata, and blocked paid index-weight live proof. No integration is entered for TASK-077 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-078 Dispatch

`TASK-078`: DataHub A-share minute bars batch/window hardening.

Handoff:

- `coordination/handoffs/TASK-078_DATAHUB_A_SHARE_MINUTE_BARS_BATCH_WINDOW_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-078_REPORT.md`
- review: `coordination/reviews/TASK-078_REVIEW.md`
- integration: N/A until review acceptance

## TASK-078 Closure

TASK-078 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-078_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` passed for the gated two-symbol A-share minute-bar smoke
- Rework required: NO

Phase gate decision after TASK-078:

- Phase switch: NO
- Reason: TASK-078 proves caller-provided multi-symbol bounded A-share minute-bar access, but `a_share_minute_bars` remains `partial` because broader intraday history continuity and full trading-grade source breadth remain unproven. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: HK daily bars and HK universe reference remain `partial`, and TASK-071 still identifies ETF/fund, index, sector, macro/policy, source-health, and blocked paid index-weight gaps that require accepted hardening or explicit owner waiver. No integration is entered for TASK-078 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-079 Dispatch

`TASK-079`: DataHub Hong Kong daily bars batch/resilience hardening.

Handoff:

- `coordination/handoffs/TASK-079_DATAHUB_HK_DAILY_BARS_BATCH_RESILIENCE_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-079_REPORT.md`
- review: `coordination/reviews/TASK-079_REVIEW.md`
- integration: N/A until review acceptance

## TASK-079 Closure

TASK-079 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-079_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py` passed for the gated two-symbol Hong Kong daily-bars smoke
- Rework required: NO

Phase gate decision after TASK-079:

- Phase switch: NO
- Reason: TASK-079 proves caller-provided multi-symbol bounded Hong Kong daily-bar access with source-resilience handling, but `hk_daily_bars` remains `partial` because broader HK history continuity and public-source redundancy remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: HK universe reference remains `partial`, and TASK-071 still identifies ETF/fund, index, sector, macro/policy, source-health, and blocked paid index-weight gaps that require accepted hardening or explicit owner waiver. No integration is entered for TASK-079 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-080 Dispatch

`TASK-080`: DataHub Hong Kong universe reference batch hardening.

Handoff:

- `coordination/handoffs/TASK-080_DATAHUB_HK_UNIVERSE_REFERENCE_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-080_REPORT.md`
- review: `coordination/reviews/TASK-080_REVIEW.md`
- integration: N/A until review acceptance

## TASK-080 Closure

TASK-080 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-080_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` passed for the gated two-symbol Hong Kong stock-reference smoke
- Rework required: NO

Phase gate decision after TASK-080:

- Phase switch: NO
- Reason: TASK-080 proves caller-provided multi-symbol bounded Hong Kong stock-reference access, but `hk_universe_reference` remains `partial` because full-market HK universe collection, dated lifecycle reconstruction, and non-stock taxonomy remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: HK financial data remains `partial`, and TASK-071 still identifies ETF/fund, index, sector, macro/policy, source-health, and blocked paid index-weight gaps that require accepted hardening or explicit owner waiver. No integration is entered for TASK-080 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-081 Dispatch

`TASK-081`: DataHub Hong Kong financial history batch hardening.

Handoff:

- `coordination/handoffs/TASK-081_DATAHUB_HK_FINANCIAL_HISTORY_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-081_REPORT.md`
- review: `coordination/reviews/TASK-081_REVIEW.md`
- integration: N/A until review acceptance

## TASK-081 Closure

TASK-081 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-081_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py` passed with both `00700.HK` and `00005.HK` covered for statements and indicators
- Rework required: NO

Phase gate decision after TASK-081:

- Phase switch: NO
- Reason: TASK-081 proves caller-provided multi-symbol bounded Hong Kong financial statements/indicators access, but `hk_financial_data` remains `partial` because broader HK market breadth and long-history continuity remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: ETF/fund daily/NAV/holdings/flow breadth and history remain partial, and TASK-071 still identifies index, sector, macro/policy, source-health, and blocked paid index-weight gaps that require accepted hardening or explicit owner waiver. No integration is entered for TASK-081 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-082 Dispatch

`TASK-082`: DataHub ETF/fund daily bars batch hardening.

Handoff:

- `coordination/handoffs/TASK-082_DATAHUB_ETF_DAILY_BARS_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-082_REPORT.md`
- review: `coordination/reviews/TASK-082_REVIEW.md`
- integration: N/A until review acceptance

## TASK-082 Closure

TASK-082 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-082_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py` passed for the gated two-symbol ETF/fund daily-bars smoke
- Rework required: NO

Phase gate decision after TASK-082:

- Phase switch: NO
- Reason: TASK-082 proves caller-provided multi-symbol bounded ETF/fund daily-bar access for supported exchange ETF/fund codes, but `fund_daily_bars` remains `partial` because broader fund breadth, longer history continuity, and non-ETF public-route coverage remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: ETF/fund NAV, holdings, scale/share, flow, and premium/discount remain partial, and TASK-071 still identifies index, sector, macro/policy, source-health, and blocked paid index-weight gaps that require accepted hardening or explicit owner waiver. No integration is entered for TASK-082 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-083 Dispatch

`TASK-083`: DataHub ETF/fund NAV batch hardening.

Handoff:

- `coordination/handoffs/TASK-083_DATAHUB_ETF_FUND_NAV_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-083_REPORT.md`
- review: `coordination/reviews/TASK-083_REVIEW.md`
- integration: N/A until review acceptance

## TASK-083 Closure

TASK-083 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-083_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py` passed for the gated two-symbol ETF/fund NAV smoke
- Rework required: NO

Phase gate decision after TASK-083:

- Phase switch: NO
- Reason: TASK-083 proves caller-provided multi-symbol bounded ETF/fund NAV access for supported public exchange ETF/fund routes, but `fund_nav` remains `partial` because broader fund breadth, longer history continuity, and non-exchange public-route coverage remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: ETF/fund holdings, scale/share, flow, premium/discount, index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver. No integration is entered for TASK-083 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-084 Dispatch

`TASK-084`: DataHub ETF/fund holdings batch hardening.

Handoff:

- `coordination/handoffs/TASK-084_DATAHUB_ETF_FUND_HOLDINGS_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-084_REPORT.md`
- review: `coordination/reviews/TASK-084_REVIEW.md`
- integration: N/A until review acceptance

## TASK-084 Closure

TASK-084 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-084_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py` passed for the gated two-symbol ETF/fund holdings smoke
- Rework required: NO

Phase gate decision after TASK-084:

- Phase switch: NO
- Reason: TASK-084 proves caller-provided multi-symbol bounded ETF/fund holdings access for supported public AKShare exchange ETF/fund routes, but `fund_holdings_composition` remains `partial` because broader fund breadth, longer history continuity, and non-exchange public-route coverage remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: ETF/fund scale/share, flow, premium/discount, index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver. No integration is entered for TASK-084 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-085 Dispatch

`TASK-085`: DataHub ETF/fund flow batch hardening.

Handoff:

- `coordination/handoffs/TASK-085_DATAHUB_ETF_FUND_FLOW_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-085_REPORT.md`
- review: `coordination/reviews/TASK-085_REVIEW.md`
- integration: N/A until review acceptance

## TASK-085 Closure

TASK-085 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-085_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py` passed for the gated two-symbol ETF/fund flow smoke
- Rework required: NO

Phase gate decision after TASK-085:

- Phase switch: NO
- Reason: TASK-085 proves caller-provided multi-symbol bounded ETF/fund exchange scale/share access through `FUND_FLOW`, but `fund_flow` remains `partial` because broader net-inflow/subscription/redemption metrics, non-exchange breadth, and longer history continuity remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: ETF/fund premium/discount still lacks a dedicated validated contract target, and TASK-071 still identifies index, sector, macro/policy, source-health, and blocked paid index-weight gaps that require accepted hardening or explicit owner waiver. No integration is entered for TASK-085 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-086 Dispatch

`TASK-086`: DataHub ETF/fund premium-discount contracts.

Handoff:

- `coordination/handoffs/TASK-086_DATAHUB_ETF_FUND_PREMIUM_DISCOUNT_CONTRACTS.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-086_REPORT.md`
- review: `coordination/reviews/TASK-086_REVIEW.md`
- integration: N/A until review acceptance

## TASK-086 Closure

TASK-086 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-086_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-086 was contract-only and explicitly forbade live/source work
- Rework required: NO

Phase gate decision after TASK-086:

- Phase switch: NO
- Reason: TASK-086 adds the dedicated `DatasetName.FUND_PREMIUM_DISCOUNT` contract and wires `fund_premium_discount` capability metadata to it, but it is contract-only and does not prove adapter-backed public source access. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: ETF/fund premium-discount source-fact adapter evidence, index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver. No integration is entered for TASK-086 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-087 Dispatch

`TASK-087`: DataHub ETF/fund premium-discount adapter.

Handoff:

- `coordination/handoffs/TASK-087_DATAHUB_ETF_FUND_PREMIUM_DISCOUNT_ADAPTER.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-087_REPORT.md`
- review: `coordination/reviews/TASK-087_REVIEW.md`
- integration: N/A until review acceptance

## TASK-087 Closure

TASK-087 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-087_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; the gated ETF/fund premium-discount smoke passed for the requested multi-symbol source-fact path
- Rework required: NO

Phase gate decision after TASK-087:

- Phase switch: NO
- Reason: TASK-087 proves bounded public ETF/fund premium-discount adapter/source-fact access, but `fund_premium_discount` remains conservative because latest-available snapshot breadth/history limitations remain. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver. No integration is entered for TASK-087 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-088 Dispatch

`TASK-088`: DataHub index daily-bars batch hardening.

Handoff:

- `coordination/handoffs/TASK-088_DATAHUB_INDEX_DAILY_BARS_BATCH_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-088_REPORT.md`
- review: `coordination/reviews/TASK-088_REVIEW.md`
- integration: N/A until review acceptance
