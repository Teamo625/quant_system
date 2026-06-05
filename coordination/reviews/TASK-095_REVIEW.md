# TASK-095 Review

## Findings

1. Blocking: supplemental Baidu resumption rows can duplicate a primary Eastmoney `resumption` event instead of merging into one record. In [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:9593), primary rows are keyed with metadata-rich identity fields, and [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:9714) unconditionally appends supplemental `resumption` records whenever `resume_date` exists. If both routes describe the same event, differing optional fields such as `raw_status` or `exchange` prevent deduplication and produce two normalized resumption records for one event. I reproduced this locally with a minimal adapter call returning one Eastmoney `复牌` row plus one matching Baidu row; the adapter returned 2 resumption records for `600000.SH` on `2026-05-30`.
2. Test gap: the live smoke still only checks that the first returned record is schema-valid and does not verify the new Baidu-backed resume path or Baidu/Eastmoney overlap handling, so the new route's claimed live evidence is not regression-protected. See [tests/datahub/test_akshare_a_share_suspension_resumption_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_a_share_suspension_resumption_live.py:119).

## Decision

Rework required. Controller closure is not allowed yet.

## Closure Readiness

- Controller closure allowed: No
- Default tests offline-safe: Yes. I independently verified `python3 -m unittest tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`, `python3 -m unittest tests/datahub/test_source_capabilities.py`, and `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py`; the live file remained default-skipped.
- Live-enabled result: PASS was reported in the execution report, but rework is still required because the merged adapter can emit duplicate resumption events and the new live route behavior is not specifically exercised by automated live coverage.
- Phase/scope/contract/test blockers: Yes. Contract behavior is currently wrong for overlapping resumption events, and coverage is missing for that overlap.

## Required Follow-up

- Merge or suppress supplemental resumption rows when the primary route already yields the same logical resumption event for the same `symbol + start_date + resume_date`.
- Add an offline regression test for primary-plus-supplemental overlapping resumption deduplication.
- Strengthen live smoke only if feasible within the handoff so the new Baidu-backed resume path is actually asserted rather than inferred from a generic non-empty sample.
