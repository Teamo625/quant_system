# TASK-100 REVIEW

## Findings

- Blocking: `quant/datahub/adapters/akshare.py:5717`-`5737` combines Baidu and Eastmoney by dropping every primary record on or after the earliest secondary date, and the new regression test at `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py:648`-`715` locks that behavior in. That does not satisfy the handoff requirement to preserve source-truth optionality and fail on conflicting duplicate facts when a second dated route is added. Cross-route disagreements are hidden instead of surfaced, and any dates missing from Eastmoney after its first available day would now be silently lost even if Baidu still had data.

## Decision

- REWORK REQUIRED.

## Closure Readiness

- Controller closure allowed: No.
- Default tests offline-safe: Yes. Independent check passed: `python3 -m unittest tests/datahub/test_datasets.py` and `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py` (`OK`, live smoke skipped by default).
- Live-enabled result: PASS per execution report (`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`), but PASS does not clear the blocking overlap/contract issue above.
- Phase/scope/contract/test blockers: Yes. Scope boundary is respected, but the second-source overlap contract is not fully implemented and lacks regression coverage for conflict or gap handling.

## Required Follow-up

- Rework the Baidu/Eastmoney overlap policy so overlapping dated facts are either preserved distinctly with explicit conflict detection or rejected when incompatible, instead of silently preferring Eastmoney from its first date onward.
- Add offline regression coverage for:
  - overlapping same-date cross-route disagreements
  - secondary-route gaps after its earliest available date
