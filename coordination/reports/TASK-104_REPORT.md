# TASK-104 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- `coordination/reports/TASK-104_REPORT.md`

## classifier fix summary
- Narrowed the A-share limit-up/down live-unavailable classifier for `gettopicpreviouspool` and `gettopiczbgcpool`.
- Route-name presence alone no longer classifies an error as environment/source unavailable.
- These optional-route tokens now require explicit upstream-unavailable context such as `source unavailable`, `route unavailable`, or HTTP/service-unavailable signals before mapping to `SKIP`.
- Existing hard-failure behavior for payload/schema/normalization defects and route-signature/call-compatibility defects is preserved.

## regression tests added
- Adapter classifier regressions for optional-route payload defects, normalization defects, and explicit upstream-unavailable messages.
- Live-test classifier regressions for the same optional-route cases.

## tests run
- `python3 -m unittest tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
  - PASS (`Ran 17 tests ... OK`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`
  - PASS (`Ran 7 tests ... OK (skipped=1)`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`
  - PASS (`Ran 7 tests ... OK`)

## default network behavior
- Default tests remain offline-safe.
- Live network access remains gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.
- No default test path performs real network IO.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: `PASS`
- Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py` passed in the current environment, including the live smoke test.
- Rework root cause addressed: messages such as `gettopicpreviouspool payload missing latest_price`, `gettopiczbgcpool row missing required source field`, and `gettopicpreviouspool invalid latest_price value` now stay hard failures instead of being downgraded to environment `SKIP`.

## deviations
- None.

## risks/follow-up
- This rework did not change the `LIMIT_UP_DOWN_EVENTS` contract, route breadth/history logic, or capability metadata.
- `a_share_limit_up_down` remains whatever prior accepted TASK-104 breadth/history work established; this report only closes the classifier-truthfulness rework scope.
