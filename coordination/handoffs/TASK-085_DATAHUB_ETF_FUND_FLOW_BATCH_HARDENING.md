# TASK-085 DataHub ETF/Fund Flow Batch Hardening

## Role

5.3 Execution Window.

## Context

TASK-084 is closed after accepted Review Agent verification. It hardened ETF/fund holdings from one-fund slices to caller-provided multi-symbol bounded report-period access with gated live PASS evidence. Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`: ETF/fund scale/share, flow, premium/discount, index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver.

This task continues the TASK-071 ETF/fund queue. Existing `FUND_FLOW` coverage is still narrow: the adapter validates a one-fund, one-date public exchange scale/share slice and preserves net-inflow/subscription/redemption optionality. The next executable gap is to harden ETF/fund flow/scale-share source facts to caller-provided multi-symbol bounded date-window behavior while preserving conservative capability truth.

This task must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden AKShare-backed ETF/fund `FUND_FLOW` access from a one-fund, one-date request into deterministic, caller-provided multi-symbol access over bounded trade-date windows for China ETF/fund instruments supported by the existing public exchange scale/share routes.

The adapter should preserve existing one-symbol behavior, reject invalid or unsupported symbols clearly, normalize records to the existing `DatasetName.FUND_FLOW` contract, keep default tests offline-safe, and include gated live smoke evidence that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

This task does not require full-market ETF/fund collection, new dataset contracts, credentialed routes, true net-inflow/subscription/redemption route discovery, premium/discount feature calculation, local warehouse refresh orchestration, or downstream feature/scanner work.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-085_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- unrelated DataHub adapters or tests
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, or private account data.

Do not implement downstream feature calculation, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Extend `AkshareETFFundFlowAdapter` for multiple requested ETF/fund symbols through the existing `SourceRequest.symbols` path.
- Preserve support for exactly one symbol.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently return full-market ETF/fund flow/scale-share tables.
- Validate and normalize ETF/fund symbol formats consistently with existing adapter behavior.
- Accept canonical forms such as `510300.ETF_CN` and supported bare six-digit forms such as `510300` where current local adapter style allows them.
- Reject A-share stock-like, Hong Kong stock, index-like, malformed, ambiguous, missing, and unsupported symbols clearly.
- Support caller-provided multi-symbol requests for supported SSE and SZSE ETF/fund code prefixes, including mixed-exchange batches where both public routes are available.
- Fetch and normalize `DatasetName.FUND_FLOW` rows for every requested valid ETF/fund symbol where the selected public route provides rows.
- Honor `start_date` and `end_date` deterministically as bounded trade-date windows. If an AKShare route only supports a single trade date, iterate or filter in a bounded deterministic way rather than widening to unbounded history.
- Require bounded date windows for all requests; avoid accidental broad history pulls.
- Preserve source-truth optionality for `net_inflow`, `subscription_amount`, `redemption_amount`, and `source_ts`.
- Keep records compatible with `DatasetRegistry.validate_record(DatasetName.FUND_FLOW, ...)`.
- Deduplicate deterministically by at least `(fund_code, trade_date, source)`.
- Sort output deterministically by `fund_code` then `trade_date`.
- If one symbol fails due to invalid input or adapter/schema/normalization behavior, fail clearly rather than returning a partial successful batch.
- If one valid requested fund yields no usable rows while another succeeds for the same bounded window, fail clearly rather than returning a partial successful batch, unless the adapter can classify a source-wide route outage.
- Keep route-name-bearing AKShare argument/signature incompatibility as a hard failure, not a live-unavailable skip.
- Do not change `DatasetName.FUND_FLOW` schema in this task.
- Update only `fund_flow` capability truth if implementation and live evidence justify it. Keep it `partial` unless the adapter demonstrably satisfies the full trading-usable ETF/fund flow breadth/history standard; otherwise refine the gap text conservatively.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_fund_flow_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py`

The live-enabled smoke should validate at least two ETF/fund symbols, such as `510300.ETF_CN` and `159915.ETF_CN`, if the upstream public routes are available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-085_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `fund_flow` capability truth changed
- source route coverage and known ETF/fund flow/scale-share limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- multi-symbol ETF/fund `FUND_FLOW` requests work through the adapter contract in offline tests
- normalized records validate against `DatasetName.FUND_FLOW`
- bounded date-window behavior is deterministic and tested
- invalid, unsupported, or no-row symbols fail clearly before returning partial batch success
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects the actual proven source breadth
