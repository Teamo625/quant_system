# Module Boundaries

## Current Rule

Only DataHub may be implemented in the next phase.

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
- feature calculations outside minimal DataHub validation metadata

## Module Ownership

| Path | Status | Allowed Work |
| --- | --- | --- |
| `quant/datahub/` | Active | Full source collection coverage, data ingestion foundation, and local warehouse |
| `quant/features/` | Placeholder | README or package marker only |
| `quant/strategies/` | Placeholder | README or package marker only |
| `quant/backtest/` | Placeholder | README or package marker only |
| `quant/scanner/` | Placeholder | README or package marker only |
| `quant/portfolio/` | Placeholder | README or package marker only |
| `quant/notification/` | Placeholder | README or package marker only |
| `quant/ai/` | Placeholder | README or package marker only |
| `quant/ui/` | Placeholder | README or package marker only |

## Boundary Enforcement

Any handoff that touches placeholder modules must explain why.

Any execution window that implements logic outside `quant/datahub/` before the phase opens is out of scope and should be rejected by review.
