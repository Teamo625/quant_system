# TASK-031 Report (Classifier Rework)

## Task
- TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_CLASSIFIER_REWORK

## Files Changed
- quant/datahub/adapters/akshare.py
- tests/datahub/test_akshare_fund_holdings_adapter.py
- tests/datahub/test_akshare_fund_holdings_live.py

## Rework Summary
This rework addresses the review/integration blocker for TASK-031 without changing the accepted business scope of the one-fund `FUND_HOLDINGS` adapter.

Implemented fixes:
1. Fixed classifier crash path
- Added module import: `import ssl` in `quant/datahub/adapters/akshare.py`.
- `AkshareETFFundHoldingsAdapter._is_fund_holdings_network_unavailable(...)` now safely evaluates the TLS/network branch that checks `ssl.SSLError` and no longer raises `NameError`.

2. Added direct deterministic adapter-side classifier coverage
- In `tests/datahub/test_akshare_fund_holdings_adapter.py`, added tests that directly call:
  - `adapter._is_fund_holdings_network_unavailable(OSError(111, ...))` => `True`
  - `adapter._is_fund_holdings_network_unavailable(ValueError("Invalid report_date value"))` => `False`
  - TLS-style case with `ssl.SSLError(...)` => `True`
- This directly exercises the adapter classifier path and prevents future false confidence from duplicate external helpers.

3. Removed duplicate-only live test classification logic
- In `tests/datahub/test_akshare_fund_holdings_live.py`, classifier assertions and live-skip decision now use the adapter method directly (`adapter._is_fund_holdings_network_unavailable(...)`) instead of relying on a duplicated local classifier helper.

Scope preservation:
- Adapter business scope remains unchanged:
  - one-fund `DatasetName.FUND_HOLDINGS`
  - source id `akshare_cn_hk_public_family`
  - no expansion to fund profile/universe ingestion or other modules
- No changes were made to future-phase modules.

## Required Reproduction Check
Command:
`python3 - <<'PY'`
`from quant.datahub.adapters.akshare import AkshareETFFundHoldingsAdapter`
`adapter = AkshareETFFundHoldingsAdapter()`
`print(adapter._is_fund_holdings_network_unavailable(OSError(111, "connection refused")))`
`print(adapter._is_fund_holdings_network_unavailable(ValueError("Invalid report_date value")))`
`PY`

Result:
- Output line 1: `True`
- Output line 2: `False`
- No exception raised

## Tests Run

### Focused rework tests
1. `python3 -m unittest tests/datahub/test_akshare_fund_holdings_adapter.py`
- PASS (23 tests)

2. `python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`
- PASS (classifier tests)
- live smoke skipped by default as designed

### Related regressions
3. `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`
- PASS (17 tests)

4. `python3 -m unittest tests/datahub/test_datasets.py`
- PASS (27 tests)

5. `python3 -m unittest tests/datahub/test_source.py`
- PASS (20 tests)

6. `python3 -m unittest tests/datahub/test_source_catalog.py`
- PASS (6 tests)

### Full default DataHub discovery
7. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- PASS (490 tests, 19 skipped)

### Mandatory gated live smoke
8. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`
- PASS
  - classifier tests PASS
  - live smoke PASS

## Default Network Behavior
- Default test mode remains offline-safe.
- Live network remains gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skipped by default.

## Live-Enabled Result
- Result: PASS
- Adapter-side network/source-unavailability classifier no longer crashes and remains available for explicit skip classification when needed.

## Deviations From Handoff
- None.

## Risks / Follow-up
- Upstream AKShare/network behavior may still change over time; current classifier now handles the previously blocking `ssl` path safely.
- Review/integration should verify blocker closure against `TASK-031_REVIEW.md` and `TASK-031_INTEGRATION.md` requirements.
