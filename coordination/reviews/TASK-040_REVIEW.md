# TASK-040 Review

## Findings

1. Blocking: `trade_date` validation currently accepts `datetime` values because the check uses `isinstance(payload["trade_date"], date)` in `quant/features/contracts.py:125`. A mapping payload with `trade_date=datetime(2026, 6, 3, 9, 30, 0)` returns `()` from `validate_feature_value_record(...)`, so timestamp-bearing records can pass a contract that declares `trade_date: date`. `tests/features/test_contracts.py` does not cover this negative path, so the gap is unguarded.

## Decision

- REWORK REQUIRED

## Closure Readiness

- Controller closure allowed: No.
- Default tests offline-safe: Yes. Independent verification passed for `python3 -m unittest discover -s tests/features -p 'test_*.py'` and `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`.
- Live-enabled result: SKIP. TASK-040 forbids live tests and introduces no live/network path. Rework is still required for the blocking contract/test issue above.
- Phase/scope/contract/test blockers: Yes. No phase or scope violation found, but there is a contract correctness blocker and a missing regression test for invalid `trade_date` type handling.

## Required Follow-up

- Reject `datetime` for `trade_date` while still accepting plain `date`.
- Add an offline regression test covering the invalid `trade_date=datetime(...)` case.
