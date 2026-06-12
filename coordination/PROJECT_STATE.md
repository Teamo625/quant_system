# Project State

Last updated by: 5.5 Controller

## Current Phase

Phase 6: PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.

## Current Implementation Scope

Phase 2.5-P DataHub Personal Trading Perfection Re-Review is closed for the public-source/no-paid scope after TASK-137. Paid Tushare index-weight live proof remains an owner-approved blocked follow-up, and DataHub residual public-source limitations remain explicitly recorded as conservative `warn` truth rather than silent completion claims.

Phase 3-P FeatureHub Personal Trading Perfection Re-Review is closed after accepted TASK-142 Review and Controller phase-gate verification. The FeatureHub readiness gate now reports `phase_closure_ready=true`, status counts `pass=7`, `warn=0`, `blocked=0`, `fail=0`, with no remaining follow-up queue or batches.

Phase 4-P Scanner Personal Trading Perfection Re-Review is closed after accepted TASK-146 Review and Controller phase-gate verification. The Scanner readiness gate now reports `phase_closure_ready=true`, status counts `pass=6`, `warn=0`, `blocked=0`, `fail=0`, with no remaining follow-up batches.

Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection is closed after accepted TASK-150 Review and Controller phase-gate verification. The StrategyLab/BacktestEngine readiness gate now reports `phase_closure_ready=true`, status counts `pass=7`, `warn=0`, `blocked=0`, `fail=0`, with no remaining follow-up queue or batches.

The owner has reopened Phase 6 because DataHub Phase 2.5-P, FeatureHub Phase 3-P, Scanner Phase 4-P, and Phase 5 StrategyLab/BacktestEngine have reached accepted public-source/no-paid/local Personal Trading Perfection closure or owner-accepted blocker disposition where applicable.

Current implementation may target only:

- `quant/portfolio/`
- `tests/portfolio/`

TASK-151 is closed after accepted Review Agent verification. It created the local/offline Phase 6 PortfolioMonitor, SignalEngine, and RiskEngine readiness gate. The initial gate reported `phase_closure_ready=false`, status counts `pass=0`, `warn=6`, `blocked=0`, `fail=0`, seven follow-up queue items, and three coherent follow-up batches.

TASK-152 is closed after accepted Review Agent verification of the portfolio/watchlist and signal lifecycle contract foundation plus the focused duplicate-update validation rework. The current Phase 6 readiness gate reports `phase_closure_ready=false`, status counts `pass=3`, `warn=3`, `blocked=0`, `fail=0`, four remaining follow-up queue items, and two coherent follow-up batches.

For the active `TASK-153` structured signal composition and risk rule foundation specifically, the next role is 5.3 Execution.

Expected next write path:

- `coordination/reports/TASK-153_REPORT.md`

Execution should follow `coordination/handoffs/TASK-153_STRUCTURED_SIGNAL_RISK_FOUNDATION.md`, modifying only allowed PortfolioMonitor/SignalEngine/RiskEngine files under `quant/portfolio/`, focused `tests/portfolio/` tests, and the report. This handoff covers `portfolio_signal_risk__personal_trading_hardening__batch_02`: `phase6__upstream_signal_composition_foundation` and `phase6__risk_rule_evaluation_foundation`. It must remain local/offline over caller-provided evidence and must not fetch data, read warehouse state, modify DataHub/FeatureHub/Scanner/StrategyLab/BacktestEngine implementation files, implement notification, AI, UI, live brokerage, automated trading, credentials, private data, hidden live network behavior, or unrelated downstream work.

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
- TASK-096 is closed after accepted Review Agent verification. It added owner-authorized `baostock_public_cn` minute-bars coverage for 5/15/30/60-minute historical bars, updated the TASK-096 report with BaoStock live-enabled PASS evidence, fixed the BaoStock live-smoke classifier truthfulness issue, and left `a_share_minute_bars` conservative at `partial`.
- TASK-097 is closed after accepted Review Agent verification. It made A-share adjustment-factor semantics first-class under `DatasetName.ADJUSTMENT_FACTORS`, added no-credential public AKShare/Sina qfq/hfq source coverage, kept `a_share_adjustment_factors` conservative because full per-trade-date continuity and public-source redundancy remain incomplete, recorded live-enabled PASS evidence, and fixed the adjustment-factor live skip classifier so Sina/source-route data failures no longer downgrade to environment `SKIP`.
- TASK-098 is closed after accepted Review Agent verification of the shared corporate-actions contract rework. It preserved the global `CORPORATE_ACTIONS` `action_family` / `source_route` requirement, fixed HK corporate-actions normalization so records validate under the shared schema, kept default tests offline-safe, and provided HK live-enabled PASS evidence for the rework.
- TASK-099 is dispatched as the next executable TASK-093 follow-up queue item: A-share valuation-history breadth hardening beyond bounded near-year public coverage where stable no-credential public routes expose source truth.
- TASK-099 is closed after accepted Review Agent verification. It expanded A-share valuation-history breadth by selecting Baidu valuation periods based on requested history breadth, proved live-enabled PASS evidence for a 450-day two-symbol request, kept default tests offline-safe, and kept `a_share_valuation_history` conservative at `partial` because full long-run continuity and no-credential second-source redundancy remain unproven.
- TASK-100 is closed after accepted Review Agent verification. The rework truthfully handles the prior Baidu non-JSON live failure mode as route unavailability, preserves default offline behavior, preserves prior overlap/gap regressions, records live-enabled PASS evidence, and does not promote `a_share_valuation_history` beyond `partial`.
- TASK-101 is closed after accepted Review Agent verification. It made A-share capital-flow route truth explicit with `source_route`, preserved route-distinct `CAPITAL_FLOW_SNAPSHOT` source facts, kept `a_share_capital_flow` conservative because no stable second dated symbol-history route is proven and the datacenter fallback remains latest-only, and provided live-enabled PASS evidence.
- TASK-102 is closed after accepted Review Agent verification. It made A-share northbound-flow semantics first-class under `DatasetName.NORTHBOUND_FLOW_SNAPSHOT`, kept `a_share_northbound_flow` conservative, recorded live-enabled PASS evidence, and completed the focused live-classifier rework so AKShare route-signature/call-compatibility defects fail rather than being downgraded to environment `SKIP`.
- TASK-103 is closed after accepted Review Agent verification. It added explicit A-share turnover/liquidity source-fact semantics, kept `a_share_turnover_liquidity` conservative and unpromoted, and completed the focused live-classifier rework so `stock_zh_a_hist` route-signature/call-compatibility defects fail rather than become environment `SKIP`.
- TASK-104 is closed after accepted Review Agent verification. It improved A-share limit-up/down route breadth/history, then completed the focused classifier-truthfulness rework so `gettopicpreviouspool` / `gettopiczbgcpool` route-name-bearing payload/schema/normalization defects fail rather than being downgraded to environment `SKIP`; live-enabled result was PASS.
- TASK-105 is dispatched as the next executable TASK-093 follow-up queue item: A-share margin financing/lending breadth and history hardening for `DatasetName.MARGIN_FINANCING_LENDING` where stable no-credential public routes expose source truth.
- TASK-105 is closed after accepted Review Agent verification. It expanded A-share margin financing/lending from a one-symbol slice to caller-provided multi-symbol bounded SSE/SZSE margin-detail history with explicit exchange/source-route provenance, kept BSE/BJ unsupported until a validated public symbol-level route is proven, kept `a_share_margin_financing_and_lending` conservative at `partial`, and provided live-enabled PASS evidence.
- TASK-106 is closed after accepted Review Agent verification. It added optional `source_route` truth to `DatasetName.FINANCIAL_STATEMENTS`, normalized A-share statement records with `source_route="stock_financial_report_sina"`, tightened financial-data live-unavailable classification so route/provider names alone no longer downgrade repository defects to `SKIP`, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `a_share_financial_statements` conservative at `partial` because second-route redundancy and full long-history continuity remain unproven.
- TASK-107 is dispatched as the next executable TASK-093 follow-up queue item: A-share financial indicators breadth and history hardening for `DatasetName.FINANCIAL_INDICATORS` where stable no-credential public routes expose source truth.
- TASK-107 is closed after accepted Review Agent verification. It added optional `source_route` and `metric_family` truth to `DatasetName.FINANCIAL_INDICATORS`, normalized A-share indicator records with `source_route="stock_financial_analysis_indicator_em"`, kept route-distinct indicator records separate, tightened financial-data provenance assertions, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `a_share_financial_indicators` conservative at `partial` because second-route redundancy, full long-history continuity, and broader cross-industry metric-family completeness remain unproven.
- TASK-108 is closed after accepted Review Agent verification of the date-window/fallback truth rework. It added live date-window assertions, prevented fallback per-day upstream/source availability failures from silently satisfying incomplete requested windows, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `a_share_company_announcements` conservative at `partial`.
- TASK-109 is closed after accepted Review Agent verification. It expanded A-share `DatasetName.MAJOR_ACTIVITY_EVENTS` from single-day block-trade detail coverage to bounded date-window detail plus symbol-date summary coverage with explicit `source_route` truth, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `a_share_major_activity_events` conservative at `partial`.
- TASK-110 is dispatched as the next executable TASK-093 follow-up queue item: Hong Kong universe breadth and dated lifecycle metadata hardening for `DatasetName.INSTRUMENT_MASTER` / `hk_universe_reference` where stable no-credential public routes expose source truth.
- TASK-110 is closed after accepted Review Agent verification. It added optional `source_route` truth to `DatasetName.INSTRUMENT_MASTER`, emitted `source_route="stock_hk_security_profile_em"` for HK stock reference records, tightened the HK instrument-master live classifier so route/provider tokens alone no longer downgrade repository defects to environment `SKIP`, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `hk_universe_reference` conservative at `partial`.
- TASK-111 is closed after accepted Review Agent verification. It added a bounded `symbols=None` current-list path using `stock_hk_spot_em` plus per-symbol profile reconciliation, kept default tests offline-safe, recorded profile-route live PASS with bounded list-route live SKIP on genuine upstream `RemoteDisconnected`, and kept `hk_universe_reference` conservative at `partial`.
- TASK-112 is closed after accepted Review Agent verification. It added a bounded HK listed-universe fallback path in `AkshareHKInstrumentMasterAdapter`: primary `stock_hk_spot_em`, fallback `sina_hk_stock_spot_page1`, both reconciled through per-symbol `stock_hk_security_profile_em`; kept default tests offline-safe; recorded gated live PASS evidence; and kept `hk_universe_reference` conservative at `partial`.
- TASK-113 is dispatched as the next Phase 2.5-P DataHub hardening handoff continuing the unresolved `hk_universe_reference` queue item. It must prove source-backed HK non-stock taxonomy and dated lifecycle/listing-status truth where stable no-credential public routes expose it, or truthfully constrain capability/source wording without promotion.
- TASK-113 is closed after accepted Review Agent verification. It tightened HK universe capability and source-catalog wording instead of over-claiming new coverage, kept default tests offline-safe, recorded gated live PASS evidence, and kept `hk_universe_reference` conservative at `partial` because proven no-credential routes remain stock-only and do not expose reusable non-stock taxonomy or trustworthy dated delist/inactive lifecycle metadata.
- TASK-114 is dispatched as the next Phase 2.5-P DataHub hardening handoff for `hk_daily_bars` history continuity and broader public-source redundancy beyond bounded batch coverage.
- TASK-114 is closed after accepted Review Agent verification. It strengthened HK daily-bar practical history continuity with the `stock_hk_daily` same-family fallback when `stock_hk_hist` is unavailable or empty, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `hk_daily_bars` conservative at `partial` because independent public-source redundancy remains unproven.
- Phase gate after TASK-114: Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports unresolved non-pass queue items and `phase_closure_ready=False`; `index_weight_history` remains an owner paid-credential blocker; optional `hk_minute_bars` remains owner-waiver-required; and required HK corporate-actions, valuation, financial, liquidity, ETF/fund, index, sector, macro/policy, and quality-report gaps still require accepted hardening or owner-accepted disposition.
- TASK-115 is dispatched as the next executable Phase 2.5-P DataHub hardening handoff for `hk_corporate_actions` taxonomy/history coverage. The preceding `hk_minute_bars` queue item has `disposition=owner_waiver_required` and is not dispatched without owner waiver or explicit feasibility scope.
- TASK-115 is closed after accepted Review Agent verification. It combined proven HK dividend/distribution route history from `stock_hk_dividend_payout_em` and `stock_hk_fhpx_detail_ths`, added explicit distribution/no-distribution taxonomy truth, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `hk_corporate_actions` conservative at `partial` because non-dividend HK corporate-action families and batch breadth remain unproven.
- Phase gate after TASK-115: Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports `overall=blocked`, `phase_closure_ready=False`, and 42 non-pass follow-up queue items; `index_weight_history` remains an owner paid-credential blocker; optional `hk_minute_bars` remains owner-waiver-required; and required HK valuation, financial, liquidity, ETF/fund, index, sector, macro/policy, and quality-report gaps still require accepted hardening or owner-accepted disposition.
- TASK-116 is dispatched as the next executable Phase 2.5-P DataHub hardening handoff for `hk_valuation_history` contract/history truth. It must prove stronger stable no-credential HK dated valuation facts, metric/source-route truth, and date-window behavior where feasible, or truthfully constrain capability/source wording without promotion.
- TASK-116 is closed after accepted Review Agent verification. It hardened HK `DatasetName.VALUATION_SNAPSHOT` from one-symbol latest valuation coverage into caller-provided HK symbol batches with bounded dated PE/PB/market-cap history, explicit `source_route` truth, deterministic date-window behavior, and conservative capability/source wording; `hk_valuation_history` remains `partial` because accepted live evidence is stale through `2022-07-13` and independent current-dated redundancy remains unproven.
- Phase gate after TASK-116: Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and 42 non-pass follow-up queue items; `index_weight_history` remains an owner paid-credential blocker; optional `hk_minute_bars` remains owner-waiver-required; and required HK financial, liquidity, ETF/fund, index, sector, macro/policy, and quality-report gaps still require accepted hardening or owner-accepted disposition.
- TASK-117 is dispatched as the next executable Phase 2.5-P DataHub hardening handoff for `hk_financial_data` breadth/history truth. It must prove stronger stable no-credential HK financial statement/indicator market breadth, report-period history, source-route/statement/metric truth, and date-window behavior where feasible, or truthfully constrain capability/source wording without promotion.
- TASK-117 is closed after accepted Review Agent verification of the focused live-classifier rework. The final Review accepted default offline-safe tests and live-enabled PASS evidence, and confirmed HK financial route-name-bearing signature/schema/payload/normalization defects now remain hard failures instead of being downgraded to environment `SKIP`; `hk_financial_data` remains conservative because the rework was classifier-only.
- Phase gate after TASK-117: Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and 42 non-pass follow-up queue items; `index_weight_history` remains an owner paid-credential blocker; optional `hk_minute_bars` remains owner-waiver-required; and required HK liquidity, ETF/fund, index, sector, macro/policy, and quality-report gaps still require accepted hardening or owner-accepted disposition.
- TASK-118 is dispatched as the next executable Phase 2.5-P DataHub hardening handoff for `hk_turnover_liquidity` canonical source-truth hardening. It must define or truthfully constrain HK turnover/liquidity canonical field semantics and checks where stable no-credential public routes expose source truth, without implementing downstream liquidity features.
- TASK-118 is closed after accepted Review Agent verification. It added explicit HK turnover/liquidity source-fact semantics over `DatasetName.DAILY_BARS`, preserved default offline safety, recorded live-enabled PASS evidence through the `stock_hk_daily` fallback while primary `stock_hk_hist` remained unavailable in this environment, and kept `hk_turnover_liquidity` conservative because turnover-rate, float-share, spread/microstructure facts, and independent public-source redundancy remain unproven.
- Phase gate after TASK-118: Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and 42 non-pass follow-up queue items; `index_weight_history` remains an owner paid-credential blocker; optional `hk_minute_bars` remains owner-waiver-required; and required ETF/fund, index, sector, macro/policy, and quality-report gaps still require accepted hardening or owner-accepted disposition.
- TASK-119 is closed after accepted Review Agent verification of the focused symbol-family truth rework. It narrowed listed-fund daily-bar support to the single proven `161725.FUND_CN` LOF/listed-fund path, preserved exchange ETF daily-bar behavior, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `fund_daily_bars` conservative at `partial`.
- Phase gate after TASK-119: Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked` and `phase_closure_ready=False`; `index_weight_history` remains an owner paid-credential blocker; optional `hk_minute_bars` remains owner-waiver-required; and required ETF/fund NAV/holdings/scale/flow/premium-discount, index, sector/concept, macro/policy, and quality-report gaps still require accepted hardening or owner-accepted disposition.
- TASK-120 is dispatched as the next executable Phase 2.5-P DataHub hardening handoff for `fund_nav` breadth/history truth. It must prove stronger stable no-credential ETF/fund NAV breadth/history where public routes expose it, or truthfully constrain capability/source wording without promotion.
- TASK-120 is closed after accepted Review Agent verification. It broadened ETF/fund `DatasetName.FUND_NAV_SNAPSHOT` source truth with explicit `FUND_CN` public-fund NAV history plus bounded ETF empty-window fallback, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `fund_nav` conservative at `partial` because some fund classes and independent public-route redundancy remain unproven.
- Phase gate after TASK-120: Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and 42 non-pass follow-up queue items; `index_weight_history` remains an owner paid-credential blocker; optional `hk_minute_bars` remains owner-waiver-required; and required ETF/fund holdings/scale/flow/premium-discount, index, sector/concept, macro/policy, and quality-report gaps still require accepted hardening or owner-accepted disposition.
- TASK-121 is dispatched as the next executable Phase 2.5-P DataHub hardening handoff for `fund_holdings_composition` breadth/history truth. It must prove stronger stable no-credential ETF/fund holdings breadth/history where public routes expose it, or truthfully constrain capability/source wording without promotion.
- TASK-121 is closed after accepted Review Agent verification. It strengthened ETF/fund holdings symbol-family truth for exchange ETFs plus explicit `FUND_CN` domestic-equity funds and kept `fund_holdings_composition` conservative because broader fund classes, non-A-share holdings taxonomy, longer continuity, and independent route redundancy remain incomplete.
- TASK-122 is closed after accepted Review Agent verification of the signed metric rework. It added the first-class `FUND_SCALE_SHARE_SNAPSHOT` contract and kept `fund_scale_and_share` conservative because adapter-backed source breadth, longer continuity, and route redundancy remained incomplete at that point.
- TASK-123 is closed after accepted Review Agent verification of the bounded-request rework. It added request-scoped ETF/fund scale/share source proof, fixed the unbounded full-table snapshot blocker, preserved default offline safety, recorded live-enabled PASS evidence, and kept `fund_scale_and_share` conservative because broader fund-family breadth, longer continuity, unit semantics, and redundancy remain incomplete.
- TASK-124 is closed after accepted Review Agent verification. It added optional `source_route` truth to `DatasetName.FUND_FLOW`, kept route-distinct records separate during deduplication, investigated but rejected aggregate/status/latest-only or call-incompatible routes as promotion evidence, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `fund_flow` conservative at `partial`.
- Phase gate after TASK-124: Phase 2.5-P remains open because DataHub still has unresolved personal trading perfection queue items; `index_weight_history` remains an owner paid-credential blocker; optional `hk_minute_bars` remains owner-waiver-required; and required ETF/fund premium-discount, index, sector/concept, macro/policy, and quality-report gaps still require accepted hardening or owner-accepted disposition.
- TASK-125 is dispatched as the next executable Phase 2.5-P DataHub hardening handoff for `fund_premium_discount` breadth/history truth. It must prove stronger stable no-credential ETF/fund premium-discount history/breadth where public routes expose it, or truthfully constrain capability/source wording without promotion.
- TASK-125 is closed after accepted Review Agent verification of the ETF/fund premium-discount live-classifier rework. It preserved the accepted `FUND_PREMIUM_DISCOUNT` breadth/history result, narrowed historical route/function-name skip matching, kept route-signature/call-compatibility defects as failures, kept default tests offline-safe, recorded gated live-enabled PASS evidence, and kept `fund_premium_discount` conservative.
- TASK-126 is closed after accepted Review Agent verification. It added major Hong Kong benchmark daily-bar support with explicit `source_route` truth, preserved bounded mainland index behavior, kept default tests offline-safe, and recorded independent live-enabled PASS evidence while keeping `index_daily_bars` conservative.
- TASK-127 is dispatched as the first post-TASK-126 capability-cluster handoff using readiness batch `index__datahub_hardening__index__batch_01` for `index_daily_bars`, `index_constituent_history`, `index_rebalance_effective_dates`, and `index_china_hk_global_benchmarks`.
- TASK-127 is closed after accepted Review Agent verification. It added curated no-credential global benchmark daily-bar support and broader China benchmark constituent support, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept all index capabilities conservative because global long-history breadth, HK/global constituent history, explicit rebalance calendars, and independent public-route redundancy remain incomplete.
- TASK-128 is dispatched as the next executable capability-cluster handoff using readiness batch `sector_concept__datahub_hardening__sector_concept__batch_01` for `sector_membership`, `sector_historical_changes`, and `sector_daily_bars`.
- TASK-128 is closed after accepted Review Agent verification of the focused sector daily-bar live-classifier rework. It kept default tests offline-safe, recorded live-enabled PASS evidence, and proved route-unavailable errors still skip while route-signature and normalized-record validation defects fail.
- TASK-129 is closed after accepted Review Agent verification. It strengthened the macro/policy/announcement capability cluster, kept default tests offline-safe, recorded independently reproduced live-enabled PASS evidence for macro, policy-document, and HK announcement smokes, and kept targeted capability/catalog wording conservative.
- TASK-130 is closed after accepted Review Agent verification. It added deterministic, bounded `DATA_QUALITY_REPORT` KPI coverage for readiness gaps, kept default behavior offline-safe, kept capability/catalog wording explicit that this is observability hardening rather than proof of source completeness, and did not require live evidence because the task was local-only.
- TASK-131 is closed after accepted Review Agent verification. It completed the A-share readiness batch `a_share__datahub_hardening__a_share__batch_01` and the focused source-catalog truth rework removing incorrect BaoStock attribution from the AKShare source-family notes.
- TASK-132 is closed after accepted Review Agent verification. It completed the A-share readiness batch `a_share__datahub_hardening__a_share__batch_02` and the focused northbound fallback truth rework, correcting `stock_hsgt_individual_detail_em` from established fallback coverage to attempted/unproven fallback truth while preserving default offline safety.
- TASK-133 is dispatched as the next executable DataHub A-share capability-cluster handoff using readiness batch `a_share__datahub_hardening__a_share__batch_03` for `a_share_financial_indicators`, `a_share_company_announcements`, and `a_share_major_activity_events`.
- TASK-135 is closed after accepted Review Agent verification. It resolved the HK minute-bars owner-waiver/blocker disposition with bounded public-source HK `MINUTE_BARS` coverage, default-gated live smoke coverage, live-enabled PASS evidence, and conservative `hk_minute_bars` capability truth.
- TASK-136 was dispatched as the DataHub ETF/fund capability-cluster handoff using readiness batch `etf_fund__datahub_hardening__etf_fund__batch_01` for `fund_daily_bars`, `fund_nav`, `fund_holdings_composition`, `fund_scale_and_share`, `fund_flow`, and `fund_premium_discount`.
- TASK-136 is closed after accepted Review Agent verification. It completed the ETF/fund capability-cluster batch, broadened proven listed-fund/LOF support for `fund_daily_bars` and `fund_premium_discount`, preserved default offline safety, recorded live-enabled PASS evidence, and kept ETF/fund capability truth conservative where public-source completeness remains unproven.
- TASK-137 is dispatched as the next executable DataHub residual index capability-cluster handoff using readiness batch `index__datahub_hardening__index__batch_01` for `index_daily_bars`, `index_constituent_history`, `index_rebalance_effective_dates`, and `index_china_hk_global_benchmarks`.
- TASK-137 is closed after accepted Review Agent verification. It completed the residual DataHub index readiness batch, strengthened index capability/catalog truth without over-promotion, preserved default offline safety, recorded live-enabled PASS evidence for index daily-bar and constituent/rebalance smokes, and kept `index_weight_history` separate as an owner paid-credential blocker.
- Phase 2.5-P DataHub is closed for the public-source/no-paid Personal Trading Perfection scope. This closure does not mean every public-source limitation disappeared; it means every ordinary DataHub hardening batch has accepted execution/review evidence, all residual `warn` / `partial` states are explicitly conservative limitation truth, and the only paid/private requirement is recorded as the owner-accepted blocked TASK-059/Tushare index-weight path.
- Phase 3-P FeatureHub Personal Trading Perfection Re-Review is opened with TASK-138 as the first audit/gate handoff.
- Owner upgraded the global phase gate to the Personal Trading Perfection Standard. Historical phase completion decisions for Phase 1, Phase 2, Phase 2.5, Phase 3, Phase 4, and Phase 5 foundation work are now treated as historical task progress only until re-reviewed against the strongest practical public-source/no-paid personal trading standard.

## Active Constraints

- Current phase is Phase 6 PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection only.
- TASK-153 is active after TASK-152 closure. Execution must now follow `coordination/handoffs/TASK-153_STRUCTURED_SIGNAL_RISK_FOUNDATION.md` and update `coordination/reports/TASK-153_REPORT.md`.
- PortfolioMonitor/SignalEngine/RiskEngine handoffs may target only `quant/portfolio/` and `tests/portfolio/` unless explicitly narrowed or expanded by the controller handoff.
- StrategyLab/BacktestEngine implementation files are not active targets; reopen them only through an explicit controller rework or blocker task.
- Scanner implementation files are not active targets; reopen Scanner only through an explicit controller rework or blocker task.
- DataHub implementation files are not active targets; reopen DataHub only through an explicit controller rework or paid/blocker task.
- FeatureHub implementation files are not active targets; reopen FeatureHub only through an explicit controller rework or blocker task.
- Paid/private credential gaps must be recorded as Blocked unless the owner provides credentials or explicitly waives them.
- Phase closure must not rely on foundation-only, partial, representative, one-symbol/one-fund/one-route, contract-only, or narrow-smoke completion.
- Scanner readiness gate work is complete after TASK-143. Universe/constraint, ranking/workflow, and artifact contract repair batches are closed after TASK-144, TASK-145, and TASK-146. Phase 4-P is closed under the Personal Trading Perfection Standard for the local Scanner module responsibility.
- Do not implement live execution. TASK-153 may only add local/offline PortfolioMonitor, SignalEngine, and RiskEngine structured signal composition and deterministic risk-rule foundation over caller-provided or local code evidence, as explicitly scoped by the handoff.
- Do not implement AI reports.
- Do not implement notifications.
- Do not implement automated trading.
- Do not implement complex UI.
- Default tests must not use live network access.
- Live tests require explicit handoff permission and environment-variable gating.
- Real source adapter and real data-fetching tasks remain DataHub-owned and require a gated live smoke test when explicitly assigned; default tests must still skip it unless explicitly enabled.
- Live-enabled network/proxy/DNS/TLS/upstream failures must be routed to a 5.3 execution rework for diagnosis and feasible repository fixes, then independently reviewed before integration or controller closure.
- Execution windows must not update project state files.

## TASK-151 Closure / TASK-152 Dispatch

Review result:

- `coordination/reviews/TASK-151_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-151 is closed as Done.
- No Integration Agent is dispatched because Review allowed Controller closure and the active workflow is `handoff -> Execution -> Review -> Controller`.
- TASK-151 closes the local/offline Phase 6 readiness gate. Review independently reran `python3 -m unittest discover -s tests/portfolio -p 'test_*.py'`; it passed with `Ran 4 tests`.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md`. Phase 6 remains incomplete because the readiness gate reports `phase_closure_ready=false`, status counts `pass=0`, `warn=6`, `blocked=0`, `fail=0`. The unresolved groups are watchlist/holding-state contracts, signal lifecycle management, structured upstream-context signal composition, risk rule evaluation, signal auditability/decision trace, and offline regression coverage for conflicts, staleness, risk blocks, and lifecycle transitions.
- Phase switch: NO. Current phase remains Phase 6 PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.
- Controller read the TASK-151 readiness `follow_up_batches`. The next executable current-phase capability cluster is `portfolio_signal_risk__personal_trading_hardening__batch_01`, covering `phase6__portfolio_watchlist_and_holding_state_contracts`, `phase6__signal_lifecycle_and_audit_contracts`, and `phase6__signal_source_link_and_decision_audit_contracts`.
- This is a three-item coherent Phase 6 cluster from readiness `follow_up_batches`; it is not a single-item exception. It is dispatched together because portfolio state, signal lifecycle, and audit/source-link contracts form the stable contract layer required before composition and risk decisions can be implemented safely.
- `coordination/handoffs/TASK-152_PORTFOLIO_SIGNAL_LIFECYCLE_CONTRACTS.md` is dispatched as the next Active 5.3 execution handoff.
- AGENTS.md is unchanged because the current phase and allowed implementation targets remain Phase 6: `quant/portfolio/` and `tests/portfolio/`.

For active TASK-152 specifically, the next role is 5.3 Execution rework. Expected write path is `coordination/reports/TASK-152_REPORT.md`. Execution must follow `coordination/handoffs/TASK-152_PORTFOLIO_SIGNAL_DUPLICATE_UPDATE_REWORK.md`, modifying only allowed PortfolioMonitor/SignalEngine/RiskEngine files under `quant/portfolio/`, focused `tests/portfolio/` tests, and the report. It must fix duplicate-symbol validation for watchlist/holding merge `updates` inputs, keep all behavior offline over caller-provided or local code evidence, and avoid DataHub/FeatureHub/Scanner/StrategyLab/BacktestEngine implementation changes, warehouse reads, live data, risk-rule evaluation, upstream composition behavior, notification, AI, UI, automated trading, credentials, private data, hidden network behavior, and unrelated downstream work.

## TASK-152 Review Rejection / Duplicate Update Rework Dispatch

Review result:

- `coordination/reviews/TASK-152_REVIEW.md`
- Decision: rejected_or_blocked
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES

Controller decision:

- TASK-152 is not closed and is not marked Done.
- No Integration Agent is dispatched because the active workflow is `handoff -> Execution -> Review -> Controller`.
- Review found a focused contract validation gap: `merge_watchlist_snapshot()` and `merge_holding_snapshot()` materialize caller-provided `updates` as dicts keyed by symbol and therefore silently accept duplicate update symbols with last-write-wins behavior.
- `coordination/handoffs/TASK-152_PORTFOLIO_SIGNAL_DUPLICATE_UPDATE_REWORK.md` is dispatched as the next Active 5.3 execution handoff.
- This is a focused Review rework and is not merged with readiness `follow_up_batches`, the later composition/risk hardening batch, the later regression coverage batch, or any ordinary Phase 6 hardening item.
- Phase switch: NO. Current phase remains Phase 6 PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.
- AGENTS.md is unchanged because the current phase and allowed implementation targets remain Phase 6: `quant/portfolio/` and `tests/portfolio/`.

For active TASK-152 specifically, the next role is 5.3 Execution rework. Expected write path is `coordination/reports/TASK-152_REPORT.md`. Execution must follow `coordination/handoffs/TASK-152_PORTFOLIO_SIGNAL_DUPLICATE_UPDATE_REWORK.md`, modifying only allowed PortfolioMonitor/SignalEngine/RiskEngine files under `quant/portfolio/`, focused `tests/portfolio/` tests, and the report. It must keep the rework minimal to duplicate-symbol update validation and regression coverage, preserve default offline safety, and avoid live data, warehouse reads, risk-rule evaluation, upstream composition behavior, notification, AI, UI, automated trading, credentials, private data, hidden network behavior, or unrelated downstream work.

## TASK-152 Closure / TASK-153 Dispatch

Review result:

- `coordination/reviews/TASK-152_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-152 is closed as Done.
- No Integration Agent is dispatched because Review allowed Controller closure and the active workflow is `handoff -> Execution -> Review -> Controller`.
- Review accepted that the duplicate-update validation gap is fixed within allowed Phase 6 scope. `merge_watchlist_snapshot()` and `merge_holding_snapshot()` now reject duplicate update symbols before last-write-wins overwrite can occur, and focused offline regressions passed.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md`. Phase 6 remains incomplete because the current readiness gate reports `phase_closure_ready=false`, status counts `pass=3`, `warn=3`, `blocked=0`, `fail=0`; unresolved groups remain structured upstream-context signal composition, risk rule evaluation, and offline regression coverage for conflicts, staleness, risk blocks, and lifecycle transitions.
- Phase switch: NO. Current phase remains Phase 6 PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.
- Controller read the current Phase 6 readiness `follow_up_batches`. TASK-152 covered `portfolio_signal_risk__personal_trading_hardening__batch_01`; the next executable current-phase capability cluster is `portfolio_signal_risk__personal_trading_hardening__batch_02`, covering `phase6__upstream_signal_composition_foundation` and `phase6__risk_rule_evaluation_foundation`.
- This is a two-item coherent Phase 6 cluster from readiness `follow_up_batches`; it is not a single-item exception. It is dispatched together because structured signal composition and risk-rule evaluation share the same Phase 6 signal decision surface and audit output contracts.
- `coordination/handoffs/TASK-153_STRUCTURED_SIGNAL_RISK_FOUNDATION.md` is dispatched as the next Active 5.3 execution handoff.
- AGENTS.md is unchanged because the current phase and allowed implementation targets remain Phase 6: `quant/portfolio/` and `tests/portfolio/`.

For active TASK-153 specifically, the next role is 5.3 Execution. Expected write path is `coordination/reports/TASK-153_REPORT.md`. Execution must follow `coordination/handoffs/TASK-153_STRUCTURED_SIGNAL_RISK_FOUNDATION.md`, modifying only allowed PortfolioMonitor/SignalEngine/RiskEngine files under `quant/portfolio/`, focused `tests/portfolio/` tests, and the report. It must implement local/offline structured signal composition and deterministic risk-rule foundation over caller-provided evidence, preserve default offline safety, update readiness truth, and avoid live data, warehouse reads, upstream module implementation changes, notification, AI, UI, automated trading, credentials, private data, hidden network behavior, or unrelated downstream work.

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

## TASK-096 BaoStock Live Classifier Rework Dispatch

Review result:

- `coordination/reviews/TASK-096_REVIEW.md`
- Decision: REJECTED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS reported for BaoStock, but not closure-sufficient because the live classifier can downgrade BaoStock-specific contract/data failures to `SKIP`
- Rework required: YES, limited to live-smoke classifier truthfulness and focused regression tests/report evidence

Controller decision:

- TASK-096 is not closed.
- TASK-096 does not enter Integration.
- Phase 2.5-P remains active.
- Downstream modules remain inactive.
- The same TASK-096 returns to 5.3 Execution for focused classifier/test/report rework.

BaoStock classifier rework handoff:

- `coordination/handoffs/TASK-096_DATAHUB_A_SHARE_MINUTE_BARS_BAOSTOCK_LIVE_CLASSIFIER_REWORK.md`

Required follow-up:

- narrow the BaoStock live-environment classifier so only real network/proxy/DNS/TLS/upstream/BaoStock service availability failures skip
- ensure BaoStock-specific normalization, schema, symbol, dataset, interval, source-contract, or data errors fail instead of skipping
- add focused offline classifier regression coverage for the Review examples
- rerun required default/offline tests and the gated BaoStock live smoke where feasible
- update `coordination/reports/TASK-096_REPORT.md` truthfully with default and live-enabled evidence
- require fresh Review Agent verification before Controller closure

Phase gate decision after TASK-096 BaoStock review rejection:

- Phase switch: NO
- Reason: `coordination/reviews/TASK-096_REVIEW.md` explicitly rejects closure and identifies a test-truthfulness blocker in the BaoStock live classifier. Phase 2.5-P remains active, downstream modules remain inactive, and the next executable task is the same TASK-096 focused classifier rework rather than Integration, Done, or a new domain.

## TASK-096 Closure / TASK-097 Dispatch

Review result:

- `coordination/reviews/TASK-096_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS for the gated BaoStock A-share minute-bars smoke
- Rework required: NO

Controller decision:

- TASK-096 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- Phase 2.5-P remains active because the TASK-093 readiness queue still contains unresolved `warn` items and one owner credential blocker.
- `a_share_minute_bars` remains conservative at `partial`; TASK-096 closes its assigned hardening item but does not close the DataHub phase.

Next handoff:

- `coordination/handoffs/TASK-097_DATAHUB_A_SHARE_ADJUSTMENT_FACTOR_CONTRACT_HARDENING.md`

Phase gate decision after TASK-096 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports non-pass follow-up queue items. The next unclosed executable DataHub hardening item is `a_share_adjustment_factors`, whose current non-pass reason is that adjustment-factor semantics are merged into generic `DatasetName.CORPORATE_ACTIONS`.

## TASK-097 Review Rejection / Classifier Rework Dispatch

Review result:

- `coordination/reviews/TASK-097_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS on review rerun, but not closure-sufficient because classifier truthfulness remains blocked
- Rework required: YES

Controller decision:

- TASK-097 remains open and returns to 5.3 Execution rework.
- Review blocking finding: `AkshareAShareAdjustmentFactorsAdapter._is_adjustment_factors_network_unavailable()` treats route/source-name-only tokens such as `"sina"`, `"finance.sina.com.cn"`, and `"stock_zh_a_daily"` as network unavailable, so messages like `ValueError("sina hfq factor not available")` can be falsely reported as environment `SKIP`.
- Phase 2.5-P remains active; downstream modules remain inactive.
- No Integration is entered, TASK-097 is not marked Done, and no phase switch occurs.

Next handoff:

- `coordination/handoffs/TASK-097_DATAHUB_A_SHARE_ADJUSTMENT_FACTOR_LIVE_CLASSIFIER_REWORK.md`

Phase gate decision after TASK-097 Review rejection:

- Phase switch: NO
- Reason: `coordination/reviews/TASK-097_REVIEW.md` explicitly rejects closure and identifies a live-truthfulness blocker in the adjustment-factor classifier. Phase 2.5-P remains active, downstream modules remain inactive, and the next executable task is the same TASK-097 focused classifier rework rather than Integration, Done, or a new domain.

## TASK-097 Closure / TASK-098 Dispatch

Review result:

- `coordination/reviews/TASK-097_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS for the gated A-share adjustment-factor smoke
- Rework required: NO

Controller decision:

- TASK-097 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- Phase 2.5-P remains active because the TASK-093 readiness queue still contains unresolved `warn` items and one owner credential blocker.
- `a_share_adjustment_factors` remains conservative at `partial`; TASK-097 closes its assigned hardening item but does not close the DataHub phase.
- The packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness queue items.

Next handoff:

- `coordination/handoffs/TASK-098_DATAHUB_A_SHARE_CORPORATE_ACTIONS_TAXONOMY_HARDENING.md`

Phase gate decision after TASK-097 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports non-pass follow-up queue items. The next unclosed executable DataHub hardening item is `a_share_corporate_actions`, whose current non-pass reason is incomplete breadth across split/dividend/rights event families.

## TASK-098 Review Rejection / Shared Contract Rework Dispatch

Review result:

- `coordination/reviews/TASK-098_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES for the targeted TASK-098 suite; no hidden default live-network behavior observed
- Live-enabled result: PASS for the gated A-share corporate-actions smoke, but not closure-sufficient because the shared contract change breaks existing HK corporate-actions validation
- Rework required: YES

Controller decision:

- TASK-098 remains open and returns to 5.3 Execution rework.
- TASK-098 is not marked Done.
- TASK-098 does not enter Integration.
- Phase 2.5-P remains active.
- Downstream modules remain inactive.
- Review blocking finding: `DatasetName.CORPORATE_ACTIONS` now globally requires `action_family` and `source_route`, but existing HK corporate-actions records do not emit those top-level fields, causing HK corporate-actions adapter/live tests to fail schema validation.

Next handoff:

- `coordination/handoffs/TASK-098_DATAHUB_CORPORATE_ACTIONS_SHARED_CONTRACT_REWORK.md`

Required follow-up:

- fix the shared corporate-actions contract rollout so HK corporate-actions records satisfy the new required fields, or narrow the schema requirement so it does not apply globally where unsupported
- preserve A-share TASK-098 taxonomy hardening unless a narrower schema rule is required for source-truth correctness
- rerun A-share and HK corporate-actions default/offline tests
- rerun gated A-share/HK corporate-actions live smokes where source paths or shared schema validation changed
- update `coordination/reports/TASK-098_REPORT.md` with the cross-suite regression, fix, tests, and live-enabled evidence
- require fresh Review Agent verification before Controller closure

Phase gate decision after TASK-098 Review rejection:

- Phase switch: NO
- Reason: `coordination/reviews/TASK-098_REVIEW.md` explicitly blocks closure due to a shared `CORPORATE_ACTIONS` contract regression in existing HK corporate-actions coverage. Phase 2.5-P remains active, downstream modules remain inactive, and the next executable task is the same TASK-098 focused shared-contract rework rather than Integration, Done, a phase switch, or a new domain.

## TASK-098 Closure / TASK-099 Dispatch

Review result:

- `coordination/reviews/TASK-098_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS for the gated HK corporate-actions shared-contract rework smoke; A-share live was not rerun in the rework because the A-share adapter path and shared schema requirement did not change
- Rework required: NO

Controller decision:

- TASK-098 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- Phase 2.5-P remains active because the TASK-093 readiness queue still contains unresolved `warn` items and one owner credential blocker.
- `a_share_corporate_actions` remains conservative; TASK-098 closes its assigned taxonomy/shared-contract hardening item but does not close the DataHub phase.
- The packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness queue items.

Next handoff:

- `coordination/handoffs/TASK-099_DATAHUB_A_SHARE_VALUATION_HISTORY_BREADTH_HARDENING.md`

Phase gate decision after TASK-098 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports non-pass follow-up queue items. The next unclosed executable DataHub hardening item is `a_share_valuation_history`, whose current non-pass reason is that public AKShare coverage is bounded to near-year valuation date windows while longer history breadth and standardized pagination remain incomplete.

## TASK-099 Closure / TASK-100 Dispatch

Review result:

- `coordination/reviews/TASK-099_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS for the gated A-share valuation-history smoke
- Rework required: NO

Controller decision:

- TASK-099 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- Phase 2.5-P remains active because the Personal Trading Perfection Standard still forbids closure while `a_share_valuation_history` remains `partial` without full long-run continuity proof or an owner-accepted disposition, and the TASK-093 readiness queue still contains other unresolved `warn` items plus one owner credential blocker.
- TASK-099 improved public AKShare/Baidu valuation-history breadth beyond bounded near-year access, but `stock_zh_valuation_baidu` remains the only validated no-credential dated valuation-history source and longest-selector continuity remains unproven.
- The packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness items.

Next handoff:

- `coordination/handoffs/TASK-100_DATAHUB_A_SHARE_VALUATION_LONG_HISTORY_CONTINUITY_HARDENING.md`

Phase gate decision after TASK-099 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`. TASK-099 leaves `a_share_valuation_history` conservative at `partial`; the next executable DataHub hardening item is the valuation-history follow-up for longest Baidu selector continuity and no-credential second-source redundancy investigation.

## TASK-100 Review Rejection / Overlap Conflict Rework Dispatch

Review result:

- `coordination/reviews/TASK-100_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS per the execution report, but not closure-sufficient because Review found a blocking overlap/contract issue
- Rework required: YES

Controller decision:

- TASK-100 remains open and returns to 5.3 Execution rework.
- TASK-100 is not marked Done.
- TASK-100 does not enter Integration.
- Phase 2.5-P remains active.
- Downstream modules remain inactive.
- Review blocking finding: the Baidu/Eastmoney valuation-history combination logic silently drops every Baidu record on or after Eastmoney's earliest date, which hides same-date cross-route disagreements and can lose Baidu records for secondary-route gaps after Eastmoney's first available day.

Next handoff:

- `coordination/handoffs/TASK-100_DATAHUB_A_SHARE_VALUATION_OVERLAP_CONFLICT_REWORK.md`

Required follow-up:

- remove or replace the first-Eastmoney-date cutover policy
- ensure overlapping same-date cross-route disagreements are either preserved as route-distinct source facts with deterministic conflict detection or rejected with a clear deterministic error/result classification
- ensure Eastmoney gaps after its earliest available date do not cause Baidu source-backed records to disappear silently
- add offline regression coverage for both Review-required cases
- rerun the required default/offline tests and the gated A-share valuation live smoke
- update `coordination/reports/TASK-100_REPORT.md` with the final overlap policy, gap handling evidence, tests, live-enabled result, and capability truth
- require fresh Review Agent verification before Controller closure

Phase gate decision after TASK-100 Review rejection:

- Phase switch: NO
- Reason: `coordination/reviews/TASK-100_REVIEW.md` explicitly blocks closure due to a second-source overlap policy that hides source-truth conflicts and can lose source-backed Baidu records. Phase 2.5-P remains active, downstream modules remain inactive, and the next executable task is the same TASK-100 focused overlap conflict rework rather than Integration, Done, a phase switch, or a new domain.

## TASK-100 Review Rejection / Baidu Live Failure Rework Dispatch

Review result:

- `coordination/reviews/TASK-100_REVIEW.md`
- Decision: REJECTED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: FAIL on independent Review rerun
- Rework required: YES

Controller decision:

- TASK-100 remains open and returns to 5.3 Execution rework.
- TASK-100 is not marked Done.
- TASK-100 does not enter Integration.
- Phase 2.5-P remains active.
- Downstream modules remain inactive.
- Review finding now blocking closure: the overlap-conflict rework itself is directionally correct and has adequate offline overlap/gap coverage, but the live-enabled A-share valuation smoke failed on the Baidu route with upstream non-JSON content (`requests.exceptions.JSONDecodeError`), while the report still recorded live `PASS`.

Next handoff:

- `coordination/handoffs/TASK-100_DATAHUB_A_SHARE_VALUATION_BAIDU_LIVE_FAILURE_REWORK.md`

Required follow-up:

- diagnose whether the Baidu non-JSON response is source/upstream/network availability that should deterministically `SKIP`, or a repository-side handling gap that should fail or be fixed
- adjust only allowed adapter/live-test/report paths as needed for truthful live behavior
- preserve the accepted Baidu/Eastmoney overlap and gap behavior
- rerun required default/offline tests and the gated A-share valuation live smoke
- update `coordination/reports/TASK-100_REPORT.md` with fresh live truth and root-cause evidence
- require fresh Review Agent verification before Controller closure

Phase gate decision after latest TASK-100 Review rejection:

- Phase switch: NO
- Reason: `coordination/reviews/TASK-100_REVIEW.md` explicitly rejects closure because the current repository live-enabled truth is `FAIL`, not the reported `PASS`, and real-source live failures must be routed to 5.3 Execution rework before Controller closure. Phase 2.5-P remains active, downstream modules remain inactive, and the next executable task is the same TASK-100 focused Baidu live failure rework rather than Integration, Done, a phase switch, or a new domain.

## TASK-100 Closure / TASK-101 Dispatch

Review result:

- `coordination/reviews/TASK-100_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS for the gated A-share valuation smoke
- Rework required: NO

Controller decision:

- TASK-100 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, domain counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and `phase_closure_ready=False`.
- `a_share_valuation_history` remains conservative at `partial`; TASK-100 closes the assigned long-history/overlap/live-failure valuation hardening item but does not close DataHub readiness.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-101_DATAHUB_A_SHARE_CAPITAL_FLOW_HISTORY_CONTINUITY_HARDENING.md`

Phase gate decision after TASK-100 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`. The next executable DataHub hardening item is `a_share_capital_flow`, whose current non-pass reason is that public AKShare supports caller-provided multi-symbol bounded capital-flow batches with deterministic bounded date-window filtering, but broader historical continuity and latest-only fallback dependence remain incomplete.

## TASK-101 Closure / TASK-102 Dispatch

Review result:

- `coordination/reviews/TASK-101_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS for the gated A-share capital-flow smoke
- Rework required: NO

Controller decision:

- TASK-101 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, domain counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and `phase_closure_ready=False`.
- `a_share_capital_flow` remains conservative at `partial`; TASK-101 closes the assigned route-truth/history-continuity hardening item but does not close DataHub readiness.
- `a_share_northbound_flow` was not promoted or changed by TASK-101 and is the next unclosed executable DataHub hardening item.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-102_DATAHUB_A_SHARE_NORTHBOUND_FLOW_CONTRACT_PROFILE_HARDENING.md`

Phase gate decision after TASK-101 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`. The next executable DataHub hardening item is `a_share_northbound_flow`, whose current non-pass reason is that northbound-specific fields are not guaranteed as a dedicated contract slice.

## TASK-102 Closure / TASK-103 Dispatch

Review result:

- `coordination/reviews/TASK-102_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS for the gated A-share northbound-flow smoke
- Rework required: NO

Controller decision:

- TASK-102 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- Phase 2.5-P remains active because `build_personal_trading_readiness_report()` still reports overall `blocked`, domain counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and `phase_closure_ready=False`.
- `a_share_northbound_flow` remains conservative at `partial`; TASK-102 closes the assigned northbound contract/profile and classifier truthfulness item but does not close DataHub readiness.
- `a_share_turnover_liquidity` is the next unclosed executable DataHub hardening item.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-103_DATAHUB_A_SHARE_TURNOVER_LIQUIDITY_CANONICAL_FIELD_HARDENING.md`

Phase gate decision after TASK-102 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`. The next executable DataHub hardening item is `a_share_turnover_liquidity`, whose current non-pass reason is that liquidity fields exist but are not yet normalized into one explicit contract/profile slice.

## TASK-103 Review Rejection / Live Classifier Rework Dispatch

Review result:

- `coordination/reviews/TASK-103_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP in the current environment due to upstream/public-route unavailability, but the live gate is not reliable enough for closure
- Rework required: YES

Controller decision:

- TASK-103 remains open and returns to 5.3 Execution rework.
- No integration is entered because Review did not allow Controller closure.
- Phase 2.5-P remains active; downstream modules remain inactive.
- Required rework is limited to narrowing `tests/datahub/test_akshare_a_share_turnover_liquidity_live.py` so `stock_zh_a_hist` route-signature/call-compatibility defects fail instead of becoming environment `SKIP`, adding focused regression coverage, rerunning the required offline/default and gated live turnover/liquidity tests, and updating `coordination/reports/TASK-103_REPORT.md` truthfully.
- The existing TASK-103 turnover/liquidity contract/profile and capability truth must not be broadened by this classifier rework.

Next handoff:

- `coordination/handoffs/TASK-103_DATAHUB_A_SHARE_TURNOVER_LIQUIDITY_LIVE_CLASSIFIER_REWORK.md`

Phase gate decision after TASK-103 Review rejection:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; TASK-103 has unresolved Review findings and cannot close until the live classifier truthfulness issue is fixed and accepted by fresh Review.

## TASK-103 Closure / TASK-104 Dispatch

Review result:

- `coordination/reviews/TASK-103_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP due to independently reproduced environment/upstream disconnect: `ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`
- Rework required: NO

Controller decision:

- TASK-103 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-103 closes the assigned turnover/liquidity canonical field and classifier truthfulness item, but `a_share_turnover_liquidity` remains conservative and unpromoted.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved non-pass follow-up queue items.
- The next unclosed executable DataHub hardening item is `a_share_limit_up_down`, whose current non-pass reason is that broader A-share limit-up/down breadth and history coverage remains incomplete beyond bounded public pool routes.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-104_DATAHUB_A_SHARE_LIMIT_UP_DOWN_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-103 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; the next executable TASK-093 queue item is `a_share_limit_up_down` with disposition `datahub_hardening`.

## TASK-104 Review Rejection / Classifier Rework Dispatch

Review result:

- `coordination/reviews/TASK-104_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS independently reproduced by Review, but not closure-ready because classifier truthfulness is blocked
- Rework required: YES

Controller decision:

- At that decision point, TASK-104 remained active and was not marked Done.
- No integration is entered.
- Phase 2.5-P remains active.
- The rework scope is limited to the Review finding: new `gettopicpreviouspool` / `gettopiczbgcpool` route-name tokens must not, by themselves, convert repository-side contract, payload, schema, normalization, or route-signature/call-compatibility defects into environment `SKIP`.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-104_DATAHUB_A_SHARE_LIMIT_UP_DOWN_LIVE_CLASSIFIER_REWORK.md`

Phase gate decision after TASK-104 Review rejection:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; TASK-104 has unresolved blocking Review findings and cannot close until the live classifier truthfulness issue is fixed and accepted by fresh Review.

## TASK-104 Closure / TASK-105 Dispatch

Review result:

- `coordination/reviews/TASK-104_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`)
- Rework required: NO

Controller decision:

- TASK-104 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-104 closes the assigned A-share limit-up/down breadth/history and focused classifier-truthfulness item, but `a_share_limit_up_down` remains conservative and unpromoted unless the accepted source capability truth proves otherwise.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved non-pass follow-up queue items.
- The next unclosed executable DataHub hardening item is `a_share_margin_financing_and_lending`, whose current non-pass reason is that public AKShare coverage remains a one-symbol adapter slice and broader trading-grade breadth/history coverage remains incomplete.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-105_DATAHUB_A_SHARE_MARGIN_FINANCING_LENDING_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-104 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; the next executable TASK-093 queue item is `a_share_margin_financing_and_lending` with disposition `datahub_hardening`.

## TASK-105 Closure / TASK-106 Dispatch

Review result:

- `coordination/reviews/TASK-105_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`)
- Rework required: NO

Controller decision:

- TASK-105 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-105 closes the assigned A-share margin financing/lending breadth/history hardening item by proving caller-provided multi-symbol bounded SSE/SZSE margin-detail history with explicit exchange/source-route provenance and schema-valid live evidence.
- `a_share_margin_financing_and_lending` remains conservative and unpromoted because no validated public BSE symbol-level route, no symbol-compatible exchange-summary normalization path, and no proven long-history continuity beyond bounded detail-route iteration are established.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved non-pass follow-up queue items.
- The next unclosed executable DataHub hardening item is `a_share_financial_statements`, whose current non-pass reason is that public AKShare caller-provided multi-symbol bounded report-period financial-statement access is validated, but broader statement-family breadth, public-source history continuity, and trading-grade completeness remain incomplete.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-106_DATAHUB_A_SHARE_FINANCIAL_STATEMENTS_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-105 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; the next executable TASK-093 queue item is `a_share_financial_statements` with disposition `datahub_hardening`.

## TASK-106 Closure / TASK-107 Dispatch

Review result:

- `coordination/reviews/TASK-106_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`)
- Rework required: NO

Controller decision:

- TASK-106 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-106 closes the assigned A-share financial-statements breadth/history/source-truth item by adding explicit `source_route` statement provenance, proving schema-valid live records from `stock_financial_report_sina`, and tightening financial-data live classifier truthfulness.
- `a_share_financial_statements` remains conservative and unpromoted because no validated second no-credential public statement route and no full long-history continuity proof are established.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved non-pass follow-up queue items.
- The next unclosed executable DataHub hardening item is `a_share_financial_indicators`, whose current non-pass reason is that public AKShare caller-provided multi-symbol bounded report-period financial-indicator access is validated, but broader indicator breadth, public-source history continuity, route truth, and trading-grade completeness remain incomplete.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-107_DATAHUB_A_SHARE_FINANCIAL_INDICATORS_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-106 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; the next executable TASK-093 queue item is `a_share_financial_indicators` with disposition `datahub_hardening`.

## TASK-107 Closure / TASK-108 Dispatch

Review result:

- `coordination/reviews/TASK-107_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`)
- Rework required: NO

Controller decision:

- TASK-107 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-107 closes the assigned A-share financial-indicators breadth/history/source-truth item by adding explicit `source_route` and `metric_family` provenance, proving schema-valid live indicator records from `stock_financial_analysis_indicator_em`, and preserving financial-statement behavior.
- `a_share_financial_indicators` remains conservative and unpromoted because no validated second no-credential public indicator route, no full long-history continuity proof, and no broad cross-industry metric-family completeness proof are established.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved non-pass follow-up queue items.
- The next unclosed executable DataHub hardening item is `a_share_company_announcements`, whose current non-pass reason is that A-share public announcement coverage remains too narrow for practical breadth/history and source-truth parity.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-108_DATAHUB_A_SHARE_COMPANY_ANNOUNCEMENTS_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-107 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; the next executable TASK-093 queue item is `a_share_company_announcements` with disposition `datahub_hardening`.

## TASK-108 Review Rejection / Date-Window Rework Dispatch

Review result:

- `coordination/reviews/TASK-108_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS, but closure remains blocked by Review findings
- Rework required: YES

Controller decision:

- TASK-108 is not closed.
- TASK-108 is not moved to Integration.
- At that point, TASK-108 remained Active for focused 5.3 Execution rework.
- Required rework is limited to adding live assertions that returned announcement dates are inside the requested bounded window and fixing or truthfully narrowing fallback date-route behavior so per-day upstream/source availability failures cannot silently satisfy incomplete requested windows.
- `a_share_company_announcements` remains conservative and must not be promoted through this rework unless source-backed evidence genuinely satisfies the Personal Trading Perfection Standard.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved non-pass follow-up queue items.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-108_DATAHUB_A_SHARE_COMPANY_ANNOUNCEMENTS_DATE_WINDOW_REWORK.md`

Phase gate decision after TASK-108 Review rejection:

- Phase switch: NO
- Reason: Review blocked TASK-108 closure; Phase 2.5-P cannot advance until focused date-window/fallback truth rework is executed and freshly accepted by Review.

## TASK-108 Closure / TASK-109 Dispatch

Review result:

- `coordination/reviews/TASK-108_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`)
- Rework required: NO

Controller decision:

- TASK-108 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-108 closes the assigned A-share company-announcements breadth/history/date-window/fallback truth item by adding bounded date-window live assertions, preserving source/market/symbol/route truth, and preventing partial fallback per-day upstream/source availability failures from silently satisfying incomplete requested windows.
- `a_share_company_announcements` remains conservative and unpromoted because broader history continuity and no-credential second-route redundancy remain unproven.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved non-pass follow-up queue items.
- The next unclosed executable DataHub hardening item is `a_share_major_activity_events`, whose current non-pass reason is that A-share major-activity event coverage remains narrow around the existing bounded block-trade detail route and lacks broader route/history continuity proof.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-109_DATAHUB_A_SHARE_MAJOR_ACTIVITY_EVENTS_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-108 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; the next executable TASK-093 queue item is `a_share_major_activity_events` with disposition `datahub_hardening`.

## TASK-109 Closure / TASK-110 Dispatch

Review result:

- `coordination/reviews/TASK-109_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`)
- Rework required: NO

Controller decision:

- TASK-109 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-109 closes the assigned A-share major-activity breadth/history item by adding bounded multi-day `stock_dzjy_mrmx` detail plus `stock_dzjy_mrtj` symbol-date summary coverage, explicit `source_route` truth, unit-normalized summary values, deterministic validation, and gated live PASS evidence.
- `a_share_major_activity_events` remains conservative and unpromoted because broader non-block-trade taxonomy, longer-history continuity, and no-credential second-source redundancy remain unproven.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved non-pass follow-up queue items.
- The next unclosed executable DataHub hardening item is `hk_universe_reference`, whose current non-pass reason is that Hong Kong universe reference still lacks full-market breadth, non-stock taxonomy coverage, and dated delisting/lifecycle metadata proof.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-110_DATAHUB_HK_UNIVERSE_BREADTH_LIFECYCLE_HARDENING.md`

Phase gate decision after TASK-109 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; the next executable TASK-093 queue item is `hk_universe_reference` with disposition `datahub_hardening`.

## TASK-110 Closure / TASK-111 Dispatch

Review result:

- `coordination/reviews/TASK-110_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`)
- Rework required: NO

Controller decision:

- TASK-110 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-110 closes the assigned HK universe profile-route provenance/classifier-truth item by adding optional `source_route` truth to `DatasetName.INSTRUMENT_MASTER`, emitting `source_route="stock_hk_security_profile_em"` on normalized HK stock reference records, and preserving hard-fail behavior for repository-side route/payload/schema/normalization/signature defects.
- `hk_universe_reference` remains conservative and unpromoted because full-market HK universe breadth, non-stock taxonomy coverage, and dated delisting/lifecycle metadata remain unproven.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports unresolved non-pass follow-up queue items and `phase_closure_ready=False`.
- The next executable DataHub hardening item remains the unresolved `hk_universe_reference` capability, now focused on HK listed-universe/list-route feasibility, non-stock taxonomy truth, and dated lifecycle/listing-status source truth where stable no-credential public routes expose it.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-111_DATAHUB_HK_LISTED_UNIVERSE_LIFECYCLE_ROUTE_FEASIBILITY_HARDENING.md`

Phase gate decision after TASK-110 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `hk_universe_reference` remains `partial` after TASK-110, and the next executable handoff continues that unresolved TASK-093 queue item.

## TASK-111 Closure / TASK-112 Dispatch

Review result:

- `coordination/reviews/TASK-111_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS overall for `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`; profile-route smoke passed and the new bounded current-list smoke skipped on genuine upstream `stock_hk_spot_em` `RemoteDisconnected`
- Rework required for TASK-111 closure: NO

Controller decision:

- TASK-111 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-111 closes the assigned HK listed-universe/list-route feasibility slice by adding a bounded `symbols=None` current-list path using `stock_hk_spot_em` plus per-symbol `stock_hk_security_profile_em` reconciliation, deterministic ordering, route provenance, offline coverage, and conservative source-capability wording.
- `hk_universe_reference` remains conservative and unpromoted because full-market HK universe breadth, stable non-stock taxonomy coverage, dated delisting/lifecycle metadata, and live PASS evidence for the new bounded current-list route remain incomplete.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports unresolved non-pass follow-up queue items and `phase_closure_ready=False`.
- The next executable DataHub hardening item remains the unresolved `hk_universe_reference` capability, now focused on diagnosing the skipped HK current-list route, proving a stable no-credential list route or fallback if feasible, or truthfully constraining capability/source wording without promotion.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-112_DATAHUB_HK_LISTED_UNIVERSE_LIVE_EVIDENCE_ROUTE_FALLBACK_HARDENING.md`

Phase gate decision after TASK-111 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `hk_universe_reference` remains `partial` after TASK-111, and the next executable handoff continues that unresolved TASK-093 queue item with a live-evidence/fallback focus.

## TASK-112 Closure / TASK-113 Dispatch

Review result:

- `coordination/reviews/TASK-112_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`)
- Rework required: NO

Controller decision:

- TASK-112 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-112 closes the assigned HK current-listed live-evidence/fallback slice by adding a bounded fallback list route, `sina_hk_stock_spot_page1`, that activates only after primary `stock_hk_spot_em` is classified as genuine environment/upstream unavailability and still reconciles through `stock_hk_security_profile_em`.
- `hk_universe_reference` remains conservative and unpromoted because TASK-112 proves only bounded current-listed stock sample access; full practical HK universe breadth, non-stock taxonomy truth, and dated delisting/lifecycle metadata remain incomplete.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports unresolved non-pass follow-up queue items and `phase_closure_ready=False`.
- The next executable DataHub hardening item remains the unresolved `hk_universe_reference` capability, now focused on source-backed HK non-stock taxonomy and dated lifecycle/listing-status truth where stable no-credential public routes expose it, or explicit source limitation wording without promotion.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-113_DATAHUB_HK_UNIVERSE_TAXONOMY_LIFECYCLE_LIMITATION_HARDENING.md`

Phase gate decision after TASK-112 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `hk_universe_reference` remains `partial` after TASK-112, and the next executable handoff continues that unresolved TASK-093 queue item with a taxonomy/lifecycle limitation focus.

## TASK-113 Closure / TASK-114 Dispatch

Review result:

- `coordination/reviews/TASK-113_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`)
- Rework required: NO

Controller decision:

- TASK-113 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-113 closes the assigned HK universe taxonomy/lifecycle limitation item by keeping `AkshareHKInstrumentMasterAdapter` behavior unchanged, tightening `hk_universe_reference` and source-catalog wording, and explicitly recording that proven no-credential HK routes remain stock-only and do not expose reusable non-stock taxonomy or trustworthy dated delist/inactive lifecycle metadata.
- `hk_universe_reference` remains conservative and unpromoted at `partial`; no further HK universe promotion is accepted without a future stable source-backed route or explicit owner disposition.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports unresolved non-pass follow-up queue items and `phase_closure_ready=False`.
- The next executable DataHub hardening item is `hk_daily_bars`, focused on history continuity and broader public-source redundancy beyond bounded batch coverage.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-114_DATAHUB_HK_DAILY_BARS_HISTORY_REDUNDANCY_HARDENING.md`

Phase gate decision after TASK-113 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `hk_daily_bars` is the next unresolved TASK-093 queue item with disposition `datahub_hardening`.

## TASK-114 Closure / TASK-115 Dispatch

Review result:

- `coordination/reviews/TASK-114_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`)
- Rework required: NO

Controller decision:

- TASK-114 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-114 closes its assigned HK daily-bars hardening item by using `stock_hk_daily` as an AKShare same-family fallback when `stock_hk_hist` is unavailable or empty, preserving local date-window filtering, deterministic normalization, and hard-fail behavior for repository defects.
- `hk_daily_bars` remains conservative and unpromoted at `partial` because the proven route redundancy is same-family AKShare fallback, not an independent no-credential public source.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports unresolved non-pass follow-up queue items and `phase_closure_ready=False`.
- The next TASK-093 queue item, `hk_minute_bars`, has `disposition=owner_waiver_required`; without owner waiver or explicit feasibility scope, it is not dispatched as the next executable implementation task.
- The next executable DataHub hardening item is `hk_corporate_actions`, focused on HK corporate-action taxonomy/history coverage where stable no-credential routes expose source truth, or explicit source limitation wording without promotion.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-115_DATAHUB_HK_CORPORATE_ACTIONS_TAXONOMY_HISTORY_HARDENING.md`

Phase gate decision after TASK-114 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `hk_corporate_actions` is the next executable unresolved TASK-093 queue item with disposition `datahub_hardening`, while optional `hk_minute_bars` remains owner-waiver-required.

## TASK-115 Closure / TASK-116 Dispatch

Review result:

- `coordination/reviews/TASK-115_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`)
- Rework required: NO

Controller decision:

- TASK-115 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-115 closes its assigned HK corporate-actions taxonomy/history hardening item by combining `stock_hk_dividend_payout_em` and `stock_hk_fhpx_detail_ths`, preserving route-distinct source truth, validating shared `DatasetName.CORPORATE_ACTIONS` records, and distinguishing `dividend_distribution` from source-backed `dividend_no_distribution`.
- `hk_corporate_actions` remains conservative and unpromoted at `partial` because non-dividend HK corporate-action families and caller-provided multi-symbol batch breadth remain unproven.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports unresolved non-pass follow-up queue items and `phase_closure_ready=False`.
- The next executable DataHub hardening item is `hk_valuation_history`, focused on HK valuation-history contract hardening, dated valuation facts, source-route/metric truth, and date-window behavior where stable no-credential routes expose source truth.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-116_DATAHUB_HK_VALUATION_HISTORY_CONTRACT_HARDENING.md`

Phase gate decision after TASK-115 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `hk_valuation_history` is the next executable unresolved TASK-093 queue item with disposition `datahub_hardening`.

## TASK-116 Closure / TASK-117 Dispatch

Review result:

- `coordination/reviews/TASK-116_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_valuation_snapshot_live.py`)
- Rework required: NO

Controller decision:

- TASK-116 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-116 closes its assigned HK valuation-history contract hardening item by expanding `AkshareHKValuationSnapshotAdapter` to caller-provided HK symbol batches with bounded dated history from `stock_hk_indicator_eniu`, explicit `source_route` truth, deterministic date-window behavior, and conservative capability/catalog wording.
- `hk_valuation_history` remains conservative and unpromoted at `partial` because accepted live evidence shows public history through `2022-07-13`, while current-dated continuity, reliable optional Baidu supplementation, and independent no-credential redundancy remain unproven.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and 42 non-pass follow-up queue items.
- The next executable DataHub hardening item is `hk_financial_data`, focused on HK financial statements/indicators market breadth, report-period history, source-route/statement/metric truth, and date-window behavior where stable no-credential routes expose source truth.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-117_DATAHUB_HK_FINANCIAL_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-116 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `hk_financial_data` is the next executable unresolved TASK-093 queue item with disposition `datahub_hardening`.

## TASK-117 Review Rejection / Classifier Rework Dispatch

Review result:

- `coordination/reviews/TASK-117_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS in the execution/review environment, but not closure-ready because repository-side route defects can still be downgraded to `SKIP`
- Rework required: YES

Controller decision:

- TASK-117 is not closed and is not moved to Integration.
- TASK-117 remains the Active task in Phase 2.5-P.
- The focused blocker is HK financial live/source-unavailability classifier truthfulness: both `tests/datahub/test_akshare_hk_financial_data_live.py` and `quant/datahub/adapters/akshare.py` can treat route-name-bearing signature, schema, payload, or normalization defects as environment/source unavailable.
- The next 5.3 Execution handoff must narrow those classifiers to genuine network/proxy/DNS/TLS/upstream/public-source availability failures, add regression coverage proving route-name-bearing repository defects fail rather than skip, rerun the default and gated live HK financial tests, and update `coordination/reports/TASK-117_REPORT.md`.
- `hk_financial_data` remains conservative and unpromoted while the classifier blocker is unresolved.
- Phase 2.5-P remains active; downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-117_DATAHUB_HK_FINANCIAL_LIVE_CLASSIFIER_REWORK.md`

Phase gate decision after TASK-117 review:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; TASK-117 has unresolved Review findings and cannot close until the HK financial classifier truthfulness issue is fixed and accepted by fresh Review.

## TASK-117 Closure / TASK-118 Dispatch

Review result:

- `coordination/reviews/TASK-117_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py`, independently rerun by Review on 2026-06-06)
- Rework required: NO

Controller decision:

- TASK-117 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-117 closes its assigned HK financial classifier truthfulness rework by limiting route-unavailable classification to genuine transport/upstream symptoms plus explicit unavailability signals.
- `hk_financial_data` remains conservative and unpromoted because the accepted rework was classifier-only and did not close broader HK financial-data breadth, long-history continuity, non-stock support, or independent public-source redundancy.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and 42 non-pass follow-up queue items.
- The next executable DataHub hardening item is `hk_turnover_liquidity`, focused on canonical source-backed HK turnover/liquidity field semantics and checks where stable no-credential public routes expose source truth.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-118_DATAHUB_HK_TURNOVER_LIQUIDITY_CANONICAL_FIELD_HARDENING.md`

Phase gate decision after TASK-117 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `hk_turnover_liquidity` is the next executable unresolved TASK-093 queue item with disposition `datahub_hardening`.

## TASK-118 Closure / TASK-119 Dispatch

Review result:

- `coordination/reviews/TASK-118_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`, independently rerun by Review on 2026-06-06)
- Rework required: NO

Controller decision:

- TASK-118 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-118 closes its assigned HK turnover/liquidity canonical field hardening item by making source-backed HK liquidity facts explicit through dated volume and traded amount, preserving `DatasetName.DAILY_BARS` compatibility, source-route truth, deterministic date-window behavior, and conservative capability/catalog wording.
- `hk_turnover_liquidity` remains conservative and unpromoted because accepted public evidence is limited to `stock_hk_hist` plus same-family `stock_hk_daily` fallback facts; turnover-rate, float-share, spread/microstructure facts, and independent no-credential public-source redundancy remain unproven.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and 42 non-pass follow-up queue items.
- The controller packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness queue items.
- The next executable DataHub hardening item is `fund_daily_bars`, focused on ETF/fund daily-bar breadth and history continuity beyond bounded public exchange ETF coverage where stable no-credential public routes expose source truth.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-119_DATAHUB_ETF_FUND_DAILY_BARS_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-118 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `fund_daily_bars` is the next executable unresolved TASK-093 queue item with disposition `datahub_hardening`.

## Historical TASK-119 Review Rejection / Symbol-Family Truth Rework Dispatch

Review result:

- `coordination/reviews/TASK-119_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS, but not closure-sufficient because Review found a source-truth blocker
- Rework required: YES

Controller decision:

- At this historical rejection checkpoint, TASK-119 remained active and was not closed.
- At this historical rejection checkpoint, TASK-119 did not enter Integration.
- At this historical rejection checkpoint, TASK-119 was not marked Done.
- The blocking finding is limited to ETF/fund daily-bar symbol-family truth: the initial implementation accepted all `16` / `18` / `150` / `501` listed-fund prefixes, while evidence and tests only proved `161725.FUND_CN` through the LOF route and Sina fallback.
- The minimum next action is a 5.3 Execution rework that either narrows listed-fund support to the actually proven family/path or adds explicit route evidence plus regression coverage for every newly accepted prefix family.
- `fund_daily_bars` remains conservative and must not be promoted from `partial` by this rework unless source-backed evidence genuinely satisfies the Personal Trading Perfection Standard, which is not expected from this narrow Review fix.
- Phase 2.5-P remains active because TASK-119 has unresolved Review findings and the DataHub readiness queue still has unresolved non-pass items.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-119_DATAHUB_ETF_FUND_DAILY_BARS_SYMBOL_FAMILY_TRUTH_REWORK.md`

Phase gate decision after TASK-119 review:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; TASK-119 has unresolved Review findings and cannot close until the ETF/fund daily-bar symbol-family truth blocker is fixed and accepted by fresh Review.

## TASK-119 Closure / TASK-120 Dispatch

Review result:

- `coordination/reviews/TASK-119_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`)
- Rework required: NO

Controller decision:

- TASK-119 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-119 closes the focused ETF/fund daily-bars symbol-family truth blocker by narrowing listed-fund daily-bar support to the single proven `161725.FUND_CN` path and rejecting previously overclaimed listed-fund prefix families without route evidence.
- Existing exchange ETF daily-bar behavior is preserved.
- `fund_daily_bars` remains conservative and unpromoted because broader listed-fund breadth, off-exchange fund breadth, longer history continuity, and independent public-route redundancy remain incomplete.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked` and `phase_closure_ready=False`.
- The next executable DataHub hardening item is `fund_nav`, focused on ETF/fund NAV breadth and history continuity beyond bounded public exchange ETF coverage where stable no-credential public routes expose source truth.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-120_DATAHUB_ETF_FUND_NAV_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-119 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `fund_nav` is the next executable unresolved TASK-093 queue item with disposition `datahub_hardening`.

## TASK-120 Closure / TASK-121 Dispatch

Review result:

- `coordination/reviews/TASK-120_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py`, independently rerun by Review)
- Rework required: NO

Controller decision:

- TASK-120 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-120 closes its assigned ETF/fund NAV breadth/history hardening item by adding explicit `FUND_CN` public-fund NAV support, bounded open-fund history, and ETF empty-window fallback while preserving existing exchange ETF behavior and clear ambiguity rejection.
- `fund_nav` remains conservative and unpromoted because some fund classes remain unproven, route-level provenance is not first-class in the dataset contract, and independent public-route redundancy remains incomplete.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and 42 non-pass follow-up queue items.
- The controller packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness queue items.
- The next executable DataHub hardening item is `fund_holdings_composition`, focused on ETF/fund holdings breadth and history continuity beyond bounded public report-period coverage where stable no-credential public routes expose source truth.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-121_DATAHUB_ETF_FUND_HOLDINGS_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-120 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `fund_holdings_composition` is the next executable unresolved TASK-093 queue item with disposition `datahub_hardening`.

## TASK-121 Closure / TASK-122 Dispatch

Review result:

- `coordination/reviews/TASK-121_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`)
- Rework required: NO

Controller decision:

- TASK-121 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-121 closes its assigned ETF/fund holdings breadth/history hardening item by adding explicit mixed ETF/fund symbol-family truth for `fund_portfolio_hold_em`, supporting exchange ETFs plus explicit `FUND_CN` domestic-equity funds where public rows normalize safely, preserving `DatasetName.FUND_HOLDINGS` compatibility, and rejecting unsafe non-A-share constituent payloads clearly.
- `fund_holdings_composition` remains conservative and unpromoted because some fund classes still emit non-A-share constituents or empty payloads, longer history continuity remains unproven, and independent public-route redundancy remains incomplete.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and unresolved non-pass follow-up queue items.
- The controller packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness queue items.
- The next executable DataHub hardening item is `fund_scale_and_share`, focused on adding a canonical ETF/fund scale/share source-fact schema because current scale/share facts are not represented as a dedicated normalized contract slice.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-122_DATAHUB_ETF_FUND_SCALE_SHARE_CANONICAL_SCHEMA.md`

Phase gate decision after TASK-121 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `fund_scale_and_share` is the next executable unresolved TASK-093 queue item with disposition `datahub_hardening`.

## TASK-122 Review Rejection / Signed Metric Rework Dispatch

Review result:

- `coordination/reviews/TASK-122_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP; no live smoke was required because the initial execution was contract/capability/catalog only
- Rework required: YES

Controller decision:

- TASK-122 remains Active and is not closed.
- No integration is entered because Review did not allow Controller closure.
- TASK-122 must not be marked Done until a fresh Review accepts the rework.
- The blocking finding is narrow: `FUND_SCALE_SHARE_SNAPSHOT` currently applies nonnegative validation to every `metric_value`, which prevents valid negative scale/share change facts even though change-style metrics are in scope.
- The next execution must fix signed metric semantics without expanding into adapter work, source collection, downstream modules, paid credentials, or hidden default live network behavior.
- Phase 2.5-P remains active; downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-122_DATAHUB_ETF_FUND_SCALE_SHARE_SIGNED_METRIC_REWORK.md`

Phase gate decision after TASK-122 Review rejection:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; TASK-122 has unresolved Review findings and cannot close until the signed metric contract blocker is fixed and accepted by fresh Review.

## TASK-122 Closure / TASK-123 Dispatch

Review result:

- `coordination/reviews/TASK-122_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; no live smoke was required or permitted for the schema/test-only signed metric rework
- Rework required: NO

Controller decision:

- TASK-122 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-122 closes the canonical ETF/fund scale/share schema and signed-metric blocker by adding `DatasetName.FUND_SCALE_SHARE_SNAPSHOT`, mapping `fund_scale_and_share` to that dedicated contract, and fixing validation so legitimate change-style negative metrics are allowed while nonnegative level metrics such as `shares_outstanding` remain rejected when negative.
- `fund_scale_and_share` remains conservative and unpromoted because TASK-122 did not add adapter-backed source emission or prove broader public-source breadth, longer history continuity, richer share-change coverage, or independent route redundancy.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` still reports unresolved non-pass follow-up queue items and `phase_closure_ready=False`.
- The controller packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness queue items.
- The next executable DataHub hardening item continues `fund_scale_and_share`, focused on ETF/fund scale/share source breadth, longer history continuity, and independent route redundancy beyond the current overlapping profile/NAV/exchange scale-share public-source proof.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-123_DATAHUB_ETF_FUND_SCALE_SHARE_SOURCE_BREADTH_HARDENING.md`

Phase gate decision after TASK-122 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; `fund_scale_and_share` remains an unresolved DataHub personal trading perfection queue item after the schema/signed-metric fix, and the next executable handoff must harden public-source scale/share breadth or constrain capability truth without promotion.

## TASK-123 Review Rejection / Bounded Request Rework Dispatch

Review result:

- `coordination/reviews/TASK-123_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS, but not closure-ready because Review found a scope/implementation blocker
- Rework required: YES

Controller decision:

- TASK-123 remains Active and is not closed.
- TASK-123 does not enter Integration because Review did not allow Controller closure.
- TASK-123 must not be marked Done until a fresh Review accepts the rework.
- The blocking finding is focused: `AkshareETFFundFlowAdapter` now unconditionally fetches Sina full-table latest snapshot routes for every `DatasetName.FUND_SCALE_SHARE_SNAPSHOT` request, including bounded ETF-only requests that already have exchange-history routes. This violates the TASK-123 bounded-request requirement.
- The non-blocking cleanup is to remove duplicate scale/share helper insertion from `AkshareETFFundNavSnapshotAdapter` unless directly required by the accepted reworked path.
- The next execution must fix bounded-request behavior with the smallest DataHub-only change, either by restricting snapshot route use to explicit request-scoped behavior that does not silently expand bounded requests or by reverting/constraining adapter-backed snapshot expansion and capability/catalog truth.
- `fund_scale_and_share` remains conservative and unpromoted.
- Phase 2.5-P remains active; downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-123_DATAHUB_ETF_FUND_SCALE_SHARE_BOUNDED_REQUEST_REWORK.md`

Phase gate decision after TASK-123 Review rejection:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; TASK-123 has unresolved Review findings and cannot close until the bounded-request blocker is fixed and accepted by fresh Review.

## TASK-123 Closure / TASK-124 Dispatch

Review result:

- `coordination/reviews/TASK-123_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-123 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-123 closes the focused ETF/fund scale/share bounded-request blocker by ensuring bounded ETF-only `FUND_SCALE_SHARE_SNAPSHOT` requests no longer invoke Sina full-table snapshot routes when exchange-history rows already cover the requested symbols.
- The accepted rework keeps Sina snapshot routes only as request-scoped fallback for uncovered bounded target symbols, removes unrelated duplicate scale/share helper code from `AkshareETFFundNavSnapshotAdapter`, preserves accepted `FUND_FLOW`, `FUND_NAV_SNAPSHOT`, and `FUND_SCALE_SHARE_SNAPSHOT` behavior, keeps default tests offline-safe, and records live-enabled PASS evidence for scale/share and fund-flow smokes.
- `fund_scale_and_share` remains conservative and unpromoted because broader fund-family breadth, longer history continuity outside ETF exchange share history, clearer raised-scale unit semantics, and independent public-route redundancy remain incomplete.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and 42 non-pass follow-up queue items.
- The controller packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness queue items.
- The next executable DataHub hardening item is `fund_flow`, focused on ETF/fund flow breadth and history beyond bounded exchange scale/share date-window slices.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-124_DATAHUB_ETF_FUND_FLOW_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-123 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection queue items remain, and `fund_flow` is the next executable ETF/fund capability with disposition `datahub_hardening`.

## TASK-124 Closure / TASK-125 Dispatch

Review result:

- `coordination/reviews/TASK-124_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-124 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-124 closes its ETF/fund flow breadth/history hardening item by adding optional `source_route` truth to `DatasetName.FUND_FLOW`, keeping route-distinct records separate during deduplication, and tightening capability/catalog wording so aggregate-only, status-only, latest-only, or call-incompatible routes are not overclaimed as stronger per-fund dated public flow proof.
- `fund_flow` remains conservative and unpromoted because no independent bounded per-fund dated public flow route, broader non-exchange fund breadth, richer net-inflow/subscription/redemption history, or public-route redundancy was proven.
- Phase 2.5-P remains active because unresolved DataHub personal trading perfection queue items remain; `index_weight_history` remains an owner paid-credential blocker, optional `hk_minute_bars` remains owner-waiver-required, and ETF/fund premium-discount, index, sector/concept, macro/policy, and quality-report gaps still require accepted hardening or owner-accepted disposition.
- The controller packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness queue items.
- The next executable DataHub hardening item is `fund_premium_discount`, focused on ETF/fund premium-discount breadth and history beyond bounded latest-available exchange snapshots.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-125_DATAHUB_ETF_FUND_PREMIUM_DISCOUNT_BREADTH_HISTORY_HARDENING.md`

Phase gate decision after TASK-124 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection queue items remain, and `fund_premium_discount` is the next executable ETF/fund capability with disposition `datahub_hardening`.

## TASK-125 Review Rejection / Live Classifier Rework Dispatch

Review result:

- `coordination/reviews/TASK-125_REVIEW.md`
- Decision: REWORK REQUIRED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS as recorded by execution, but not closure-ready because classifier truthfulness is blocked
- Rework required: YES

Controller decision:

- At that point, TASK-125 remained Active and was not marked Done.
- No integration is entered.
- The rework is limited to the Review finding: historical ETF/fund premium-discount route function-name tokens such as `fund_etf_hist_em`, `fund_lof_hist_em`, and `fund_etf_hist_sina` must not cause route-signature or call-compatibility defects to be classified as environment/source unavailability.
- Next execution must narrow `_is_fund_premium_discount_route_unavailable()`, add focused regression coverage for historical-route TypeError/call-compatibility failures, preserve default offline safety, and record a truthful gated live result.
- At that point, Phase 2.5-P remained active because unresolved DataHub personal trading perfection queue items remained; TASK-125 could not close until fresh Review accepted the rework and explicitly allowed Controller closure.

Next handoff:

- `coordination/handoffs/TASK-125_DATAHUB_ETF_FUND_PREMIUM_DISCOUNT_LIVE_CLASSIFIER_REWORK.md`

Phase gate decision after TASK-125 review rejection:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; TASK-125 has unresolved Review blocking findings and must receive a focused 5.3 Execution rework plus fresh Review before closure.

## TASK-125 Closure / TASK-126 Dispatch

Review result:

- `coordination/reviews/TASK-125_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-125 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-125 closes the ETF/fund premium-discount breadth/history and classifier-truthfulness item by preserving the accepted `DatasetName.FUND_PREMIUM_DISCOUNT` hardening result and narrowing `_is_fund_premium_discount_route_unavailable()` so historical route/function-name tokens alone no longer downgrade route-signature or call-compatibility defects into environment `SKIP`.
- The accepted rework adds focused regression coverage for `TypeError("fund_etf_hist_em() got an unexpected keyword argument 'adjust'")` and for route-name-bearing repository-side payload/schema-style failures, keeps default tests offline-safe, and records gated live-enabled PASS evidence.
- `fund_premium_discount` remains conservative and unpromoted because broader listed-fund breadth, off-exchange fund coverage, and independent direct public-route redundancy remain incomplete.
- Phase 2.5-P remains active because unresolved DataHub personal trading perfection queue items remain; `index_weight_history` remains an owner paid-credential blocker, optional `hk_minute_bars` remains owner-waiver-required, and index, sector/concept, macro/policy, and quality-report gaps still require accepted hardening or owner-accepted disposition.
- The controller packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness queue items.
- The next executable DataHub hardening item is `index_daily_bars`, focused on benchmark breadth and broader China/HK/global index daily-bar coverage beyond the bounded core benchmark slice.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-126_DATAHUB_INDEX_DAILY_BARS_BREADTH_BENCHMARK_HARDENING.md`

Phase gate decision after TASK-125 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection queue items remain, and `index_daily_bars` is the next executable index capability with disposition `datahub_hardening`.

## TASK-126 Closure / TASK-127 Dispatch

Review result:

- `coordination/reviews/TASK-126_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-126 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-126 closes the focused index daily-bars breadth/benchmark hardening item by preserving bounded mainland benchmark daily-bar behavior, adding major Hong Kong benchmark daily-bar support with explicit `source_route` truth, keeping default tests offline-safe, and recording independently reproduced live-enabled PASS evidence.
- `index_daily_bars` remains conservative because global benchmark history, independent public-route redundancy, and broader non-mainland benchmark completeness remain unresolved follow-up work.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches.
- The controller packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness batches.
- The next dispatch applies the current capability-cluster policy. Controller read DataHub readiness `follow_up_batches` and selected the coherent index batch `index__datahub_hardening__index__batch_01`, covering `index_daily_bars`, `index_constituent_history`, `index_rebalance_effective_dates`, and `index_china_hk_global_benchmarks`.
- Earlier A-share, Hong Kong, and ETF/fund readiness batches still contain conservative `warn` items after accepted hardening passes, but the immediate post-TASK-126 executable continuation is the adjacent index-domain batch rather than another single follow-up item.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-127_DATAHUB_INDEX_BENCHMARK_CLUSTER_HARDENING.md`

Phase gate decision after TASK-126 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection readiness batches remain, and the next executable current-phase work is the index capability cluster with disposition `datahub_hardening`.

## TASK-127 Closure / TASK-128 Dispatch

Review result:

- `coordination/reviews/TASK-127_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-127 is closed as Done.
- No integration is entered because Review allowed Controller closure and no strict integration workflow was required.
- TASK-127 closes the index benchmark capability cluster by adding curated no-credential global benchmark daily-bar support through `index_global_hist_sina`, broadening China benchmark constituent support for `000688` and `399005`, preserving bounded mainland/HK daily-bar behavior, preserving dated membership/effective-date truth where public constituent routes expose it, keeping default tests offline-safe, and recording live-enabled PASS evidence for daily-bar and constituent/rebalance smokes.
- `index_daily_bars`, `index_constituent_history`, `index_rebalance_effective_dates`, and `index_china_hk_global_benchmarks` remain conservative and unpromoted because the accepted global route is a curated recent-window slice, stable major US benchmark history remains unproven, HK/global constituent history remains unresolved, an explicit index-level rebalance-calendar dataset is still absent, and independent public-route redundancy is incomplete.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches.
- The controller packet's stale `Next Task: TASK-064` reference is not used because TASK-064 is already Done and downstream phases remain inactive while Phase 2.5-P still has unresolved DataHub readiness batches.
- Controller read DataHub readiness `follow_up_batches`. TASK-127 covered `index__datahub_hardening__index__batch_01`; the next batch, `index__owner_credential_blocker__index_index_capability_readiness_index_weight_history__batch_01`, is not executable without owner-provided paid Tushare token scope and remains blocked.
- The next executable current-phase capability cluster is `sector_concept__datahub_hardening__sector_concept__batch_01`, covering `sector_membership`, `sector_historical_changes`, and `sector_daily_bars`.
- Earlier A-share, Hong Kong, ETF/fund, and index readiness batches still contain conservative `warn` items after accepted hardening passes, but the immediate post-TASK-127 executable continuation is the next unblocked sector/concept capability cluster from `follow_up_batches`.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-128_DATAHUB_SECTOR_CONCEPT_CLUSTER_HARDENING.md`

Phase gate decision after TASK-127 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection readiness batches remain, the paid index-weight batch is blocked without owner credential scope, and the next executable current-phase work is the sector/concept capability cluster with disposition `datahub_hardening`.

## TASK-128 Review Rejection / Rework Dispatch

Review result:

- `coordination/reviews/TASK-128_REVIEW.md`
- Decision: REJECTED pending focused rework
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS, but not closure-grade because the sector daily-bar live classifier can mask repository-side defects
- Rework required: YES

Controller decision:

- TASK-128 remains Active and must not be marked Done.
- No integration is entered because Integration Agent is retired and Review did not allow Controller closure.
- The rework is intentionally minimal and must not be merged with readiness `follow_up_batches` or ordinary sector/concept hardening.
- The only Review blocker to dispatch is `tests/datahub/test_akshare_sector_live.py`: broad `ValueError` handling in the changed sector daily-bar live smoke can downgrade repository-side schema/contract/normalization/date-window defects into environment/source `SKIP`.
- The next 5.3 Execution must update `coordination/reports/TASK-128_REPORT.md` and preserve default offline safety plus explicit live gating.
- Phase 2.5-P remains active; downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-128_DATAHUB_SECTOR_DAILY_BAR_LIVE_CLASSIFIER_REWORK.md`

Phase gate decision after TASK-128 rejected review:

- Phase switch: NO
- Reason: TASK-128 has unresolved Review findings and Controller closure is not allowed. Current-phase work remains the focused sector daily-bar live-classifier rework.

## TASK-128 Closure / TASK-129 Dispatch

Review result:

- `coordination/reviews/TASK-128_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-128 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-128 closes the sector/concept capability cluster plus the focused sector daily-bar live-classifier rework. The accepted rework adds focused classifier regressions proving route-unavailable errors still map to environment `SKIP`, while route-signature and normalized-record validation defects do not; it also removes the broad `ValueError` catch-and-skip path so bounded empty or mismatched sector daily-bar results fail instead of being downgraded to environment/source unavailability.
- Default tests remain offline-safe, and Review independently reproduced live-enabled PASS for `tests.datahub.test_akshare_sector_live`.
- `sector_membership`, `sector_historical_changes`, and `sector_daily_bars` remain conservative because broader taxonomy history, explicit change-event timelines, classification-version metadata, long-history proof, and independent public-route redundancy remain incomplete.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, and unresolved non-pass follow-up batches.
- Controller read DataHub readiness `follow_up_batches`. TASK-128 covered `sector_concept__datahub_hardening__sector_concept__batch_01`; the next executable current-phase capability cluster is `macro_policy__datahub_hardening__macro_policy__batch_01`, covering `macro_observations`, `macro_indicator_definitions`, `macro_release_metadata`, `policy_documents`, and `company_announcements_cross_market`.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-129_DATAHUB_MACRO_POLICY_CLUSTER_HARDENING.md`

Phase gate decision after TASK-128 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection readiness batches remain, and `macro_policy__datahub_hardening__macro_policy__batch_01` is the next executable current-phase capability cluster.

## TASK-129 Closure / TASK-130 Dispatch

Review result:

- `coordination/reviews/TASK-129_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-129 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-129 closes the macro/policy capability cluster. Review verified the work stayed within `quant/datahub/` and `tests/datahub/`, independently reproduced default offline-safe tests, and reproduced live-enabled PASS evidence for the materially changed macro, policy-document, and HK announcement smokes.
- `macro_observations`, `macro_indicator_definitions`, `macro_release_metadata`, `policy_documents`, and `company_announcements_cross_market` remain conservative because broader macro release/revision depth, policy authority/history breadth, and full cross-market announcement parity remain incomplete.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches.
- Controller read DataHub readiness `follow_up_batches`. TASK-129 covered `macro_policy__datahub_hardening__macro_policy__batch_01`; the next executable current-phase batch is `quality_reports__datahub_hardening__source__batch_01`, covering `source_coverage_metadata`.
- This is a single-item handoff because `quality_reports__datahub_hardening__source__batch_01` contains only one coherent local quality-report coverage metadata item. It cannot be merged with prior A-share/HK/ETF/index/sector/macro batches because those already have accepted hardening passes and reopening them here would create an unrelated mixed-domain task. It also cannot be merged with `index_weight_history` because that is an owner paid-credential blocker, or with `hk_minute_bars` because that is owner-waiver-required.
- `index_weight_history` remains an owner credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-130_DATAHUB_QUALITY_REPORT_COVERAGE_KPI_HARDENING.md`

Phase gate decision after TASK-129 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection readiness batches remain, and `quality_reports__datahub_hardening__source__batch_01` is the next executable current-phase DataHub quality-report batch.

## TASK-130 Closure / TASK-131 Dispatch

Review result:

- `coordination/reviews/TASK-130_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP; TASK-130 is local-only quality-report metadata hardening
- Rework required: NO

Controller decision:

- TASK-130 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-130 closes the local quality-report coverage KPI hardening batch. Review accepted deterministic and bounded `DATA_QUALITY_REPORT` KPI coverage for readiness gaps, verified default offline-safe tests, and confirmed no hidden live-network path.
- The KPI work improves readiness observability only. It does not prove any real-source adapter became complete, and conservative capability/catalog wording remains required.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=4`, `warn=5`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches.
- Controller read DataHub readiness `follow_up_batches` after TASK-130. The next executable current-phase capability cluster is `a_share__datahub_hardening__a_share__batch_01`, covering `a_share_listing_delisting_st_status`, `a_share_suspension_resumption`, `a_share_minute_bars`, `a_share_adjustment_factors`, `a_share_corporate_actions`, and `a_share_valuation_history`.
- This is a six-item coherent A-share cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because the items share the same A-share domain, public-source continuity/source-truth theme, and DataHub adapter/source metadata surface.
- `index_weight_history` remains an owner paid-credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-131_DATAHUB_A_SHARE_LIFECYCLE_CONTINUITY_CLUSTER_HARDENING.md`

Phase gate decision after TASK-130 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection readiness batches remain, and `a_share__datahub_hardening__a_share__batch_01` is the next executable current-phase capability cluster.

## TASK-131 Review Rejection / Source-Catalog Truth Rework Dispatch

Review result:

- `coordination/reviews/TASK-131_REVIEW.md`
- Decision: REJECTED pending focused rework
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS for the materially changed real-source paths recorded in `coordination/reports/TASK-131_REPORT.md`
- Rework required: YES

Controller decision:

- TASK-131 remains Active and must not be marked Done.
- No integration is entered because the Integration Agent is retired and Review did not allow Controller closure.
- The rework is intentionally minimal because Review identified one source-catalog truth blocker: the `akshare_cn_hk_public_family` notes in `quant/datahub/source_catalog.py` must not claim BaoStock `5/15/30/60` minute-bar history. BaoStock coverage belongs under the separate `baostock_public_cn` source family.
- This Review rework must not be merged with readiness `follow_up_batches` or ordinary future hardening work.
- Phase 2.5-P remains active; downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-131_DATAHUB_A_SHARE_SOURCE_CATALOG_TRUTH_REWORK.md`

Phase gate decision after TASK-131 Review rejection:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; TASK-131 has unresolved Review findings and cannot close until the source-catalog truth blocker is fixed and accepted by fresh Review.

## TASK-131 Closure / TASK-132 Dispatch

Review result:

- `coordination/reviews/TASK-131_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS based on accepted prior TASK-131 material real-source evidence; live tests were not rerun for the focused catalog-wording rework
- Rework required: NO

Controller decision:

- TASK-131 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-131 closes the A-share lifecycle and continuity capability cluster using readiness batch `a_share__datahub_hardening__a_share__batch_01`, plus the focused source-catalog truth rework. The accepted rework removes the incorrect BaoStock attribution from `akshare_cn_hk_public_family` notes and preserves BaoStock minute-bar truth only under `baostock_public_cn`.
- Default tests remain offline-safe; Review independently reran `python3 -m unittest tests.datahub.test_source_catalog` and it passed.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, and unresolved non-pass follow-up batches.
- Controller read DataHub readiness `follow_up_batches`. TASK-131 covered `a_share__datahub_hardening__a_share__batch_01`; the next executable current-phase capability cluster is `a_share__datahub_hardening__a_share__batch_02`, covering `a_share_capital_flow`, `a_share_northbound_flow`, `a_share_turnover_liquidity`, `a_share_limit_up_down`, `a_share_margin_financing_and_lending`, and `a_share_financial_statements`.
- This is a six-item coherent A-share cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because the items share the same A-share domain, public-source flow/liquidity/market-constraint/financial-statement truth theme, and DataHub adapter/source metadata surface.
- `index_weight_history` remains an owner paid-credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-132_DATAHUB_A_SHARE_FLOW_LIQUIDITY_FINANCIAL_CLUSTER_HARDENING.md`

Phase gate decision after TASK-131 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection readiness batches remain, and `a_share__datahub_hardening__a_share__batch_02` is the next executable current-phase capability cluster.

## TASK-132 Review Rejection / Northbound Fallback Truth Rework Dispatch

Review result:

- `coordination/reviews/TASK-132_REVIEW.md`
- Decision: Rejected pending focused truth rework
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP overall because `limit_up_down` and `financial_statements` passed, but the material northbound route change skipped after `stock_hsgt_individual_em` appeared stale for the recent bounded window and `stock_hsgt_individual_detail_em` failed upstream with `TypeError: 'NoneType' object is not subscriptable`
- Rework required: YES

Controller decision:

- TASK-132 is not closed and is not marked Done.
- No Integration Agent is dispatched.
- A focused Review rework is dispatched instead of merging with later readiness `follow_up_batches`.
- The rework scope is limited to correcting `a_share_northbound_flow` capability/catalog truth so `stock_hsgt_individual_detail_em` is described as attempted/currently unproven fallback truth, not established fallback coverage.
- Phase 2.5-P remains active and downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-132_DATAHUB_A_SHARE_NORTHBOUND_FALLBACK_TRUTH_REWORK.md`

Phase gate decision after TASK-132 Review rejection:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; TASK-132 has unresolved Review findings and cannot close until northbound fallback source truth is fixed and accepted by fresh Review.

## TASK-132 Closure / TASK-133 Dispatch

Review result:

- `coordination/reviews/TASK-132_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP for the preserved northbound evidence; no further rework required because the accepted rework was wording/test-only and corrected the source-truth overstatement
- Rework required: NO

Controller decision:

- TASK-132 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-132 closes the A-share flow/liquidity/market-constraint/financial-statement readiness batch `a_share__datahub_hardening__a_share__batch_02` plus the focused northbound fallback truth rework. The accepted rework keeps `stock_hsgt_individual_em` as the only currently proven northbound route and records `stock_hsgt_individual_detail_em` as attempted but unproven pending fresh live evidence.
- Default tests remain offline-safe; Review independently reran source capability, source catalog, northbound adapter, and default env-gated northbound live-module tests.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, and unresolved non-pass follow-up batches.
- Controller read DataHub readiness `follow_up_batches`. TASK-131 covered `a_share__datahub_hardening__a_share__batch_01`; TASK-132 covered `a_share__datahub_hardening__a_share__batch_02`; the next executable current-phase capability cluster is `a_share__datahub_hardening__a_share__batch_03`, covering `a_share_financial_indicators`, `a_share_company_announcements`, and `a_share_major_activity_events`.
- This is a three-item coherent A-share cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because the items share the same A-share domain, public-source breadth/history/source-redundancy theme, and DataHub adapter/source metadata surface.
- `index_weight_history` remains an owner paid-credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- The optional `hk_minute_bars` queue item remains owner-waiver-required and is not dispatched without owner waiver or explicit feasibility scope.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-133_DATAHUB_A_SHARE_FINANCIAL_ANNOUNCEMENT_ACTIVITY_CLUSTER_HARDENING.md`

Phase gate decision after TASK-132 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection readiness batches remain, and `a_share__datahub_hardening__a_share__batch_03` is the next executable current-phase capability cluster.

## TASK-133 Closure / TASK-134 Dispatch

Review result:

- `coordination/reviews/TASK-133_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-133 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-133 closes the A-share financial-indicator, announcement, and activity readiness batch `a_share__datahub_hardening__a_share__batch_03`. The accepted work strengthened `a_share_major_activity_events` with exchange-specific insider holding-change source truth, preserved accepted `a_share_financial_indicators` and `a_share_company_announcements` behavior, kept default tests offline-safe, and kept all targeted capabilities conservative where public-source completeness remains unproven.
- Review independently reran the major-activity adapter tests, default-gated live module tests, source capability/catalog tests, and the live-enabled major-activity smoke; all passed with default live gating preserved.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, and unresolved non-pass follow-up batches.
- Controller read DataHub readiness `follow_up_batches`. TASK-131, TASK-132, and TASK-133 covered the three A-share `datahub_hardening` batches. The next executable current-phase capability cluster is `hong_kong__datahub_hardening__hong_kong__batch_01`, covering `hk_universe_reference`, `hk_daily_bars`, `hk_corporate_actions`, `hk_valuation_history`, `hk_financial_data`, and `hk_turnover_liquidity`.
- This is a six-item coherent Hong Kong stock cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because the items share the same Hong Kong domain, no-credential public-source breadth/history/source-redundancy theme, and DataHub adapter/source metadata surface.
- `hk_minute_bars` remains an owner-waiver-required adjacent batch and is not merged into TASK-134 because no owner waiver or explicit HK minute-bar feasibility scope has been provided.
- `index_weight_history` remains an owner paid-credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-134_DATAHUB_HK_CAPABILITY_CLUSTER_HARDENING.md`

Phase gate decision after TASK-133 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection readiness batches remain, and `hong_kong__datahub_hardening__hong_kong__batch_01` is the next executable current-phase capability cluster.

## TASK-134 Review Rejection / HK Cluster Scope Rework Dispatch

Review result:

- `coordination/reviews/TASK-134_REVIEW.md`
- Decision: `rejected_or_blocked`
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS for the changed `hk_corporate_actions` path only
- Rework required: YES

Controller decision:

- TASK-134 is not closed and is not marked Done.
- No Integration Agent is dispatched.
- A focused Review rework is dispatched instead of merging with later readiness `follow_up_batches`.
- The rework scope is limited to resolving the Review blocker: the initial execution/report only hardened `hk_corporate_actions`, while the assigned `hong_kong__datahub_hardening__hong_kong__batch_01` also requires `hk_universe_reference`, `hk_daily_bars`, `hk_valuation_history`, `hk_financial_data`, and `hk_turnover_liquidity` to be hardened or to have concrete implementation/live-source blocker evidence recorded.
- The accepted `hk_corporate_actions` TASK-134 behavior should be preserved unless a genuine defect is found.
- `hk_minute_bars` remains owner-waiver-required and outside this rework.
- Phase 2.5-P remains active and downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-134_DATAHUB_HK_CLUSTER_SCOPE_REWORK.md`

Phase gate decision after TASK-134 Review rejection:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; TASK-134 has unresolved Review findings and cannot close until the HK cluster scope blocker is fixed or concretely dispositioned and accepted by fresh Review.

## TASK-134 Closure / TASK-135 Dispatch

Review result:

- `coordination/reviews/TASK-134_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-134 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-134 closes the Hong Kong capability-cluster readiness batch `hong_kong__datahub_hardening__hong_kong__batch_01`, including the focused scope rework. Review accepted the changed `hk_universe_reference` live path and accepted explicit conservative limitation/blocker wording plus regression assertions for `hk_daily_bars`, `hk_valuation_history`, `hk_financial_data`, and `hk_turnover_liquidity`; the accepted `hk_corporate_actions` behavior is preserved.
- Default tests remain offline-safe; Review independently reran source capability, source catalog, HK instrument-master adapter, and HK instrument-master live tests, and relied on execution report PASS evidence for unchanged HK daily-bar, valuation, financial, and corporate-action live paths.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=4`, `warn=5`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches.
- Controller read DataHub readiness `follow_up_batches`. TASK-131, TASK-132, TASK-133, and TASK-134 covered the A-share and Hong Kong `datahub_hardening` batches. The next adjacent readiness batch is `hong_kong__owner_waiver_required__hong_kong_hong_kong_capability_readiness_hk_minute_bars__batch_01`, covering only `hk_minute_bars`.
- This is a single-item handoff because the batch has `disposition=owner_waiver_required`, `hk_minute_bars` is optional, no current dataset mapping is assigned, and HK minute-bar source/contract feasibility is distinct from the next ETF/fund hardening batch. This falls under the owner-waiver/blocker single-item exception in `coordination/PHASE_GATE.md`; it is not merged with ETF/fund hardening.
- `index_weight_history` remains an owner paid-credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-135_DATAHUB_HK_MINUTE_BARS_FEASIBILITY_BLOCKER_DISPOSITION.md`

Phase gate decision after TASK-134 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection batches remain, and `hong_kong__owner_waiver_required__hong_kong_hong_kong_capability_readiness_hk_minute_bars__batch_01` is the next adjacent current-phase blocker disposition before moving to later ordinary hardening batches.

## TASK-135 Closure / TASK-136 Dispatch

Review result:

- `coordination/reviews/TASK-135_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-135 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-135 resolves the adjacent HK minute-bars owner-waiver/blocker disposition. Review accepted that the implementation stayed in Phase 2.5-P DataHub scope, kept default tests offline-safe, added gated live PASS evidence, and truthfully promoted `hk_minute_bars` from optional missing to conservative `partial` based on bounded no-credential public-source proof.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, and unresolved non-pass follow-up batches.
- Controller read DataHub readiness `follow_up_batches`. TASK-131, TASK-132, TASK-133, TASK-134, and TASK-135 covered the A-share batches, the Hong Kong hardening batch, and the adjacent HK minute-bars blocker-disposition batch. The next executable current-phase capability cluster is `etf_fund__datahub_hardening__etf_fund__batch_01`, covering `fund_daily_bars`, `fund_nav`, `fund_holdings_composition`, `fund_scale_and_share`, `fund_flow`, and `fund_premium_discount`.
- This is a six-item coherent ETF/fund cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because the items share the same ETF/fund domain, public-source breadth/history/source-redundancy theme, overlapping AKShare adapter/source metadata surface, and downstream DataHub contract consumers.
- `index_weight_history` remains an owner paid-credential blocker and must not be promoted without future paid-scope credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-136_DATAHUB_ETF_FUND_CAPABILITY_CLUSTER_HARDENING.md`

Phase gate decision after TASK-135 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection batches remain, and `etf_fund__datahub_hardening__etf_fund__batch_01` is the next executable current-phase capability cluster.

## TASK-136 Closure / TASK-137 Dispatch

Review result:

- `coordination/reviews/TASK-136_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-136 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-136 closes the ETF/fund capability-cluster readiness batch `etf_fund__datahub_hardening__etf_fund__batch_01`. Review accepted that changes stayed within DataHub scope, default tests remained offline-safe, gated live smokes passed, and residual ETF/fund limitations remain truthfully conservative rather than promoted.
- Phase 2.5-P remains active because `build_default_personal_trading_readiness_report()` reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=4`, `warn=5`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches.
- Controller read DataHub readiness `follow_up_batches`. TASK-131 through TASK-136 covered the A-share batches, Hong Kong hardening batch, HK minute-bars blocker-disposition batch, and ETF/fund hardening batch. The next unresolved current-phase capability cluster in deterministic batch order after ETF/fund is `index__datahub_hardening__index__batch_01`, covering `index_daily_bars`, `index_constituent_history`, `index_rebalance_effective_dates`, and `index_china_hk_global_benchmarks`.
- This is a four-item coherent residual index cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because the items share the same index domain, benchmark breadth/history/source-redundancy theme, AKShare adapter/source metadata surface, and downstream DataHub contract consumers.
- The separate `index__owner_credential_blocker__index_index_capability_readiness_index_weight_history__batch_01` remains blocked and is not merged into TASK-137 because it requires owner-provided paid Tushare credential scope and future credentialed live PASS evidence.
- Downstream modules remain inactive.

Next handoff:

- `coordination/handoffs/TASK-137_DATAHUB_INDEX_RESIDUAL_CAPABILITY_CLUSTER_HARDENING.md`

Phase gate decision after TASK-136 closure:

- Phase switch: NO
- Reason: Phase 2.5-P is not complete under `coordination/PHASE_GATE.md`; unresolved DataHub personal trading perfection batches remain, and `index__datahub_hardening__index__batch_01` is the next executable current-phase residual capability cluster after the accepted ETF/fund batch.

## TASK-137 Closure / TASK-138 Dispatch

Review result:

- `coordination/reviews/TASK-137_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: NO

Controller decision:

- TASK-137 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-137 closes the residual DataHub index capability-cluster readiness batch `index__datahub_hardening__index__batch_01`. Review accepted that the changes stayed within DataHub scope, default tests remained offline-safe, live-enabled index daily-bar and constituent/rebalance suites passed, and remaining US/global breadth, long-history continuity, and rebalance-calendar limits stayed explicitly conservative rather than over-promoted.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md` to Phase 2.5-P. DataHub now has accepted closure evidence for every ordinary public-source/no-paid hardening batch dispatched from the readiness queue: A-share, Hong Kong, HK minute-bars blocker disposition, ETF/fund, index, sector/concept, macro/policy, quality reports, local storage, refresh metadata, and source-health diagnostics.
- Phase 2.5-P is closed for the public-source/no-paid Personal Trading Perfection scope. Residual `warn` / `partial` states are not treated as hidden completion; they are accepted conservative limitation truth after hardening attempts and tests. `index_weight_history` remains an explicit owner-accepted paid credential blocker under TASK-059 / Tushare and must not be promoted without future owner-provided paid scope and credentialed live PASS review.
- FeatureHub remains historical foundation progress only under the new standard. The next phase is Phase 3-P FeatureHub Personal Trading Perfection Re-Review, starting with an audit/gate handoff rather than direct indicator expansion.

Next handoff:

- `coordination/handoffs/TASK-138_FEATUREHUB_PERSONAL_TRADING_READINESS_GATE.md`

Phase gate decision after TASK-137 closure:

- Phase switch: YES, to Phase 3-P FeatureHub Personal Trading Perfection Re-Review.
- Reason: DataHub has no unresolved `fail`; ordinary public-source/no-paid DataHub hardening batches have accepted execution/review evidence; residual public-source limits are explicit conservative `warn` truth; and the only paid/private DataHub requirement is recorded as owner-accepted blocked scope. FeatureHub must now be re-reviewed against the Personal Trading Perfection Standard before Scanner or later phases can rely on it.

## TASK-138 Closure / TASK-139 Dispatch

Review result:

- `coordination/reviews/TASK-138_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-138 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-138 closes the FeatureHub personal trading readiness gate. The accepted gate stayed inside Phase 3-P scope, added only local/offline FeatureHub readiness logic and tests, and emitted deterministic follow-up queue/batch structures.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md` to Phase 3-P. FeatureHub is not phase-complete: TASK-138 reports `phase_closure_ready=false`, status counts `pass=0`, `warn=7`, `blocked=0`, `fail=0`, and all seven roadmap capability groups remain `warn`.
- Controller read the FeatureHub readiness `follow_up_batches`. The next executable current-phase capability cluster is `featurehub_technical_indicators_batch_01`, covering `FH-TECH-001` through `FH-TECH-005`: rolling helpers/EMA, MACD/RSI/KDJ, Bollinger/ATR, volume-turnover-liquidity, and gap/breakout primitives.
- This is a five-item coherent FeatureHub technical-indicator cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because the items share the same `price_volume_technical_core` group, caller-provided daily-bar input surface, offline calculation semantics, and `quant/features/technical.py` / `tests/features/test_technical.py` implementation area.
- AGENTS.md is not changed because the implementation phase and allowed implementation targets remain Phase 3-P with `quant/features/` and `tests/features/`.

Next handoff:

- `coordination/handoffs/TASK-139_FEATUREHUB_TECHNICAL_INDICATORS_CORE_EXPANSION.md`

Phase gate decision after TASK-138 closure:

- Phase switch: NO.
- Reason: Phase 3-P is not complete under `coordination/PHASE_GATE.md`; the accepted readiness gate reports all FeatureHub Personal Trading Perfection capability groups as `warn`, and `featurehub_technical_indicators_batch_01` is the next executable current-phase capability cluster.

## TASK-139 Review Rejection / Test Coverage Rework Dispatch

Review result:

- `coordination/reviews/TASK-139_REVIEW.md`
- Decision: REJECTED pending test-completeness rework
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES

Controller decision:

- TASK-139 is not closed and is not marked Done.
- No integration is entered because the Integration Agent is retired and Review did not allow Controller closure.
- Review found no phase/scope violation, no hidden live network behavior, and no need for live rework. The blocker is narrow: missing handoff-required negative-path tests for the new EMA and oscillator families.
- The rework is intentionally not merged with FeatureHub readiness `follow_up_batches` or the next valuation/flow hardening batch. It falls under the `coordination/PHASE_GATE.md` small-handoff exception for Review rework.
- AGENTS.md is not changed because the implementation phase and allowed implementation targets remain Phase 3-P with `quant/features/` and `tests/features/`.

Next handoff:

- `coordination/handoffs/TASK-139_FEATUREHUB_TECHNICAL_INDICATOR_TEST_COVERAGE_REWORK.md`

Phase gate decision after TASK-139 rejected Review:

- Phase switch: NO.
- Reason: TASK-139 had unresolved blocking Review findings, so Phase 3-P could not close or advance to the next FeatureHub readiness batch. The next Active work at that point was the focused TASK-139 test coverage rework.

## TASK-139 Second Review Rejection / MACD Long-Window Rework Dispatch

Review result:

- `coordination/reviews/TASK-139_REVIEW.md`
- Decision: REJECTED pending one more focused test rework
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES

Controller decision:

- TASK-139 is not closed and is not marked Done.
- No integration is entered because the Integration Agent is retired and Review did not allow Controller closure.
- Review found the prior rework closed most missing technical-indicator negative-path coverage, but one blocking item remains: `calculate_macd()` validates `long_window` independently and `tests/features/test_technical.py` still lacks direct invalid `long_window` regression coverage. The report also overstates MACD invalid-window coverage as fully addressed.
- The rework is intentionally not merged with FeatureHub readiness `follow_up_batches` or other ordinary hardening items. It falls under the `coordination/PHASE_GATE.md` small-handoff exception for Review rework.
- AGENTS.md is not changed because the implementation phase and allowed implementation targets remain Phase 3-P with `quant/features/` and `tests/features/`.

Next handoff:

- `coordination/handoffs/TASK-139_FEATUREHUB_MACD_LONG_WINDOW_TEST_REWORK.md`

Phase gate decision after the second TASK-139 rejected Review:

- Phase switch: NO.
- Reason: TASK-139 has an unresolved blocking Review finding, so Phase 3-P cannot close or advance to the next FeatureHub readiness batch. The next Active work is the focused TASK-139 MACD long-window invalid-value test rework.

## TASK-139 Closure / TASK-140 Dispatch

Review result:

- `coordination/reviews/TASK-139_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-139 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-139 closes the first ordinary Phase 3-P FeatureHub hardening batch, including the focused Review reworks. The accepted final rework stayed inside FeatureHub test/report scope, added direct `calculate_macd(..., long_window=0, ...)` invalid-window regression coverage, corrected the overstated report item, and introduced no hidden network behavior.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md` to Phase 3-P. FeatureHub is still not phase-complete: TASK-138 reports `phase_closure_ready=false`, all seven FeatureHub roadmap capability groups were `warn`, and the remaining readiness batches for valuation/flow, relative features, and batch/downstream contracts are not yet accepted.
- Controller read the FeatureHub readiness `follow_up_batches` after TASK-139 closure. The next executable current-phase capability cluster is `featurehub_valuation_flow_batch_01`, covering `FH-VAL-001` and `FH-FLOW-001`.
- This is a two-item coherent FeatureHub valuation/flow cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because both items share caller-provided historical-row normalization, window validation, finite numeric handling, local feature-output semantics, and the `quant/features/valuation.py` / `quant/features/capital_flow.py` implementation surface.
- AGENTS.md is not changed because the implementation phase and allowed implementation targets remain Phase 3-P with `quant/features/` and `tests/features/`.

Next handoff:

- `coordination/handoffs/TASK-140_FEATUREHUB_VALUATION_FLOW_EXPANSION.md`

Phase gate decision after TASK-139 closure:

- Phase switch: NO.
- Reason: Phase 3-P is not complete under `coordination/PHASE_GATE.md`; accepted TASK-139 closes only the first technical-indicator batch, while TASK-138 still leaves valuation/flow, relative-feature, and batch/downstream contract groups requiring accepted current-phase hardening or explicit disposition. The next Active work is the `featurehub_valuation_flow_batch_01` capability cluster.

## TASK-140 Closure / TASK-141 Dispatch

Review result:

- `coordination/reviews/TASK-140_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-140 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-140 closes the Phase 3-P valuation/flow hardening batch. The accepted implementation stayed inside `quant/features/**` and `tests/features/**`, added valuation PE/PB/PS-style outputs plus bounded percentile/relative-history helpers, expanded capital/northbound/fund-flow rolling and intensity helpers, updated readiness truth, and introduced no DataHub fetches, credentials, warehouse reads, live paths, or downstream Scanner/strategy behavior.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md` to Phase 3-P. FeatureHub is still not phase-complete: the relative-feature batch and batch/downstream contract/test batch remain unresolved, and no Controller audit has found Phase 3-P ready for closure under the Personal Trading Perfection Standard.
- Controller read the FeatureHub readiness `follow_up_batches` after TASK-140 closure. The next executable current-phase capability cluster is `featurehub_relative_features_batch_01`, covering `FH-REL-001` and `FH-REL-002`.
- This is a two-item coherent FeatureHub relative-feature cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because both items share caller-provided stock/sector/index input alignment, bounded window validation, finite numeric handling, local feature-output semantics, and the new `quant/features/relative.py` / `tests/features/test_relative.py` implementation surface.
- AGENTS.md is not changed because the implementation phase and allowed implementation targets remain Phase 3-P with `quant/features/` and `tests/features/`.

Next handoff:

- `coordination/handoffs/TASK-141_FEATUREHUB_RELATIVE_FEATURES_EXPANSION.md`

Phase gate decision after TASK-140 closure:

- Phase switch: NO.
- Reason: Phase 3-P is not complete under `coordination/PHASE_GATE.md`; accepted TASK-140 closes the valuation/flow batch, while relative-feature and batch/downstream contract groups still require accepted current-phase hardening or explicit disposition. The next Active work is the `featurehub_relative_features_batch_01` capability cluster.

## TASK-141 Closure / TASK-142 Dispatch

Review result:

- `coordination/reviews/TASK-141_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-141 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-141 closes the Phase 3-P relative-feature hardening batch. The accepted implementation stayed inside `quant/features/**` and `tests/features/**`, added deterministic stock-vs-sector, sector-strength, index-relative, breadth, and rotation primitives over caller-provided rows, updated readiness truth, and introduced no DataHub fetches, credentials, warehouse reads, live paths, or downstream Scanner/strategy behavior.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md` to Phase 3-P. FeatureHub is still not phase-complete: TASK-141 raises readiness counts to `pass=4`, `warn=3`, `blocked=0`, `fail=0`, but the batch API, downstream metric-identity/consumability, and aligned offline regression coverage groups remain unresolved. No Controller audit has found Phase 3-P ready for closure under the Personal Trading Perfection Standard.
- Controller read the FeatureHub readiness `follow_up_batches` after TASK-141 closure. The next executable current-phase capability cluster is `featurehub_batch_contracts_batch_01`, covering `FH-BATCH-001`, `FH-CONTRACT-001`, and `FH-TEST-001`.
- This is a three-item coherent FeatureHub batch/contract/test cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because the items share the same FeatureHub batch orchestration, metric identity, persistence compatibility, export, and offline regression-test contract surface.
- AGENTS.md is not changed because the implementation phase and allowed implementation targets remain Phase 3-P with `quant/features/` and `tests/features/`.

Next handoff:

- `coordination/handoffs/TASK-142_FEATUREHUB_BATCH_CONTRACTS_CONSUMABILITY.md`

Phase gate decision after TASK-141 closure:

- Phase switch: NO.
- Reason: Phase 3-P is not complete under `coordination/PHASE_GATE.md`; accepted TASK-141 closes the relative-feature batch, while batch/downstream contract/test groups still require accepted current-phase hardening or explicit disposition. The next Active work is the `featurehub_batch_contracts_batch_01` capability cluster.

## TASK-142 Closure / TASK-143 Dispatch

Review result:

- `coordination/reviews/TASK-142_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-142 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-142 closes the Phase 3-P FeatureHub batch contracts and downstream consumability batch. Review accepted deterministic batch calculation, metric-level downstream identity, persistence compatibility, readiness-gate closure truth, default offline safety, and no hidden live network behavior.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md` to Phase 3-P. The local FeatureHub readiness gate now reports `phase_closure_ready=true`, status counts `pass=7`, `warn=0`, `blocked=0`, `fail=0`, `follow_up_queue_count=0`, and `follow_up_batches_count=0`.
- Phase 3-P is closed under the Personal Trading Perfection Standard for the public-source/no-paid scope. Required FeatureHub capability groups are satisfied: price/volume technical core, valuation features, capital-flow/money-flow features, sector/market-relative features, batch calculation APIs, persistence/downstream consumability, and aligned offline test coverage. The accepted TASK-139 through TASK-142 hardening sequence provides the implementation and regression evidence. No live evidence is required because FeatureHub is pure local/offline calculation over caller-provided DataHub-shaped inputs.
- No remaining FeatureHub `partial`, `warn`, `blocked`, or public-source limitation is being treated as completion; the readiness queue is empty after accepted hardening. Legacy FeatureHub record compatibility risk is documented in TASK-142 as a deliberate `1.0.0` fallback, while new writes use the metric-identity `1.1.0` contract.
- The next phase is Phase 4-P Scanner Personal Trading Perfection Re-Review. Scanner historical tasks TASK-064 through TASK-068 are useful foundation progress only and are not enough to close Scanner under the roadmap standard because ranking/scoring, exclusion/market-constraint handling, realistic repeated scan workflows, stale/missing feature handling, and complete downstream handoff readiness still require audit and follow-up disposition.
- `coordination/handoffs/TASK-143_SCANNER_PERSONAL_TRADING_READINESS_GATE.md` is dispatched as the first Phase 4-P audit/gate handoff.
- AGENTS.md is updated because the implementation phase and allowed implementation target changed to Phase 4-P with `quant/scanner/` and `tests/scanner/`.

Next handoff:

- `coordination/handoffs/TASK-143_SCANNER_PERSONAL_TRADING_READINESS_GATE.md`

Phase gate decision after TASK-142 closure:

- Phase switch: YES, to Phase 4-P Scanner Personal Trading Perfection Re-Review.
- Reason: Phase 3-P is complete under `coordination/PHASE_GATE.md`; all FeatureHub Personal Trading Perfection capability groups are `pass`, all Phase 3-P tasks have accepted lifecycle artifacts, default tests are offline-safe, no live-source rework is required, and no remaining FeatureHub follow-up batch exists. Scanner is the next prerequisite phase before StrategyLab/BacktestEngine can resume.

## TASK-143 Closure / TASK-144 Dispatch

Review result:

- `coordination/reviews/TASK-143_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-143 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-143 closes the Phase 4-P Scanner personal trading readiness gate. Review accepted that the gate stayed inside `quant/scanner/` and `tests/scanner/`, is deterministic and local-only, keeps default tests offline-safe, and truthfully reports Phase 4-P as not closure-ready.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md` to Phase 4-P. The Scanner readiness gate reports `phase_closure_ready=false`, status counts `pass=1`, `warn=5`, `blocked=0`, `fail=0`.
- Phase 4-P remains open because Scanner has not yet satisfied the roadmap standard for universe/exclusion handling, ranking/scoring and explicit ordering, candidate artifact downstream handoff metadata, stale/missing feature policy, suspension/limit-up/down and market-specific constraints, and aligned offline workflow regressions.
- Controller read the Scanner readiness `follow_up_batches`. The next executable current-phase capability cluster is `scanner_universe_constraints_batch_01`, covering `SCN-UNI-001`, `SCN-UNI-002`, `SCN-CONSTRAINT-001`, and `SCN-CONSTRAINT-002`.
- This is a four-item coherent Scanner universe/constraint cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because the items share scan-input eligibility, universe validation, exclusion-list composition, constraint-policy, and offline runner/test surfaces.
- `coordination/handoffs/TASK-144_SCANNER_UNIVERSE_CONSTRAINTS_HARDENING.md` is dispatched as the next Active 5.3 execution handoff.
- AGENTS.md is unchanged because the current phase remains Phase 4-P and allowed implementation targets remain `quant/scanner/` and `tests/scanner/`.

Next handoff:

- `coordination/handoffs/TASK-144_SCANNER_UNIVERSE_CONSTRAINTS_HARDENING.md`

Phase gate decision after TASK-143 closure:

- Phase switch: NO.
- Reason: Phase 4-P is not complete under `coordination/PHASE_GATE.md`; accepted TASK-143 only codifies the Scanner readiness truth and emits follow-up batches, while the first ordinary universe/constraint hardening cluster still requires accepted execution/review evidence.

## TASK-144 Review Rejection / Universe Snapshot Consistency Rework Dispatch

Review result:

- `coordination/reviews/TASK-144_REVIEW.md`
- Decision: REJECTED_OR_BLOCKED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES

Controller decision:

- TASK-144 is not closed and is not marked Done.
- No integration is entered because Review rejected Controller closure and the Integration Agent is retired.
- Review found a focused Scanner contract/test defect: `compose_universe_membership(...)` validates `UniverseDefinition` and `UniverseMembershipSnapshot` independently but does not enforce cross-consistency, so a HK/hong_kong_stock definition can be paired with a CN snapshot and reach scan execution.
- The next Active 5.3 Execution handoff is `coordination/handoffs/TASK-144_SCANNER_UNIVERSE_SNAPSHOT_CONSISTENCY_REWORK.md`.
- This is a focused Review rework. It must not be merged with `scanner_ranking_workflow_batch_01`, `scanner_artifact_contract_repair_batch_01`, or any ordinary Scanner readiness follow-up batch.
- AGENTS.md is unchanged because the current phase remains Phase 4-P and allowed implementation targets remain `quant/scanner/` and `tests/scanner/`.

For active TASK-144 specifically, the next role is 5.3 Execution. Expected write path is `coordination/reports/TASK-144_REPORT.md`. Execution must follow `coordination/handoffs/TASK-144_SCANNER_UNIVERSE_SNAPSHOT_CONSISTENCY_REWORK.md`, modifying only allowed Scanner universe/runner files, focused Scanner tests, and the report. It must keep all behavior offline over caller-provided data and avoid DataHub/FeatureHub implementation changes, StrategyLab, BacktestEngine, portfolio/signal/risk logic, AI, notification, UI, automated trading, credentials, private data, or hidden network behavior.

Phase switch: NO for the TASK-144 rejected Review / universe snapshot consistency rework dispatch. Current phase remains Phase 4-P Scanner Personal Trading Perfection Re-Review.

## TASK-144 Closure / TASK-145 Dispatch

Review result:

- `coordination/reviews/TASK-144_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-144 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-144 closes the Phase 4-P Scanner universe/constraint hardening batch `scanner_universe_constraints_batch_01`, including the focused definition/snapshot consistency rework. Review accepted that the final rework stayed inside `quant/scanner/` and `tests/scanner/`, enforced cross-consistency between `UniverseDefinition` and `UniverseMembershipSnapshot`, added focused universe and runner regressions, preserved default offline safety, and required no live evidence because the handoff forbade live tests.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md` to Phase 4-P. Phase 4-P remains incomplete because Scanner still lacks accepted ranking/scoring and explicit research-priority ordering, and the separate artifact provenance/downstream handoff metadata contract repair remains pending.
- Controller read the Scanner readiness `follow_up_batches`. TASK-144 covered `scanner_universe_constraints_batch_01`; the next executable current-phase capability cluster is `scanner_ranking_workflow_batch_01`, covering `SCN-RANK-001` and `SCN-TEST-001`.
- This is a two-item coherent Scanner ranking/workflow cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because ranking/scoring changes must land with deterministic offline workflow regressions proving ordering semantics, tie breaks, and interaction with existing universe/constraint behavior.
- The remaining `scanner_artifact_contract_repair_batch_01` / `SCN-ART-001` is not merged into TASK-145 because persisted artifact provenance and downstream handoff metadata are an isolated contract-repair item with compatibility blast radius.
- `coordination/handoffs/TASK-145_SCANNER_RANKING_WORKFLOW_HARDENING.md` is dispatched as the next Active 5.3 execution handoff.
- AGENTS.md is unchanged because the current phase remains Phase 4-P and allowed implementation targets remain `quant/scanner/` and `tests/scanner/`.

At the TASK-144 closure dispatch point, TASK-145 was assigned to 5.3 Execution with expected write path `coordination/reports/TASK-145_REPORT.md`. Execution was to follow `coordination/handoffs/TASK-145_SCANNER_RANKING_WORKFLOW_HARDENING.md`, modifying only allowed Scanner contract/matching/runner/readiness/storage-compatibility files, focused Scanner tests, and the report. That original execution produced `coordination/reports/TASK-145_REPORT.md`; Review later rejected Controller closure and the current active handoff is the focused TASK-145 ranking normalization rework.

Phase switch: NO for the TASK-144 closure / TASK-145 dispatch. Current phase remains Phase 4-P Scanner Personal Trading Perfection Re-Review.

## TASK-145 Review Rejection / Ranking Normalization Rework Dispatch

Review result:

- `coordination/reviews/TASK-145_REVIEW.md`
- Decision: REJECTED_OR_BLOCKED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES

Controller decision:

- TASK-145 is not closed and is not marked Done.
- No integration is entered because Review rejected Controller closure and the Integration Agent is retired.
- Review found a focused Scanner ranking-config normalization defect: a mapping ranking payload may contain dataclass `RankingCriterion` items accepted by validation, but `_normalize_ranking_config(...)` subscripts those criteria as mappings and raises raw `TypeError` for `run_scan(..., ranking={"criteria": (RankingCriterion(...),)})`.
- The next Active 5.3 Execution handoff is `coordination/handoffs/TASK-145_SCANNER_RANKING_NORMALIZATION_REWORK.md`.
- This is a focused Review rework. It must not be merged with readiness `follow_up_batches`, `scanner_artifact_contract_repair_batch_01`, or any ordinary Scanner hardening item.
- AGENTS.md is unchanged because the current phase remains Phase 4-P and allowed implementation targets remain `quant/scanner/` and `tests/scanner/`.

For active TASK-145 specifically, the next role is 5.3 Execution rework. Expected write path is `coordination/reports/TASK-145_REPORT.md`. Execution must follow `coordination/handoffs/TASK-145_SCANNER_RANKING_NORMALIZATION_REWORK.md`, modifying only allowed Scanner runner/contract files if needed, focused Scanner tests, and the report. It must keep all behavior offline over caller-provided data and avoid DataHub/FeatureHub implementation changes, StrategyLab, BacktestEngine, portfolio/signal/risk logic, AI, notification, UI, automated trading, credentials, private data, hidden network behavior, artifact provenance repair, or downstream handoff metadata work.

Phase switch: NO for the TASK-145 rejected Review / ranking normalization rework dispatch. Current phase remains Phase 4-P Scanner Personal Trading Perfection Re-Review.

## TASK-145 Closure / TASK-146 Dispatch

Review result:

- `coordination/reviews/TASK-145_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-145 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-145 closes the Phase 4-P Scanner ranking/workflow hardening batch `scanner_ranking_workflow_batch_01`, including the focused ranking normalization rework. Review accepted that mixed mapping-plus-dataclass ranking criteria now normalize through the controlled path, regression coverage exists, default tests are offline-safe, and no live evidence is required because Scanner is local-only.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md` to Phase 4-P. Phase 4-P remains incomplete because the Scanner artifact provenance and downstream handoff metadata contract repair remains pending.
- Controller read the Scanner readiness `follow_up_batches`. TASK-144 covered `scanner_universe_constraints_batch_01`; TASK-145 covered `scanner_ranking_workflow_batch_01`; the next unresolved current-phase batch is `scanner_artifact_contract_repair_batch_01`, covering `SCN-ART-001`.
- This is a single-item handoff under the `coordination/PHASE_GATE.md` small-handoff exception. It is not merged with other work because persisted artifact schema/provenance and downstream handoff metadata have compatibility blast radius, and no adjacent unresolved Scanner readiness item remains.
- `coordination/handoffs/TASK-146_SCANNER_ARTIFACT_CONTRACT_REPAIR.md` is dispatched as the next Active 5.3 execution handoff.
- AGENTS.md is unchanged because the current phase remains Phase 4-P and allowed implementation targets remain `quant/scanner/` and `tests/scanner/`.

For active TASK-146 specifically, the next role is 5.3 Execution. Expected write path is `coordination/reports/TASK-146_REPORT.md`. Execution must follow `coordination/handoffs/TASK-146_SCANNER_ARTIFACT_CONTRACT_REPAIR.md`, modifying only allowed Scanner contracts/storage/runner-readiness files, focused Scanner tests, and the report. It must keep all behavior offline over caller-provided data and avoid DataHub/FeatureHub implementation changes, StrategyLab, BacktestEngine, portfolio/signal/risk logic, AI, notification, UI, automated trading, credentials, private data, or hidden network behavior.

Phase switch: NO for the TASK-145 closure / TASK-146 dispatch. Current phase remains Phase 4-P Scanner Personal Trading Perfection Re-Review.

## TASK-146 Review Rejection / Empty Ranked Artifact Rework Dispatch

Review result:

- `coordination/reviews/TASK-146_REVIEW.md`
- Decision: REJECTED_OR_BLOCKED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES

Controller decision:

- TASK-146 is not closed and is not marked Done.
- No integration is entered because Review rejected Controller closure and the Integration Agent is retired.
- Review found a focused artifact-contract defect: ranked scan metadata can exist when a ranking config is supplied, but storage infers ranked/unranked state from candidate rows only. A ranked scan that legitimately produces zero candidates is treated as unranked, rejects ranking provenance during persistence, and would produce a false downstream handoff `ranked=false`.
- The next Active 5.3 Execution handoff is `coordination/handoffs/TASK-146_SCANNER_EMPTY_RANKED_ARTIFACT_REWORK.md`.
- This is a focused Review rework. It must not be merged with readiness `follow_up_batches` or any ordinary Scanner hardening item.
- AGENTS.md is unchanged because the current phase remains Phase 4-P and allowed implementation targets remain `quant/scanner/` and `tests/scanner/`.

For active TASK-146 specifically, the next role is 5.3 Execution rework. Expected write path is `coordination/reports/TASK-146_REPORT.md`. Execution must follow `coordination/handoffs/TASK-146_SCANNER_EMPTY_RANKED_ARTIFACT_REWORK.md`, modifying only allowed Scanner storage/runner/contract/readiness files where needed, focused Scanner tests, and the report. It must keep all behavior offline over caller-provided data and avoid DataHub/FeatureHub implementation changes, StrategyLab, SignalEngine, BacktestEngine, portfolio/risk logic, AI, notification, UI, automated trading, credentials, private data, hidden network behavior, or unrelated artifact-contract churn.

Phase switch: NO for the TASK-146 rejected Review / empty ranked artifact rework dispatch. Current phase remains Phase 4-P Scanner Personal Trading Perfection Re-Review.

## TASK-146 Closure / TASK-070 Re-Dispatch

Review result:

- `coordination/reviews/TASK-146_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-146 is closed as Done.
- No integration is entered because Review allowed Controller closure and the Integration Agent is retired.
- TASK-146 closes the final Phase 4-P Scanner readiness batch `scanner_artifact_contract_repair_batch_01` / `SCN-ART-001`, including the focused empty-ranked artifact persistence rework. Review accepted that ranked-state derivation now follows explicit artifact ranking provenance, empty ranked artifacts persist truthfully, downstream handoff metadata remains correct, regression coverage was added, default tests are offline-safe, and no live evidence is required because Scanner is local-only.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md` to Phase 4-P. The Scanner Personal Trading Perfection standard requires universe definition/validation, deterministic batch filtering, ranking/scoring and ordering, candidate persistence with reproducibility/downstream handoff metadata, missing/stale/market-constraint handling, and realistic offline workflow regression coverage. Accepted TASK-143 through TASK-146 evidence now covers all of those groups.
- Controller verified `build_scanner_personal_readiness_gate()` now reports `phase_closure_ready=true`, status counts `pass=6`, `warn=0`, `blocked=0`, `fail=0`, and no remaining `follow_up_batches`.
- Phase 4-P has no remaining Ready, In Progress, or In Review tasks. All Phase 4-P tasks have handoff/report/review lifecycle artifacts, and their reviews allow Controller closure. No real-source live evidence is required because Scanner work is local/offline over caller-provided inputs; live-enabled result SKIP is expected and accepted for TASK-143 through TASK-146.
- No Scanner public-source limitation, partial state, blocked item, or owner-waiver dependency remains undispositioned in the Controller decision matrix. The single-item TASK-146 dispatch remains justified by persisted artifact schema/provenance compatibility blast radius.
- Phase switch: YES, to Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.
- TASK-070 is re-dispatched as the next Active 5.3 Execution handoff because its prior prerequisite block is cleared by accepted DataHub Phase 2.5-P, FeatureHub Phase 3-P, and Scanner Phase 4-P closure.
- `coordination/handoffs/TASK-070_BACKTEST_HISTORICAL_REPLAY_PRIMITIVES.md` was the Active handoff at re-dispatch time and is now superseded by the focused TASK-070 side-coercion rework handoff.
- AGENTS.md is updated because the current phase changed to Phase 5 and allowed implementation targets are now `quant/strategies/`, `quant/backtest/`, `tests/strategies/`, and `tests/backtest/`.

For TASK-070 at that re-dispatch point, the next role was 5.3 Execution. Expected write path was `coordination/reports/TASK-070_REPORT.md`. Execution had to follow `coordination/handoffs/TASK-070_BACKTEST_REPLAY_SIDE_COERCION_REWORK.md`, modifying only files allowed by that handoff, keeping all behavior offline, and avoiding DataHub/FeatureHub/Scanner implementation changes, production portfolio/signal/risk modules, AI, notification, UI, automated trading, credentials, private data, hidden network behavior, broader report-generation scope, or ordinary Phase 5 hardening outside the Review finding.

Phase switch: YES for the TASK-146 closure / TASK-070 re-dispatch. Current phase is Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.

## TASK-070 Review Rejection / Rework Dispatch

Review result:

- `coordination/reviews/TASK-070_REVIEW.md`
- Decision: REJECTED_OR_BLOCKED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES

Controller decision:

- At that rejection-dispatch point, TASK-070 remained Active and was not closed.
- No Integration Agent is dispatched because the active workflow is `handoff -> Execution -> Review -> Controller`, and Review has not accepted closure.
- The Review finding is narrow: `validate_trade_intent()` accepts caller-provided side strings such as `"buy"` / `"sell"`, but `run_historical_replay()` dispatches by enum identity, allowing a valid `"buy"` string to be mis-executed as the non-buy path and rejected as `insufficient_position`.
- A focused 5.3 Execution rework is dispatched at `coordination/handoffs/TASK-070_BACKTEST_REPLAY_SIDE_COERCION_REWORK.md`.
- The rework is intentionally minimal and must not be batched with ordinary Phase 5 readiness follow-up work, report expansion, strategy logic, or other hardening items.
- Phase remains Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection. AGENTS.md phase boundary and allowed implementation targets are unchanged.

For TASK-070 at that rejection-dispatch point, the next role was 5.3 Execution. Expected write path was `coordination/reports/TASK-070_REPORT.md`. Execution had to follow `coordination/handoffs/TASK-070_BACKTEST_REPLAY_SIDE_COERCION_REWORK.md`, modifying only files allowed by that handoff, keeping default tests offline-safe, and avoiding DataHub/FeatureHub/Scanner implementation changes, production portfolio/signal/risk modules, AI, notification, UI, automated trading, credentials, private data, hidden network behavior, and broader report-generation scope.

## TASK-070 Closure / TASK-147 Dispatch

Review result:

- `coordination/reviews/TASK-070_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-070 is closed as Done.
- No Integration Agent is dispatched because Review allowed Controller closure and the active workflow is `handoff -> Execution -> Review -> Controller`.
- TASK-070 closes the focused BacktestEngine historical replay side-coercion rework. Review accepted that `run_historical_replay()` now normalizes `TradeIntent.side` with the same semantics accepted by contract validation, so caller-provided `"buy"` and `"sell"` strings execute like their `TradeSide` enum values.
- Review independently reran `python3 -m unittest discover -s tests/backtest -p 'test_*.py'` and `python3 -m unittest discover -s tests -p 'test_*.py'`; both passed. Default tests remain offline-safe. Live-enabled result is `SKIP` because TASK-070 forbade live tests and no real-source work was in scope.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md`. Phase 5 remains incomplete because accepted TASK-069 and TASK-070 evidence covers foundation contracts and a deterministic replay primitive only. The roadmap still requires concrete strategy rule evaluation, owner-approved starter strategy library, parameter metadata/versioning and repeatable experiment configuration, cost/slippage/cash/position/fill/calendar assumption depth, result summaries and performance/drawdown/risk/report-ready outputs, multi-configuration comparison, and reproducibility coverage.
- Phase switch: NO. Current phase remains Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.
- Because Phase 5 does not yet have a local readiness gate or follow-up batches, Controller dispatches an audit/gate task before ordinary hardening. This is not a single ordinary hardening item; it is the gate needed to classify coverage and produce coherent follow-up batches under `coordination/PHASE_GATE.md`.
- `coordination/handoffs/TASK-147_STRATEGY_BACKTEST_PERSONAL_TRADING_READINESS_GATE.md` is dispatched as the next Active 5.3 Execution handoff.
- AGENTS.md is unchanged because the current phase and allowed implementation targets remain Phase 5: `quant/strategies/`, `quant/backtest/`, `tests/strategies/`, and `tests/backtest/`.

For active TASK-147 specifically, the next role is 5.3 Execution. Expected write path is `coordination/reports/TASK-147_REPORT.md`. Execution must follow `coordination/handoffs/TASK-147_STRATEGY_BACKTEST_PERSONAL_TRADING_READINESS_GATE.md`, modifying only allowed StrategyLab/BacktestEngine files, focused Phase 5 tests, and the report. It must create deterministic readiness/audit output, follow-up queue, and follow-up batches while keeping all behavior offline over caller-provided or local code evidence. It must avoid DataHub/FeatureHub/Scanner implementation changes, concrete strategy behavior, new replay model behavior, performance metric/report implementation, comparison workflows, production portfolio/signal/risk modules, AI, notification, UI, automated trading, credentials, private data, and hidden network behavior.

## TASK-147 Closure / TASK-148 Dispatch

Review result:

- `coordination/reviews/TASK-147_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-147 is closed as Done.
- No Integration Agent is dispatched because Review allowed Controller closure and the active workflow is `handoff -> Execution -> Review -> Controller`.
- TASK-147 closes the local/offline Phase 5 StrategyLab and BacktestEngine readiness gate. Review accepted that the gate stayed within `quant/backtest/**`, `tests/backtest/**`, and the execution report, and that it truthfully kept Phase 5 non-closure-ready instead of over-claiming foundation/replay work as complete.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md`. Phase 5 remains incomplete because the readiness gate reports `phase_closure_ready=false`, status counts `pass=1`, `warn=6`, `blocked=0`, `fail=0`. The unresolved `warn` groups are strategy definition/starter library, parameter metadata/versioning/repeatable experiments, replay assumptions/market rules, metrics/report outputs, multi-configuration comparison, and reproducibility/boundary regressions.
- Phase switch: NO. Current phase remains Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.
- Controller read the TASK-147 readiness `follow_up_batches`. The next executable current-phase capability cluster is `strategy_backtest__personal_trading_hardening__batch_01`, covering `phase5__strategy_definition_and_starter_library` and `phase5__parameter_versioning_and_experiment_config`.
- This is a two-item coherent Phase 5 cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because executable starter strategy rules and repeatable experiment configuration identity share strategy ids, parameter metadata, parameter-set validation/versioning, and deterministic local run inputs.
- `coordination/handoffs/TASK-148_STRATEGY_STARTER_EXPERIMENT_CONFIG_HARDENING.md` is dispatched as the next Active 5.3 execution handoff.
- AGENTS.md is unchanged because the current phase and allowed implementation targets remain Phase 5: `quant/strategies/`, `quant/backtest/`, `tests/strategies/`, and `tests/backtest/`.

For active TASK-148 specifically, the next role is 5.3 Execution. Expected write path is `coordination/reports/TASK-148_REPORT.md`. Execution must follow `coordination/handoffs/TASK-148_STRATEGY_STARTER_EXPERIMENT_CONFIG_HARDENING.md`, modifying only allowed StrategyLab/BacktestEngine files, focused Phase 5 tests, and the report. It must add deterministic offline starter strategy rule evaluation and repeatable experiment configuration over caller-provided/local inputs only. It must avoid DataHub/FeatureHub/Scanner implementation changes, warehouse reads, live data, production portfolio/signal/risk modules, AI, notification, UI, automated trading, credentials, private data, and hidden network behavior.

## TASK-148 Review Rejection / Contract Truth Rework Dispatch

Review result:

- `coordination/reviews/TASK-148_REVIEW.md`
- Decision: REJECTED_OR_BLOCKED
- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES

Controller decision:

- TASK-148 remains Active and is not closed or marked Done.
- No Integration Agent is dispatched because the active workflow is `handoff -> Execution -> Review -> Controller`.
- Review found two focused blockers: repeatable experiment config validation does not reject stale or mismatched `experiment_id` values after material normalized-content changes, and starter strategy definitions declare entry-only output intent while evaluators emit both `enter_long` and `exit_long` signals.
- A focused 5.3 Execution rework is dispatched at `coordination/handoffs/TASK-148_STRATEGY_EXPERIMENT_CONTRACT_TRUTH_REWORK.md`.
- The rework is intentionally minimal and must not be batched with ordinary Phase 5 readiness `follow_up_batches`, replay assumptions, metrics/report outputs, multi-configuration comparison, reproducibility work, or other hardening items.
- Phase switch: NO. Current phase remains Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.
- AGENTS.md is unchanged because the current phase and allowed implementation targets remain Phase 5: `quant/strategies/`, `quant/backtest/`, `tests/strategies/`, and `tests/backtest/`.

For active TASK-148 specifically, the next role is 5.3 Execution rework. Expected write path is `coordination/reports/TASK-148_REPORT.md`. Execution must follow `coordination/handoffs/TASK-148_STRATEGY_EXPERIMENT_CONTRACT_TRUTH_REWORK.md`, modifying only files allowed by that rework handoff. It must keep default tests offline-safe and avoid DataHub/FeatureHub/Scanner implementation changes, warehouse reads, live data, production portfolio/signal/risk modules, AI, notification, UI, automated trading, credentials, private data, hidden network behavior, and unrelated Phase 5 readiness work.

## TASK-148 Closure / TASK-149 Dispatch

Review result:

- `coordination/reviews/TASK-148_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-148 is closed as Done.
- No Integration Agent is dispatched because Review allowed Controller closure and the active workflow is `handoff -> Execution -> Review -> Controller`.
- TASK-148 closes Phase 5 readiness batch `strategy_backtest__personal_trading_hardening__batch_01`, including the focused contract-truth rework. Review accepted that `validate_repeatable_experiment_config()` now rejects stale/mismatched `experiment_id` values and starter strategy metadata truthfully declares entry/exit output intent.
- Review independently reran `python3 -m unittest discover -s tests/strategies -p 'test_*.py'` and `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`; both passed. Default tests remain offline-safe. Live-enabled result is `SKIP` because TASK-148 was local/offline only.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md`. Phase 5 remains incomplete because the current readiness gate reports `phase_closure_ready=false`, status counts `pass=3`, `warn=4`, `blocked=0`, `fail=0`. The unresolved groups are replay assumptions/market rules, metrics/report outputs, multi-configuration comparison, and reproducibility/boundary regressions.
- Phase switch: NO. Current phase remains Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.
- Controller read the TASK-147/TASK-148 readiness `follow_up_batches`. TASK-148 covered `strategy_backtest__personal_trading_hardening__batch_01`; the next executable current-phase capability cluster is `strategy_backtest__personal_trading_hardening__batch_02`, covering `phase5__replay_assumptions_and_market_rules` and `phase5__metrics_and_report_outputs`.
- This is a two-item coherent Phase 5 cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because execution assumptions and evaluation outputs should be hardened together so metrics and report-ready summaries reflect explicit replay semantics rather than implicit simplifications.
- `coordination/handoffs/TASK-149_REPLAY_ASSUMPTIONS_METRICS_HARDENING.md` is dispatched as the next Active 5.3 execution handoff.
- AGENTS.md is unchanged because the current phase and allowed implementation targets remain Phase 5: `quant/strategies/`, `quant/backtest/`, `tests/strategies/`, and `tests/backtest/`.

For active TASK-149 specifically, the next role is 5.3 Execution. Expected write path is `coordination/reports/TASK-149_REPORT.md`. Execution must follow `coordination/handoffs/TASK-149_REPLAY_ASSUMPTIONS_METRICS_HARDENING.md`, modifying only files allowed by that handoff. It must keep default tests offline-safe and avoid DataHub/FeatureHub/Scanner implementation changes, warehouse reads, live data, production portfolio/signal/risk modules, AI, notification, UI, automated trading, credentials, private data, hidden network behavior, and unrelated Phase 5 comparison/reproducibility work.

## TASK-149 Closure / TASK-150 Dispatch

Review result:

- `coordination/reviews/TASK-149_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-149 is closed as Done.
- No Integration Agent is dispatched because Review allowed Controller closure and the active workflow is `handoff -> Execution -> Review -> Controller`.
- TASK-149 closes Phase 5 readiness batch `strategy_backtest__personal_trading_hardening__batch_02`. Review accepted that replay assumptions, market rules, metrics, and report-ready outputs stayed local/offline and within `quant/backtest/**`, `tests/backtest/**`, and the execution report.
- Review independently reran `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`; it passed with `Ran 31 tests`. Default tests remain offline-safe. Live-enabled result is `SKIP` because TASK-149 was local/offline only.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md`. Phase 5 remains incomplete because the current readiness gate reports `phase_closure_ready=false`, status counts `pass=5`, `warn=2`, `blocked=0`, `fail=0`. The unresolved groups are multi-configuration comparison workflows and broader comparison-workflow reproducibility regressions.
- Phase switch: NO. Current phase remains Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.
- Controller read the Phase 5 readiness `follow_up_batches`. TASK-148 covered `strategy_backtest__personal_trading_hardening__batch_01`; TASK-149 covered `strategy_backtest__personal_trading_hardening__batch_02`; the next executable current-phase cluster is `strategy_backtest__personal_trading_hardening__batch_03`, covering `phase5__multi_configuration_comparison` and `phase5__reproducibility_and_boundary_regressions`.
- This is a two-item coherent Phase 5 cluster from readiness `follow_up_batches`. It is dispatched together under the capability-cluster policy because comparison workflows need deterministic regression coverage so repeated offline research runs do not depend on manual orchestration or hidden data patching.
- `coordination/handoffs/TASK-150_COMPARISON_REPRODUCIBILITY_HARDENING.md` is dispatched as the next Active 5.3 execution handoff.
- AGENTS.md is unchanged because the current phase and allowed implementation targets remain Phase 5: `quant/strategies/`, `quant/backtest/`, `tests/strategies/`, and `tests/backtest/`.

For active TASK-150 specifically, the next role is 5.3 Execution. Expected write path is `coordination/reports/TASK-150_REPORT.md`. Execution must follow `coordination/handoffs/TASK-150_COMPARISON_REPRODUCIBILITY_HARDENING.md`, modifying only files allowed by that handoff. It must keep default tests offline-safe and avoid DataHub/FeatureHub/Scanner implementation changes, warehouse reads, live data, production portfolio/signal/risk modules, AI, notification, UI, automated trading, credentials, private data, hidden network behavior, and unrelated downstream work.

## TASK-150 Closure / TASK-151 Dispatch

Review result:

- `coordination/reviews/TASK-150_REVIEW.md`
- Decision: ACCEPTED
- Controller closure allowed: YES
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: NO

Controller decision:

- TASK-150 is closed as Done.
- No Integration Agent is dispatched because Review allowed Controller closure and the active workflow is `handoff -> Execution -> Review -> Controller`.
- TASK-150 closes Phase 5 readiness batch `strategy_backtest__personal_trading_hardening__batch_03`, covering multi-configuration comparison workflows and reproducibility/boundary regressions. Review accepted that the comparison workflow stays local/offline and within `quant/backtest/**`, `tests/backtest/**`, and the execution report.
- Review independently reran `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`; it passed with `Ran 38 tests`. Default tests remain offline-safe. Live-enabled result is `SKIP` because TASK-150 was local/offline only.
- Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md`. Phase 5 is complete because the current StrategyLab/BacktestEngine readiness gate reports `phase_closure_ready=true`, status counts `pass=7`, `warn=0`, `blocked=0`, `fail=0`, `follow_up_queue=0`, and `follow_up_batches=0`.
- The Phase 5 completion audit covers the roadmap-required local/offline module responsibility: strategy definition and starter rule evaluation, parameter metadata/versioning and repeatable experiment configuration, deterministic historical replay over caller-provided or approved local inputs, cost/slippage/cash/position/fill/calendar assumptions, metrics and report-ready outputs, multi-configuration comparison, invalid-config/date/missing-bar/assumption/reproducibility tests, and no hidden live-data dependency.
- No Phase 5 `partial`, `warn`, `fail`, or blocked current-scope item is being treated as closure. No real-source live smoke is required for Phase 5 because the module scope is local/offline and Review confirmed no network, warehouse, DataHub, FeatureHub, Scanner, credential, browser/session, or clock dependency was introduced.
- Phase switch: YES. Current phase is now Phase 6 PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.
- `coordination/handoffs/TASK-151_PORTFOLIO_SIGNAL_RISK_READINESS_GATE.md` is dispatched as the next Active 5.3 execution handoff.
- TASK-151 is an audit/gate task rather than a single ordinary hardening item. It is dispatched because Phase 6 starts from a placeholder module and needs a deterministic readiness matrix, follow-up queue, and coherent follow-up batches before ordinary portfolio/signal/risk hardening proceeds.
- AGENTS.md is updated because the current phase changed to Phase 6 and allowed implementation targets are now `quant/portfolio/` and `tests/portfolio/`.

For active TASK-151 specifically, the next role is 5.3 Execution. Expected write path is `coordination/reports/TASK-151_REPORT.md`. Execution must follow `coordination/handoffs/TASK-151_PORTFOLIO_SIGNAL_RISK_READINESS_GATE.md`, modifying only `quant/portfolio/`, `tests/portfolio/`, and the report. It must keep all behavior offline over local code evidence and avoid DataHub/FeatureHub/Scanner/StrategyLab/BacktestEngine implementation changes, warehouse reads, live data, notification, AI, UI, automated trading, credentials, private data, hidden network behavior, and unrelated downstream work.
