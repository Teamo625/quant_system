# TASK-100 REPORT

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
  - `coordination/reports/TASK-100_REPORT.md`

- tests run:
  - `python3 -m unittest tests/datahub/test_datasets.py`
    - PASS (`Ran 42 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py`
    - PASS (`Ran 9 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
    - PASS (`Ran 36 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
    - PASS (`Ran 33 tests ... OK`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS (`OK (skipped=1)`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS (`Ran 3 tests in 7.488s ... OK`)

- default network behavior:
  - Default tests remain offline-safe.
  - The live smoke is still explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - Verified default gating with `env -u QUANT_SYSTEM_LIVE_TESTS ...` -> live smoke skipped.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks:
  - Final truth: PASS.
  - Current rerun on 2026-06-06:
    - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - Result: `Ran 3 tests in 7.488s ... OK`
  - Review-observed failure path:
    - Prior independent review recorded a Baidu-route `requests.exceptions.JSONDecodeError` caused by upstream non-JSON content.
    - This execution did not reproduce that failure on live reruns; current upstream returned usable data.
  - Rework policy:
    - Baidu-route `JSONDecodeError` / equivalent non-JSON upstream responses are now treated as route unavailable in `AkshareAShareValuationSnapshotAdapter._is_baidu_route_shape_unavailable`.
    - That path now bubbles into the existing `RuntimeError("... primary route unavailable ...")` handling instead of surfacing as an uncaught repository FAIL.
    - The live classifier regression now explicitly treats that wrapped primary-route-unavailable case as environment/source unavailability.

- whether the Review-observed Baidu non-JSON failure reproduced:
  - No.
  - I reran the gated live smoke before and after the patch; both live reruns passed in the current environment.

- final classifier/adapter policy for Baidu non-JSON or equivalent upstream responses:
  - Non-JSON / `JSONDecodeError` on the Baidu primary route is classified as upstream/source unavailability for live-smoke truthfulness.
  - Normal repository-side contract/data/schema failures still fail and are not downgraded to `SKIP`.

- evidence that repository-side contract/data/schema failures are not broadly misclassified as environment/source unavailability:
  - Existing regression `test_adapter_does_not_mask_non_network_primary_route_errors` still passes and keeps `ValueError("bad payload")` as a hard failure.
  - Existing live-classifier regression `test_classifier_keeps_contract_failures_as_non_environment_issue` still passes.
  - New regression `test_adapter_classifies_baidu_non_json_responses_as_route_unavailable` proves the new branch is scoped to the non-JSON upstream case.

- confirmation that the previously accepted Baidu/Eastmoney overlap and gap behavior remains intact:
  - Yes.
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py` passed after the rework, including the previously accepted overlap/gap coverage added for TASK-100.
  - No overlap-merging or record-deduplication logic changed in this rework.

- whether normalized successful records validate against `DatasetName.VALUATION_SNAPSHOT`:
  - Yes.
  - The live smoke validates every returned record through `DatasetRegistry.validate_record(...)`, and the live run passed.

- whether `a_share_valuation_history` capability truth changed:
  - No.
  - It remains `partial`.

- deviations:
  - None.

- risks/follow-up:
  - Baidu live availability remains upstream-dependent; future non-JSON responses may still occur, but they should now report truthfully as route-unavailable `SKIP` rather than a misleading `PASS`.
  - This rework does not improve long-history completeness or second-source redundancy, so it must not be treated as capability closure.
