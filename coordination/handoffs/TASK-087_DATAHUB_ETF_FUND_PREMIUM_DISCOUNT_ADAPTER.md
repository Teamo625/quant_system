# TASK-087 DataHub ETF/Fund Premium-Discount Adapter

## Role

5.3 Execution Window.

## Context

TASK-086 is closed after accepted Review Agent verification. It added the canonical `DatasetName.FUND_PREMIUM_DISCOUNT` contract and mapped `fund_premium_discount` to that dedicated source-fact dataset while keeping capability truth conservative.

Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`: ETF/fund premium-discount source access is not adapter-proven, and index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver.

This task continues the TASK-071 ETF/fund queue. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Implement bounded public AKShare-backed ETF/fund premium-discount source-fact adapter coverage for `DatasetName.FUND_PREMIUM_DISCOUNT`.

The adapter should support caller-provided ETF/fund symbols over bounded trade-date windows, normalize source facts to the existing `FUND_PREMIUM_DISCOUNT` contract, keep default tests offline-safe, and include gated live smoke evidence that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

This task does not require full-market ETF/fund collection, new dataset contracts, credentialed routes, local warehouse refresh orchestration, downstream feature calculation, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_fund_premium_discount_adapter.py`
- `tests/datahub/test_akshare_fund_premium_discount_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-087_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/datasets.py`
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

Do not implement downstream premium/discount feature calculation, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Add a source adapter, using a clear name such as `AkshareETFFundPremiumDiscountAdapter`, for `DatasetName.FUND_PREMIUM_DISCOUNT`.
- Export the adapter from `quant/datahub/adapters/__init__.py` if local adapter export style requires it.
- Use only public no-credential AKShare routes that truthfully provide ETF/fund premium-discount facts or route-local price/NAV/reference-NAV fields sufficient to normalize a premium-discount source fact.
- Do not derive premium-discount by joining unrelated DataHub datasets in this task.
- Preserve source truth. Do not invent prices, NAV, IOPV/reference NAV, rates, or amounts when the source route does not provide them.
- Support `SourceRequest.symbols` with caller-provided ETF/fund symbols.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently return full-market ETF/fund premium-discount tables.
- Accept canonical forms such as `510300.ETF_CN` and supported bare six-digit ETF/fund forms such as `510300` where current local adapter style allows them.
- Reject A-share stock-like, Hong Kong stock, index-like, malformed, ambiguous, missing, and unsupported symbols clearly.
- Require bounded `start_date` and `end_date`; avoid accidental broad history pulls.
- Honor `start_date` and `end_date` deterministically. If a public route supports only one date per call, iterate or filter bounded dates rather than widening the request.
- Normalize records to `DatasetName.FUND_PREMIUM_DISCOUNT` with at least:
  - `fund_code`
  - `market`
  - `trade_date`
  - `premium_discount_rate` or another contract-valid premium/discount metric
  - optional market price / close price when truthfully available
  - optional NAV / IOPV / reference NAV when truthfully available
  - optional `premium_discount_amount` when truthfully available
  - optional route/category/source timestamp fields when useful for source truth
  - `source`
  - `ingested_at`
  - `schema_version`
- Keep records compatible with `DatasetRegistry.validate_record(DatasetName.FUND_PREMIUM_DISCOUNT, ...)`.
- Deduplicate deterministically by at least `(fund_code, trade_date, source, source_route)` when route metadata is available.
- Sort output deterministically by `fund_code` then `trade_date`.
- If one requested symbol is invalid or unsupported, fail clearly rather than returning a partial successful batch.
- If one valid requested fund yields no usable rows while another succeeds for the same bounded window, fail clearly rather than returning a partial successful batch, unless the adapter can classify a source-wide route outage.
- Keep route-name-bearing AKShare argument/signature incompatibility as a hard failure, not a live-unavailable skip.
- Add or update route-unavailability classification narrowly for network/proxy/DNS/TLS/upstream/public-source availability conditions.
- Update source catalog metadata only if needed to reflect the actual public route coverage for `FUND_PREMIUM_DISCOUNT`.
- Update `fund_premium_discount` capability truth only if implementation and live evidence justify it. Keep it `partial` unless the adapter demonstrably satisfies the full trading-usable ETF/fund premium-discount breadth/history standard; otherwise refine the gap text conservatively.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_fund_premium_discount_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest -v tests/datahub/test_akshare_fund_premium_discount_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_premium_discount_live.py`

The live-enabled smoke should validate at least two ETF/fund symbols, such as `510300.ETF_CN` and `159915.ETF_CN`, if the upstream public routes are available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-087_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `fund_premium_discount` capability truth changed
- source route coverage and known ETF/fund premium-discount limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- ETF/fund `FUND_PREMIUM_DISCOUNT` requests work through the adapter contract in offline tests
- normalized records validate against `DatasetName.FUND_PREMIUM_DISCOUNT`
- bounded date-window behavior is deterministic and tested
- invalid, unsupported, or no-row symbols fail clearly before returning partial batch success
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects the actual proven source breadth
