# DataHub

DataHub is the first module allowed for implementation.

Responsibilities:

- collect all required upstream data sources for the expanded research scope:
  - A-share full data
  - Hong Kong stock full data
  - ETF and fund full data
  - index data
  - concise global equity market data
  - industry and concept sector data
  - global and China macroeconomic data
  - policy, news, and announcement data
- normalize symbols, calendars, and schemas
- persist local raw and normalized datasets
- validate data quality
- expose stable outputs to downstream modules

Current status:

- Phase 1 foundation is complete through `TASK-005`
- Phase 2 now targets comprehensive full-domain source collection coverage
- the next active task is `TASK-006`, a code-level comprehensive source catalog and coverage matrix
