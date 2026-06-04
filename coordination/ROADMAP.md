# Roadmap

## Phase 0: Governance and Blueprint

Status: Completed

Goals:

- initialize project structure
- define project rules
- document complete architecture
- document module boundaries
- define DataHub data contracts
- create task protocol
- create testing policy
- prepare first DataHub handoff

## Phase 1: DataHub Foundation

Status: Completed

Goals:

- define DataHub package skeleton
- define local storage layout
- define dataset registry
- define source adapter interfaces
- define schema validation foundation
- add offline fixtures and default tests

## Phase 2: DataHub Comprehensive Source Collection

Status: Completed

Goals:

- collect comprehensive data-source coverage for the current product scope
- cover A-share full-market data, including reference, calendar, price/volume, corporate actions, valuation, capital flow, and quality metadata
- cover Hong Kong stock full-market data, including reference, calendar, price/volume, corporate actions, valuation where available, and quality metadata
- cover ETF and fund data, including reference, price/volume, holdings or composition where available, flow/scale where available, and quality metadata
- cover index data for China, Hong Kong, and key global benchmarks
- cover concise global equity market data for major markets and benchmark instruments
- cover industry and concept sector data, including membership, classification, and sector quote data where available
- cover global and China macroeconomic data relevant to market research
- cover policy, news, and announcement data with source provenance and update metadata
- maintain a complete DataHub source catalog and coverage matrix across all required domains
- implement source adapters for every approved source/dataset/domain needed by the expanded Phase 2 scope
- persist raw and normalized data locally
- add update metadata for source refreshes
- add data quality checks for collected datasets
- add mandatory live-source smoke coverage for every real-source adapter or real data-fetching task, safely gated and skipped by default
- route live-enabled network/source failures through execution rework plus independent review before acceptance

Progress:

- Previous pre-rescope TASK-006 through TASK-009 Phase 2 handoffs were removed after owner-directed scope change.
- TASK-006 completed the DataHub comprehensive source catalog and coverage matrix.
- TASK-007 completed expanded domain stable dataset/schema contracts.
- TASK-008 completed expanded contract semantic validation and invalid-sample coverage.
- TASK-009 completed explicit semantic validation rules and removed broad keyword-coupled validation.
- TASK-010 completed semantic rule integrity checks to prevent schema/rule drift.
- TASK-011 completed source adapter contract foundation for comprehensive Phase 2 sources.
- TASK-012 completed the first accepted real-source AKShare adapter slice for A-share `daily_bars`, including gated live smoke evidence.
- TASK-013 completed AKShare A-share `trading_calendar`, including source-catalog alignment and gated live smoke evidence.
- TASK-014 completed AKShare Hong Kong stock `daily_bars`, including live-network root-cause evidence and a feasible fallback path for intermittent Eastmoney HK source instability.
- TASK-015 completed AKShare ETF/fund `fund_nav_snapshot`, including offline adapter coverage, exports, and gated live smoke evidence.
- TASK-016 completed AKShare China index `index_daily_bars`, including source catalog alignment, offline adapter coverage, exports, and gated live smoke evidence.
- TASK-017 completed AKShare industry/concept sector `sector_daily_bars`, including live-network diagnosis reworks and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-018 completed AKShare `sector_master`, including live duplicate rework and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-019 completed AKShare `sector_membership`, including live evidence + live PASS rework and closure-ready acceptance by review/integration.
- TASK-020 completed AKShare `index_constituents`, including deterministic offline tests and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-021 completed AKShare `global_equity_snapshot`, including live-route reworks for Eastmoney/Sina instability and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-022 completed AKShare `news_events`, including deterministic offline tests and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-023 completed HKEX `company_announcements`, including symbol-filter rework closure and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-024 completed AKShare China macro `macro_indicator_master` and `macro_observations`, including `is_preliminary` rework closure and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-025 completed the local refresh metadata and `DATA_QUALITY_REPORT` baseline, including deterministic offline tests and accepted offline-only integration.
- TASK-026 completed AKShare A-share `instrument_master`, including active Shanghai/Shenzhen/Beijing stock reference records and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-027 completed AKShare A-share `corporate_actions`, including one-symbol dividend/corporate-action records and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-028 completed AKShare A-share `valuation_snapshot`, including live-network rework closure, source-truth optionality for `float_market_cap`, and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-029 completed AKShare A-share `capital_flow_snapshot`, including live-network rework closure, source-truth optionality for `net_inflow` / `northbound_net_buy` / `turnover_rate`, and bounded one-symbol datacenter fallback accepted by review/integration.
- TASK-030 completed public `POLICY_DOCUMENTS` adapter coverage under `macro_policy_public_sources`, including closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-031 completed AKShare `FUND_HOLDINGS` one-fund coverage after classifier rework, including accepted direct classifier coverage and closure-ready live-enabled PASS evidence.
- TASK-032 completed AKShare HK `INSTRUMENT_MASTER` one-symbol coverage, including deterministic offline tests and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-033 completed AKShare HK `CORPORATE_ACTIONS` one-symbol dividend/corporate-action coverage, including deterministic offline tests and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-034 completed AKShare HK `VALUATION_SNAPSHOT` one-symbol coverage, including deterministic offline tests, minimal HK source-catalog alignment, and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-035 completed AKShare `FUND_PROFILE` one-fund coverage, including deterministic offline tests and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-036 completed DataHub source catalog implementation reconciliation, including accepted index constituents and A-share corporate-actions catalog alignment plus focused offline catalog tests.
- TASK-037 completed HKEX-backed Hong Kong `TRADING_CALENDAR` adapter coverage, including deterministic offline tests and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-038 completed narrow AKShare-backed China ETF `DAILY_BARS` adapter coverage after live-network rework, including bounded fallback for classified Eastmoney route unavailability and closure-ready live-enabled PASS evidence accepted by review/integration.
- TASK-039 completed the narrow local-only DataHub warehouse refresh runner, including raw and curated persistence from `SourceResult`, refresh metadata, `DATA_QUALITY_REPORT` output, and offline-only PASS evidence accepted by review/integration.
- Phase 2 is complete after TASK-039 controller closure under `coordination/PHASE_GATE.md`.

## Phase 2.5: DataHub Trading-Grade Source Capability

Status: Completed for no-paid-credential scope

Intent:

Phase 2.5 exists because the owner clarified that the next milestone is not collecting every data point locally. The milestone is completing the DataHub source-capability layer so the system can access all data domains needed for rigorous short-term and medium/long-term quant research when requested.

Goals:

- define a trading-grade source capability matrix for short-term and medium/long-term quant data needs
- identify gaps between current Phase 2 narrow source slices and complete source capability
- extend DataHub source catalog/contracts where needed for missing trading-grade domains
- implement batch-capable and parameterized source adapters only through explicit handoffs
- cover A-share, Hong Kong stock, ETF/fund, index, sector/concept, macro, policy, news, announcement, and data-quality/source-health domains
- include short-term data needs such as minute bars, limit-up/down, suspension/resumption, turnover/liquidity, margin financing/securities lending, capital flow, northbound flow, block/dragon-tiger style market activity where reliable sources exist
- include medium/long-term data needs such as financial statements, financial indicators, valuation history, corporate actions, listing/delisting/ST history, index constituent/weight history, sector classification history, fund holdings/scale/flow, macro observations, and announcement/policy metadata
- preserve default offline tests and use gated live smokes for real-source work
- do not require full-market or full-history data to be collected locally during this phase
- do not implement FeatureHub, scanner, strategy, backtest, signal, risk, portfolio, AI, notification, UI, or automated trading logic

Progress:

- TASK-041 completed the code-level trading-grade source capability audit and gap matrix that follow-up contract and adapter tasks can use.
- TASK-042 completed stable DataHub dataset contracts for required TASK-041 capabilities that previously had no `DatasetName` mapping, without adding adapters or live calls.
- TASK-043 completed a narrow public AKShare Hong Kong financial-statement and financial-indicator adapter slice with accepted offline tests, default offline-safe live tests, and live-enabled PASS evidence; `hk_financial_data` is now `partial`.
- TASK-044 completed a narrow public AKShare A-share financial-statement and financial-indicator adapter slice with accepted offline tests, default offline-safe live tests, and live-enabled PASS evidence; `a_share_financial_statements` and `a_share_financial_indicators` are now `partial`.
- TASK-045 completed a narrow public AKShare A-share margin financing/lending adapter slice after live skip/fail classifier rework, with accepted offline tests, default offline-safe live tests, live-enabled PASS evidence, and regression coverage proving route-name-bearing AKShare argument/signature compatibility errors remain hard failures.
- TASK-046 completed a narrow no-credential public AKShare A-share company-announcements adapter slice with accepted offline tests, default offline-safe live tests, and live-enabled PASS evidence; `a_share_company_announcements` is now `partial`.
- TASK-047 completed a contract-only A-share limit-up/down source-fact schema target, `DatasetName.LIMIT_UP_DOWN_EVENTS`, so later adapter work can avoid overloading `DatasetName.DAILY_BARS`.
- TASK-048 completed bounded public AKShare adapter coverage for `LIMIT_UP_DOWN_EVENTS`, with accepted offline tests, default offline-safe live tests, and live-enabled PASS evidence; `a_share_limit_up_down` is now `partial`.
- TASK-049 completed bounded public AKShare adapter coverage for `MAJOR_ACTIVITY_EVENTS` after live-route rework; the prior route/date `SKIP` was diagnosed and fixed in the gated live smoke, default tests remain offline-safe, and live-enabled rework smoke result was PASS with accepted review/integration.
- TASK-050 completed a narrow public AKShare A-share `MINUTE_BARS` adapter slice with accepted offline tests, default offline-safe live tests, and live-enabled PASS evidence; `a_share_minute_bars` is now `partial`.
- TASK-051 completed a narrow public AKShare ETF/fund `FUND_FLOW` adapter slice with accepted offline tests, default offline-safe live tests, and live-enabled PASS evidence; `fund_flow` is now `partial`, with public exchange scale/share source-truth limitations preserved.
- TASK-052 completed an explicit DataHub source-fact contract for A-share suspension/resumption events so this required capability no longer relies on generic `CORPORATE_ACTIONS` mapping; `a_share_suspension_resumption` remains `planned` pending adapter-backed source coverage.
- TASK-053 completed bounded public AKShare adapter coverage for `DatasetName.SUSPENSION_RESUMPTION_EVENTS`, with accepted offline tests, default offline-safe live tests, and live-enabled PASS evidence; `a_share_suspension_resumption` is now `partial`.
- TASK-054 completed offline source truth reconciliation for accepted public macro/policy adapter coverage; `macro_observations`, `macro_indicator_definitions`, and `policy_documents` now reconcile to conservative `partial` status instead of planned-only source truth.
- TASK-055 completed the explicit `DatasetName.INDEX_WEIGHT_HISTORY` source-fact contract for index x symbol x effective-date weight history; `index_weight_history` now maps to the dedicated contract and remains conservatively `planned` under credentialed `tushare_pro_cn_core`.
- TASK-056 completed bounded repository-level Tushare Pro adapter coverage and gated smoke tests for `DatasetName.INDEX_WEIGHT_HISTORY`; default tests remain offline-safe, but live-enabled execution skipped because local `TUSHARE_TOKEN` and `tushare` SDK prerequisites were absent, so live source coverage is not proven and `index_weight_history` remains `planned`.
- TASK-057 completed a narrow Tushare index-weight live-evidence/prerequisite rework with accepted review/integration; local `tushare` SDK availability is now confirmed, but live-enabled execution still skipped because `TUSHARE_TOKEN` is unset, so live source coverage is not proven and `index_weight_history` remains `planned`.
- TASK-058 completed offline metadata reconciliation for `index_weight_history`, correcting stale wording while preserving `planned` status and leaving credentialed live PASS evidence as the remaining blocker.
- TASK-059 initial credentialed live PASS execution and subsequent retry reworks stopped truthfully because `TUSHARE_TOKEN` was unset; Review requires another token-required rework because no credentialed live smoke ran and no `INDEX_WEIGHT_HISTORY` PASS evidence exists. The owner directed skipping this paid-token path for now, so TASK-059 is retained as a blocked paid-credential follow-up and `index_weight_history` remains `planned`.
- Phase 2.5 is complete for the no-paid-credential scope after TASK-058, with paid Tushare index-weight live proof deferred.

## Phase 3: FeatureHub

Status: Completed

Goals:

- compute technical features
- compute valuation and capital-flow features where available
- version feature outputs
- consume only DataHub contracts

Progress:

- TASK-040 completed FeatureHub foundation contracts after accepted trade-date validation rework. FeatureHub now has importable contract primitives, schema metadata, validation helpers, and offline tests; default tests remain offline-safe and no live test was required.
- TASK-060 completed the first current Phase 3 technical feature calculation slice, adding pure offline price technical primitives over caller-provided daily-bar-like records with accepted review.
- TASK-061 completed the pure offline valuation feature calculation slice over caller-provided valuation-snapshot-like records with accepted review; default tests remain offline-safe and no live test was required.
- TASK-062 completed the pure offline capital-flow feature calculation slice over caller-provided capital-flow-snapshot-like records with accepted review; default tests remain offline-safe and no live test was required.
- TASK-063 completed FeatureHub output persistence/versioning after accepted rework. The records-plus-manifest write path now preflights manifest conflicts before replacing records JSONL, default tests remain offline-safe, and no live tests were required.
- Phase 3 is complete after TASK-063 controller closure under `coordination/PHASE_GATE.md`.

## Phase 4: Scanner

Status: In progress

Goals:

- define universes
- scan full market using DataHub and FeatureHub
- produce candidate lists
- persist scan artifacts

Progress:

- TASK-064 Scanner foundation contracts is dispatched as the first Phase 4 execution task. Scope is limited to pure offline Scanner contract primitives and validation under `quant/scanner/` and `tests/scanner/`; ranking, strategy, backtest, signal, risk, portfolio, AI, notification, UI, automated trading, live data, and warehouse reads remain out of scope.

## Phase 5: StrategyLab and BacktestEngine

Status: Planned

Goals:

- define strategy research interface
- implement historical replay
- add cost and slippage assumptions
- generate backtest reports

## Phase 6: PortfolioMonitor, SignalEngine, and RiskEngine

Status: Planned

Goals:

- track watchlists and holdings
- combine scan and strategy outputs into signals
- apply risk rules
- maintain signal state

## Phase 7: Notification and AIReport

Status: Planned

Goals:

- deliver approved alerts
- generate structured AI explanations
- ground reports in DataHub, FeatureHub, Scanner, and SignalEngine outputs

## Phase 8: Local Web UI

Status: Planned

Goals:

- expose local dashboards
- inspect DataHub status and data quality
- browse scans, signals, reports, and portfolio state
- keep UI local-first
