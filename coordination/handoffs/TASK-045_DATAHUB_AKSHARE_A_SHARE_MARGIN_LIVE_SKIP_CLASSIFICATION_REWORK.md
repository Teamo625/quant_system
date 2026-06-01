# TASK-045 Rework: A-share Margin Financing/Lending Live Skip Classification

## Task ID

TASK-045

## Rework Handoff

`coordination/handoffs/TASK-045_DATAHUB_AKSHARE_A_SHARE_MARGIN_LIVE_SKIP_CLASSIFICATION_REWORK.md`

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

The initial TASK-045 execution report exists at:

- `coordination/reports/TASK-045_REPORT.md`

The Review Agent wrote:

- `coordination/reviews/TASK-045_REVIEW.md`

Review decision:

- `CHANGES_REQUESTED`

Blocking finding:

- The adapter/live-test unavailable classifiers can incorrectly classify adapter-compatibility errors as live environment/source unavailability because route-name substrings such as `stock_margin_detail_sse` and `stock_margin_detail_szse` are treated as unavailable tokens.
- This can make live-enabled smoke tests `SKIP` on AKShare argument/signature drift or adapter compatibility failures.
- The original handoff requires network/proxy/DNS/TLS/upstream/source availability problems to be skippable, but adapter/schema/normalization issues must remain hard failures.

This rework must fix only that review finding and the minimum tests/report updates needed to prove it.

## Required Reading

The execution window must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-045_DATAHUB_AKSHARE_A_SHARE_MARGIN_FINANCING_LENDING_ADAPTER.md`
- `coordination/reports/TASK-045_REPORT.md`
- `coordination/reviews/TASK-045_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`

Read broader files only if needed to implement the narrow fix or run the permitted tests.

## Goal

Tighten TASK-045 margin financing/lending live unavailable classification so:

- true network/proxy/DNS/TLS/upstream/public-source availability failures can still be classified as live skip diagnostics
- pure adapter compatibility, contract, schema, normalization, or AKShare function argument/signature errors remain hard failures
- live smoke behavior follows the original TASK-045 fail/skip boundary

## Allowed Files

The execution window may create or modify only:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`
- `coordination/reports/TASK-045_REPORT.md`

Do not modify other files unless one of the permitted tests proves that a directly related local test helper must move. If that happens, record the exact reason in the report.

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
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

1. Fix unavailable classification narrowly.
   - Remove route-name-only tokens from unavailable classifiers if they cause adapter/argument errors to be classified as environment/source unavailability.
   - Preserve skip classification for actual network/proxy/DNS/TLS/timeout/upstream/public-source availability failures.
   - Do not hide or downgrade adapter compatibility errors, missing required fields, schema validation failures, normalization errors, or invalid AKShare function call/signature problems.

2. Add regression coverage.
   - Add or update tests proving an error message containing route names such as `stock_margin_detail_sse` or `stock_margin_detail_szse`, when representing an argument/signature/field compatibility issue, is not classified as live environment unavailable.
   - Cover both relevant classification surfaces if they both exist:
     - adapter-side route unavailable classifier
     - live-test skip classifier
   - The regression must fail before the fix and pass after the fix.

3. Preserve the original TASK-045 adapter scope.
   - Do not add a new source route unless required by the classification fix.
   - Do not add cross-source fallback.
   - Do not expand to broad A-share universe ingestion or full-history backfill.
   - Do not change source capability truth or catalog coverage unless directly required by a failing permitted test; this rework is not a capability-expansion task.

4. Update the TASK-045 execution report.
   - Append or revise `coordination/reports/TASK-045_REPORT.md` with a rework section.
   - Include files changed, tests run, default network behavior, live-enabled PASS/SKIP/FAIL result, root-cause evidence if live skip/fail occurs, deviations, and residual risks.
   - Keep the report truthful: if the live-enabled smoke skips or fails because of network/proxy/DNS/TLS/upstream/source availability, say so and include evidence plus feasible fixes attempted.

## Testing Requirements

Run focused tests:

`python3 -m unittest tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`

Run the relevant live-enabled smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`

Run the full DataHub default suite unless an environment problem prevents it:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If shared AKShare classification behavior changes in a way that could affect existing adapters, also run:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

If any command cannot run, record the exact command and reason in `coordination/reports/TASK-045_REPORT.md`.

## Acceptance Criteria

This rework is acceptable when:

- route-name-bearing adapter argument/signature compatibility errors are not classified as live environment/source unavailable
- adapter/schema/normalization issues remain hard failures in live-enabled smoke
- genuine network/proxy/DNS/TLS/timeout/upstream/public-source availability failures can still be reported as explicit live skips
- regression tests cover the review finding
- default tests remain offline-safe
- live smoke is gated by `QUANT_SYSTEM_LIVE_TESTS=1`
- `coordination/reports/TASK-045_REPORT.md` records the rework and test truth
- no forbidden coordination files or future-phase modules are changed by the execution window

## Report Path

`coordination/reports/TASK-045_REPORT.md`

## Review Path

`coordination/reviews/TASK-045_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-045_INTEGRATION.md`
