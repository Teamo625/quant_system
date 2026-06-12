# TASK-145 Review

## Findings

1. `quant/scanner/runner.py:354` still has a blocking ranking-config normalization gap. `validate_scan_ranking_config(...)` accepts dataclass criterion items inside a mapping payload, but `_normalize_ranking_config(...)` then iterates `payload["criteria"]` and subscripts each item as a mapping at lines 372-381. A caller using `run_scan(..., ranking={"criteria": (RankingCriterion(...),)})` gets a raw `TypeError: 'RankingCriterion' object is not subscriptable` instead of accepted normalization or a controlled `InvalidScanRankingConfigError`. This contradicts the reported clear invalid-input behavior for ranking config and is not covered by [tests/scanner/test_runner.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/scanner/test_runner.py:139), which only covers pure dataclass config and pure dict config.

## Closure Status

- decision: rejected_or_blocked
- controller_closure_allowed: no
- default_tests_offline_safe: yes
- live_enabled_result: SKIP
- rework_required: yes

## Closure Readiness

- Controller should not close TASK-145 yet.
- Default tests are offline-safe, and independent review reruns passed: `test_contracts`, `test_matching`, `test_runner`, `test_personal_readiness`, `test_storage`, and full `tests/scanner` discovery.
- Live-enabled result is `SKIP`, which is acceptable for this local-only Scanner task; no live rework is needed.
- Rework is required for the ranking config normalization/contract gap above, plus a regression test covering mixed mapping-plus-dataclass ranking input. No phase-scope violation or hidden default network behavior was found.
