# TASK-031 Review

## Task
- TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_ADAPTER

## Findings
1. [HIGH] Live network-unavailable classification path crashes with `NameError`
- Location: [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:8240)
- In `AkshareETFFundHoldingsAdapter._is_fund_holdings_network_unavailable(...)`, code references `ssl.SSLError` but `ssl` is not imported in this module.
- Impact:
  - When AKShare fetch raises an exception, `_fetch_rows_for_fund_code(...)` calls this classifier.
  - The classifier itself raises `NameError`, breaking the intended "network/proxy/DNS/TLS/upstream unavailability => skip/diagnose" boundary.
  - This violates the handoff requirement to classify environment/source unavailability cleanly for live smoke diagnostics.
- Reproduction evidence (executed during review):
  - `python3 - <<'PY' ... adapter._is_fund_holdings_network_unavailable(OSError(111,'connection refused')) ... PY`
  - Output: `NameError name 'ssl' is not defined`
- Required fix direction:
  - Import `ssl` in `quant/datahub/adapters/akshare.py` (or remove `ssl.SSLError` reference with an equivalent safe check), and add deterministic test coverage that executes this adapter method path directly.

2. [MEDIUM] Test coverage gap on adapter-side unavailability classifier
- Location: [tests/datahub/test_akshare_fund_holdings_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_fund_holdings_live.py:1)
- Current live test file duplicates a local `_is_live_environment_unavailable(...)` helper instead of exercising `AkshareETFFundHoldingsAdapter._is_fund_holdings_network_unavailable(...)`.
- Impact:
  - Adapter classifier defects (like the `ssl` import issue above) can bypass test detection.
- Suggested follow-up (non-blocking once Finding 1 is fixed):
  - Reuse adapter classifier in tests or add dedicated unit tests for the adapter classifier path.

## Scope and Policy Checks
- Phase scope: PASS (changes limited to DataHub + tests + report files).
- Forbidden paths modified: none detected for TASK-031 changed files.
- Default offline behavior: PASS (default live smoke is gated and skipped unless `QUANT_SYSTEM_LIVE_TESTS=1`).
- Source/dataset scope: PASS (`DatasetName.FUND_HOLDINGS`, source `akshare_cn_hk_public_family`, one-symbol boundary implemented).

## Verification Performed
1. `python3 -m unittest tests/datahub/test_akshare_fund_holdings_adapter.py`
- PASS (20 tests)

2. `python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`
- PASS (classifier tests), live smoke skipped by default

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`
- PASS (including live smoke)

4. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- PASS (487 tests, 19 skipped)

5. Related regressions:
- `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py` PASS
- `python3 -m unittest tests/datahub/test_datasets.py` PASS
- `python3 -m unittest tests/datahub/test_source.py` PASS
- `python3 -m unittest tests/datahub/test_source_catalog.py` PASS

6. Additional targeted reproduction:
- Adapter classifier invocation with `OSError(111, ...)` reproduces `NameError: name 'ssl' is not defined`.

## Decision
- CHANGES_REQUESTED

## Follow-up Requirements
- Fix Finding 1 in allowed TASK-031 files and provide updated report evidence.
- Add/adjust deterministic test coverage so adapter-side network-unavailable classification path is directly exercised.
