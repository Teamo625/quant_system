# Module Boundaries

## Current Rule

Only DataHub Phase 2.5 source-capability work may be implemented in the current phase.

All other modules are placeholders. They may contain README files, interface notes, or empty package markers only. They must not contain business logic.

## Allowed Now

Allowed in Phase 0:

- governance files
- system architecture documents
- module boundary documents
- data contract documents
- coordination files
- placeholder directories
- DataHub task handoff planning

Allowed in Phase 1:

- DataHub local storage foundation
- DataHub schema definitions
- DataHub source adapter interfaces
- DataHub offline fixtures
- DataHub validation utilities
- DataHub CLI or scripts only when explicitly assigned
- DataHub tests that do not use live network by default

Allowed in Phase 2:

- DataHub source catalog and coverage matrix for all required comprehensive Phase 2 data domains
- DataHub source adapters and ingestion helpers only when explicitly assigned
- local raw and normalized DataHub warehouse behavior
- source update metadata and DataHub data quality checks
- live source smoke tests only when explicitly assigned and environment-gated

Allowed in Phase 2.5:

- DataHub trading-grade source capability requirements and gap matrices
- DataHub dataset/source contract extensions needed to make short-term and medium/long-term quant data source access complete
- DataHub source adapters, source capability metadata, source freshness metadata, and ingestion helpers only when explicitly assigned
- batch-capable source interfaces, pagination/limit/rate-limit abstractions, and offline fixture coverage when explicitly assigned
- gated live source smoke tests for real-source work, skipped by default
- no requirement to collect all historical or full-market data locally during this phase

Allowed in Phase 3:

- FeatureHub package and contract foundations
- feature output schemas and validation helpers
- feature calculations only when explicitly assigned by controller handoff
- offline tests that consume DataHub contracts or local fixtures
- no live market data access from FeatureHub

## Not Allowed Yet

Do not implement:

- strategy rules
- stock picking rules
- trading signals
- AI-generated research reports
- push notification delivery
- automated trading
- complex frontend UI
- scanner ranking logic
- backtest execution engine
- portfolio, signal, or risk logic beyond placeholder markers

## Module Ownership

| Path | Status | Allowed Work |
| --- | --- | --- |
| `quant/datahub/` | Active | Phase 2.5 source-capability work and explicitly assigned DataHub tasks |
| `quant/features/` | Planned | FeatureHub contracts and feature work only after Phase 3 is reopened |
| `quant/strategies/` | Placeholder | README or package marker only |
| `quant/backtest/` | Placeholder | README or package marker only |
| `quant/scanner/` | Placeholder | README or package marker only |
| `quant/portfolio/` | Placeholder | README or package marker only |
| `quant/notification/` | Placeholder | README or package marker only |
| `quant/ai/` | Placeholder | README or package marker only |
| `quant/ui/` | Placeholder | README or package marker only |

## Boundary Enforcement

Any handoff that touches placeholder modules must explain why.

Any execution window that implements logic outside `quant/datahub/` before the corresponding phase opens is out of scope and should be rejected by review. FeatureHub work is paused until the controller reopens Phase 3.
