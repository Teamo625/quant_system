# TASK-096 DataHub A-share Minute Bars BaoStock Live Classifier Rework

## Role

5.3 Execution Window.

## Context

TASK-096 remains active in Phase 2.5-P. Do not close the task, do not enter Integration, and do not update controller-owned project state.

The Review Agent rejected the BaoStock history-source result because the BaoStock live smoke classifier can silently downgrade source-specific contract/data failures to environment-unavailable `SKIP`.

Blocking review finding:

- `tests/datahub/test_baostock_a_share_minute_bars_live.py` includes `"baostock"` in the generic network token list and then treats any matching exception message as environment-unavailable.
- Review independently verified that `_is_live_environment_unavailable(ValueError("Invalid BaoStock date value: bad")) == True` and `_is_live_environment_unavailable(ValueError("Source symbol mismatch for BaoStock A-share minute-bars adapter")) == True`.
- This makes the current BaoStock live PASS evidence not closure-safe, because future normalization, schema, symbol, or contract regressions could be downgraded to `SKIP`.

## Objective

Fix only the BaoStock live-smoke classifier truthfulness issue found by Review.

The rework is successful only if:

- actual network/proxy/DNS/TLS/upstream/BaoStock service availability failures can still skip the gated live smoke;
- BaoStock-specific normalization, schema, symbol, dataset, interval, or source-contract/data errors fail the live test instead of skipping;
- focused offline classifier regression tests prove both sides of that boundary;
- default tests remain offline-safe;
- the TASK-096 report records truthful default and live-enabled results after the rework.

## Allowed Files

You may modify only:

- `tests/datahub/test_baostock_a_share_minute_bars_live.py`
- `coordination/reports/TASK-096_REPORT.md`

Do not modify `quant/datahub/` adapter/source-capability/source-catalog code in this rework unless the owner or Controller issues a new handoff. This handoff is classifier/test-truthfulness only.

Do not edit:

- `AGENTS.md`
- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- any inactive downstream module

## Required Implementation Guidance

- Remove broad source-name matching that turns any message containing `baostock` into an environment skip.
- Keep environment skip detection tied to real transport/service availability evidence, such as concrete network exception classes, request/urllib3 modules, socket/timeout/connection errors, or narrowly phrased service/login availability messages.
- Add or strengthen tests proving the Review examples are non-environment failures:
  - `ValueError("Invalid BaoStock date value: bad")`
  - `ValueError("Source symbol mismatch for BaoStock A-share minute-bars adapter")`
- Add at least one positive regression proving a genuine BaoStock service/network availability message can still skip, without relying on a bare `"baostock"` token alone.
- Preserve default live-test gating with `QUANT_SYSTEM_LIVE_TESTS`; no default test may perform a real network call.

## Required Tests

Run and record results in `coordination/reports/TASK-096_REPORT.md`:

- `python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py`
- `python3 -m unittest tests/datahub/test_baostock_a_share_minute_bars_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`

Run the gated live smoke if the environment can reach BaoStock:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py`

The live-enabled result must be recorded truthfully as `PASS`, `SKIP`, or `FAIL` with root-cause evidence. If it skips for a real network/proxy/DNS/TLS/upstream/service availability reason, record the exact exception class/message evidence. If it fails because of a contract/data issue, do not convert that failure to `SKIP`.

## Report Requirements

Update `coordination/reports/TASK-096_REPORT.md` with:

- files changed;
- tests run and results;
- default network behavior;
- live-enabled BaoStock result and evidence;
- explicit statement that BaoStock-specific contract/data errors are no longer classified as environment-unavailable skips;
- deviations, if any;
- risks or follow-up.

## Scope Guardrails

- Keep `a_share_minute_bars` conservative at `partial`.
- Do not add new source routes.
- Do not implement full-market collection, unbounded backfill, 1-minute historical support, FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio/signal/risk, AI, notification, UI, or automated trading.
- Do not use credentials, tokens, cookies, or private account data.

## Next Step After Execution

After this execution report is written, the next required role is Review Agent. The Review Agent must update `coordination/reviews/TASK-096_REVIEW.md` and decide whether Controller closure is allowed.
