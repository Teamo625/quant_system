# Context Snapshot

Last updated by: 5.5 Controller
Last updated after: TASK-028 closure and TASK-029 dispatch

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

## Active Task

Active task: `TASK-029` - DataHub AKShare A-share capital flow snapshot adapter.

Handoff:

- `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_SNAPSHOT_ADAPTER.md`

Expected report:

- `coordination/reports/TASK-029_REPORT.md`

Expected review:

- `coordination/reviews/TASK-029_REVIEW.md`

Expected integration:

- `coordination/integrations/TASK-029_INTEGRATION.md`

TASK-029 scope focus:

- keep scope limited to one-symbol A-share capital-flow snapshot records for `DatasetName.CAPITAL_FLOW_SNAPSHOT`
- preserve source id `akshare_cn_hk_public_family`
- recommended primary route is `stock_individual_fund_flow(stock="<6-digit-code>", market="<sh|sz|bj>")`
- supplemental bounded route for turnover is `stock_zh_a_hist(symbol="<6-digit-code>", period="daily", ...)`
- optional bounded northbound route is `stock_hsgt_individual_em(symbol="<6-digit-code>")` only if robust for the requested symbol
- require exactly one requested A-share stock symbol and reject invalid, HK, ETF/fund, index, or ambiguous symbols clearly
- normalize canonical symbols such as `600000.SH`, `000001.SZ`, and `920000.BJ`
- set `market=CN`, `source=akshare_cn_hk_public_family`, `ingested_at`, and `schema_version`
- normalize `trade_date` from source flow date
- populate truthful flow fields without inventing placeholders
- if bounded sources cannot truthfully provide currently required `net_inflow`, `northbound_net_buy`, and/or `turnover_rate`, allow only minimal `DatasetRegistry` optionality hardening for those fields with focused tests and report rationale
- keep `main_net_inflow` required unless source evidence proves the primary route cannot support the task
- support `start_date` / `end_date` filtering after normalized `trade_date`
- preserve duplicate, malformed payload, required-field, optional-field, date, numeric, source-unit, and route-precedence boundaries
- keep default tests offline-safe
- add and truthfully report mandatory gated live smoke (`QUANT_SYSTEM_LIVE_TESTS=1`)
- do not implement HK, ETF, fund, index, policy, valuation, corporate-action, full-market capital-flow, feature, scanner, strategy, AI report, notification, or UI logic
- do not expand to non-DataHub modules

## Phase Gate Decision

After TASK-028 review/integration acceptance, Phase 2 remains open.

Reason: TASK-028 is accepted and integrated, but the current phase still has incomplete required slices after TASK-028, including A-share capital-flow expansion, policy adapters, additional A-share/HK/ETF-fund expansion, additional index/global expansion, and additional local warehouse refresh/quality behaviors.

Controller action taken:

- Phase remains Phase 2.
- TASK-028 is closed as Done.
- TASK-029 AKShare A-share capital flow snapshot adapter was dispatched as the next executable task.

Phase switch: NO.

## Coordination Notes

Controller-owned files remain the source of truth for phase and task state:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/CONTEXT_SNAPSHOT.md`

Execution windows must not modify controller-owned files. They should only follow the active handoff and write the required report.

For real-source adapter work, execution windows must keep default tests offline, provide mandatory gated live smoke evidence, and diagnose/fix live blockers within the handoff's allowed files where feasible before review and integration.
