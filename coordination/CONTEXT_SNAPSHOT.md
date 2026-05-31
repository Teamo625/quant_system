# Context Snapshot

Last updated by: 5.5 Controller
Last updated after: TASK-038 closure and TASK-039 dispatch

## Project Role and Scope

This repository is a phased personal quantitative research and signal system focused on A-shares, Hong Kong stocks, ETFs/funds, indices, sectors/concepts, macro data, and policy/news/announcement data.

The only implementation area currently open is DataHub:

- `quant/datahub/`
- `tests/datahub/`

Future modules remain placeholder-only until their phases are explicitly opened by the controller:

- `quant/features/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/scanner/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Default tests must remain offline. For any Phase 2 task that implements a real source adapter or real data-fetching behavior, an explicitly gated live smoke test is mandatory. Live smoke tests must be skipped by default and enabled only by `QUANT_SYSTEM_LIVE_TESTS=1` plus explicit handoff permission.

If a live-enabled smoke fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the controller must keep the task open, dispatch a 5.3 execution rework for diagnosis and feasible code/test/report fixes, and require fresh Review Agent acceptance plus integration before closure.

## Current Phase

Current phase: Phase 2 - DataHub Comprehensive Source Collection.

Phase 2 is not complete.

## Completed Work

### Phase 0

`PHASE-0-INIT` completed the initial coordination baseline.

### Phase 1

Phase 1 completed foundational DataHub preparation:

- `TASK-001`: package skeleton and architecture placeholders
- `TASK-002`: local storage baseline
- `TASK-003`: provider and contract baseline
- `TASK-004`: adjustment/trading-calendar foundations
- `TASK-005`: DataHub quality/reporting baseline

### Phase 2

The original selected-adapter TASK-006 through TASK-009 line was removed after the owner expanded Phase 2 to comprehensive source collection.

Completed Phase 2 tasks after the rescope:

- `TASK-006`: DataHub comprehensive source catalog
- `TASK-007`: expanded domain schema contracts
- `TASK-008`: expanded contract semantic validation
- `TASK-009`: explicit semantic validation rules
- `TASK-010`: semantic rule integrity checks
- `TASK-011`: source adapter contract foundation
- `TASK-012`: AKShare A-share daily bar adapter
- `TASK-013`: AKShare A-share trading calendar adapter
- `TASK-014`: AKShare Hong Kong daily bar adapter
- `TASK-015`: AKShare ETF/fund NAV snapshot adapter
- `TASK-016`: AKShare China index daily bar adapter
- `TASK-017`: AKShare sector daily bar adapter with live-network rework closure and live-enabled PASS evidence
- `TASK-018`: AKShare sector master adapter with live duplicate rework closure and live-enabled PASS evidence
- `TASK-019`: AKShare sector membership adapter with live evidence + live PASS rework closure
- `TASK-020`: AKShare index constituents adapter with live-enabled PASS evidence
- `TASK-021`: AKShare global equity snapshot adapter with live-route rework closure and live-enabled PASS evidence
- `TASK-022`: AKShare news events adapter with live-enabled PASS evidence
- `TASK-023`: HKEX company announcements adapter with symbol-filter rework closure and live-enabled PASS evidence
- `TASK-024`: AKShare China macro adapter with `is_preliminary` rework closure and live-enabled PASS evidence
- `TASK-025`: local refresh metadata and `DATA_QUALITY_REPORT` baseline with offline-only PASS evidence
- `TASK-026`: AKShare A-share `instrument_master` adapter with live-enabled PASS evidence
- `TASK-027`: AKShare A-share `corporate_actions` dividend/corporate-action slice with live-enabled PASS evidence
- `TASK-028`: AKShare A-share `valuation_snapshot` adapter with live-network rework closure and live-enabled PASS evidence; `float_market_cap` is optional to preserve source-truth behavior
- `TASK-029`: AKShare A-share `capital_flow_snapshot` adapter with live-network rework closure and live-enabled PASS evidence; primary AKShare route remains preferred, with bounded one-symbol datacenter fallback only for source/network unavailability
- `TASK-030`: public `POLICY_DOCUMENTS` adapter under `macro_policy_public_sources` with live-enabled PASS evidence
- `TASK-031`: AKShare ETF/fund `FUND_HOLDINGS` one-fund adapter with classifier rework closure and live-enabled PASS evidence
- `TASK-032`: AKShare Hong Kong stock `INSTRUMENT_MASTER` one-symbol adapter with live-enabled PASS evidence
- `TASK-033`: AKShare Hong Kong stock `CORPORATE_ACTIONS` one-symbol dividend/corporate-action adapter with live-enabled PASS evidence
- `TASK-034`: AKShare Hong Kong stock `VALUATION_SNAPSHOT` one-symbol adapter with minimal HK source-catalog alignment and live-enabled PASS evidence
- `TASK-035`: AKShare `FUND_PROFILE` one-fund adapter under `akshare_cn_hk_public_family` with live-enabled PASS evidence
- `TASK-036`: DataHub source catalog implementation reconciliation with offline-only PASS evidence
- `TASK-037`: HKEX Hong Kong `TRADING_CALENDAR` adapter under `hkex_disclosure_and_calendar_family` with live-enabled PASS evidence
- `TASK-038`: AKShare China ETF exchange-traded `DAILY_BARS` adapter under `akshare_cn_hk_public_family` with live-network rework closure and live-enabled PASS evidence

## Active Task

Active task: `TASK-039` - DataHub local warehouse refresh runner.

Handoff:

- `coordination/handoffs/TASK-039_DATAHUB_LOCAL_WAREHOUSE_REFRESH_RUNNER.md`

Expected report:

- `coordination/reports/TASK-039_REPORT.md`

Expected review:

- `coordination/reviews/TASK-039_REVIEW.md`

Expected integration:

- `coordination/integrations/TASK-039_INTEGRATION.md`

TASK-039 scope focus:

- add a local-only DataHub warehouse refresh runner that consumes an adapter plus `SourceRequest`
- fetch through existing `fetch_source_result(...)` and persist normalized records to the curated layer
- persist raw source records to the raw layer using the same local JSONL convention, without inventing a new remote source contract
- write refresh metadata through existing `LocalRefreshQualityHelper`
- emit and persist `DatasetName.DATA_QUALITY_REPORT` records for record count, schema validation, and metadata persistence
- preserve default tests as offline-safe and free of hidden network calls
- do not add live tests or real source calls for this local-only runner task
- do not implement scheduling, broad multi-source orchestration, retries, incremental windows, dependency graphs, strategies, features, scanner, AI, notification, UI, or automated trading
- do not expand to non-DataHub modules

## Phase Gate Decision

After TASK-038 review/integration results, Phase 2 remains open and TASK-038 is controller-closed as Done.

Reason: TASK-038 is accepted, integrated, and counted Done after its explicit live-network rework. The rework report, review, and integration record live-enabled PASS evidence after diagnosing the prior proxy/network skip to `push2his.eastmoney.com` and adding bounded fallback behavior for classified ETF daily-bar source unavailability. Phase 2 still has local-warehouse work beyond source adapter slices: the roadmap requires raw and normalized local persistence, refresh metadata, and data quality checks for collected datasets. Existing storage and quality helpers are present, but no narrow runner currently ties `SourceResult` fetch output to local raw/curated persistence plus metadata and `DATA_QUALITY_REPORT` output.

Controller action taken:

- Phase remains Phase 2.
- TASK-038 is closed as Done.
- TASK-039 DataHub local warehouse refresh runner was dispatched as the next executable task.

Phase switch: NO.

## Coordination Notes

Controller-owned files remain the source of truth for phase and task state:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/CONTEXT_SNAPSHOT.md`

Execution windows must not modify controller-owned files. They should only follow the active handoff and write the required report.

For real-source adapter work, execution windows must keep default tests offline, provide mandatory gated live smoke evidence, and diagnose/fix live blockers within the handoff's allowed files where feasible before review and integration.

For TASK-039 specifically, this is a local-only warehouse runner task. It must not add live tests or perform real network calls. Any adapter used in tests must be a fixture adapter, and default tests should patch network connection helpers where useful to prove the runner is offline-safe.
