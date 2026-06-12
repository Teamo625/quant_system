# TASK-146 Scanner artifact contract repair

## Role

5.3 Execution Window.

## Phase

Phase 4-P Scanner Personal Trading Perfection Re-Review.

## Context

TASK-145 is closed after accepted Review Agent verification of the ranking normalization rework. The final TASK-145 Review allows Controller closure, confirms default Scanner tests are offline-safe, and records live-enabled `SKIP` as correct because Scanner work is local-only.

Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md`. Phase 4-P remains incomplete because the Scanner readiness gate still has one unresolved follow-up batch:

- batch id: `scanner_artifact_contract_repair_batch_01`
- item: `SCN-ART-001`
- disposition: `contract_repair`
- theme: candidate artifact schema and downstream handoff provenance

This is a single-item handoff by design. It falls under the Phase Gate small-handoff exception because persisted artifact schema/provenance and downstream handoff metadata have compatibility blast radius. Do not merge this contract repair with StrategyLab, BacktestEngine, signal, portfolio, risk, AI, notification, UI, automated trading, DataHub, or FeatureHub work.

## Objective

Repair Scanner candidate-list artifact contracts so repeated personal research workflows can reproduce, inspect, and hand off scan results without hidden manual context.

Implement practical, offline-only support for:

- explicit universe snapshot provenance in candidate-list artifacts
- ranking-configuration reproducibility metadata when ranked scans are persisted
- downstream handoff metadata suitable for later StrategyLab/SignalEngine consumers, without implementing those downstream modules
- deterministic manifest serialization and checksum behavior that preserves artifact safety
- readiness-gate truth updates so Phase 4-P can close only if every Scanner capability group is genuinely complete

Keep all behavior local and deterministic. Do not fetch data, read warehouse state, call DataHub or FeatureHub adapters, use credentials, or implement strategy/backtest, signal, portfolio, risk, AI, notification, UI, or automated trading behavior.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-146_SCANNER_ARTIFACT_CONTRACT_REPAIR.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-143_REPORT.md`
- `coordination/reviews/TASK-143_REVIEW.md`
- `coordination/reports/TASK-144_REPORT.md`
- `coordination/reviews/TASK-144_REVIEW.md`
- `coordination/reports/TASK-145_REPORT.md`
- `coordination/reviews/TASK-145_REVIEW.md`
- `quant/scanner/contracts.py`
- `quant/scanner/storage.py`
- `quant/scanner/runner.py`
- `quant/scanner/personal_readiness.py`
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_storage.py`
- `tests/scanner/test_runner.py`
- `tests/scanner/test_personal_readiness.py`

Read `quant/scanner/universe.py`, `quant/scanner/matching.py`, and their tests only if needed to preserve compatibility with universe/ranking outputs already accepted in TASK-144 and TASK-145.

## Allowed Writes

Only:

- `quant/scanner/contracts.py`
- `quant/scanner/storage.py`
- `quant/scanner/runner.py` only for minimal artifact metadata propagation from existing scan execution outputs if required
- `quant/scanner/personal_readiness.py`
- `quant/scanner/__init__.py` only for minimal exports
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_storage.py`
- `tests/scanner/test_runner.py` only if runner metadata propagation is touched
- `tests/scanner/test_personal_readiness.py`
- new focused files under `tests/scanner/` if they keep coverage clearer
- `coordination/reports/TASK-146_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-146_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/features/**`
- `tests/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not fetch live data, call source adapters, read local warehouse state, use credentials, or introduce hidden network behavior.

## Implementation Requirements

Artifact contract repair must:

- preserve existing candidate JSONL row compatibility unless a clearly versioned contract extension is required
- extend manifest or artifact metadata with universe snapshot provenance, including at minimum stable universe identity and snapshot/as-of context sufficient to reproduce a caller-provided scan input
- capture ranking configuration reproducibility when a candidate list contains ranked rows, including criteria feature references, directions, weights, and deterministic ordering assumptions
- add downstream handoff metadata that identifies the artifact purpose, producing Scanner run, schema/manifest versions, and later-consumer context without invoking downstream modules
- keep content checksum deterministic and tied to serialized candidate rows, and keep manifest serialization stable
- preserve overwrite and partial-write safety
- validate malformed or incomplete new metadata with explicit contract errors rather than silent omission
- keep ranked and unranked artifact behavior deterministic and backward-compatible where feasible
- avoid storing credentials, raw private data, live-source state, or any StrategyLab/SignalEngine execution semantics

Readiness update must:

- update `quant/scanner/personal_readiness.py` so `scanner_artifact_contract_repair_batch_01` / `SCN-ART-001` truthfully reflects the new implementation state
- set `phase_closure_ready=true` only if every Scanner capability group is genuinely `pass`
- leave any unresolved artifact limitation as `warn` with a follow-up item instead of over-claiming closure
- ensure the readiness gate reports no remaining follow-up queue or batches only if Phase 4-P is truly closure-ready

## Tests

Required default tests:

- `python3 -m unittest tests.scanner.test_contracts`
- `python3 -m unittest tests.scanner.test_storage`
- `python3 -m unittest tests.scanner.test_runner`
- `python3 -m unittest tests.scanner.test_personal_readiness`
- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`

No live tests are required or allowed. Default tests must remain offline-safe.

## Completion Report

Write `coordination/reports/TASK-146_REPORT.md` with:

- files changed
- implemented artifact contract/provenance metadata
- implemented downstream handoff metadata
- manifest/checksum/compatibility behavior
- readiness-gate updates and whether Phase 4-P is closure-ready
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local Scanner work
- deviations from the handoff
- risks or follow-up tasks
