# TASK-122 Review

## Findings

- Blocking: `FUND_SCALE_SHARE_SNAPSHOT` globally rejects negative `metric_value` via `nonnegative_numeric_fields=("metric_value",)` in [quant/datahub/datasets.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/datasets.py:1325). That is too strict for the contract this handoff asked for, because the task explicitly called out scale/share change as an in-scope example and the capability gap text still frames richer share-change coverage as future work ([handoff](/Users/chenziheng/Documents/量化分析代码/quant_system/coordination/handoffs/TASK-122_DATAHUB_ETF_FUND_SCALE_SHARE_CANONICAL_SCHEMA.md:37), [capability](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/source_capabilities.py:715)). Existing `FUND_FLOW.shares_change` also remains sign-bearing rather than nonnegative-only. As written, the new canonical schema cannot represent valid negative share-change observations, so the contract is not yet safe to treat as the dedicated scale/share fact slice.

## Decision

Rework required before Controller closure.

## Closure Readiness

- Controller closure allowed: No.
- Default tests offline-safe: Yes. Independent rerun of `python3 -m unittest tests.datahub.test_datasets tests.datahub.test_source_capabilities tests.datahub.test_source_catalog` passed, and this task introduced no adapter or live-path changes.
- Live-enabled result: SKIP. No live smoke was required because execution was contract/capability/catalog only; no live rework is needed unless a later handoff changes adapters.
- Phase/scope/contract/test blockers: Scope is clean and focused tests pass, but there is a blocking contract issue: the canonical metric schema currently forbids legitimate negative share-change facts.

## Required Follow-up

- Relax or condition the `metric_value` semantic rule so the canonical dataset can represent negative share-change metrics without weakening validation for inherently nonnegative scale/AUM/share-level metrics.
- Update focused dataset tests to cover the accepted negative-share-change case and any remaining nonnegative-only metric cases.
