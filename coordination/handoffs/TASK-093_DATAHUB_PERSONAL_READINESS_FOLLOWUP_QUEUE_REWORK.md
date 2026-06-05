# TASK-093 Rework: DataHub Personal Readiness Follow-Up Queue

Role: 5.3 Execution Window

## Context

TASK-093 remains open. Do not close the task, do not enter Integration, and do not treat the current DataHub phase as complete.

The first TASK-093 gate added a deterministic offline `pass` / `warn` / `blocked` / `fail` DataHub readiness matrix. The current Controller action is a minimal rework dispatch before closure: make the gate's follow-up output concrete enough for Controller to dispatch the next DataHub hardening task without inferring from broad prose.

Review/context findings to address:

- Remaining DataHub domains are still `warn` or `blocked`; DataHub phase closure is not allowed.
- `index_weight_history` must remain `blocked` unless the owner later reopens paid Tushare credentials and a credentialed live smoke records a real PASS.
- Existing follow-up recommendations are broad themes; the gate should expose a stable, structured, Controller-ready queue that maps each non-pass readiness result to the next DataHub-only hardening or blocker disposition.

## Objective

Rework the offline TASK-093 readiness gate so it emits a deterministic structured follow-up queue for every `warn`, `blocked`, or `fail` readiness outcome.

The queue must let Controller answer, without manual interpretation:

- which domain owns the gap
- which status applies: `warn`, `blocked`, or `fail`
- which capability IDs or operational check IDs caused the gap
- why the item is not closure-ready under the Personal Trading Perfection Standard
- what the next executable DataHub handoff theme should be
- whether the item needs code hardening, owner credential/action, or explicit owner waiver before phase closure

## Allowed Writes

Modify only:

- `quant/datahub/personal_readiness.py`
- `quant/datahub/__init__.py` only if export wiring is needed
- `tests/datahub/test_personal_readiness.py`
- `coordination/reports/TASK-093_REPORT.md`

## Forbidden

- Do not modify `quant/features/`, `tests/features/`, Scanner, StrategyLab, BacktestEngine, PortfolioMonitor, SignalEngine, RiskEngine, AI, UI, notification, automated trading, or downstream modules.
- Do not change DataHub source adapters in this rework.
- Do not add paid credentials, private tokens, cookies, or private account data.
- Do not add live tests for this task.
- Do not perform real network calls in default tests or task implementation.
- Do not edit controller-owned coordination state files.
- Do not mark any `partial`, `warn`, or `blocked` capability as phase-complete.

## Implementation Requirements

Keep the implementation offline, deterministic, and small.

Add a stable follow-up representation. A dataclass or similarly typed immutable structure is preferred. Each follow-up item should include, at minimum:

- stable `follow_up_id`
- `domain_id`
- `status`
- one or more `source_check_ids` or `capability_ids`
- concise `reason`
- `next_handoff_theme`
- disposition such as `datahub_hardening`, `owner_credential_blocker`, `owner_waiver_required`, or `contract/source_mapping_repair`

Required behavior:

- `PersonalTradingReadinessReport` must expose the structured queue in deterministic order.
- Existing string follow-up output may remain for compatibility, but tests must cover the structured queue.
- `index_weight_history` must produce a `blocked` follow-up item that clearly requires owner-provided paid credential scope and future credentialed live PASS evidence.
- Warn domains must produce follow-up items tied to their partial capability IDs or quality/coverage checks instead of only broad domain-level prose.
- Any `fail` result from missing contracts, source mappings, registry contracts, information-domain coverage, storage, refresh, quality, or source-health checks must create a repair-oriented follow-up item.
- The default report counts should remain conservative: non-pass domains must not be promoted to `pass`.

## Tests

Run:

- `python3 -m unittest tests/datahub/test_personal_readiness.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`

Do not run live-enabled tests for this rework.

Default tests must remain offline-safe.

## Report Requirements

Rewrite `coordination/reports/TASK-093_REPORT.md` with:

- files changed
- rework summary
- structured follow-up queue schema
- domains covered
- pass/warn/blocked/fail matrix summary
- Controller-ready follow-up queue summary, including the blocked `index_weight_history` item
- tests run
- default network behavior
- live-enabled result: `SKIP`, because TASK-093 forbids live tests
- deviations from the handoff
- risks or follow-up tasks
