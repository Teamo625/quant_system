# TASK-098 Report

## files changed
- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_live.py`

## tests run
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest tests/datahub/test_datasets.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py` -> PASS (`live` case skipped by default, classifier tests passed)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py` -> PASS

## default network behavior
- Default/offline suite stays network-safe.
- `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py` uses injected fixtures only.
- `tests/datahub/test_akshare_a_share_corporate_actions_live.py` skips the real-source smoke when `QUANT_SYSTEM_LIVE_TESTS` is unset.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Evidence:
  - Live smoke with `QUANT_SYSTEM_LIVE_TESTS=1` passed end to end.
  - Direct live sample via `AkshareAShareCorporateActionsAdapter` for `600584.SH`, `start_date=2000-01-01`, `end_date=<today>` returned `record_count=18`.
  - Live rights-issue record was normalized from `source_route=stock_allotment_cninfo` with:
    - `event_type=rights_issue`
    - `event_date=2010-10-22`
    - `announcement_date=2010-10-11`
    - `record_date=2010-10-13`
    - `raw_payload_ref=AKCA|600584.SH|rights_issue|2010-10-22|cninfo_rights_issue|...`
  - Live dividend records for the same symbol used `source_route=stock_dividend_cninfo`.
- No network/proxy/DNS/TLS skip occurred in the enabled run.

## corporate-action taxonomy/profile chosen and why
- Kept one canonical dataset: `DatasetName.CORPORATE_ACTIONS`.
- Made event taxonomy explicit at the top level with required `action_family` and `source_route`.
- Added optional top-level `announcement_date`, `record_date`, and `ex_date` so downstream research can use source-backed milestone dates without unpacking opaque nested payloads.
- Preserved event-specific detail in `value`.
- Chosen event families proven by public source:
  - `dividend` / `action_family=dividend_distribution`
  - `rights_issue` / `action_family=rights_issue`
- This is the smallest stable public-source path that makes family semantics explicit without inventing split/consolidation facts.

## public-route investigation result by event family
- Dividend / cash-bonus / bonus-share / transfer-share:
  - Proven via `stock_dividend_cninfo`.
  - Normalized as `event_type=dividend`, `action_family=dividend_distribution`.
  - Distribution components remain explicit in `value.distribution_components`.
- Rights issue:
  - New primary route: `stock_allotment_cninfo`.
  - Reason: public no-credential route, symbol-scoped, supports `start_date`/`end_date`, and exposes source-backed implementation dates/pricing fields.
  - Sina `stock_history_dividend_detail(indicator=配股)` kept as fallback only.
- Split / consolidation:
  - No stable no-credential public route was proven in this task.
  - Not inferred from prices or adjustment factors.

## capability truth changed?
- `a_share_corporate_actions` remains `PARTIAL`.
- Updated truth wording to reflect proven public coverage:
  - dividend/cash-bonus/transfer-share distribution events
  - bounded CNInfo rights-issue implementation events
- No promotion to `COVERED`; split/consolidation and broader family breadth are still incomplete.

## deviations
- None.

## risks/follow-up
- Public-source split/consolidation coverage is still unproven and needs a separate handoff if a stable route is found.
- Dividend primary route is still source-bounded by caller-side filtering rather than native date-window parameters on `stock_dividend_cninfo`.
- Cross-route duplicate reconciliation is still conservative; if future work combines multiple live routes for the same family, route-priority merge rules may need explicit hardening.
