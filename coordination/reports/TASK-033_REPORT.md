# TASK-033 Report

## Task
- `TASK-033_DATAHUB_AKSHARE_HK_CORPORATE_ACTIONS_ADAPTER`

## Files Changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_hk_corporate_actions_live.py`

## Implementation Summary
- Added `AkshareHKCorporateActionsAdapter` for `DatasetName.CORPORATE_ACTIONS` under source id `akshare_cn_hk_public_family`.
- Scope is strictly one requested HK stock symbol:
  - accepts `00700.HK` and `00700`
  - normalizes symbol to canonical `00700.HK`
  - rejects missing/multiple/malformed/non-HK symbol forms clearly.
- Implemented bounded route strategy:
  - primary: `stock_hk_dividend_payout_em(symbol=<5-digit-code>)`
  - optional fallback (network-unavailable only): `stock_hk_fhpx_detail_ths(symbol=<source-native-code>)`
  - fallback symbol normalization is deterministic and bounded.
- Implemented deterministic normalization to `CORPORATE_ACTIONS` contract:
  - `symbol`, `market=HK`, `event_type=dividend`, `event_date`
  - structured `value` including available source-truth fields (announcement date, fiscal year, distribution type, raw plan text, payout date, register-book period, progress, scrip-dividend flag)
  - safe optional extraction for `cash_dividend_per_share` + `cash_currency` from plan text when pattern is clear
  - deterministic `raw_payload_ref` based on canonical identity + stable row signature hash
  - optional `source_ts` from announcement date
  - `source`, `ingested_at`, `schema_version`.
- Implemented deterministic event-date fallback order:
  1) ex-dividend date (`除净日`/equivalent),
  2) announcement date,
  3) payout date.
- Implemented deterministic `start_date` / `end_date` filtering on normalized `event_date`.
- Implemented duplicate boundaries:
  - benign exact duplicates deduped deterministically
  - conflicting duplicates on same stable identity hard-fail.
- Implemented malformed payload / required-field / date / serializability failure checks with explicit errors.
- Implemented HK corporate-actions live-network unavailability classifier and route-unavailable wrapping for live skip diagnostics.
- Exported adapter in `quant.datahub.adapters` and `quant.datahub` package exports.

## Tests Run

### Focused TASK-033 tests
1. `python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
   - PASS (19 tests)
2. `python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`
   - PASS (3 tests, live smoke skipped by default)
3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`
   - PASS (3 tests, live smoke PASS)

### Related regressions from handoff
4. `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`
   - PASS (20 tests)
5. `python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
   - PASS (19 tests)
6. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
   - PASS (10 tests)
7. `python3 -m unittest tests/datahub/test_datasets.py`
   - PASS (27 tests)
8. `python3 -m unittest tests/datahub/test_source.py`
   - PASS (20 tests)
9. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - PASS (535 tests, 21 skipped)

## Default Network Behavior
- Default test mode remains offline-safe.
- Live network tests are skipped by default and only run when explicitly enabled via `QUANT_SYSTEM_LIVE_TESTS=1`.

## Live-Enabled Result
- Result: **PASS**
- Command:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`
- Evidence:
  - classifier tests PASS
  - live smoke PASS
  - at least one normalized HK `CORPORATE_ACTIONS` record validated by `DatasetRegistry.validate_record(...)`.

## Deviations From Handoff
- None.

## Risks / Follow-up
- Upstream AKShare source vocabulary/format may evolve (especially `分红方案` wording and fallback-route field conventions). Current logic preserves source-truth text and only parses cash fields when pattern is explicit; future source drift should continue to be monitored by live smoke.
- Fallback route is only used when primary route fails for environment/source-availability reasons; it is intentionally bounded and does not expand to broad HK universe ingestion.
