# TASK-017: DataHub Sector Live Network Evidence Rework

## Task ID

TASK-017

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-017 implemented a narrow AKShare-backed China industry/concept `sector_daily_bars` adapter and deterministic offline tests. The first review found the adapter and offline behavior acceptable, but did not accept the task for closure because the explicitly enabled live smoke test skipped due to a network/proxy failure:

- command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_live.py`
- result: `OK (skipped=1)`
- observed root cause: `ProxyError` to Eastmoney path `79.push2.eastmoney.com`
- review decision: `REWORK_REQUIRED (NOT ACCEPTED FOR CLOSURE)`
- integration decision: `NOT_INTEGRATED_FOR_CLOSURE (Blocked by Review Gate)`

Per `AGENTS.md`, a real-source task with a live-enabled network/proxy/DNS/TLS/upstream skip cannot be accepted or closed solely from that skipped result. A 5.3 execution window must perform explicit diagnosis, make feasible repository-level code/test/report improvements, record the current PASS/SKIP/FAIL truthfully, and then send the task through fresh review and integration.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-017_DATAHUB_SECTOR_LIVE_NETWORK_EVIDENCE_REWORK.md`
- `coordination/reports/TASK-017_REPORT.md`
- `coordination/reviews/TASK-017_REVIEW.md`
- `coordination/integrations/TASK-017_INTEGRATION.md`

## Goal

Diagnose and rework the TASK-017 live-enabled sector smoke path. The rework must determine whether the `ProxyError`/Eastmoney availability issue is repository-fixable, implement a feasible fix or guard where practical, and update `coordination/reports/TASK-017_REPORT.md` with fresh evidence.

This is a rework of TASK-017 only. Do not broaden into new sector master/membership adapters, scanner logic, strategy logic, or downstream modules.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py` only if export changes are required by a narrowly scoped fix
- `quant/datahub/__init__.py` only if export changes are required by a narrowly scoped fix
- `tests/datahub/test_akshare_sector_adapter.py`
- `tests/datahub/test_akshare_sector_live.py`
- `tests/datahub/test_source_catalog.py` only if a narrowly scoped catalog assertion must be adjusted
- `coordination/reports/TASK-017_REPORT.md`

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

## Required Diagnosis

Add fresh evidence to `coordination/reports/TASK-017_REPORT.md` for the currently observed live-enabled behavior.

At minimum, diagnose and record:

- proxy-related environment variables with values redacted or shown as `<unset>`:
  - `HTTP_PROXY`
  - `HTTPS_PROXY`
  - `ALL_PROXY`
  - `NO_PROXY`
  - lowercase variants
- DNS resolution for the failing Eastmoney host observed in the live skip, especially `79.push2.eastmoney.com`
- TCP connectivity to `79.push2.eastmoney.com:443`
- TLS/HTTPS behavior for the relevant host or endpoint
- AKShare routing evidence showing which upstream function and host are used for:
  - `stock_board_concept_hist_em`
  - `stock_board_industry_hist_em`
- whether alternative AKShare public sector functions exist in the installed version that can return compatible sector daily bars without the failing Eastmoney path
- a clear attribution judgment:
  - repository adapter/data-contract bug
  - live-test classification bug
  - external network/proxy/source availability issue
  - mixed or uncertain

Do not commit credentials, cookies, proxy secrets, or private account data.

## Required Rework Behavior

If a repository-level fix is feasible, implement it within the allowed files. Examples of feasible fixes include:

- adding a narrowly scoped fallback to another AKShare function/source that preserves typed sector semantics and `DatasetName.SECTOR_DAILY_BARS`
- making live smoke choose the most reliable available industry/concept route while preserving adapter/data-contract failures as failures
- tightening live network-unavailability classification so network/proxy skips are clear but adapter/schema bugs are not masked
- improving adapter exception handling only for true network/source unavailability, without hiding malformed payloads or contract violations

If no repository-level fix is feasible, do not merely repeat that the live test skipped. The report must explain why no safe fallback exists within TASK-017 scope and give concrete operator action, such as outbound network/proxy allowlisting for Eastmoney quote endpoints used by AKShare sector functions.

## Required Test Commands

Default tests must remain offline.

Run:

`python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_sector_live.py`

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run relevant focused regression tests if shared AKShare adapter logic or exports are touched, for example:

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Because this is a real-source live-network rework, run the gated live smoke command:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_live.py`

The live-enabled result must be recorded truthfully as `PASS`, `SKIP`, or `FAIL`.

## Acceptance Criteria

The rework is acceptable when:

- default tests remain offline and pass
- the live smoke remains skipped by default
- the live-enabled sector smoke result is recorded truthfully as `PASS`, `SKIP`, or `FAIL`
- live-enabled network/proxy/DNS/TLS/upstream failures include root-cause evidence, not just a bare skip message
- any feasible repository-level fix or guard is implemented and covered by offline tests
- adapter/data-contract bugs are not hidden behind live skip classification
- no future-phase module contains new logic
- `coordination/reports/TASK-017_REPORT.md` is updated with:
  - files changed
  - tests run
  - default network behavior
  - live-enabled PASS/SKIP/FAIL result
  - root-cause evidence
  - repository-fix feasibility judgment
  - deviations from this rework handoff
  - risks or follow-up operator actions

## Report Path

`coordination/reports/TASK-017_REPORT.md`

## Review Path

`coordination/reviews/TASK-017_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-017_INTEGRATION.md`

## Out of Scope

Everything outside TASK-017 sector live-network diagnosis and feasible repository-level rework is out of scope.
