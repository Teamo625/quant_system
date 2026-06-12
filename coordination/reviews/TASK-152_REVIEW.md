# TASK-152 Review

## Findings

1. `quant/portfolio/contracts.py:336-380` does not reject duplicate symbols inside the caller-provided `updates` iterable for `merge_watchlist_snapshot()` and `merge_holding_snapshot()`. Both helpers materialize a dict keyed by symbol and silently let the last duplicate win, which violates the handoff requirement to validate duplicate symbols in deterministic update/merge helpers. Minimal local repro on this branch shows duplicate `000001` updates are accepted and earlier entries are overwritten instead of raising. `tests/portfolio/test_contracts.py:23-218` exercises duplicate rejection only during snapshot construction, so this missed path is not covered.

## Decision

Rejected pending execution rework. The task is close, but the duplicate-update validation requirement is not fully implemented yet.

## Closure Status

- decision: rejected_or_blocked
- controller_closure_allowed: no
- default_tests_offline_safe: yes
- live_enabled_result: SKIP
- rework_required: yes

## Closure Readiness

- Controller cannot close `TASK-152` yet.
- Default tests are offline-safe.
- Live-enabled result is `SKIP` because this was an explicitly local/offline-only handoff; that is not the blocker.
- Blocking item: phase/scope are fine, but the contract/test surface still misses duplicate-symbol validation for merge/update inputs, so handoff contract coverage is incomplete.
