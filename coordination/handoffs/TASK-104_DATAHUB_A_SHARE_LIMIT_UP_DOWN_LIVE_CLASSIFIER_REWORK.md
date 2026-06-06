# TASK-104 Rework: DataHub A-share Limit-Up/Down Live Classifier Truthfulness

## Task ID

TASK-104

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

The initial TASK-104 execution expanded A-share `DatasetName.LIMIT_UP_DOWN_EVENTS` breadth/history with bounded multi-date iteration and additional Eastmoney route families. Review rejected Controller closure because the new live-unavailable token expansion can misclassify repository-side route contract, payload, schema, or normalization defects as environment `SKIP`.

Blocking Review finding:

- `gettopicpreviouspool` and `gettopiczbgcpool` were added to broad substring unavailable-token lists in both adapter and live test classifier code.
- A repository-side error such as `ValueError("gettopicpreviouspool payload missing latest_price")` can therefore become live-unavailable instead of a hard failure.
- This violates the handoff and `AGENTS.md` rule that route-signature, schema, payload, and normalization defects must fail rather than downgrade to `SKIP`.

This rework is deliberately narrow. Do not rework the broader TASK-104 implementation unless directly required to fix the classifier truthfulness issue.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-104_DATAHUB_A_SHARE_LIMIT_UP_DOWN_BREADTH_HISTORY_HARDENING.md`
- `coordination/handoffs/TASK-104_DATAHUB_A_SHARE_LIMIT_UP_DOWN_LIVE_CLASSIFIER_REWORK.md`
- `coordination/reports/TASK-104_REPORT.md`
- `coordination/reviews/TASK-104_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py` only if adapter-level classifier regression coverage is placed there

## Goal

Fix the TASK-104 live/source-unavailable classifier so the newly added limit-up/down route names do not, by themselves, convert repository-side contract, payload, schema, normalization, or route-signature/call-compatibility defects into environment `SKIP`.

The rework must preserve legitimate `SKIP` classification for genuine network/proxy/DNS/TLS/upstream/source availability failures.

## Allowed Files

Execution may create or modify only:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py` only if needed for focused classifier regression coverage
- `coordination/reports/TASK-104_REPORT.md`

## Forbidden Files

Execution must not modify:

- `AGENTS.md`
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
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

1. Narrow the adapter live-unavailable classifier around `gettopicpreviouspool` and `gettopiczbgcpool` so route-name presence alone is insufficient for `SKIP`.
2. Narrow the live-test classifier consistently with the adapter classifier.
3. Add focused regression tests proving route-name-bearing repository defects remain hard failures, including payload/schema/normalization style messages such as missing required fields.
4. Preserve hard failure behavior for route signature/call-compatibility defects.
5. Preserve `SKIP` behavior only for genuine environment/upstream/source availability failures, including network/proxy/DNS/TLS/connection failures and source unavailable responses.
6. Do not change the `LIMIT_UP_DOWN_EVENTS` dataset contract, route breadth, source capability status, source catalog truth, downstream modules, paid/private sources, or default live-network behavior unless directly necessary for this classifier fix.

## Required Test Commands

Run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`

Run gated live:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`

If the fix touches source capability or catalog metadata despite this rework's narrow goal, stop and document why in the report before running any extra tests required by the touched file.

## Report Requirements

Update `coordination/reports/TASK-104_REPORT.md` with a rework section that includes:

- files changed during the rework
- classifier fix summary
- regression tests added
- tests run and results
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- confirmation that route-name-bearing payload/schema/normalization defects now fail rather than skip
- deviations from this rework handoff
- remaining risks or follow-up tasks
