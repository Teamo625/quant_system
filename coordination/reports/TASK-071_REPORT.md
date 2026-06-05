# TASK-071 Report - DataHub Trading-Usable Gap Audit

## Summary

DataHub is not yet trading-usable under the current `coordination/ROADMAP.md` standard.

The current codebase has broad contracts, source metadata, many bounded adapter slices, offline tests, default-gated live smokes, raw/curated persistence, refresh metadata, and quality-report plumbing. However, most real-source capabilities are still intentionally narrow: one-symbol, one-fund, one-index, one-sector, bounded one-day, bounded route, or limited-history slices. This is enough foundation evidence, but not enough for realistic batch research, scanner preparation, or short/medium-long horizon workflows without ad hoc source patching.

Current deterministic capability matrix from `quant/datahub/source_capabilities.py`:

- `covered`: 11
- `partial`: 42
- `planned`: 1
- `missing`: 1 optional item
- `blocked`: 1 practical paid-credential blocker, represented in code as planned because the bounded adapter exists but credentialed live evidence is absent

## Files Changed

- `coordination/reports/TASK-071_REPORT.md`

No DataHub code, tests, or controller-owned project state files were changed.

## Tests Run

No code tests were required by this audit-only handoff.

I ran a local introspection command only, using `python3`, to count statuses from `DEFAULT_REQUIRED_SOURCE_CAPABILITIES`. It performed no network access.

## Default Network Behavior

Default test behavior remains offline-safe based on the existing gated live-test pattern under `tests/datahub/*_live.py`. This task did not run live tests and did not set live environment variables.

## Live-Enabled Result

`SKIP / not run` because TASK-071 is audit-only and does not permit live-enabled source validation.

## Deviations From Handoff

None.

## Capability Matrix

| Capability group | Status | Evidence | Trading-usable gap |
| --- | --- | --- | --- |
| A-share instrument universe reference | covered | `a_share_universe_reference` is `covered`; TASK-026 accepted `AkshareAShareInstrumentMasterAdapter`; `quant/datahub/adapters/akshare.py` supports symbol filtering after loading exchange lists. | No immediate DataHub hardening gap found for current standard. |
| A-share listing/delisting/ST lifecycle | partial | `a_share_listing_delisting_st_status` is `partial` in `quant/datahub/source_capabilities.py`. | ST history and lifecycle deltas are not fully standardized as first-class history. |
| A-share trading calendar | covered | `a_share_trading_calendar` is `covered`; TASK-013 accepted live evidence. | No immediate DataHub hardening gap found. |
| A-share daily bars | partial | TASK-012 accepted one real-source slice; `AkshareAShareDailyBarAdapter` rejects multi-symbol requests with "currently supports exactly one symbol". | Highest-priority gap: not batch-capable across a research universe. |
| A-share minute bars | partial | TASK-050 accepted `AkshareAShareMinuteBarsAdapter`; adapter is explicitly "bounded one-symbol" and requires one bounded trade date. | Needs batch symbol and wider intraday history/window behavior before short-term research use. |
| A-share corporate actions / adjustment factors | partial | TASK-027 accepted one-symbol dividend/corporate-action coverage; adjustment factors are folded into `CORPORATE_ACTIONS`. | Event-family taxonomy and dedicated adjustment-factor semantics are incomplete. |
| A-share suspension/resumption | partial | TASK-052 added contract; TASK-053 accepted bounded public AKShare slice. | Breadth, exact resumption confirmation, and taxonomy depth remain incomplete. |
| A-share limit-up/down | partial | TASK-047 added contract; TASK-048 accepted bounded one-trade-date pool route. | Needs date-range/breadth history and canonical event coverage. |
| A-share margin financing/lending | partial | TASK-045 accepted one-symbol/date-slice adapter and live rework. | Needs symbol/date breadth and history hardening. |
| A-share valuation history | partial | TASK-028 accepted valuation snapshot adapter; capability notes say snapshot-oriented historical depth is not standardized. | Needs broad valuation history and pagination/date-range hardening. |
| A-share capital flow and northbound flow | partial | TASK-029 accepted one-symbol capital-flow snapshot plus bounded fallback; northbound fields are not guaranteed as a dedicated contract slice. | Needs historical continuity and dedicated northbound-flow profile. |
| A-share financial statements and indicators | partial | TASK-044 accepted one-symbol financial statement/indicator slices. | Needs batch symbols, long-history coverage, and route breadth. |
| A-share announcements and major activity | partial | TASK-046 accepted one-symbol announcements; TASK-049 accepted bounded block-trade route for major activity. | Needs breadth/history and broader activity taxonomy. |
| Hong Kong instrument universe reference | partial | TASK-032 accepted one-symbol HK instrument-master coverage. | Needs broad HK universe and delisting metadata coverage. |
| Hong Kong trading calendar | covered | TASK-037 accepted HKEX trading-calendar adapter with live evidence. | No immediate DataHub hardening gap found. |
| Hong Kong daily bars | partial | TASK-014 accepted narrow HK daily bars; `AkshareHKDailyBarAdapter` rejects multi-symbol requests. | Needs batch HK symbol coverage and source-resilience hardening. |
| Hong Kong minute bars | missing | `hk_minute_bars` is optional and has no stable dataset mapping. | Optional feasibility/contract task only; not a required closure blocker unless owner promotes it. |
| Hong Kong corporate actions / valuation / financial data | partial | TASK-033, TASK-034, and TASK-043 accepted one-symbol HK slices. | Needs event-family depth, history, and batch hardening. |
| Hong Kong announcements/disclosures | covered | `hk_announcements_disclosures` is `covered`; TASK-023 accepted HKEX announcements and symbol-filter rework. | No immediate DataHub hardening gap found. |
| ETF/fund reference and profile | covered | `fund_reference` and `fund_profile_details` are `covered`; TASK-035 accepted fund profile. | No immediate DataHub hardening gap found. |
| ETF/fund daily bars, NAV, holdings, scale/share, flow, premium/discount | partial | TASK-015, TASK-031, TASK-038, and TASK-051 accepted bounded slices. | Needs broader ETF/fund universe, historical continuity, net-inflow/subscription/redemption where available, and explicit premium/discount validation. |
| Index daily bars and benchmark coverage | partial | TASK-016 accepted index bars; global benchmark support remains concise via TASK-021. | Needs broader China/HK/global benchmark universe and batch hardening. |
| Index constituents and rebalance metadata | partial | TASK-020 accepted constituents; rebalance dates are not first-class fields. | Needs historical continuity and explicit rebalance/effective-date metadata. |
| Index weight history | blocked | TASK-056/TASK-057 built and checked bounded Tushare path; TASK-059 report/review show `TUSHARE_TOKEN` unset and no credentialed live PASS. | Paid/private credential gate. Must stay blocked/planned unless owner supplies token or explicitly waives. |
| Sector/concept master | covered | TASK-018 accepted sector master and live duplicate rework. | No immediate DataHub hardening gap found. |
| Sector membership/history/daily bars | partial | TASK-017 and TASK-019 accepted sector quote and membership slices. | Needs classification-version metadata, membership history, and broader quote continuity. |
| Macro observations and indicator definitions | partial | TASK-024 and TASK-054 accepted bounded China macro/public-source reconciliation. | Needs broader indicator coverage, revision history, and release metadata. |
| Policy documents | partial | TASK-030 and TASK-054 accepted public gov.cn metadata coverage. | Needs broader authority coverage, pagination depth, and history. |
| News events | covered | TASK-022 accepted AKShare news events. | No immediate DataHub hardening gap found. |
| Cross-market company announcements | partial | HK coverage is stronger; A-share coverage is one-symbol via TASK-046. | Needs A-share/HK parity and normalization. |
| Source freshness, schema validation, refresh metadata | covered | TASK-025 and TASK-039 accepted quality/refresh/local warehouse plumbing; `source_freshness`, `source_schema_validation`, and `source_refresh_metadata` are `covered`. | No immediate DataHub hardening gap found. |
| Source coverage metadata and availability health | partial | `source_coverage_metadata` and `source_availability_health` are `partial`. | Needs first-class coverage KPIs and source health/failure-state records. |

## Paid / Private Credential Blockers

- `index_weight_history`: blocked on a valid `TUSHARE_TOKEN`. The repository has a bounded Tushare adapter and gated live smoke, but TASK-056, TASK-057, and TASK-059 all record that no credentialed live PASS validated a schema-valid `DatasetName.INDEX_WEIGHT_HISTORY` record. The owner previously directed skipping the paid-token path for now, so this must remain a blocked follow-up and must not block no-paid-credential DataHub hardening if explicitly waived.

## Risks And Follow-Up Tasks

1. Batch and parameterized access is the largest systemic gap. `SourceRequest.symbols` supports a sequence, but many real adapters intentionally reject multi-symbol inputs or require one bounded date. That prevents realistic universe-level DataHub usage.
2. Most `partial` statuses have valid live smoke evidence for narrow slices, but that evidence should not be read as trading-usable breadth.
3. Historical continuity is weaker than point-in-time/snapshot coverage across valuation, capital flow, financials, index constituents, sector membership, fund NAV/holdings/flow, macro, and policy.
4. Source availability diagnostics exist through errors, live-skip classifiers, refresh metadata, and quality reports, but source health is not yet a first-class dataset section with standardized failure states.
5. The optional HK minute-bars gap is missing a contract and should remain optional unless the owner says HK intraday is required.

## Prioritized DataHub Hardening Queue

1. `TASK-072`: A-share daily bars batch and parameterized access hardening. This is the highest-leverage gap because downstream FeatureHub, Scanner, strategy research, and liquidity/turnover features all depend on broad daily bar access.
2. A-share instrument lifecycle/ST/listing status history hardening. This prevents downstream scans from including invalid, delisted, or special-treatment names without manual filtering.
3. A-share valuation/capital-flow/financial-history batch hardening. These feed medium/long-term scoring, valuation features, and factor research.
4. A-share minute bars date-window/batch expansion. Needed for short-term research, but less foundational than daily bars.
5. HK daily bars and HK universe breadth hardening. Needed before HK scanner/backtest work is trading-usable.
6. ETF/fund daily/NAV/holdings/flow breadth and history hardening.
7. Index constituent history/rebalance metadata and benchmark universe expansion.
8. Sector membership history/classification versioning and sector daily-bar continuity.
9. Macro/policy breadth, release metadata, and revision history.
10. Source coverage KPI and availability-health schema/report hardening.
11. Blocked paid credential follow-up: Tushare `INDEX_WEIGHT_HISTORY` credentialed live PASS, only after owner supplies a valid token or waives this capability.

## Recommended Next Execution Handoff

Proposed task id/title:

- `TASK-072 DataHub A-share daily bars batch access hardening`

Objective:

- Expand the existing A-share daily bars DataHub capability from a one-symbol adapter slice to practical, parameterized, batch-capable public-source access over multiple requested A-share symbols and bounded date ranges, while keeping default tests offline-safe and live smoke gated.

Allowed implementation files:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_adapter.py`
- `tests/datahub/test_akshare_live.py`
- optionally `tests/datahub/datahub_fixtures.py` if shared offline fixtures need narrow additions
- `coordination/reports/TASK-072_REPORT.md`

Likely tests:

- Focused offline tests proving:
  - multiple requested A-share symbols are accepted and normalized
  - output is deterministically sorted and deduplicated by symbol/date/source
  - unsupported symbols still fail clearly
  - date bounds are respected
  - one-symbol behavior remains backward compatible
- Default-gated live test path proving it skips without `QUANT_SYSTEM_LIVE_TESTS=1`.
- Explicit live-enabled smoke, if controller permits, proving at least two A-share symbols can be fetched and schema-validated from the real public source without changing default offline behavior.

Why this is highest priority:

- Daily bars are the base dependency for price/volume features, turnover/liquidity calculations, universe scans, starter strategy research, and later backtest replay. The current implementation has accepted source evidence but still rejects multi-symbol requests. Hardening this first reduces the largest mismatch between the existing DataHub foundation and the trading-usable completion standard.
