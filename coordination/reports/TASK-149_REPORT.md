# TASK-149 Report

## files changed

- `quant/backtest/contracts.py`
- `quant/backtest/replay.py`
- `quant/backtest/personal_readiness.py`
- `quant/backtest/__init__.py`
- `quant/backtest/README.md`
- `tests/backtest/test_contracts.py`
- `tests/backtest/test_replay.py`
- `tests/backtest/test_personal_readiness.py`

## replay assumptions and market-rule behavior

- Added explicit `ReplayAssumptions` metadata on `ReplayConfig`, propagated into replay results and report payloads.
- Replay now walks every calendar day in the requested date window instead of only dates with bars/intents.
- Missing-bar dates now still produce snapshots; same-day intents without a caller-provided bar are rejected as `missing_market_bar`.
- Zero-volume bars are treated as unusable for fills; same-day intents are rejected as `unusable_market_bar`, and marking uses the latest usable prior close.
- Corporate-action handling is now explicit and local-only: replay never computes adjustments and records caller-declared price semantics as `adjusted`, `unadjusted`, or `as_provided`.
- Cost/slippage/fill/cash/position carry-forward semantics remain deterministic and validated through config/report contracts.

## metrics and report-output capabilities

- Expanded `ReplaySummary` beyond ending equity / total return / max drawdown with win/loss counts, win/loss rates, turnover, transaction/slippage totals, exposure, ending position count, and date-coverage facts.
- Added serialization-friendly `ReplayReport` output with:
  - assumptions
  - summary
  - coverage
  - end-state facts
  - rejected-intent breakdown
  - optional artifact reference validation
- Kept existing summary fields and existing replay entry points backward-compatible.

## readiness gate update

- Updated local Phase 5 readiness metadata to mark:
  - `replay_assumptions_costs_fills_and_market_calendar` -> `pass`
  - `result_metrics_drawdown_risk_and_report_outputs` -> `pass`
- Gate truth after this task:
  - `phase_closure_ready=false`
  - status counts: `pass=5`, `warn=2`, `blocked=0`, `fail=0`
  - next recommended batch: `strategy_backtest__personal_trading_hardening__batch_03`

## tests run

- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'` -> PASS (`Ran 31 tests`)

## default network behavior

- Offline-safe only.
- No network calls, live data access, warehouse reads, DataHub/FeatureHub/Scanner reads, credentials, browser/session state, or hidden IO were added.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence

- `SKIP`
- Root cause / evidence: this handoff is local/offline StrategyLab and BacktestEngine hardening only; live tests were not required or allowed.

## deviations

- None.

## risks/follow-up

- Phase 5 remains open. Multi-configuration comparison workflows are still not first-class.
- Reproducibility coverage improved for replay assumptions/report shape, but broader comparison-workflow reproducibility remains pending under the remaining batch.
- `ReplayAssumptions.price_adjustment` defaults to `as_provided`; callers should set `adjusted` or `unadjusted` explicitly when their local bars are known.
