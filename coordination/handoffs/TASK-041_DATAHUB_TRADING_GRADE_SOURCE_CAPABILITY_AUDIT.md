# TASK-041: DataHub Trading-Grade Source Capability Audit

## Task ID

TASK-041

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

The owner clarified that the intended next milestone is not collecting every data point locally. The milestone is completing the DataHub source-capability layer so the system can access all data domains needed for rigorous short-term and medium/long-term quant research when requested.

Phase 2 is complete for its original approved scope, but many implemented adapters are intentionally narrow source slices, such as one-symbol, one-fund, selected indicators, or single-request refresh. FeatureHub TASK-040 is paused before execution while Phase 2.5 closes the source-capability gap.

The execution window must read:

- `AGENTS.md`
- `docs/01_SYSTEM_ARCHITECTURE.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-041_DATAHUB_TRADING_GRADE_SOURCE_CAPABILITY_AUDIT.md`

## Goal

Create a deterministic DataHub trading-grade source capability audit that makes missing source capabilities explicit and testable before Phase 2.5 adapter implementation begins.

This task should answer, in code and tests:

- what data source capabilities are required for short-term quant analysis
- what data source capabilities are required for medium/long-term quant analysis
- which current DataHub datasets/source families already cover each capability
- which capabilities are only partially covered by current narrow adapters
- which capabilities are missing and need follow-up handoffs

Do not collect full-market or full-history data locally in this task.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-041_REPORT.md`

Suggested implementation locations:

- `quant/datahub/source_capabilities.py`
- `quant/datahub/__init__.py` only if exports are added
- `tests/datahub/test_source_capabilities.py`

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

### 1. Source capability primitives

Add a small deterministic DataHub module that defines source-capability primitives, such as:

- capability id
- capability name
- research horizon: short-term, medium/long-term, or both
- market/domain: A-share, Hong Kong, ETF/fund, index, sector/concept, macro, policy/news/announcement, or source quality
- expected granularity/frequency where relevant
- required/optional status for trading-grade research
- mapped DataHub `DatasetName` contracts where current contracts exist
- mapped source families from the existing source catalog where relevant
- current status: covered, partial, missing, or planned
- gap reason and recommended next handoff theme

Keep this as a planning/capability audit, not a data downloader.

### 2. Required capability coverage

The audit must include at least these capability groups:

- A-share reference/universe, listing/delisting/ST status, trading calendar, suspension/resumption, daily bars, minute bars, adjustment factors, corporate actions, valuation history, capital flow, northbound flow, turnover/liquidity, limit-up/down, margin financing/securities lending, financial statements, financial indicators, announcements, and major activity data where reliable public/commercial sources exist
- Hong Kong stock reference/universe, trading calendar, daily bars, minute bars if available, corporate actions, valuation, announcements/disclosures, financial data, and liquidity/turnover data
- ETF/fund reference, daily bars, NAV, holdings/composition, scale/share, flow, premium/discount, and fund profile
- Index daily bars, constituent history, weight history, rebalance/effective dates, and key China/HK/global benchmarks
- Industry/concept sector classification, membership, historical membership/classification changes, and sector daily bars
- Macro observations, macro indicator definitions, release metadata, policy documents, news events, and company announcements
- Data quality/source health capabilities such as freshness, coverage, source availability, schema validation, and refresh metadata

### 3. Gap checks

Provide helper functions that can answer:

- all required capabilities
- capabilities by research horizon
- capabilities by market/domain
- missing capabilities
- partial capabilities
- capabilities that have no stable `DatasetName` mapping yet
- capabilities that rely on planned or credentialed source families

### 4. Offline tests

Add deterministic tests proving:

- all required capability groups exist
- short-term and medium/long-term horizons both have explicit coverage requirements
- missing and partial capabilities are reported clearly
- existing Phase 2 datasets/source catalog entries are linked where applicable
- no default test performs live network access

### 5. Scope boundaries

Do not implement:

- broad live downloading
- full-market collection
- full-history backfill
- scheduler/orchestration/retry framework
- real feature calculations
- scanner ranking or stock picking
- strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic

## Testing Requirements

Default tests must be offline.

Live tests are forbidden for TASK-041.

Run focused tests:

`python3 -m unittest tests/datahub/test_source_capabilities.py`

Run existing related tests:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run full DataHub default tests:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If any command cannot run, report the exact reason in `coordination/reports/TASK-041_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- a deterministic DataHub source-capability audit exists under `quant/datahub/**`
- the audit distinguishes full, partial, missing, and planned source capabilities
- short-term and medium/long-term quant requirements are both represented
- current Phase 2 catalog/dataset coverage is linked where applicable
- tests validate the capability matrix without live network access
- no data is broadly fetched or collected locally
- no future-phase modules are modified
- report exists at `coordination/reports/TASK-041_REPORT.md`
- report includes files changed, tests run, default network behavior, live-enabled status, deviations, and follow-up tasks

## Report Path

`coordination/reports/TASK-041_REPORT.md`

## Review Path

`coordination/reviews/TASK-041_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-041_INTEGRATION.md`
