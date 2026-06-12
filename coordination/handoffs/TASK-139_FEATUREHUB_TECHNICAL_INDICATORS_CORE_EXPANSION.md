# TASK-139 FeatureHub technical indicators core expansion

## Role

5.3 Execution Window.

## Phase

Phase 3-P FeatureHub Personal Trading Perfection Re-Review.

## Context

TASK-138 is closed after accepted Review Agent verification. It added the deterministic FeatureHub personal trading readiness gate and found that Phase 3-P is not closure-ready:

- `phase_closure_ready=false`
- status counts: `pass=0`, `warn=7`, `blocked=0`, `fail=0`
- current FeatureHub technical coverage is still representative only: close-to-close return, simple moving average, and realized volatility

The next executable readiness batch is `featurehub_technical_indicators_batch_01`, covering:

- `FH-TECH-001`: rolling helpers and EMA-family primitives
- `FH-TECH-002`: MACD, RSI, and KDJ/stochastic oscillator families
- `FH-TECH-003`: Bollinger Bands and ATR
- `FH-TECH-004`: volume-turnover-liquidity features
- `FH-TECH-005`: gap and breakout primitives

This is a coherent FeatureHub technical capability cluster. It must stay within FeatureHub and must not implement Scanner ranking, strategy rules, backtest execution, portfolio/signal/risk logic, DataHub source adapters, AI, notification, UI, or automated trading.

## Objective

Expand the pure offline FeatureHub price/volume technical core so scanner/strategy-ready technical feature calculations are no longer limited to the current representative slice.

Implement deterministic, caller-provided-input calculations for the technical indicator families in the assigned batch, with focused offline tests and no hidden live/network behavior.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-139_FEATUREHUB_TECHNICAL_INDICATORS_CORE_EXPANSION.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-138_REPORT.md`
- `coordination/reviews/TASK-138_REVIEW.md`
- `quant/features/contracts.py`
- `quant/features/technical.py`
- `tests/features/test_technical.py`
- `tests/features/test_personal_readiness.py`

Read other `quant/features/` or `tests/features/` files only as needed to preserve local patterns. Do not read or modify DataHub implementation files unless needed only to understand existing enum imports; DataHub is not an implementation target.

## Allowed Writes

Only:

- `quant/features/**`
- `tests/features/**`
- `coordination/reports/TASK-139_REPORT.md`

Suggested implementation locations:

- `quant/features/technical.py`
- `quant/features/__init__.py` only for minimal exports if needed
- `tests/features/test_technical.py`
- `tests/features/test_personal_readiness.py` only if the readiness snapshot must be updated after the new technical batch lands

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-139_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not fetch live data, call source adapters, read credentials, use browser/session state, or introduce hidden network behavior.

## Implementation Requirements

### 1. Preserve current technical API behavior

Keep existing TASK-060 behavior and tests passing:

- daily-bar normalization sorts rows and rejects duplicate dates
- mixed symbol/market inputs fail
- non-positive or non-finite close values fail
- current close-to-close return, SMA, and realized-volatility calculations keep their accepted semantics
- emitted `FeatureValueRecord` outputs continue to validate under the current contract

### 2. Add rolling helper primitives

Add deterministic rolling helper coverage that later indicators can share, including:

- positive integer window validation
- trailing-window extraction over normalized rows
- deterministic behavior for insufficient rows
- finite-output validation

Keep helpers internal or public according to existing module style, but cover behavior with tests when the helper is part of the intended API.

### 3. Add EMA-family primitives

Implement exponential moving average calculations over close prices using deterministic trailing rows. The implementation must define and test the seed behavior, smoothing factor, insufficient-row behavior, and invalid-window behavior.

### 4. Add momentum oscillators

Implement MACD, RSI, and KDJ/stochastic oscillator calculations over caller-provided daily bars.

Tests must cover at least:

- normal calculation paths
- insufficient history
- flat/no-loss or no-gain edge behavior where applicable
- invalid windows or invalid parameter ordering
- deterministic output ordering and finite outputs

### 5. Add bands, range, volume, and breakout primitives

Implement:

- Bollinger Bands over close prices
- ATR over high/low/close-like inputs
- volume-turnover-liquidity feature calculations over caller-provided bar or turnover inputs
- gap and breakout primitives for practical short-term research

If the current `DailyBarInput` shape is too narrow for high/low/open/volume/turnover fields, extend it conservatively while preserving backward compatibility for existing close-only callers. New required fields must be required only by calculations that need them.

### 6. Feature record outputs

Where practical, provide `FeatureValueRecord` builder functions consistent with the existing `PRICE_TECHNICAL` contract. Because TASK-138 identified metric-level identity as a later contract gap, do not invent a broad downstream identity contract in this task. Keep any multi-indicator record emission conservative, documented by tests, and compatible with the current schema.

### 7. Update readiness truth

After implementing the batch, update the FeatureHub readiness gate only as far as the new evidence justifies:

- `price_volume_technical_core` should reflect the newly implemented technical families.
- Do not promote unrelated capability groups.
- Do not mark Phase 3-P closure-ready unless every roadmap-required FeatureHub group is actually complete under `coordination/ROADMAP.md`.

## Scope Boundaries

Do not implement:

- valuation feature expansion
- capital-flow/fund-flow expansion
- sector-relative or market-relative features
- batch calculation orchestration APIs
- metric-level downstream identity contract repair beyond what is strictly needed for current compatibility
- scanner filters, ranking, scoring, or candidate selection
- strategy/backtest behavior
- DataHub source adapters or warehouse refresh
- portfolio, signal, risk, AI, notification, UI, or automated trading behavior

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run narrower focused tests during development as needed.

No live tests are required or allowed. Default tests must be offline-safe.

## Completion Report

Write `coordination/reports/TASK-139_REPORT.md` with:

- files changed
- implemented technical indicator families and any intentionally deferred edge
- readiness gate changes, including whether `price_volume_technical_core` remains `warn` or becomes `pass`
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is pure offline FeatureHub work
- deviations from this handoff
- risks or follow-up tasks

## Acceptance Criteria

The task is acceptable when:

- the assigned `featurehub_technical_indicators_batch_01` items are implemented or explicitly constrained with evidence
- existing TASK-060 technical behavior remains backward-compatible
- new technical calculations are pure, deterministic, and covered by offline tests
- FeatureHub readiness truth is updated without over-promoting unrelated groups
- no DataHub or downstream module implementation files are changed
- default tests remain offline-safe
- report exists at `coordination/reports/TASK-139_REPORT.md`

## Report Path

`coordination/reports/TASK-139_REPORT.md`

## Review Path

`coordination/reviews/TASK-139_REVIEW.md`

## Integration Path

N/A. Integration Agent is retired; Review is the closure gate before Controller.
