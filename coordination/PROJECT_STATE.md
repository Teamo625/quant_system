# Project State

Last updated by: 5.5 Controller

## Current Phase

Phase 5: StrategyLab and BacktestEngine.

## Current Implementation Scope

StrategyLab and BacktestEngine Phase 5 work is active. The current handoff opens pure offline BacktestEngine historical replay primitives over caller-provided data.

Current implementation may target only:

- `quant/strategies/`
- `quant/backtest/`
- `tests/strategies/`
- `tests/backtest/`

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
- TASK-070 is dispatched for pure offline BacktestEngine historical replay primitives over caller-provided market bars and caller-provided dated trade intents

## Active Constraints

- Do not implement DataHub source adapters or new source-capability work unless the controller explicitly reopens a DataHub task.
- Do not implement concrete trading strategies beyond explicitly assigned StrategyLab contract primitives.
- Do not implement scanner ranking or stock-picking logic.
- Do not implement backtest execution beyond the explicitly assigned BacktestEngine handoff sub-scope.
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

## Phase Gate Decision

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
