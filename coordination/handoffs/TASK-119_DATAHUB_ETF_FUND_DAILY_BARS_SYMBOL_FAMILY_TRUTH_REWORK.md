# TASK-119 DataHub ETF/Fund Daily-Bars Symbol-Family Truth Rework

## Role

5.3 Execution Window.

## Context

TASK-119 initial execution attempted to broaden ETF/fund `DatasetName.DAILY_BARS` support from exchange ETF-only behavior to listed ETF plus listed fund/LOF daily-bar support. Review rejected closure.

Review finding:

- Blocking: `AkshareETFDailyBarAdapter` accepts all `16` / `18` / `150` / `501` prefixes as listed-fund daily-bar families, but implementation evidence and tests only prove `161725.FUND_CN` through the LOF route and Sina fallback. This overextends accepted symbol truth beyond proven public-source evidence and conflicts with the conservative boundary from TASK-082.

Controller decision:

- TASK-119 is not closed.
- Do not enter Integration.
- Do not mark TASK-119 Done.
- Dispatch this minimal rework handoff to fix the Review finding only.

## Objective

Resolve the ETF/fund daily-bar symbol-family truthfulness blocker without widening phase scope.

Execution must choose one of these paths:

1. Prefer the minimal conservative fix: narrow accepted listed-fund/LOF symbol-family support to only the actually proven family/path from the initial TASK-119 evidence; or
2. Add explicit route evidence plus offline regression coverage for every newly accepted listed-fund prefix family (`16`, `18`, `150`, `501`) before keeping those prefixes supported.

Either path must keep `fund_daily_bars` conservative and must not promote the capability beyond `partial`.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-119_DATAHUB_ETF_FUND_DAILY_BARS_BREADTH_HISTORY_HARDENING.md`
- `coordination/handoffs/TASK-119_DATAHUB_ETF_FUND_DAILY_BARS_SYMBOL_FAMILY_TRUTH_REWORK.md`
- `coordination/reports/TASK-119_REPORT.md`
- `coordination/reviews/TASK-119_REVIEW.md`
- `coordination/reports/TASK-082_REPORT.md`
- `coordination/reviews/TASK-082_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
- `tests/datahub/test_akshare_etf_daily_bar_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

Read related DataHub tests only if needed to make this focused rework.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
- `tests/datahub/test_akshare_etf_daily_bar_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_akshare_etf_fund_daily_bar*.py` file needed to cover this rework
- `coordination/reports/TASK-119_REPORT.md`

Do not edit controller-owned coordination files, review files, integration files, downstream modules, credentials, or unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not use credentials, tokens, cookies, private account data, paid sources, browser session state, or hidden default live network behavior.

## Rework Requirements

- Keep existing accepted exchange ETF behavior for symbols such as `510300.ETF_CN` and `159915.ETF_CN`.
- Fix the Review blocker by making listed-fund/LOF accepted symbol families match the evidence.
- If narrowing support, make unsupported listed-fund prefixes fail clearly and update capability/catalog wording and tests so the system does not imply all `16` / `18` / `150` / `501` families are proven.
- If keeping all accepted prefixes, add explicit source-route evidence and focused regression tests for each prefix family. The report must name the concrete tested symbol for each prefix and state which route returned schema-valid source-backed daily bars.
- Do not infer broader listed-fund taxonomy from prefix shape alone unless route evidence and tests prove it.
- Preserve `DatasetName.DAILY_BARS` compatibility; do not add NAV, premium/discount, fund-flow, derived feature, or downstream fields.
- Preserve bounded caller-provided requests, deterministic sorting, date-window filtering, invalid range rejection, canonical symbols, `market="CN"`, and clear malformed/unsupported symbol errors.
- Preserve default offline safety and keep live tests explicitly gated.
- Keep live/source classifiers narrow: network/proxy/DNS/TLS/upstream/source unavailability may skip, but repository-side route-signature, schema, payload, normalization, and duplicate-conflict defects must fail.
- Update `coordination/reports/TASK-119_REPORT.md` so it truthfully reflects the final supported symbol families, exact route evidence, tests, live result, and the Review blocker resolution.

## Required Tests

Run at minimum:

- `python3 -m unittest tests/datahub/test_akshare_etf_daily_bar_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`

If a new focused ETF/fund daily-bar test file is added, also run its default/offline path.

Live smoke requirement:

- Because this rework changes or constrains a real-source adapter path, rerun the relevant gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence.
- If live-enabled smoke skips or fails due to network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible; do not close from a bare undocumented skip.

## Completion Report

Update `coordination/reports/TASK-119_REPORT.md` with:

- files changed
- implementation summary
- exact Review finding addressed
- supported ETF/fund daily-bar symbol families after rework
- route/source evidence for every accepted listed-fund family, or explicit unsupported-family behavior
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `fund_daily_bars` capability truth changed
- confirmation that exchange ETF compatibility was preserved
- deviations from this rework handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete only when:

- the Review blocker is fixed by evidence-backed support or conservative rejection,
- accepted symbol-family behavior no longer overclaims unproven listed-fund support,
- default tests remain offline-safe,
- gated live evidence is recorded truthfully,
- `fund_daily_bars` remains conservative unless fully proven, and
- no inactive downstream module behavior is introduced.
