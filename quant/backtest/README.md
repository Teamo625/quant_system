# BacktestEngine Offline Replay and Experiment Config

BacktestEngine is open for local/offline Phase 5 replay and experiment-configuration work.

Current scope:

- repeatable experiment configuration over explicit local metadata only
- deterministic experiment identity and normalized serialization output
- declarative backtest request contracts
- caller-provided `ReplayConfig` derived from `BacktestRequest`
- explicit replay assumption metadata carried in `ReplayConfig.assumptions`
- caller-provided `MarketBar` and `TradeIntent` replay inputs
- deterministic historical replay over local in-memory inputs
- per-date portfolio/equity snapshots and final replay summary metrics
- serialization-friendly `ReplayReport` output for later comparison/report workflows

Replay assumptions:

- replay is fully offline and never reads DataHub, FeatureHub, Scanner, or persisted artifacts
- replay walks every calendar day in the requested date window and carries cash/positions forward deterministically
- orders execute on the same-day close with configured basis-point slippage
- transaction cost is applied on traded notional
- intents with missing same-day bars or unusable zero-volume bars are reported as rejected
- non-trading or missing-bar dates still produce snapshots without inferring an upstream calendar
- positions mark to the latest usable caller-provided close seen on or before each replay date
- corporate-action handling is caller-owned: the engine never computes adjustment factors and only records whether prices were declared `adjusted`, `unadjusted`, or `as_provided`

Non-goals for this phase slice:

- strategy generation or signal logic
- ranking, candidate generation, or portfolio/risk engines
- live data access, warehouse reads, scheduling, persistence, or report rendering
- production-grade execution simulation or market microstructure modeling
