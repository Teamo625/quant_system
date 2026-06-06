# Project State

Last updated by: 5.5 Controller

## Current Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review.

## Current Implementation Scope

Phase 2.5 Core DataHub hardening is historical no-paid source-capability progress, with paid Tushare index-weight live proof retained as an owner-approved blocked follow-up. The owner has reopened DataHub as Phase 2.5-P before FeatureHub resumes because every phase, including historically completed foundation phases, must reach the strongest practical public-source/no-paid personal quantitative trading perfection standard before being treated as final.

Current implementation may target only:

- `quant/datahub/`
- `tests/datahub/`

For the active `TASK-096` BaoStock history-source review specifically, implementation is complete and the next role is Review Agent.

Expected next write path:

- `coordination/reviews/TASK-096_REVIEW.md`

Review should assess the owner-authorized BaoStock public-source replacement path recorded in commit `e3138fe` and `coordination/reports/TASK-096_REPORT.md`.

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
- TASK-088 completed bounded public index daily-bars batch/benchmark hardening with accepted review and live-enabled PASS evidence; `index_daily_bars` remains conservative because broader benchmark breadth, longer history continuity, and non-mainland/global benchmark coverage remain incomplete
- Phase gate after TASK-088: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; index constituent/rebalance metadata, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver
- TASK-089 completed bounded public index constituents batch/rebalance metadata hardening with accepted review and live-enabled PASS evidence; `index_constituent_history` and `index_rebalance_effective_dates` remain conservative because broader benchmark breadth, longer constituent continuity, and explicit rebalance-calendar truth remain incomplete
- Phase gate after TASK-089: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; sector membership/history, macro/policy depth, source-health metadata, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver
- TASK-090 completed bounded public sector membership batch/history hardening with accepted review and live-enabled PASS evidence; `sector_membership` and `sector_historical_changes` remain conservative because full sector taxonomy history, explicit change-event timelines, and classification-version metadata remain incomplete
- Phase gate after TASK-090: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; macro/policy depth, source-health metadata, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver
- TASK-091 completed public macro/policy depth hardening with accepted review and live-enabled PASS evidence for caller-parameterized macro indicator and policy route-selector access; macro/policy capability truth remains conservative because broader macro release/revision and policy authority/history coverage remains incomplete
- Phase gate after TASK-091: Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`; source-health metadata remains `partial`, and the paid index-weight live PASS path remains blocked pending owner-provided paid credential or explicit waiver
- TASK-092 completed DataHub source-health metadata hardening after accepted TypeError-classification rework; source-health diagnostics now preserve unsupported-request classification only for clear request/signature/contract mismatches while internal fetch-stage `TypeError` failures remain non-unsupported `fetch_failed`, default tests are offline-safe, and live-enabled result is SKIP because the rework was local-only
- Phase gate after TASK-092: Phase 2.5 Core is historical no-paid DataHub source-capability progress, not final phase completion. Accepted hardening from TASK-071 through TASK-092 covers batch/parameterized access across the priority A-share, Hong Kong, ETF/fund, index, sector, macro/policy, source-health, local persistence, refresh metadata, quality-report, and failure-diagnostic groups. Real-source hardening tasks supplied gated live PASS evidence where live source access was in scope; contract/local-only tasks remained offline-safe. The remaining Tushare index-weight live PASS path is explicitly retained as blocked by paid credential availability under TASK-059 and is not promoted.
- Owner reopened DataHub as Phase 2.5-P Personal Trading Perfection Re-Review before FeatureHub resumes. The prior FeatureHub TASK-093 dispatch is replaced and deferred; TASK-093 is now dispatched as an offline DataHub perfection re-review gate across historical DataHub Phase 1/2/2.5 work and all existing DataHub domains.
- TASK-093 is closed after accepted Review Agent verification of the offline readiness gate follow-up queue rework. The gate now emits a stable Controller-ready follow-up queue for every non-pass domain/check, preserves `index_weight_history` as blocked, and keeps all downstream modules inactive.
- TASK-094 is dispatched as the first executable TASK-093 follow-up queue item: A-share status-history continuity hardening for dated ST/*ST continuity and broader lifecycle taxonomy where stable no-credential public routes expose source truth.
- TASK-094 is closed after accepted Review Agent verification. It added source-backed A-share lifecycle/status-history evidence where public routes expose it, kept `a_share_listing_delisting_st_status` conservative at `partial`, kept default tests offline-safe, and provided live-enabled PASS evidence.
- TASK-095 is dispatched as the next executable TASK-093 follow-up queue item: A-share suspension/resumption breadth and taxonomy hardening for `DatasetName.SUSPENSION_RESUMPTION_EVENTS` where stable no-credential public routes expose source truth.
- TASK-095 initial review rejected the result because overlapping Eastmoney and Baidu route rows could produce duplicate logical resumption records and coverage did not yet regression-protect the new Baidu-backed path; the focused rework is now closed after accepted Review Agent verification. It fixed duplicate logical resumption events, added offline overlap regression coverage, strengthened live smoke assertions where feasible, kept default tests offline-safe, and provided live-enabled PASS evidence.
- TASK-096 is dispatched as the next executable TASK-093 follow-up queue item: A-share minute-bars history continuity and broader public-source breadth hardening for `DatasetName.MINUTE_BARS`.
- TASK-096 initial review rejected the result because the new public `1`-minute retention guard used fixed calendar days instead of source-backed trading-day retention, and the live-enabled Eastmoney smoke still skipped on proxy/connectivity availability. The focused retention rework was accepted for scope by Review, and subsequent Eastmoney live rerun reports were accepted as truthful but not closure-ready. The owner then explicitly authorized replacing the blocked Eastmoney-only rerun path with a BaoStock no-credential public-source history path. Commit `e3138fe` added `baostock_public_cn` minute-bars coverage, updated the TASK-096 report with BaoStock live-enabled PASS evidence, and left `a_share_minute_bars` conservative at `partial`. TASK-096 is now in Review for the BaoStock history-source implementation.
- Owner upgraded the global phase gate to the Personal Trading Perfection Standard. Historical phase completion decisions for Phase 1, Phase 2, Phase 2.5, Phase 3, Phase 4, and Phase 5 foundation work are now treated as historical task progress only until re-reviewed against the strongest practical public-source/no-paid personal trading standard.

## Active Constraints

- Current phase is Phase 2.5-P DataHub Personal Trading Perfection Re-Review only.
- TASK-096 is active as a DataHub-only A-share minute-bars BaoStock history-source review after owner-authorized replacement of the blocked Eastmoney-only live rerun path. It remains open and cannot enter Controller closure until fresh Review acceptance records whether the BaoStock live-enabled PASS evidence allows closure.
- DataHub readiness and hardening handoffs may target only `quant/datahub/` and `tests/datahub/` unless explicitly expanded by the controller.
- Paid/private credential gaps must be recorded as Blocked unless the owner provides credentials or explicitly waives them.
- Phase closure must not rely on foundation-only, partial, representative, one-symbol/one-fund/one-route, contract-only, or narrow-smoke completion.
- Controller must not restore FeatureHub until DataHub has no unresolved `fail`, no unexplained `partial`, and all remaining `warn` / `blocked` gaps have owner-accepted rationale under the public-source/no-paid scope.
- Do not implement FeatureHub technical indicators or feature-library expansion until Phase 2.5-P closes and FeatureHub is explicitly reopened.
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

The owner directed skipping this paid-token path for now because `TUSHARE_TOKEN` requires a paid credential. The controller does not mark TASK-059 Done and does not promote `index_weight_history`; instead, TASK-059 moves to the blocked backlog as an explicit paid-credential follow-up. The prior Phase 2.5 no-paid scope closure is historical progress only under the current Personal Trading Perfection Standard.

Historical phase switch: YES, to Phase 3. This was later superseded by the owner-directed trading-usable gate reopen and, after TASK-092, by the Phase 2.5-P personal trading perfection re-review recorded below.

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

The owner replaced the prior foundation-only gate interpretation with stricter personal trading completion gates. Under the updated standard, the earliest incomplete prerequisite phase is DataHub because many Phase 2/2.5 capabilities were representative, narrow, partial, planned, or blocked rather than proven broad enough for practical quant workflows.

Decision:

- Phase switch: REOPENED PRIOR PHASE, to Phase 2.5 DataHub hardening
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
- Reason: DataHub remains below the required personal trading completion standard. The TASK-071 audit found 11 covered, 42 partial, 1 planned, and 1 optional missing capability, with a practical paid `TUSHARE_TOKEN` blocker for index weight history.

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

## TASK-088 Closure

TASK-088 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-088_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; the gated index daily-bars smoke passed for the requested two-index bounded benchmark path
- Rework required: NO

Phase gate decision after TASK-088:

- Phase switch: NO
- Reason: TASK-088 proves caller-provided multi-index bounded daily-bar access for core mainland benchmark symbols, but `index_daily_bars` remains conservative because broader benchmark breadth, longer history continuity, and non-mainland/global benchmark coverage remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: index constituent/rebalance metadata, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver. No integration is entered for TASK-088 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-089 Dispatch

`TASK-089`: DataHub index constituents batch/rebalance hardening.

Handoff:

- `coordination/handoffs/TASK-089_DATAHUB_INDEX_CONSTITUENTS_BATCH_REBALANCE_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-089_REPORT.md`
- review: `coordination/reviews/TASK-089_REVIEW.md`
- integration: N/A until review acceptance

## TASK-089 Closure

TASK-089 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-089_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; the gated index constituents smoke passed for the requested multi-index bounded constituent path
- Rework required: NO

Phase gate decision after TASK-089:

- Phase switch: NO
- Reason: TASK-089 proves caller-provided multi-index bounded index constituent access with effective-date-like membership metadata where public sources expose it, but `index_constituent_history` and `index_rebalance_effective_dates` remain conservative because broader benchmark breadth, longer constituent continuity, and explicit rebalance-calendar truth remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: sector membership/history, macro/policy depth, source-health metadata, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver. No integration is entered for TASK-089 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-090 Dispatch

`TASK-090`: DataHub sector membership batch/history hardening.

Handoff:

- `coordination/handoffs/TASK-090_DATAHUB_SECTOR_MEMBERSHIP_BATCH_HISTORY_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-090_REPORT.md`
- review: `coordination/reviews/TASK-090_REVIEW.md`
- integration: N/A until review acceptance

## TASK-090 Closure

TASK-090 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-090_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; the gated sector membership smoke passed for the requested industry/concept multi-sector bounded membership path
- Rework required: NO

Phase gate decision after TASK-090:

- Phase switch: NO
- Reason: TASK-090 proves caller-provided multi-sector bounded sector membership access with membership date/history fields preserved where public source rows expose them, but `sector_membership` and `sector_historical_changes` remain conservative because full sector taxonomy history, explicit change-event timelines, and classification-version metadata remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: macro/policy depth, source-health metadata, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver. No integration is entered for TASK-090 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-091 Closure

TASK-091 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-091_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (macro), PASS (policy)
- Rework required: NO

Phase gate decision after TASK-091:

- Phase switch: NO
- Reason: TASK-091 proves caller-parameterized public macro indicator definitions/observations and bounded policy route-selector access with schema-valid live smoke evidence, but macro/policy capability truth remains conservative because broader macro release/revision history, release-calendar completeness, wider indicator families, broader policy authority coverage, and deeper policy history remain incomplete. Phase 2.5 remains incomplete under `coordination/ROADMAP.md`: source-health metadata remains `partial`, and paid index-weight live proof remains blocked by unprovided paid credential. No integration is entered for TASK-091 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-092 Closure

TASK-092 is closed after Review Agent acceptance of the TypeError-classification rework.

Review result:

- `coordination/reviews/TASK-092_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-092 is local-only and no live test was permitted
- Rework required: NO

Phase gate decision after TASK-092:

- Phase 2.5 Core decision: historical no-paid DataHub source-capability progress, not final phase completion.
- Owner reopen decision: Phase switch YES, to Phase 2.5-P DataHub Personal Trading Perfection Re-Review before FeatureHub resumes.
- Reason: The accepted TASK-071 audit plus TASK-072 through TASK-092 hardening tasks prove broad practical DataHub source-capability progress, but the owner requires a final deterministic public-source/no-paid personal trading perfection re-review across historical DataHub Phase 1/2/2.5 work and all existing DataHub domains before downstream FeatureHub expansion continues. Paid/private sources remain excluded for now, and `index_weight_history` remains blocked/planned rather than promoted.

## TASK-093 Dispatch

`TASK-093`: DataHub personal trading perfection re-review gate.

Handoff:

- `coordination/handoffs/TASK-093_DATAHUB_PERSONAL_TRADING_READINESS_GATE.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-093_REPORT.md`
- review: `coordination/reviews/TASK-093_REVIEW.md`
- integration: N/A until review acceptance

Scope:

- offline-first DataHub perfection re-review model and pass/warn/blocked/fail matrix
- historical DataHub Phase 1/2/2.5 work plus all existing DataHub domains, storage, refresh metadata, quality reports, and source-health diagnostics
- no unresolved `fail`, no unexplained `partial`, and no silent public-source limitation may be treated as phase completion
- no FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or live tests

## TASK-093 Rework Dispatch

TASK-093 is not closed and Integration is not entered.

Rework handoff:

- `coordination/handoffs/TASK-093_DATAHUB_PERSONAL_READINESS_FOLLOWUP_QUEUE_REWORK.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-093_REPORT.md`
- review: `coordination/reviews/TASK-093_REVIEW.md`
- integration: N/A until fresh review acceptance

Rework scope:

- keep Phase 2.5-P active
- keep allowed implementation target limited to `quant/datahub/` and `tests/datahub/`
- add deterministic structured follow-up queue output to the offline TASK-093 readiness gate
- map every `warn`, `blocked`, or `fail` readiness result to a Controller-ready DataHub follow-up or owner action/blocker disposition
- keep `index_weight_history` blocked unless the owner reopens paid credentialed scope and future live evidence proves PASS
- do not modify DataHub source adapters, downstream modules, paid credentials, or live tests

Phase gate decision for this Controller action:

- Phase switch: NO
- Historical reason at rework dispatch time: TASK-093 was still open and the active work was a DataHub-only rework of the offline readiness gate. DataHub could not close under the Personal Trading Perfection Standard until the reworked gate had fresh execution/report evidence, independent review acceptance, and Controller could evaluate every remaining `warn` / `blocked` / `fail` item without unexplained partials or silent public-source limitations.

## TASK-093 Closure

TASK-093 is closed after Review Agent acceptance of the follow-up queue rework.

Review result:

- `coordination/reviews/TASK-093_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES for TASK-093 itself
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-093 forbade live tests
- Rework required: NO

Phase gate decision after TASK-093:

- Phase switch: NO
- Reason: DataHub is not closure-ready under the Personal Trading Perfection Standard. The accepted gate reports overall `blocked`, phase closure `false`, domain counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and a 42-item structured follow-up queue. Open readiness gaps remain intentionally surfaced as `warn` / `blocked` outcomes and must be dispatched, fixed, explicitly blocked, or owner-waived before FeatureHub can reopen.
- Paid/private scope: `index_weight_history` remains an owner credential blocker and must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.
- No integration is entered for TASK-093 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-094 Dispatch

`TASK-094`: DataHub A-share status-history continuity hardening.

Handoff:

- `coordination/handoffs/TASK-094_DATAHUB_A_SHARE_STATUS_HISTORY_CONTINUITY_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-094_REPORT.md`
- review: `coordination/reviews/TASK-094_REVIEW.md`
- integration: N/A until review acceptance

Scope:

- extend existing public AKShare-backed `DatasetName.INSTRUMENT_STATUS_HISTORY` coverage only where stable no-credential routes expose dated ST/*ST/risk-warning continuity or lifecycle taxonomy source truth
- preserve current bounded listing, delisting, current normal/ST snapshot, and SZ short-name delta behavior
- keep default tests offline-safe and live smoke explicitly gated
- do not synthesize historical continuity from current snapshots or name-prefix heuristics
- do not touch FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or controller-owned coordination state

## TASK-094 Closure

TASK-094 is closed after Review Agent acceptance.

Review result:

- `coordination/reviews/TASK-094_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py` ran 4 tests OK
- Rework required: NO

Phase gate decision after TASK-094:

- Phase switch: NO
- Reason: DataHub is not closure-ready under the Personal Trading Perfection Standard. TASK-094 improved source-backed A-share lifecycle/status-history evidence but intentionally kept `a_share_listing_delisting_st_status` `partial`; the accepted review explicitly preserves SH terminal delist semantics as follow-up contract debt. The TASK-093 queue still contains unresolved `warn` items and one owner credential blocker, so FeatureHub must remain inactive.
- Paid/private scope: `index_weight_history` remains an owner credential blocker and must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.
- No integration is entered for TASK-094 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-095 Dispatch

`TASK-095`: DataHub A-share suspension/resumption breadth and taxonomy hardening.

Handoff:

- `coordination/handoffs/TASK-095_DATAHUB_A_SHARE_SUSPENSION_RESUMPTION_BREADTH_TAXONOMY_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-095_REPORT.md`
- review: `coordination/reviews/TASK-095_REVIEW.md`
- integration: N/A until review acceptance

Scope:

- extend existing public AKShare-backed `DatasetName.SUSPENSION_RESUMPTION_EVENTS` coverage only where stable no-credential routes expose suspension/resumption breadth, exact resumption evidence, or source-backed event taxonomy
- preserve current bounded suspension-table behavior and schema validation
- keep default tests offline-safe and live smoke explicitly gated
- do not infer a resumption event, exact end date, or taxonomy from ambiguous source text or absence of a row
- do not touch FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or controller-owned coordination state

## TASK-095 Rework Dispatch

Review result:

- `coordination/reviews/TASK-095_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS was reported, but not sufficient for closure because adapter behavior can duplicate overlapping resumption events and the live smoke does not specifically assert the Baidu-backed path or overlap handling

Rework handoff:

- `coordination/handoffs/TASK-095_DATAHUB_A_SHARE_SUSPENSION_RESUMPTION_DEDUP_LIVE_REWORK.md`

Required rework:

- keep TASK-095 active and do not enter Integration
- fix Eastmoney/Baidu overlap handling so one logical resumption event is emitted for the same `symbol + start_date + resume_date`
- add offline regression coverage for the reviewed duplicate case
- strengthen live smoke assertions for Baidu-backed exact resumption or overlap behavior where feasible without making tests flaky or live by default
- update `coordination/reports/TASK-095_REPORT.md` with truthful rework evidence

Phase gate decision after TASK-095 Review:

- Phase switch: NO
- Reason: TASK-095 has unresolved blocking Review findings and cannot count toward Phase 2.5-P closure. Phase 2.5-P remains active, downstream modules remain inactive, and TASK-095 must pass fresh Review before Controller can consider closure.

## TASK-095 Closure

TASK-095 is closed after Review Agent acceptance of the deduplication/live-coverage rework.

Review result:

- `coordination/reviews/TASK-095_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS; `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py` ran 4 tests OK
- Rework required: NO

Phase gate decision after TASK-095:

- Phase switch: NO
- Reason: TASK-095 fixes the reviewed A-share suspension/resumption duplicate logical event blocker and closes its assigned TASK-093 queue item, but DataHub is not closure-ready under the Personal Trading Perfection Standard. The TASK-093 queue still contains unresolved `warn` items and one owner credential blocker; `a_share_minute_bars` is the next executable `datahub_hardening` item.
- Paid/private scope: `index_weight_history` remains an owner credential blocker and must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.
- No integration is entered for TASK-095 because Review allowed Controller closure and no strict integration workflow was required.

## TASK-096 Dispatch

`TASK-096`: DataHub A-share minute-bars history continuity hardening.

Handoff:

- `coordination/handoffs/TASK-096_DATAHUB_A_SHARE_MINUTE_BARS_HISTORY_CONTINUITY_HARDENING.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-096_REPORT.md`
- review: `coordination/reviews/TASK-096_REVIEW.md`
- integration: N/A until review acceptance

Scope:

- extend existing public AKShare-backed `DatasetName.MINUTE_BARS` coverage only where stable no-credential routes expose stronger historical continuity, bounded-window, interval, or route-breadth source truth
- preserve current caller-provided symbol access, schema validation, deterministic duplicate handling, and default offline-safe tests
- keep live smoke explicitly gated with `QUANT_SYSTEM_LIVE_TESTS=1`
- do not introduce full-market minute-bar collection, unbounded history backfill, credentialed routes, FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or controller-owned state edits

## TASK-096 Rework Dispatch

Review result:

- `coordination/reviews/TASK-096_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP because Eastmoney was unreachable through the local proxy / connectivity path
- Rework required: YES

Rework handoff:

- `coordination/handoffs/TASK-096_DATAHUB_A_SHARE_MINUTE_BARS_RETENTION_LIVE_REWORK.md`

Required rework:

- keep TASK-096 active and do not enter Integration
- replace the fixed `10` calendar-day public `1`-minute retention guard with source-backed trading-day-aware handling or an equivalent source-backed rule that does not reject still-reachable `5`-trading-day data around long exchange closures before attempting the public route
- add offline regression coverage for holiday / long-closure spans plus stale-window rejection
- rerun and diagnose the gated Eastmoney live smoke; report `PASS`, `SKIP`, or `FAIL` truthfully and do not claim Controller closure readiness from an unresolved network/source skip
- preserve DataHub-only Phase 2.5-P scope, offline-safe defaults, bounded caller-provided symbol requests, schema validation, deterministic duplicate handling, and conservative `a_share_minute_bars` capability truth unless source-backed live evidence justifies a change

Phase gate decision after TASK-096 Review:

- Phase switch: NO
- Reason: TASK-096 has unresolved blocking Review findings and cannot count toward Phase 2.5-P closure. Phase 2.5-P remains active, downstream modules remain inactive, and TASK-096 must pass fresh Review before Controller can consider closure.

## TASK-096 Live PASS Rerun Dispatch

Review result:

- `coordination/reviews/TASK-096_REVIEW.md`
- Decision: ACCEPTED for the requested retention rework scope, but Controller closure is not allowed
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP because Eastmoney remained unreachable through the local proxy / connectivity path
- Rework required: YES, limited to a fresh live-environment rerun from an Eastmoney-reachable environment or working proxy path

Live PASS rerun handoff:

- `coordination/handoffs/TASK-096_DATAHUB_A_SHARE_MINUTE_BARS_LIVE_PASS_RERUN.md`

Required follow-up:

- keep TASK-096 active and do not enter Integration
- rerun the default/offline minute-bars and source-capability tests
- rerun the gated Eastmoney live smoke from a live-capable environment
- update `coordination/reports/TASK-096_REPORT.md` with truthful `PASS`, `SKIP`, or `FAIL` evidence, including proxy/environment conditions
- change adapter/tests/capability metadata only if new live evidence reveals a repository-side defect inside the allowed DataHub scope
- require fresh Review Agent verification before Controller closure

Phase gate decision after TASK-096 retention rework review:

- Phase switch: NO
- Reason: TASK-096 still lacks mandatory live-enabled PASS evidence for a real-source DataHub task. Phase 2.5-P remains active, downstream modules remain inactive, and the next executable task is the same TASK-096 live PASS rerun rather than a new phase or a new domain.

## TASK-096 Eastmoney Reachability Live PASS Rerun Dispatch

Review result:

- `coordination/reviews/TASK-096_REVIEW.md`
- Decision: ACCEPTED as a truthful live-rerun report, but TASK-096 is not closure-ready
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES, limited to another fresh live-environment rerun from a host with end-to-end Eastmoney API reachability or a verified working proxy path

Latest live-rerun evidence:

- The report includes explicit default-skip evidence with `env -u QUANT_SYSTEM_LIVE_TESTS ...` because the shell had `QUANT_SYSTEM_LIVE_TESTS=1` preset.
- Python resolved a system proxy path to `127.0.0.1:7892`.
- Direct `NO_PROXY='*'` and `curl` probes still ended in remote disconnect / empty reply against the Eastmoney API endpoint.
- Review found no new repository-side phase, contract, code, or test blocker beyond the mandatory live PASS gate remaining open.

Eastmoney reachability live PASS rerun handoff:

- `coordination/handoffs/TASK-096_DATAHUB_A_SHARE_MINUTE_BARS_EASTMONEY_REACHABILITY_LIVE_PASS_RERUN.md`

Required follow-up:

- keep TASK-096 active and do not enter Integration
- rerun the required default/offline minute-bars and source-capability tests
- rerun the gated Eastmoney live smoke from an environment with verified Eastmoney reachability or a working proxy path
- include explicit default-skip verification if `QUANT_SYSTEM_LIVE_TESTS` is preset in the shell
- update `coordination/reports/TASK-096_REPORT.md` with truthful `PASS`, `SKIP`, or `FAIL` evidence, including proxy/environment conditions and reachability evidence
- change adapter/tests/capability metadata only if new live evidence reveals a repository-side defect inside the allowed DataHub scope
- require fresh Review Agent verification before Controller closure

Phase gate decision after TASK-096 live rerun review:

- Phase switch: NO
- Reason: TASK-096 still lacks mandatory live-enabled PASS evidence for a real-source DataHub task. Phase 2.5-P remains active, downstream modules remain inactive, and the next executable task is another same-task Eastmoney reachability live PASS rerun rather than a new phase or a new domain.

## TASK-096 Verified Eastmoney Live PASS Rerun Dispatch

Review result:

- `coordination/reviews/TASK-096_REVIEW.md`
- Decision: ACCEPTED as a truthful live-rerun report, but TASK-096 is not closure-ready
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES, limited to a fresh rerun from a host with end-to-end Eastmoney API reachability or a verified working proxy path

Controller decision:

- TASK-096 is not closed and does not enter Integration.
- The latest Review found no new repository-side phase, contract, code, or test blocker beyond the mandatory live PASS gate remaining open.
- The packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while TASK-096 is Active and not closure-ready.

Verified Eastmoney live PASS rerun handoff:

- `coordination/handoffs/TASK-096_DATAHUB_A_SHARE_MINUTE_BARS_VERIFIED_EASTMONEY_LIVE_PASS_RERUN.md`

Required follow-up:

- keep TASK-096 active and do not enter Integration
- rerun the required default/offline minute-bars and source-capability tests
- rerun the gated Eastmoney live smoke from an environment with verified Eastmoney reachability or a working proxy path
- include explicit default-skip verification if `QUANT_SYSTEM_LIVE_TESTS` is preset in the shell
- update `coordination/reports/TASK-096_REPORT.md` with truthful `PASS`, `SKIP`, or `FAIL` evidence, including proxy/environment conditions and reachability evidence
- change adapter/tests/capability metadata only if new live evidence reveals a repository-side defect inside the allowed DataHub scope
- require fresh Review Agent verification before Controller closure

Phase gate decision after latest TASK-096 live rerun review:

- Phase switch: NO
- Reason: `coordination/reviews/TASK-096_REVIEW.md` explicitly says Controller closure is not allowed and live-enabled result is `SKIP`; under `coordination/PHASE_GATE.md`, a real-source task with a live-enabled network/proxy/upstream skip cannot count as Done. Phase 2.5-P remains active, downstream modules remain inactive, and the next executable task is the same TASK-096 verified Eastmoney live PASS rerun.

## TASK-096 BaoStock Minute-Bars History Source Review Dispatch

Owner-authorized route update:

- The previous Eastmoney-only rerun path remained blocked because the `push2his.eastmoney.com` minute-bars API still produced remote disconnect / empty reply in this environment.
- The owner explicitly authorized replacing that blocked Eastmoney-only closure route with a BaoStock no-credential public-source history path.
- Implementation commit: `e3138fe TASK-096 add baostock minute bar history source`
- Report: `coordination/reports/TASK-096_REPORT.md`

Controller decision:

- TASK-096 is not closed.
- TASK-096 moves to Review for the BaoStock implementation and updated report.
- Phase 2.5-P remains active pending fresh Review Agent acceptance.
- Downstream modules remain inactive.

BaoStock Review handoff:

- `coordination/handoffs/TASK-096_DATAHUB_A_SHARE_MINUTE_BARS_BAOSTOCK_HISTORY_SOURCE_REVIEW.md`

Required follow-up:

- Review Agent must read the new handoff, the updated report, and commit `e3138fe`.
- Review Agent must write `coordination/reviews/TASK-096_REVIEW.md`.
- Review must explicitly say whether Controller closure is allowed, whether default tests are offline-safe, whether BaoStock live-enabled result is PASS/SKIP/FAIL, and whether rework is required.

Phase gate decision after TASK-096 BaoStock implementation dispatch:

- Phase switch: NO
- Reason: TASK-096 still requires fresh Review Agent acceptance before Controller can determine closure. Phase 2.5-P remains active and downstream modules remain inactive.
