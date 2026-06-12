# TASK-136 DataHub ETF/fund capability cluster hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-135 is closed after accepted Review Agent verification. It resolved the HK minute-bars owner-waiver/blocker disposition by adding a bounded no-credential HK `DatasetName.MINUTE_BARS` path with focused offline tests, default-gated live smoke coverage, live-enabled PASS evidence, and conservative `hk_minute_bars` capability truth.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and unresolved non-pass readiness batches. The current phase must continue with DataHub hardening before FeatureHub or downstream phases reopen.

Controller read DataHub readiness `follow_up_batches`. TASK-131 through TASK-135 covered the A-share batches, the Hong Kong hardening batch, and the adjacent HK minute-bars owner-waiver/blocker batch. The next executable current-phase capability cluster is:

- batch id: `etf_fund__datahub_hardening__etf_fund__batch_01`
- disposition: `datahub_hardening`
- recommended theme: `cluster harden DataHub capabilities: fund_daily_bars, fund_nav, fund_holdings_composition, fund_scale_and_share, fund_flow, fund_premium_discount`

Included follow-up items:

- `etf_fund__etf_fund_capability_readiness__fund_daily_bars`
- `etf_fund__etf_fund_capability_readiness__fund_nav`
- `etf_fund__etf_fund_capability_readiness__fund_holdings_composition`
- `etf_fund__etf_fund_capability_readiness__fund_scale_and_share`
- `etf_fund__etf_fund_capability_readiness__fund_flow`
- `etf_fund__etf_fund_capability_readiness__fund_premium_discount`

This is a coherent ETF/fund cluster because the items share the same domain, no-credential public-source breadth/history/source-redundancy theme, overlapping AKShare adapter/source metadata surface, and downstream DataHub contract consumers. Do not split it into single-item work unless a concrete implementation, schema, live-source, or Review blocker forces a focused rework.

## Objective

Strengthen stable no-credential public-source proof for the ETF/fund batch capabilities where feasible, or truthfully constrain DataHub capability/source wording without promotion when public routes remain incomplete.

The work must address all included capabilities:

- `fund_daily_bars`: broaden or truthfully constrain listed-fund/off-exchange fund daily-bar support, history continuity, route/source truth, and public-route redundancy beyond accepted exchange ETF behavior and the single proven `161725.FUND_CN` listed-fund path.
- `fund_nav`: broaden or truthfully constrain ETF/fund NAV breadth, public-fund class coverage, date-window behavior, and route redundancy beyond accepted exchange ETF plus explicit `FUND_CN` public-fund history coverage.
- `fund_holdings_composition`: broaden or truthfully constrain fund-class support, holdings taxonomy, non-A-share constituent handling, report-period continuity, and public-route redundancy beyond accepted `fund_portfolio_hold_em` proof.
- `fund_scale_and_share`: broaden or truthfully constrain fund-family support, longer scale/share history continuity, scale-unit semantics, bounded request behavior, and independent route redundancy beyond accepted exchange share history plus request-scoped snapshot fallback.
- `fund_flow`: prove richer bounded per-fund dated flow metrics where stable public routes expose them, or keep capability/catalog wording conservative around aggregate-only, status-only, latest-only, and call-incompatible routes.
- `fund_premium_discount`: broaden or truthfully constrain listed-fund/off-exchange premium-discount breadth, historical listed-price plus NAV composite coverage, latest snapshot behavior, and independent direct public-route redundancy.

Keep all ETF/fund capabilities conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source/no-paid personal trading completeness.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-136_DATAHUB_ETF_FUND_CAPABILITY_CLUSTER_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-119_REPORT.md`
- `coordination/reviews/TASK-119_REVIEW.md`
- `coordination/reports/TASK-120_REPORT.md`
- `coordination/reviews/TASK-120_REVIEW.md`
- `coordination/reports/TASK-121_REPORT.md`
- `coordination/reviews/TASK-121_REVIEW.md`
- `coordination/reports/TASK-122_REPORT.md`
- `coordination/reviews/TASK-122_REVIEW.md`
- `coordination/reports/TASK-123_REPORT.md`
- `coordination/reviews/TASK-123_REVIEW.md`
- `coordination/reports/TASK-124_REPORT.md`
- `coordination/reviews/TASK-124_REVIEW.md`
- `coordination/reports/TASK-125_REPORT.md`
- `coordination/reviews/TASK-125_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- relevant ETF/fund DataHub tests listed below

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py` only if an adapter export needs a minimal compatibility update
- `quant/datahub/datasets.py` only if a minimal schema-compatible ETF/fund source-fact clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
- `tests/datahub/test_akshare_etf_daily_bar_live.py`
- `tests/datahub/test_akshare_fund_nav_adapter.py`
- `tests/datahub/test_akshare_fund_nav_live.py`
- `tests/datahub/test_akshare_fund_holdings_adapter.py`
- `tests/datahub/test_akshare_fund_holdings_live.py`
- `tests/datahub/test_akshare_fund_scale_share_adapter.py`
- `tests/datahub/test_akshare_fund_scale_share_live.py`
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- `tests/datahub/test_akshare_fund_premium_discount_adapter.py`
- `tests/datahub/test_akshare_fund_premium_discount_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_akshare_*fund*.py` or `tests/datahub/test_akshare_*etf*.py` file needed for this handoff
- `coordination/reports/TASK-136_REPORT.md`

If a tightly related ETF/fund test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-136_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- unrelated DataHub adapters or tests
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not use credentials, tokens, cookies, browser session state, private account data, paid sources, or hidden default live network behavior.

Do not implement FeatureHub indicators, scanner ranking, strategies, backtests, portfolio/signal/risk logic, AI reports, notifications, UI, or automated trading.

## Implementation Requirements

- Preserve accepted TASK-119 through TASK-125 behavior unless a genuine defect is found.
- Prefer caller-provided, bounded symbol/date/report-period requests. Keep `symbols=None`, unbounded full-market fetches, or full-table snapshot routes out of default behavior unless explicitly bounded, request-scoped, tested, and justified.
- Emit only source-backed facts. Do not invent OHLCV, NAV, holdings, flow, scale/share, premium/discount, source timestamps, route provenance, scale units, holdings taxonomy, or report dates.
- Preserve route/source truth with stable `source_route` or equivalent provenance where records are emitted.
- Route-distinct facts must remain distinguishable when values can differ.
- Honor requested `start_date`, `end_date`, and report-period filters deterministically where the dataset supports them. If a route returns wider history, filter to the requested window.
- Reject malformed, ambiguous, unsupported, A-share stock, Hong Kong stock, index, and unsupported fund/ETF symbols clearly unless a route is explicitly proven to support the requested family.
- If a batch includes one invalid symbol or one repository-side schema/normalization defect, fail clearly rather than returning partial successful output.
- If a valid requested ETF/fund yields no usable rows while another succeeds for the same bounded request, fail clearly unless execution can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, route-signature, call-compatibility, unbounded-fetch, or date-window defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep included ETF/fund capabilities conservative unless full practical public-source breadth, history continuity, and redundancy are genuinely proven.
- If no stable broader no-credential route is feasible for a capability, record attempted route names and observed limitations in the report, add or preserve tests that prevent overclaiming, and leave capability truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_etf_daily_bar_adapter`
- `python3 -m unittest tests.datahub.test_akshare_fund_nav_adapter`
- `python3 -m unittest tests.datahub.test_akshare_fund_holdings_adapter`
- `python3 -m unittest tests.datahub.test_akshare_fund_scale_share_adapter`
- `python3 -m unittest tests.datahub.test_akshare_fund_flow_adapter`
- `python3 -m unittest tests.datahub.test_akshare_fund_premium_discount_adapter`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_etf_daily_bar_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_nav_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_holdings_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_scale_share_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live`
- focused ETF/fund tests for every changed adapter/test file

Live smoke requirement:

- If any real-source ETF/fund path is added or materially changed, run the relevant live smoke once with `QUANT_SYSTEM_LIVE_TESTS=1` when feasible.
- Live smokes must be explicitly gated and skipped by default.
- Live-enabled smoke should validate at least one newly supported or materially changed symbol family, route, or dataset path when upstream routes are available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If a live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-136_REPORT.md` with:

- files changed
- implementation summary by included capability
- selected readiness batch id and included follow-up ids
- ETF/fund route/source-family investigation result
- supported symbol families, market suffixes, date/report-period behavior, source-route truth, and deduplication behavior
- known public-source limitations and why any capability remains conservative
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for each materially changed real-source path
- whether any of the six ETF/fund capability truths changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- The ETF/fund capability cluster has stronger public-source proof or stricter capability/catalog truth for all included follow-up items.
- Any emitted records validate against their dataset contracts.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
- `coordination/reports/TASK-136_REPORT.md` is complete.
