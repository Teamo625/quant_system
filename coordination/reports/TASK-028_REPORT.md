# TASK-028 Execution Report (A-share Valuation Live-Network Rework)

## Task

- Task ID: `TASK-028`
- Active Handoff: `coordination/handoffs/TASK-028_DATAHUB_AKSHARE_A_SHARE_VALUATION_LIVE_NETWORK_REWORK.md`
- Dataset Scope: `DatasetName.VALUATION_SNAPSHOT` (A-share one-symbol slice only)
- Module Scope: DataHub only

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
- `tests/datahub/test_datasets.py`
- `coordination/reports/TASK-028_REPORT.md`

## Live Blocker Reproduction (Before Rework)

Reproduced handoff blocker before behavior changes:

- Command:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
- Result:
  - `OK (skipped=1)`
- Skip evidence:
  - `RuntimeError: AKShare A-share valuation market-cap route unavailable: ProxyError ... host='push2.eastmoney.com' ... Unable to connect to proxy ... RemoteDisconnected(...)`

Diagnosis:

1. Core valuation route `stock_zh_valuation_baidu` is reachable in this environment.
2. Skip was caused by supplemental route `stock_individual_info_em` hard-failing on proxy/network to `push2.eastmoney.com`.
3. Adapter design made this supplemental route closure-blocking because `float_market_cap` was required and route failure raised runtime error.

## Rework Summary

Implemented repository-level fixes to remove unnecessary live dependency on blocked supplemental route while preserving source-truth and bounded scope:

1. `float_market_cap` contract optionality hardening (minimal, source-truth aligned):
   - `DatasetName.VALUATION_SNAPSHOT` schema changed:
     - `float_market_cap`: `required=False`
   - Kept required core fields unchanged:
     - `symbol`, `market`, `trade_date`, `pe_ttm`, `pb`, `market_cap`, `source`, `ingested_at`, `schema_version`
   - Preserved existing optionality for:
     - `ps_ttm`, `dividend_yield`

2. Adapter merge/requiredness behavior updated:
   - `AkshareAShareValuationSnapshotAdapter` now requires merged metrics:
     - `pe_ttm`, `pb`, `market_cap`
   - `float_market_cap` is emitted only when truthfully available.
   - No placeholder synthesis is introduced (does not set `float_market_cap = market_cap`).

3. Supplemental route failure no longer blocks valid core record:
   - For network/proxy/DNS/TLS/upstream unavailability on `stock_individual_info_em`, adapter now treats route as unavailable and continues with bounded core valuation data.
   - Non-network contract/normalization errors still fail fast.

4. Supplemental route field handling adjusted:
   - `stock_individual_info_em` metrics are now optional merges:
     - `market_cap` overrides baidu market cap when truthfully present.
     - `float_market_cap` included only if present and valid.
   - Malformed payload boundaries remain hard-fail.

## Test Updates

Updated offline and live tests to align with rework target:

1. `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
   - `float_market_cap` missing no longer treated as failure.
   - Added/updated coverage for:
     - supplemental route network unavailable but valid core record emitted
     - no placeholder emission for `float_market_cap`
     - required core fields still hard-fail when missing at source boundary

2. `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
   - live assertions accept missing `float_market_cap` (when absent), while still requiring numeric core fields.

3. `tests/datahub/test_datasets.py`
   - required-field expectation updated for `VALUATION_SNAPSHOT` (`float_market_cap` removed from required set).

## Tests Run

1. Pre-fix blocker reproduction  
   - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`  
   - Result: `OK (skipped=1)` with `push2.eastmoney.com` proxy failure evidence

2. Focused offline adapter test  
   - `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`  
   - Result: PASS (`Ran 24 tests`)

3. Focused live test (default gate)  
   - `python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`  
   - Result: PASS (`Ran 3 tests`, `OK (skipped=1)`)

4. Gated live smoke after rework  
   - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`  
   - Result: PASS (`Ran 3 tests`, `OK`)

5. Required related regressions  
   - `python3 -m unittest tests/datahub/test_datasets.py` -> PASS (`Ran 27 tests`)  
   - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 6 tests`)  
   - `python3 -m unittest tests/datahub/test_akshare_adapter.py` -> PASS (`Ran 10 tests`)  
   - `python3 -m unittest tests/datahub/test_source.py` -> PASS (`Ran 20 tests`)  
   - `python3 -m unittest tests/datahub/test_quality.py` -> PASS (`Ran 7 tests`)

6. Full DataHub discovery  
   - `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`  
   - Result: PASS (`Ran 417 tests`, `OK (skipped=16)`)

## Default Network Behavior

- Default test runs remain offline-safe.
- New/updated offline tests use fixtures/injected callables only.
- Live tests remain explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.

## Live-Enabled Result (Mandatory)

- Final live-enabled status after rework: `PASS`
- Evidence command:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
- Output tail:
  - `Ran 3 tests ... OK`

## Source-Truth Optionality Rationale

`float_market_cap` was moved to optional because, in the bounded one-symbol valuation slice, truthful acquisition of this field depends on supplemental route availability (`stock_individual_info_em`) that can be externally unavailable (proxy/network/upstream) while core bounded valuation route remains available. Optionality preserves truthful output and avoids placeholder fabrication.

## Deviations From Handoff

- None.

## Risks / Follow-Up

1. If future bounded, stable, no-credential routes can reliably provide `float_market_cap` across target symbols/environments, requiredness can be revisited by controller-governed interface process.
2. Upstream AKShare payload shapes remain drift-prone; current adapter keeps malformed/contract errors as hard failures and network/source availability as classified live diagnostics.
