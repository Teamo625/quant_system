# TASK-017: DataHub Sector Live PASS Rework

## Task ID

TASK-017

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-017 implemented `AkshareSectorDailyBarAdapter` for `DatasetName.SECTOR_DAILY_BARS` and completed an initial live-network evidence rework. The latest review still did not accept closure:

- latest review decision: `REWORK_REQUIRED (NOT ACCEPTED FOR CLOSURE)`
- latest integration decision: `NOT_INTEGRATED_FOR_CLOSURE (Blocked by Review Gate)`
- live-enabled command still returns `OK (skipped=1)`:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_live.py`
- observed failing routes include Eastmoney-backed hosts such as:
  - `91.push2his.eastmoney.com`
  - `79.push2.eastmoney.com`
- review now requires the live-enabled sector smoke to reach `PASS` in the current environment before TASK-017 can be accepted for closure.

This rework continues TASK-017 only. It must not expand into sector master, sector membership, scanner, strategy, or future-phase work.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-017_DATAHUB_SECTOR_LIVE_PASS_REWORK.md`
- `coordination/reports/TASK-017_REPORT.md`
- `coordination/reviews/TASK-017_REVIEW.md`
- `coordination/integrations/TASK-017_INTEGRATION.md`

## Goal

Make the TASK-017 live-enabled sector smoke pass in the current environment:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_live.py`

The target result is `OK` with `test_live_akshare_sector_daily_bars_smoke ... ok`, not `OK (skipped=1)`.

If the execution window proves the blocker cannot be fixed within repository code/tests because it requires external network/proxy/TLS policy changes, it must record that truthfully with concrete evidence and operator actions. However, under the current review gate, that result should still be treated as not closure-ready unless the live-enabled smoke reaches `PASS`.

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

## Required Investigation

Continue from the existing evidence in `coordination/reports/TASK-017_REPORT.md`. At minimum, determine and record:

- whether `198.18.0.x` resolution for Eastmoney hosts indicates a local proxy, network appliance, transparent proxy, or DNS interception path
- where proxy behavior is introduced, even when proxy environment variables are unset:
  - shell environment
  - Python/requests environment
  - macOS network proxy settings, if inspectable without exposing secrets
  - DNS resolver behavior
  - transparent gateway behavior, if inferable from probes
- whether direct TLS trust can be made valid in the current Python/runtime environment without committing certificates or secrets
- whether any AKShare sector route can return `DatasetName.SECTOR_DAILY_BARS` compatible daily bars without the blocked Eastmoney hosts
- whether source-native BK identifiers, concept names, industry names, HTTPS endpoints, or HTTP endpoints differ in current live behavior
- whether an adapter-level or live-test route order change can produce a real successful sector daily-bar sample without hiding adapter/schema failures

Do not commit credentials, cookies, proxy secrets, certificates, private account data, or machine-local sensitive configuration.

## Required Rework Behavior

Implement a repository-level fix if feasible. Acceptable fixes include:

- adding a safe fallback route that preserves typed `INDUSTRY:` / `CONCEPT:` semantics and produces valid `DatasetName.SECTOR_DAILY_BARS`
- adding source-native route handling that bypasses a failing name-list endpoint and reaches a working kline endpoint
- adjusting live-smoke candidate order to prefer a route verified to pass in the current environment
- tightening network classification so only true transport/source availability failures can skip
- adding offline regression coverage for any new fallback or route behavior

Do not mask malformed payloads, schema/semantic validation errors, unsupported identifiers, or adapter bugs as live skips.

## Required PASS Evidence

To be closure-ready, the report must include a successful live-enabled run:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_live.py`

Expected closure-ready result:

- `Ran 1 test`
- `OK`
- `test_live_akshare_sector_daily_bars_smoke ... ok`

If this cannot be achieved, record the live result truthfully and state explicitly that TASK-017 remains not closure-ready under the current review gate.

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

Run the gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_live.py`

## Acceptance Criteria

The rework is closure-ready only when:

- default tests remain offline and pass
- live smoke remains skipped by default
- live-enabled sector smoke reaches `PASS` in the current environment
- the report includes the successful live-enabled command output
- any repository-level fix is covered by offline tests
- adapter/data-contract bugs remain hard failures
- no future-phase module contains new logic
- `coordination/reports/TASK-017_REPORT.md` is updated with:
  - files changed
  - tests run
  - default network behavior
  - live-enabled PASS/SKIP/FAIL result
  - root-cause analysis
  - repository-level fix details
  - remaining risks or operator actions

If live-enabled sector smoke remains `SKIP` or `FAIL`, the report must say TASK-017 is not closure-ready under the current review gate.

## Report Path

`coordination/reports/TASK-017_REPORT.md`

## Review Path

`coordination/reviews/TASK-017_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-017_INTEGRATION.md`

## Out of Scope

Everything outside TASK-017 sector live PASS rework is out of scope.
