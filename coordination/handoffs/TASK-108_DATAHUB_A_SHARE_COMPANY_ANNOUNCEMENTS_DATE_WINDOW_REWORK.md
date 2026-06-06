# TASK-108 Rework: DataHub A-share Company Announcements Date-Window Truth

## Task ID

TASK-108

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-108 initial execution hardened A-share company-announcement fetching with bounded multi-symbol requests, optional `source_route` provenance, and gated live PASS evidence while keeping `a_share_company_announcements` conservative at `partial`.

The Review Agent rejected closure in `coordination/reviews/TASK-108_REVIEW.md`.

Blocking findings to address:

1. The live smoke does not assert date-window truth. It builds a bounded request but does not verify that returned announcement dates fall inside the requested window.
2. The fallback date-route path can silently return partial history for a requested window. When the primary route is unavailable, per-day fallback failures classified as upstream/network unavailability are skipped with `continue`, and the adapter only raises if every fallback day fails. This can make a multi-day request succeed with missing days while the implementation/report claim bounded date-window hardening.

This rework is narrow. Do not reopen the whole TASK-108 implementation for unrelated changes.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-108_DATAHUB_A_SHARE_COMPANY_ANNOUNCEMENTS_BREADTH_HISTORY_HARDENING.md`
- `coordination/handoffs/TASK-108_DATAHUB_A_SHARE_COMPANY_ANNOUNCEMENTS_DATE_WINDOW_REWORK.md`
- `coordination/reports/TASK-108_REPORT.md`
- `coordination/reviews/TASK-108_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `tests/datahub/test_akshare_a_share_company_announcements_live.py`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`

## Goal

Make TASK-108 date-window/history truth closure-ready by fixing the two Review findings with minimal implementation and test changes.

Required outcomes:

- The gated live smoke must assert that at least one returned live `COMPANY_ANNOUNCEMENTS` record has a publish date/time inside the exact bounded request window.
- The adapter must not silently present a fallback date-window request as successful when per-day fallback upstream/source availability failures leave part of the requested fallback window unproven.
- Offline tests must regression-protect the selected behavior.
- The report must truthfully state the final live-enabled PASS/SKIP/FAIL result and any remaining fallback/date-window limitation.

## Allowed Files

Execution may create or modify only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py` only if claimed fallback/date-window capability wording must be narrowed
- `tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `tests/datahub/test_akshare_a_share_company_announcements_live.py`
- `tests/datahub/test_source_capabilities.py` only if `source_capabilities.py` changes
- `coordination/reports/TASK-108_REPORT.md`

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

1. Preserve the existing `DatasetName.COMPANY_ANNOUNCEMENTS` contract and existing optional `source_route` behavior unless a test exposes a direct incompatibility from the prior TASK-108 work.
2. Keep default tests offline-safe. No default test may perform real network IO.
3. Keep `symbols=None` or empty symbols as a hard error and keep request breadth bounded.
4. Preserve route-signature, call-compatibility, payload, schema, and normalization defects as hard failures.
5. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`.
6. Fix fallback date-route handling by choosing one explicit truth-preserving behavior:
   - fail or mark the whole requested fallback window unavailable when any required fallback day is unavailable, with root-cause evidence; or
   - narrow the adapter/report/capability wording so fallback coverage is explicitly latest/partial-route limited, and add tests proving this limitation is not represented as full window history.
7. Do not promote `a_share_company_announcements` to `covered`.
8. Do not add credentials, paid/private sources, browser scraping, schedulers/backfills, FeatureHub logic, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Offline Tests

Add or update focused offline tests proving:

- fallback date-route partial upstream/source availability cannot silently satisfy a requested multi-day window as complete history;
- valid fallback/date-window results still sort and validate deterministically where the selected behavior allows success;
- live-unavailable classifier behavior still distinguishes real environment/upstream unavailability from repository-side defects;
- no default test performs network IO.

## Mandatory Live Smoke

Run:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`

The live test must:

- skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1`;
- use no credentials;
- validate at least one live `COMPANY_ANNOUNCEMENTS` record through `DatasetRegistry` when public routes are reachable;
- assert source, market, canonical A-share symbol, `source_route`, and publish-time/date-window behavior;
- explicitly verify returned announcement publish dates are within the bounded request window;
- fail on adapter/schema/normalization/signature defects;
- skip only for genuine environment/upstream/source availability issues, with root-cause evidence.

If the live-enabled run fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will still require fresh Review Agent acceptance.

## Required Test Commands

Run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`

Run if touched:

- `python3 -m unittest tests/datahub/test_source_capabilities.py`

If the implementation touches shared AKShare behavior beyond the company-announcement path, run the narrow related regression tests needed to prove no collateral breakage and document them in the report.

## Report Requirements

Update `coordination/reports/TASK-108_REPORT.md` with:

- files changed in this rework
- implementation summary focused on the Review findings
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- explicit statement of how the live smoke proves date-window truth
- explicit statement of fallback date-route behavior under partial per-day upstream/source availability
- whether `a_share_company_announcements` capability truth changed
- deviations from this handoff
- risks or follow-up tasks
