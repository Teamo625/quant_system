# BacktestEngine Historical Replay Primitives

BacktestEngine is open for Phase 5 offline historical replay foundation work.

Current scope:

- declarative backtest request contracts
- caller-provided `ReplayConfig` derived from `BacktestRequest`
- caller-provided `MarketBar` and `TradeIntent` replay inputs
- deterministic historical replay over local in-memory inputs
- per-date portfolio/equity snapshots and final replay summary metrics

Replay assumptions:

- replay is fully offline and never reads DataHub, FeatureHub, Scanner, or persisted artifacts
- orders execute on the same-day close with configured basis-point slippage
- transaction cost is applied on traded notional
- intents with missing or unusable same-day bars are reported as rejected
- snapshots mark positions to the latest caller-provided close seen on or before each replay date

Non-goals for this phase slice:

- strategy generation or signal logic
- ranking, candidate generation, or portfolio/risk engines
- live data access, scheduling, persistence, or report rendering
- production-grade execution simulation or market microstructure modeling
