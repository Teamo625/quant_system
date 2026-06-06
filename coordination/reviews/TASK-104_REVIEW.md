# TASK-104 Review

## Findings
- Blocking: the new live-unavailable token expansion will misclassify route-specific contract/normalization failures as environment `SKIP`. Both classifiers now return `True` on a plain repository-side error such as `ValueError("gettopicpreviouspool payload missing latest_price")`, because `gettopicpreviouspool` / `gettopiczbgcpool` were added to broad substring token lists in [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:11346) and [tests/datahub/test_akshare_a_share_limit_up_down_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_a_share_limit_up_down_live.py:44), while the test suite only covers generic proxy and signature cases, not the new route-token regression path ([tests/datahub/test_akshare_a_share_limit_up_down_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_a_share_limit_up_down_live.py:91)). This violates the handoff/AGENTS rule that route-signature/schema/normalization defects must fail rather than downgrade to `SKIP`.

## Decision
- Rework required before Controller closure.
- No phase-scope violation found. File touch set stays inside allowed DataHub/report scope.

## Closure Readiness
- Controller closure allowed: No
- Default tests offline-safe: Yes
- Live-enabled result: PASS independently reproduced with `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`, but rework is still required because skip/fail classification is not truthful for the newly added route tokens.
- Phase/scope/contract/test blockers: Yes
  - contract/test blocker: new `gettopicpreviouspool` / `gettopiczbgcpool` token paths can mask repository defects as environment `SKIP`

## Required Follow-up
- Narrow the live-unavailable classifiers so new route-name tokens do not, by themselves, convert repository-side contract/normalization errors into `SKIP`.
- Add focused regression tests proving messages that mention the new routes but describe payload/schema/normalization defects remain `FAIL`.
