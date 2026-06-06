# Roadmap

## Phase Completion Policy

The roadmap target is a personally usable quantitative trading research and signal system at the strongest practical public-source completeness level, not a connected foundation demo and not a partial module slice.

From this point onward, a phase may be marked finally complete only when it satisfies the phase's Personal Trading Perfection Standard below. A foundation slice, one-symbol/one-fund adapter, one-route demonstration, representative feature primitive, contract-only module, narrow smoke-test path, or `partial` capability may close an individual task, but it must not close the phase.

Historical phase-complete decisions remain useful task history only. Previously completed Phase 1, Phase 2, Phase 2.5, Phase 3, Phase 4, and Phase 5 foundation work is reclassified as historical foundation progress until it passes the Personal Trading Perfection Standard.

Controller rules:

- Treat previously completed foundation phases as useful groundwork, not proof that the final module is personally trading-perfect.
- Before switching phase, compare current implementation against the relevant Personal Trading Perfection Standard.
- If any required capability group is missing, dispatch an expansion task in the current phase or reopen the earliest prerequisite phase that owns the gap.
- Public-source/no-paid capability gaps must be fixed or explicitly carried as `warn` / `blocked` with owner-accepted rationale; they must not silently pass.
- Paid/private requirements are outside the current required implementation scope, but must be recorded as `blocked` unless the owner provides credentials and explicitly reopens that scope.
- Prefer capability-expansion tasks over moving further downstream when downstream work would depend on incomplete upstream breadth.

## Personal Trading Perfection Standards

### DataHub

DataHub is personally trading-perfect only when it can support realistic A-share, Hong Kong stock, ETF/fund, index, sector, macro, policy/news/announcement research workflows at the strongest practical public-source completeness level without ad hoc source patching.

Required capability groups:

- full symbol/instrument reference coverage for A-share, Hong Kong stock, ETF/fund, major indices, and sectors/concepts
- daily and intraday market data capability where needed for short-term research, with clear source freshness and market-calendar handling
- corporate actions, listing/delisting/ST/suspension/resumption, limit-up/down, margin financing/lending, capital flow, northbound/major activity data where reliable public or credentialed sources exist
- financial statements, financial indicators, valuation history, fund holdings/scale/flow, index constituents and weights, sector membership/history, macro observations, policy/news/announcements
- batch-capable and parameterized source access, not only one-symbol examples
- local raw/normalized persistence, refresh metadata, data-quality reports, source capability metadata, and failure diagnostics
- gated live evidence for each real-source capability or an explicit owner-approved blocked/waived status
- no unresolved `fail`, no unexplained `partial`, and no silent public-source limitation in the Controller readiness matrix

### FeatureHub

FeatureHub is personally trading-perfect only when it provides a complete practical scanner/strategy-ready feature library over validated DataHub-shaped inputs, not only a few representative indicators.

Required capability groups:

- price/volume technical indicator core set, including returns, moving averages, EMA, MACD, RSI, KDJ/stochastic, Bollinger Bands, ATR, volatility, volume/turnover/liquidity features, gap/breakout style primitives, and rolling window helpers
- valuation features, including PE/PB/PS style values, earnings yield/book-to-price, valuation percentile or relative valuation where source history exists
- capital-flow and money-flow features, including main/northbound/fund-flow levels, rolling changes, intensity/normalization, and missing-source behavior
- sector-relative and market-relative features, including stock-vs-sector returns, sector strength, index-relative performance, and breadth/rotation primitives where source data exists
- feature batch calculation APIs that can consume caller-provided or locally refreshed data consistently
- feature output persistence/versioning and downstream Scanner/StrategyLab consumability
- offline tests for success, missing data, window boundaries, invalid input, duplicate dates, and schema compatibility
- no indicator family, market-relative feature group, persistence path, or downstream contract gap may remain unexplained as `partial`

### Scanner

Scanner is personally trading-perfect only when it can turn FeatureHub outputs and universes into robust candidate lists for repeated personal research workflows, including ranking, exclusion, persistence, and market-specific constraints.

Required capability groups:

- universe definition and validation for A-share, Hong Kong stock, ETF/fund, sector, index, custom watchlist, and exclusion lists
- deterministic feature-filter evaluation over batches, not only one symbol
- ranking/scoring and explicitly configured ordering suitable for research candidate prioritization
- candidate-list persistence with manifests, reproducibility metadata, and downstream handoff to StrategyLab/SignalEngine
- support for missing features, stale features, suspended/limit-up/down securities, and market-specific constraints
- tests for realistic multi-symbol scans, invalid filters, missing values, deterministic ordering, and artifact safety
- no scan mode, ranking path, universe handling path, or artifact workflow may remain only partially implemented without an explicit owner-accepted blocker

### StrategyLab and BacktestEngine

Phase 5 is personally trading-perfect only when it supports realistic offline strategy research and historical validation for personal use, with practical starter strategies, repeatable experiments, and decision-quality reports.

Required capability groups:

- strategy definition contracts, concrete strategy rule evaluation, and an owner-approved starter strategy library
- parameter metadata, validation, versioning, and repeatable experiment configuration
- deterministic historical replay over caller-provided or approved local market data
- cost, slippage, cash, position, fill, and market-calendar assumptions documented and test-covered
- backtest result summaries, performance metrics, drawdown/risk metrics, and report-ready outputs
- support for comparing multiple strategy configurations without hidden live data or manual data patching
- tests for invalid configs, date boundaries, missing bars, corporate-action/source assumptions where applicable, and reproducibility
- no strategy execution, replay, cost/slippage, metric, report, or reproducibility path may remain merely foundational without an explicit owner-accepted blocker

### PortfolioMonitor, SignalEngine, and RiskEngine

Phase 6 is personally trading-perfect only when scan/strategy/backtest outputs can be converted into managed signal state with practical personal risk controls and auditable decision records.

Required capability groups:

- watchlist and holding-state contracts with deterministic updates
- signal lifecycle management, including created/updated/expired/closed states
- combination of Scanner, StrategyLab, BacktestEngine, and portfolio context into structured signals
- risk rules for exposure, concentration, liquidity, drawdown, position sizing guidance, blacklists, suspensions, and market-specific constraints
- auditability of why a signal exists and why it passed or failed risk checks
- tests for conflicting signals, stale data, risk-blocked signals, and lifecycle transitions
- no signal lifecycle, risk rule, portfolio state, or audit path may remain partially implemented without an explicit owner-accepted blocker

### Notification and AIReport

Phase 7 is personally trading-perfect only when approved alerts and explanations are grounded in structured system outputs and are reliable enough for personal monitoring.

Required capability groups:

- alert routing, throttling, state, and audit logs
- data-grounded AI explanations that cite DataHub/FeatureHub/Scanner/SignalEngine inputs rather than inventing hidden analysis
- daily/weekly summaries, signal narratives, risk notes, and source-linked report artifacts
- tests for alert deduplication, blocked alerts, missing data, and explanation grounding
- no alert channel, grounding rule, report artifact, or explanation path may remain partially implemented without an explicit owner-accepted blocker

### Local Web UI

Phase 8 is personally trading-perfect only when the local user can operate the full personal quant workflow without reading code.

Required capability groups:

- DataHub status, refresh, source-capability, and data-quality views
- market data browser for symbols, ETFs/funds, sectors, macro, news/announcements where available
- feature, scan, candidate-list, strategy, backtest, signal, risk, notification, and report views
- local-first workflows for running or inspecting approved offline tasks
- clear handling for missing credentials, source failures, stale data, and blocked capabilities
- responsive, usable local UI tests or browser verification for critical workflows
- no core workflow view, inspection path, error state, or local operation path may remain partially implemented without an explicit owner-accepted blocker

## Phase 0: Governance and Blueprint

Status: Historical governance baseline complete; not a final product-readiness phase

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

Status: Historical foundation complete; pending perfection re-review through DataHub gates

Goals:

- define DataHub package skeleton
- define local storage layout
- define dataset registry
- define source adapter interfaces
- define schema validation foundation
- add offline fixtures and default tests

## Phase 2: DataHub Comprehensive Source Collection

Status: Historical foundation complete; pending perfection re-review through Phase 2.5-P

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
- Phase 2 foundation scope was closed after TASK-039 controller closure under the earlier foundation gate.
- Under the current Personal Trading Perfection Standard, DataHub remains incomplete until Phase 2.5-P confirms the strongest practical public-source breadth, batch access, diagnostics, storage/refresh/quality paths, and blocked/waived limitations.

## Phase 2.5: DataHub Trading-Grade Source Capability

Status: Historical source-capability core complete; pending Phase 2.5-P perfection re-review before FeatureHub resumes

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
- Phase 2.5 was previously closed for the no-paid-credential foundation scope after TASK-058, with paid Tushare index-weight live proof deferred.
- Under the current personal trading completion standard, Phase 2.5 is reopened.
- TASK-071 completed the current DataHub trading-usable gap audit and found DataHub not closure-ready; it recommended A-share daily-bars batch hardening as the highest-priority next gap.
- TASK-072 completed A-share daily-bars batch hardening with accepted review and live-enabled PASS evidence; `a_share_daily_bars` is now `covered`.
- TASK-073 completed contract-only A-share instrument status-history coverage; `DatasetName.INSTRUMENT_STATUS_HISTORY` now exists, relevant source families advertise the dataset, and `a_share_listing_delisting_st_status` maps to it while remaining `partial`.
- TASK-074 completed bounded public AKShare A-share `INSTRUMENT_STATUS_HISTORY` adapter coverage with accepted offline tests, default offline-safe live tests, and live-enabled PASS evidence; `a_share_listing_delisting_st_status` remains conservative rather than over-promoted.
- TASK-075 completed A-share `VALUATION_SNAPSHOT` batch/date-window hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded near-year valuation access; `a_share_valuation_history` remains `partial` because broader history/pagination remains incomplete.
- TASK-076 completed A-share `CAPITAL_FLOW_SNAPSHOT` batch/date-window hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded capital-flow access; `a_share_capital_flow` and `a_share_northbound_flow` remain `partial` because broader historical continuity and dedicated northbound coverage remain incomplete.
- TASK-077 completed A-share `FINANCIAL_STATEMENTS` and `FINANCIAL_INDICATORS` batch/report-period hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded financial-history access; `a_share_financial_statements` and `a_share_financial_indicators` remain `partial` because public AKShare breadth/history completeness beyond the bounded report-period slice remains unproven.
- TASK-078 completed A-share `MINUTE_BARS` batch/date-window hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded intraday access; `a_share_minute_bars` remains `partial` because broader intraday history continuity and full trading-grade breadth remain unproven.
- TASK-079 completed Hong Kong `DAILY_BARS` batch/resilience hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded date-window access; `hk_daily_bars` remains `partial` because broader history continuity and source redundancy remain incomplete.
- TASK-080 completed Hong Kong `INSTRUMENT_MASTER` / universe-reference batch hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded stock-reference access; `hk_universe_reference` remains `partial` because full-market HK universe collection, dated lifecycle reconstruction, and non-stock taxonomy remain outside this slice.
- TASK-081 completed Hong Kong `FINANCIAL_STATEMENTS` / `FINANCIAL_INDICATORS` batch/report-period hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded report-period access; `hk_financial_data` remains `partial` because broader HK market breadth and long-history continuity remain incomplete.
- TASK-082 completed ETF/fund `DAILY_BARS` batch/date-window hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded exchange ETF/fund daily-bar access; `fund_daily_bars` remains `partial` because broader fund breadth, longer history continuity, and non-ETF public-route coverage remain unproven.
- TASK-083 completed ETF/fund `FUND_NAV_SNAPSHOT` batch/date-window hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded ETF/fund NAV access; `fund_nav` remains `partial` because broader fund breadth, longer history continuity, and non-exchange public-route coverage remain incomplete.
- TASK-084 completed ETF/fund `FUND_HOLDINGS` batch/report-period hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded report-period holdings access; `fund_holdings_composition` remains `partial` because broader fund breadth, longer history continuity, and non-exchange public-route coverage remain incomplete.
- TASK-085 completed ETF/fund `FUND_FLOW` batch/date-window hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-symbol bounded public exchange scale/share access; `fund_flow` remains `partial` because richer net-inflow/subscription/redemption metrics, non-exchange breadth, and longer history continuity remain incomplete.
- TASK-086 completed contract-only ETF/fund premium-discount source-fact schema coverage; `fund_premium_discount` now maps to `DatasetName.FUND_PREMIUM_DISCOUNT` and remains `partial` pending adapter-backed public source evidence.
- TASK-087 completed bounded public ETF/fund `FUND_PREMIUM_DISCOUNT` adapter/source-fact coverage with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for the requested multi-symbol path; `fund_premium_discount` remains `partial` because latest-available snapshot breadth/history limitations remain.
- TASK-088 completed public index `INDEX_DAILY_BARS` batch/benchmark hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-index bounded core mainland benchmark access; `index_daily_bars` remains `partial` because broader benchmark breadth, longer history continuity, and non-mainland/global benchmark coverage remain incomplete.
- TASK-089 completed public index `INDEX_CONSTITUENTS` batch/rebalance hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided multi-index bounded constituent access; `index_constituent_history` and `index_rebalance_effective_dates` remain `partial` because broader benchmark breadth, longer constituent continuity, and explicit rebalance-calendar truth remain incomplete.
- TASK-090 completed public sector `SECTOR_MEMBERSHIP` batch/history hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-provided industry/concept multi-sector bounded membership access; `sector_membership` and `sector_historical_changes` remain `partial` because full sector taxonomy history, explicit change-event timelines, and classification-version metadata remain incomplete.
- TASK-091 completed public macro/policy depth hardening with accepted offline/default tests, default offline-safe live tests, and live-enabled PASS evidence for caller-parameterized macro indicator definitions/observations and bounded policy route selectors; `macro_observations`, `macro_indicator_definitions`, `macro_release_metadata`, and `policy_documents` remain `partial` because broader public macro breadth, first-class release/revision history, release-calendar completeness, broader authority coverage, and deeper policy history remain incomplete.
- TASK-092 completed source-health metadata hardening after accepted TypeError-classification rework. Clear request/signature/contract mismatches still map to `unsupported_request`, while internal fetch-stage `TypeError` failures remain non-unsupported `fetch_failed`; focused offline tests passed and no live tests were permitted.
- Phase 2.5 Core is complete only as historical no-paid source-capability progress. TASK-071 through TASK-092 prove important practical source-capability breadth, batch/parameterized access, local persistence, refresh metadata, data-quality reporting, source-health metadata, and failure diagnostics, but they do not close DataHub under the Personal Trading Perfection Standard until Phase 2.5-P re-review is accepted.
- Paid/private credential capabilities remain blocked unless the owner provides credentials or explicitly waives the limitation. `TASK-059` remains a blocked paid Tushare follow-up, and `index_weight_history` must not be promoted without future credentialed live PASS evidence.

## Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

Status: Reopened before FeatureHub resumes

Intent:

Phase 2.5-P exists because the owner requires every step, including historically completed DataHub foundation/source phases, to reach the strongest practical personal-use quant trading perfection level before continuing. For now this means public-source/no-paid maximum practical completeness; paid/private data is not included, and `index_weight_history` remains blocked unless credentials are later provided and the scope is reopened.

Gate:

- build a deterministic perfection re-review matrix across all historical DataHub work from Phase 1, Phase 2, Phase 2.5, and Phase 2.5-P
- cover all existing DataHub domains: A-share, Hong Kong stock, ETF/fund, index, sector/concept, macro/policy, storage, refresh metadata, quality reports, and source-health diagnostics
- classify each domain and capability with stable `pass`, `warn`, `blocked`, or `fail` outcomes
- surface public-source breadth, history, freshness, taxonomy, and reliability limitations as explicit `warn` or `blocked` results, not silent passes
- fail missing contracts, missing source mappings, inconsistent status truth, unresolved `partial` claims, or missing required local storage/refresh/quality/source-health paths
- keep default tests offline-safe and forbid live tests unless a later hardening handoff explicitly gates them
- dispatch follow-up DataHub hardening tasks until Controller can see no unresolved `fail`, no unexplained `partial`, and every remaining `warn` or `blocked` item has an owner-acceptable reason

Progress:

- TASK-093 completed the offline DataHub personal trading perfection re-review gate and accepted follow-up queue rework. The gate reports overall `blocked`, phase closure `false`, domain counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and a deterministic 42-item Controller-ready queue across A-share, Hong Kong, ETF/fund, index, sector/concept, macro/policy, quality reports, storage/refresh, and source-health diagnostics.
- TASK-094 completed the first executable TASK-093 queue item with accepted review and live-enabled PASS evidence. It improved A-share `INSTRUMENT_STATUS_HISTORY` lifecycle evidence where public routes expose source truth, while keeping `a_share_listing_delisting_st_status` conservative because full dated ST/*ST continuity and explicit SH terminal delist dates remain incomplete.
- TASK-095 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence after rework. It expanded A-share `SUSPENSION_RESUMPTION_EVENTS` source coverage where public routes expose source truth, fixed duplicate logical resumption events across overlapping Eastmoney/Baidu route rows, added offline overlap regression coverage, and kept `a_share_suspension_resumption` conservative.
- TASK-096 completed the next executable TASK-093 queue item with accepted review after BaoStock classifier rework. It added owner-authorized `baostock_public_cn` no-credential 5/15/30/60-minute historical bar coverage, kept `a_share_minute_bars` conservative at `partial`, recorded BaoStock live-enabled PASS evidence, and fixed the live-smoke classifier so BaoStock-specific contract/data failures no longer downgrade to environment-unavailable `SKIP`.
- TASK-097 completed the next executable TASK-093 queue item with accepted review after classifier rework. It added first-class `DatasetName.ADJUSTMENT_FACTORS` semantics and no-credential public AKShare/Sina qfq/hfq source coverage, kept `a_share_adjustment_factors` conservative because full per-trade-date continuity and public-source redundancy remain incomplete, recorded live-enabled PASS evidence, and fixed the live-smoke classifier so Sina/source-route data failures no longer downgrade to environment-unavailable `SKIP`.
- TASK-098 completed the next executable TASK-093 queue item with accepted review after shared-contract rework. It made A-share corporate-action taxonomy explicit for source-backed dividend/distribution and bounded rights-issue event families, preserved the shared `CORPORATE_ACTIONS` `action_family` / `source_route` contract, fixed HK corporate-actions normalization so existing HK records validate under the shared schema, kept default tests offline-safe, and recorded live-enabled PASS evidence for the HK rework path.
- TASK-099 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence. It expanded A-share `VALUATION_SNAPSHOT` valuation-history breadth by selecting Baidu valuation periods based on requested history breadth, proved a 450-day two-symbol live path, and kept `a_share_valuation_history` conservative because full long-run continuity and no-credential second-source redundancy remain unproven.
- TASK-100 completed the next A-share valuation-history hardening item with accepted review and live-enabled PASS evidence after overlap-conflict and Baidu live-failure reworks. It validates route-distinct Baidu/Eastmoney overlap and gap behavior, treats Baidu upstream non-JSON responses as route unavailability, keeps default tests offline-safe, and keeps `a_share_valuation_history` conservative because full long-run continuity and no-credential redundancy remain incomplete.
- TASK-101 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence. It made A-share `CAPITAL_FLOW_SNAPSHOT` route truth explicit with `source_route`, preserved route-distinct capital-flow source facts, kept `a_share_capital_flow` conservative because no stable second dated symbol-history route is proven and the datacenter fallback remains latest-only, and did not promote or change `a_share_northbound_flow`.
- TASK-102 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence after live-classifier rework. It made A-share northbound-flow semantics first-class under `DatasetName.NORTHBOUND_FLOW_SNAPSHOT`, kept `a_share_northbound_flow` conservative because only one no-credential route is proven and broader northbound metric coverage remains incomplete, and narrowed the dedicated northbound live classifier so route-signature/call-compatibility defects fail rather than downgrade to environment `SKIP`.
- TASK-103 completed the next executable TASK-093 queue item with accepted review after live-classifier rework. It added explicit A-share turnover/liquidity source-fact semantics, kept `a_share_turnover_liquidity` conservative because public-source redundancy and broader liquidity breadth remain incomplete, and narrowed the dedicated live classifier so `stock_zh_a_hist` route-signature/call-compatibility defects fail rather than downgrade to environment `SKIP`. The final live-enabled result is `SKIP` due to independently reproduced upstream/environment disconnect, not a repository-side contract or signature failure.
- TASK-104 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence after classifier rework. It expanded A-share `LIMIT_UP_DOWN_EVENTS` route breadth/history where public routes expose source truth and narrowed the `gettopicpreviouspool` / `gettopiczbgcpool` live classifier so route-name-bearing repository defects fail rather than downgrade to environment `SKIP`.
- TASK-105 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence. It expanded A-share `MARGIN_FINANCING_LENDING` from a one-symbol slice to caller-provided multi-symbol bounded SSE/SZSE margin-detail history with explicit exchange/source-route provenance, kept BSE/BJ handling truthful by rejecting unsupported symbols until a validated public route is proven, and kept `a_share_margin_financing_and_lending` conservative because BSE symbol-level coverage, symbol-compatible exchange-summary reconciliation, and long-history continuity remain incomplete.
- TASK-106 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence. It added explicit A-share `FINANCIAL_STATEMENTS` source-route truth for `stock_financial_report_sina`, proved schema-valid live statement records, tightened financial-data live classifier truthfulness, and kept `a_share_financial_statements` conservative because second-route redundancy and full long-history continuity remain unproven.
- TASK-107 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence. It added explicit A-share `FINANCIAL_INDICATORS` route and metric-family truth for `stock_financial_analysis_indicator_em`, kept route-distinct indicator records separate, tightened financial-data provenance assertions, and kept `a_share_financial_indicators` conservative because second-route redundancy, full long-history continuity, and broader cross-industry metric-family completeness remain unproven.
- TASK-108 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence after focused date-window/fallback truth rework. It added bounded multi-symbol A-share company-announcement access and `source_route` truth, added live assertions that announcement dates stay inside the requested bounded window, prevented fallback per-day upstream/source availability failures from silently satisfying incomplete windows, and kept `a_share_company_announcements` conservative because broader history continuity and no-credential second-route redundancy remain unproven.
- TASK-109 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence. It expanded A-share `DatasetName.MAJOR_ACTIVITY_EVENTS` from single-day block-trade detail coverage to bounded date-window detail plus symbol-date summary coverage with explicit `source_route` truth, kept default tests offline-safe, and kept `a_share_major_activity_events` conservative because broader non-block-trade taxonomy, longer-history continuity, and no-credential second-source redundancy remain unproven.
- TASK-110 completed the next executable TASK-093 queue item with accepted review and live-enabled PASS evidence. It added explicit profile-route provenance to Hong Kong `DatasetName.INSTRUMENT_MASTER` records, tightened HK instrument-master live-classifier truthfulness, and kept `hk_universe_reference` conservative because full-market HK universe breadth, non-stock taxonomy coverage, and dated delisting/lifecycle metadata remain unproven.
- TASK-111 completed the next Phase 2.5-P DataHub hardening task with accepted review. It added a bounded `symbols=None` HK current-listed list path using `stock_hk_spot_em` plus per-symbol `stock_hk_security_profile_em` reconciliation, kept default tests offline-safe, and kept `hk_universe_reference` conservative because the new bounded list route was not live-pass-proven in this environment and full-market breadth, non-stock taxonomy, and dated lifecycle metadata remain incomplete.
- TASK-112 completed the next Phase 2.5-P DataHub hardening task with accepted review and live-enabled PASS evidence. It added a bounded HK listed-universe fallback path using `sina_hk_stock_spot_page1` when primary `stock_hk_spot_em` is genuinely environment/upstream unavailable, kept route-distinct source truth, preserved hard-fail behavior for repository defects, and kept `hk_universe_reference` conservative because only bounded current-listed stock sample access is proven.
- TASK-113 completed the next Phase 2.5-P DataHub hardening task with accepted review and live-enabled PASS evidence. It tightened HK universe capability and source-catalog wording instead of over-claiming new coverage, explicitly recording that proven no-credential routes remain stock-only and do not expose reusable non-stock taxonomy or trustworthy dated delist/inactive lifecycle metadata; `hk_universe_reference` remains conservative at `partial`.
- TASK-114 completed the next Phase 2.5-P DataHub hardening task with accepted review and live-enabled PASS evidence. It strengthened HK `DAILY_BARS` history continuity through the AKShare same-family `stock_hk_daily` fallback when `stock_hk_hist` is unavailable or empty, kept default tests offline-safe, tightened capability/catalog truth, and kept `hk_daily_bars` conservative because independent no-credential public-source redundancy remains unproven.
- TASK-115 completed the next Phase 2.5-P DataHub hardening task with accepted review and live-enabled PASS evidence. It strengthened HK `CORPORATE_ACTIONS` dividend-related route/taxonomy/history truth by combining `stock_hk_dividend_payout_em` and `stock_hk_fhpx_detail_ths`, distinguishing `dividend_distribution` from source-backed `dividend_no_distribution`, and keeping `hk_corporate_actions` conservative because non-dividend HK corporate-action families and batch breadth remain unproven.
- TASK-116 completed the next Phase 2.5-P DataHub hardening task with accepted review and live-enabled PASS evidence. It strengthened HK `VALUATION_SNAPSHOT` valuation-history truth by adding caller-provided HK symbol batches with bounded dated `stock_hk_indicator_eniu` PE/PB/market-cap history, optional same-date Baidu supplementation when reachable, explicit `source_route` truth, deterministic date-window behavior, and conservative capability/source wording; `hk_valuation_history` remains conservative because accepted live evidence is stale through `2022-07-13` and independent current-dated redundancy remains unproven.
- TASK-117 completed the next Phase 2.5-P DataHub hardening task with accepted review after focused live-classifier rework. It proved HK financial route-name-bearing signature/schema/payload/normalization defects now remain hard failures instead of being downgraded to environment `SKIP`, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `hk_financial_data` conservative because the rework was classifier-only and broader HK financial breadth/history limitations remain.
- TASK-118 completed the next Phase 2.5-P DataHub hardening task with accepted review and live-enabled PASS evidence. It made HK turnover/liquidity source facts explicit through dated volume and traded amount under `DatasetName.DAILY_BARS`, preserved source-route truth and fallback behavior, and kept `hk_turnover_liquidity` conservative because turnover-rate, float-share, spread/microstructure facts, and independent public-source redundancy remain unproven.
- TASK-119 remains active after Review rejection. Initial execution broadened ETF/fund daily-bar support, but Review found the accepted listed-fund prefix families overextended beyond proven evidence: tests and live evidence only proved `161725.FUND_CN` through the LOF route and Sina fallback while implementation accepted all `16` / `18` / `150` / `501` prefixes. A focused symbol-family truth rework is dispatched; TASK-119 must not close until fresh Review accepts evidence-backed support or conservative rejection.
- Phase 2.5-P remains open. `index_weight_history` remains an owner credential blocker; optional `hk_minute_bars` requires owner waiver or future feasibility scope; the remaining `warn` items, including ETF/fund, index, sector/concept, macro/policy, and quality-report gaps, require DataHub hardening or explicit owner-accepted disposition before FeatureHub can reopen.

## Phase 3: FeatureHub

Status: Historical foundation complete; deferred until Phase 2.5-P closes

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
- Phase 3 foundation scope was closed after TASK-063 controller closure under the earlier foundation gate.
- Under the current Personal Trading Perfection Standard, FeatureHub remains incomplete. Its next expansion is deferred until Phase 2.5-P DataHub Personal Trading Perfection Re-Review closes. The previous FeatureHub TASK-093 dispatch is no longer active because TASK-093 is reused for the DataHub perfection re-review gate.

## Phase 4: Scanner

Status: Historical foundation complete; personally trading-perfect incomplete pending DataHub and FeatureHub perfection closure

Goals:

- define universes
- scan full market using DataHub and FeatureHub
- produce candidate lists
- persist scan artifacts

Progress:

- TASK-064 completed pure offline Scanner foundation contracts and validation under `quant/scanner/` and `tests/scanner/`, with accepted review and no live test requirement.
- TASK-065 completed pure offline Scanner universe definition and membership snapshot validation helpers with accepted review.
- TASK-066 completed pure local Scanner candidate-list JSONL and manifest persistence for already-built artifacts with accepted review.
- TASK-067 completed pure offline Scanner filter matching primitives over caller-provided feature values with accepted review.
- TASK-068 completed pure offline in-memory Scanner scan runner primitives from caller-provided universe, feature values, and filters with accepted review.
- Phase 4 foundation scope was closed after TASK-068 controller closure under the earlier foundation gate.
- Under the current Personal Trading Perfection Standard, Scanner remains incomplete until it is reopened after DataHub and FeatureHub perfection closure and expanded to ranking/scoring plus practical scan workflows.

## Phase 5: StrategyLab and BacktestEngine

Status: Historical foundation complete; paused pending prerequisite DataHub, FeatureHub, and Scanner perfection closure

Goals:

- define strategy research interface
- implement historical replay
- add cost and slippage assumptions
- generate backtest reports

Progress:

- TASK-069 completed pure offline StrategyLab and BacktestEngine foundation contracts for strategy definitions and backtest request/result metadata, with accepted review and no live test requirement.
- TASK-070 BacktestEngine historical replay primitives was dispatched, then deferred back to Backlog when the owner replaced foundation-only phase gates with stricter personal trading gates.
- Phase 5 must not continue until DataHub, then FeatureHub, then Scanner have reached accepted Personal Trading Perfection closure or explicit owner-accepted blocked status.

## Phase 6: PortfolioMonitor, SignalEngine, and RiskEngine

Status: Planned; must meet Personal Trading Perfection Standard when reopened

Goals:

- track watchlists and holdings
- combine scan and strategy outputs into signals
- apply risk rules
- maintain signal state

## Phase 7: Notification and AIReport

Status: Planned; must meet Personal Trading Perfection Standard when reopened

Goals:

- deliver approved alerts
- generate structured AI explanations
- ground reports in DataHub, FeatureHub, Scanner, and SignalEngine outputs

## Phase 8: Local Web UI

Status: Planned; must meet Personal Trading Perfection Standard when reopened

Goals:

- expose local dashboards
- inspect DataHub status and data quality
- browse scans, signals, reports, and portfolio state
- keep UI local-first
