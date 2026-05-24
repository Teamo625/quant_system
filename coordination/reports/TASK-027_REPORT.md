# TASK-027 Execution Report (DataHub AKShare A-share Corporate Actions Adapter)

## Task

- Task ID: `TASK-027`
- Active Handoff: `coordination/handoffs/TASK-027_DATAHUB_AKSHARE_A_SHARE_CORPORATE_ACTIONS_ADAPTER.md`
- Dataset Scope: `DatasetName.CORPORATE_ACTIONS` (A-share single-symbol dividend slice)
- Module Scope: DataHub only

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_live.py`
- `coordination/reports/TASK-027_REPORT.md`

## Implementation Summary

Implemented `AkshareAShareCorporateActionsAdapter` under source `akshare_cn_hk_public_family`, with strict scope limited to one-symbol A-share dividend/corporate-actions for `DatasetName.CORPORATE_ACTIONS`.

1. Added bounded route behavior:
   - primary route: `stock_dividend_cninfo(symbol="<6-digit-code>")`
   - optional fallback for network-route resilience: `stock_history_dividend_detail(symbol="<6-digit-code>", indicator="分红")`
   - fallback is used only on classified network/source unavailability from primary route

2. Added strict symbol boundary and one-symbol requirement:
   - requires exactly one requested symbol
   - accepts canonical or raw 6-digit forms (e.g. `600000.SH`, `600000`)
   - infers suffix by code prefix:
     - `6xxxxx -> .SH`
     - `0xxxxx/3xxxxx -> .SZ`
     - `4/8/9xxxxx -> .BJ`
   - rejects invalid formats, market-code mismatch, HK/ETF-like invalid prefixes, and index-like `399xxx` values

3. Added deterministic normalization for `CORPORATE_ACTIONS`:
   - fields: `symbol`, `market`, `event_date`, `event_type`, `value`, `raw_payload_ref`, `source`, optional `source_ts`, `ingested_at`, `schema_version`
   - fixed values:
     - `market=CN`
     - `event_type=dividend`
     - `source=akshare_cn_hk_public_family`
   - `event_date` fallback order:
     - ex-dividend/ex-right date (`除权日` / `除权除息日`)
     - record date (`股权登记日`)
     - announcement date (`实施方案公告日期` / `公告日期`)
   - `value` structured payload includes available:
     - cash dividend ratio
     - bonus share ratio
     - transfer share ratio
     - progress/status
     - dividend type
     - report period
     - plan explanation
     - unit metadata (`per_10_shares`, `CNY`)
   - `raw_payload_ref` deterministic hash identity derived from canonical symbol/event_type/event_date and stable serialized source row

4. Added boundary handling:
   - DataFrame-like and list-of-mapping payload support
   - malformed payload and missing required event-date fields hard-fail
   - invalid date/value/non-serializable payload values hard-fail
   - start/end date filtering runs after normalized `event_date`
   - benign exact duplicate rows are deduplicated deterministically
   - conflicting duplicates on same stable identity hard-fail
   - network/proxy/DNS/TLS/upstream/source unavailability is explicitly classified for live diagnostics

5. Exported adapter in:
   - `quant.datahub.adapters.__init__`
   - `quant.datahub.__init__`

## Tests Added or Changed

- Added `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py` (offline deterministic):
  - SourceAdapter compatibility
  - normalization + `DatasetRegistry.validate_record(...)` coverage
  - symbol normalization and rejection boundaries
  - event-date fallback order and date filtering
  - structured `value` population
  - deterministic `raw_payload_ref`
  - duplicate/conflicting duplicate behavior
  - malformed payload/missing required fields/invalid values boundaries
  - network classification behavior boundaries

- Added `tests/datahub/test_akshare_a_share_corporate_actions_live.py`:
  - default skip gate via `QUANT_SYSTEM_LIVE_TESTS`
  - live smoke fetch with bounded symbol sample (`600000.SH`)
  - schema validation and critical normalized-field assertions
  - environment/source unavailability classification to `skipTest(...)`
  - adapter/schema issues remain hard failures

## Tests Run

1. `python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
   - Result: PASS (`Ran 19 tests`)

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`
   - Result: PASS (`Ran 3 tests`, `OK (skipped=1)`)

3. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
   - Result: PASS (`Ran 10 tests`)

4. `python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_adapter.py`
   - Result: PASS (`Ran 21 tests`)

5. `python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_live.py`
   - Result: PASS (`Ran 3 tests`, `OK (skipped=1)`)

6. `python3 -m unittest tests/datahub/test_source.py`
   - Result: PASS (`Ran 20 tests`)

7. `python3 -m unittest tests/datahub/test_quality.py`
   - Result: PASS (`Ran 7 tests`)

8. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - Result: PASS (`Ran 390 tests`, `OK (skipped=15)`)

9. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`
   - Result: PASS (`Ran 3 tests in 0.752s`, `OK`)
   - Note: observed non-blocking `DeprecationWarning` from upstream akshare package importlib-resources usage.

## Default Network Behavior

- Default test runs remain offline-safe.
- New offline adapter tests use injected fixture payload/functions only; no real network calls are required.
- Live smoke test is explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skipped by default.

## Live-Enabled Result (Mandatory)

- Live-enabled status: `PASS`
- Evidence:
  - command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`
  - output tail: `Ran 3 tests in 0.752s`, `OK`

## Deviations From Handoff

- None.

## Risks / Follow-Up

1. Upstream AKShare corporate-actions route schema may evolve (field names, optional columns, or value types), and future source drift should be covered by extending field-key mappings and offline boundary tests together.
2. Fallback route currently activates only for classified network/source unavailability, intentionally preserving contract/normalization failures as hard failures.
3. Live environment intermittency (proxy/DNS/TLS/upstream reachability) remains an external risk; current implementation provides explicit classification and reportable diagnostics.
