# TASK-063: FeatureHub Output Persistence and Versioning

## Task ID

TASK-063

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 3: FeatureHub

## Context

TASK-062 is accepted by Review and closed by the controller. It completed the pure offline capital-flow primitive slice without changing DataHub or future-phase modules.

This task opens the next narrow FeatureHub foundation slice: local, deterministic persistence/versioning for already-built `FeatureValueRecord` outputs. Do not fetch data, read the DataHub warehouse, rank securities, schedule feature jobs, create scanner behavior, or introduce strategy/backtest/signal/risk/portfolio logic.

The execution window must read:

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-063_FEATUREHUB_OUTPUT_PERSISTENCE_VERSIONING.md`
- `quant/features/contracts.py`
- `quant/features/technical.py`
- `quant/features/valuation.py`
- `quant/features/capital_flow.py`
- `tests/features/test_contracts.py`
- `tests/features/test_technical.py`
- `tests/features/test_valuation.py`
- `tests/features/test_capital_flow.py`

## Goal

Add a small offline FeatureHub persistence/versioning layer for local `FeatureValueRecord` outputs.

## Allowed Files

The execution window may create or modify only:

- `quant/features/**`
- `tests/features/**`
- `coordination/reports/TASK-063_REPORT.md`

Suggested implementation locations:

- `quant/features/storage.py`
- `quant/features/__init__.py`
- `tests/features/test_storage.py`

## Forbidden Files

The execution window must not modify:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

### 1. Pure local feature output persistence

Implement deterministic local persistence helpers for caller-provided `FeatureValueRecord` values.

The slice should include at least:

- serialization of validated `FeatureValueRecord` records to JSON-compatible dictionaries
- deserialization back to `FeatureValueRecord` with validation
- writing records to a local JSONL file
- reading records from a local JSONL file
- optional lightweight manifest or metadata output that records schema version, record count, and feature names present

Keep all behavior pure and local except for explicit file IO requested by the caller. The functions must not import DataHub source adapters, read DataHub warehouse files, call live sources, depend on network access, or introduce orchestration/scheduling.

### 2. Versioning behavior

Persist enough version information for future readers to reject unsupported feature output versions.

At minimum:

- every stored record must preserve `schema_version`
- reads must reject missing, empty, malformed, or unsupported `schema_version`
- reads must reject records that fail `validate_feature_value_record`
- JSON date/datetime encoding must round-trip deterministically

Do not widen the `FeatureValueRecord` contract unless unavoidable. If richer batch/run identity, metric identity, partitioning, or lineage fields are needed, report them as follow-ups instead of widening this slice.

### 3. Input validation and edge cases

Handle edge cases deterministically:

- empty record lists
- invalid record instances or mappings
- unsupported feature names
- unsupported source datasets
- non-finite numeric values
- timestamp-bearing `trade_date` values
- invalid `created_at` values
- malformed JSONL rows
- unsupported schema versions
- parent directory missing or file path already existing, with clear documented behavior

The implementation may raise `ValueError`, `TypeError`, or `FileNotFoundError` for invalid caller input. Prefer the smaller API surface.

### 4. Scope boundaries

Do not implement:

- scanner ranking, candidate selection, or universe logic
- buy/sell signals
- strategy rules
- backtest execution
- portfolio or risk logic
- feature orchestration, scheduling, refresh runners, or dependency graphs
- DataHub source adapters, DataHub warehouse reads, or broad local market collection
- AI reports, notifications, UI, or automated trading

## Testing Requirements

Run focused tests:

`python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run DataHub default regression if the implementation imports DataHub dataset identifiers directly or indirectly:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Default tests must remain offline-safe. No live tests are required or allowed for TASK-063.

## Report Requirements

Write `coordination/reports/TASK-063_REPORT.md` with:

- files changed
- tests run and results
- default network behavior
- live-enabled result as `SKIP` because TASK-063 is not a real-source task and this handoff forbids live tests
- deviations from this handoff
- risks or follow-up tasks

## Acceptance Criteria

The task is acceptable when:

- the storage/versioning module imports cleanly
- deterministic offline tests cover write/read round trips and invalid input/JSONL/version cases
- all persisted and reloaded `FeatureValueRecord` objects pass the existing contract validator
- no DataHub implementation files are changed
- no future phase modules are changed
- default tests remain free of hidden network calls
- report exists at `coordination/reports/TASK-063_REPORT.md`

## Report Path

`coordination/reports/TASK-063_REPORT.md`

## Review Path

`coordination/reviews/TASK-063_REVIEW.md`

## Integration Path

N/A until review acceptance.
