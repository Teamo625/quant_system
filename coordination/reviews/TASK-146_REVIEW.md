# TASK-146 Review

## Findings

- High: Empty ranked scan artifacts cannot be persisted, so the new artifact contract is not actually closure-ready. `run_scan` now always carries `artifact_context.ranking` when a ranking config is supplied ([quant/scanner/runner.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/scanner/runner.py:290)), but storage infers ranked/unranked solely from candidate rows ([quant/scanner/storage.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/scanner/storage.py:305), [quant/scanner/storage.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/scanner/storage.py:333)). A ranked scan that legitimately yields zero candidates therefore raises `ValueError: ... ranking must be omitted for unranked artifacts` during persistence, and the downstream handoff `ranked` flag would also be false. This violates the handoff requirement to preserve ranking reproducibility for persisted ranked scans and makes `phase_closure_ready=true` premature ([quant/scanner/personal_readiness.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/scanner/personal_readiness.py:118), [coordination/reports/TASK-146_REPORT.md](/Users/chenziheng/Documents/量化分析代码/quant_system/coordination/reports/TASK-146_REPORT.md:54)). Coverage missed this boundary: [tests/scanner/test_storage.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/scanner/test_storage.py:213) only exercises ranked persistence with non-empty candidate rows.

## Closure Status

- decision: rejected_or_blocked
- controller_closure_allowed: no
- default_tests_offline_safe: yes
- live_enabled_result: SKIP
- rework_required: yes

## Closure Readiness

- Controller cannot close TASK-146 yet.
- Default tests remain offline-safe. Review reran `python3 -m unittest tests.scanner.test_storage tests.scanner.test_runner tests.scanner.test_contracts tests.scanner.test_personal_readiness` and they passed, but an independent ranked-empty persistence repro failed.
- Live-enabled result is `SKIP`; this is local Scanner work and the handoff forbids live tests.
- Blocking items remain in contract/test readiness: ranked-state derivation must come from ranking metadata/config rather than non-empty candidate rows, and regression coverage must include empty ranked artifact persistence before Phase 4-P closure can be claimed.
