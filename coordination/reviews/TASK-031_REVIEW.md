# TASK-031 Review (Classifier Rework)

## Task
- TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_CLASSIFIER_REWORK

## Findings
- No blocking findings.
- Previous blocker closure confirmed:
  - `AkshareETFFundHoldingsAdapter._is_fund_holdings_network_unavailable(...)` no longer raises `NameError` on OSError/network classification path.
  - `quant/datahub/adapters/akshare.py` now imports `ssl`, and `ssl.SSLError` branch is executable.
- Required direct classifier coverage confirmed:
  - adapter-side classifier is directly exercised in unit tests for:
    - `OSError(111, ...) -> True`
    - `ValueError("Invalid report_date value") -> False`
    - `ssl.SSLError(...) -> True`
- Live test helper duplication issue addressed:
  - `tests/datahub/test_akshare_fund_holdings_live.py` now uses adapter classifier directly for assertions and skip classification.

## Scope and Policy Checks
- Phase scope: PASS (DataHub adapter/tests/report only).
- Forbidden files: no violations detected in this rework.
- Business scope preservation: PASS (still one-fund `DatasetName.FUND_HOLDINGS`, source `akshare_cn_hk_public_family`).
- Default network behavior: PASS (live test remains gated by `QUANT_SYSTEM_LIVE_TESTS=1`, skipped by default).

## Verification Performed By Review
1. `python3 -m unittest tests/datahub/test_akshare_fund_holdings_adapter.py`
- PASS (23 tests)

2. `python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`
- PASS (classifier tests), live smoke skipped by default

3. Targeted reproduction check:
- `python3 - <<'PY' ... print(adapter._is_fund_holdings_network_unavailable(...)) ... PY`
- Output observed: `True` then `False`
- No exception raised

4. Related regressions:
- `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py` PASS (17)
- `python3 -m unittest tests/datahub/test_datasets.py` PASS (27)
- `python3 -m unittest tests/datahub/test_source.py` PASS (20)
- `python3 -m unittest tests/datahub/test_source_catalog.py` PASS (6)

5. Full default DataHub discovery:
- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- PASS (490 tests, 19 skipped)

6. Mandatory gated live smoke:
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`
- PASS (including live smoke)

## Decision
- ACCEPTED

## Follow-up Requirements
- None blocking for integration.
