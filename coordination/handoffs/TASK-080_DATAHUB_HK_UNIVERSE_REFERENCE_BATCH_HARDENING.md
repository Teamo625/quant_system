# TASK-080 DataHub Hong Kong Universe Reference Batch Hardening

## Role

5.3 Execution Window.

## Context

TASK-071 found DataHub not trading-usable because many real-source capabilities remain narrow source slices. TASK-079 closed the first Hong Kong batch/resilience slice by proving caller-provided multi-symbol bounded HK `DAILY_BARS` access with live-enabled PASS evidence, but Phase 2.5 remains open.

The next highest-priority Hong Kong gap is `hk_universe_reference`: the current `AkshareHKInstrumentMasterAdapter` is still validated as a one-symbol HK stock reference slice. Trading-usable downstream research needs deterministic caller-provided HK stock reference batches for validation and metadata lookup, without silently collecting the full HK market.

This task must stay within DataHub. Do not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden AKShare-backed Hong Kong `INSTRUMENT_MASTER` access from a one-symbol slice into deterministic caller-provided multi-symbol HK stock reference access.

The adapter should preserve existing one-symbol behavior, validate the full requested batch before source calls, fetch and normalize each requested HK stock symbol, reject unsupported/non-stock instruments clearly, keep default tests offline-safe, and include gated live smoke evidence that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

This task does not require full-market HK universe collection, full-history listing/delisting reconstruction, a new dataset schema, HK minute bars, FeatureHub calculations, scanner workflows, strategy/backtest logic, or private/credentialed sources.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_akshare_hk_instrument_master_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-080_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than the required report
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- unrelated DataHub adapters or tests
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, or private account data.

Do not implement downstream feature calculation, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Extend `AkshareHKInstrumentMasterAdapter` for multiple requested Hong Kong stock symbols through the existing `SourceRequest.symbols` path.
- Preserve support for exactly one HK stock symbol.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently fetch the full HK market in this task.
- Validate the full requested symbol batch before making source calls so invalid inputs do not produce partial successful batches.
- Continue accepting canonical `00700.HK`-style symbols and existing raw 5-digit HK stock code behavior where already supported.
- Reject A-share, ETF/fund, index-like, malformed, ambiguous, missing, or unsupported symbols clearly.
- Fetch each requested valid HK stock symbol through the existing no-credential public AKShare security-profile route unless implementation finds an already-local public route that is safer and remains within this handoff.
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures. Treat only actual network/proxy/DNS/TLS/upstream availability failures as source-unavailable conditions.
- Normalize records to `DatasetName.INSTRUMENT_MASTER` without changing its schema.
- Preserve source-truth optionality. Do not invent delisting dates, security type, exchange, or status values beyond existing schema-compatible behavior.
- If the public source identifies a requested symbol as a non-stock instrument, fail clearly rather than returning a stock record.
- Deduplicate deterministically by at least `(symbol, source)`.
- Sort output deterministically by symbol.
- If one symbol fails due to invalid input, adapter behavior, schema validation, or normalization, fail clearly rather than returning a partial successful batch.
- Keep `start_date` and `end_date` accepted by the adapter interface but do not make them imply historical listing reconstruction in this task.
- Update `hk_universe_reference` capability truth conservatively. Keep it `partial` unless implementation and live evidence demonstrably satisfy the full trading-usable breadth/delisting standard; otherwise refine gap text to reflect proven batch stock-reference access and remaining limitations.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`

The live-enabled smoke should validate at least two Hong Kong stock symbols for `INSTRUMENT_MASTER` if the upstream public route is available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-080_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `hk_universe_reference` capability truth changed
- source route coverage, batch behavior, non-stock rejection behavior, and known HK reference limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- multi-symbol HK instrument-master requests work through the adapter contract in offline tests
- full-batch validation prevents partial successful batches after invalid requested symbols
- normalized records validate against `DatasetName.INSTRUMENT_MASTER`
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects the actual proven source breadth
