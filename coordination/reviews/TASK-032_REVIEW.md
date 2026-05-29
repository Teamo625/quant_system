# TASK-032 Review

## Task
- TASK-032_DATAHUB_AKSHARE_HK_INSTRUMENT_MASTER_ADAPTER

## Findings
- No blocking findings.
- Implementation matches handoff scope for a narrow one-symbol HK `INSTRUMENT_MASTER` slice:
  - adapter added as `AkshareHKInstrumentMasterAdapter`
  - source route bounded to `stock_hk_security_profile_em(symbol=<single_code>)`
  - one-symbol HK validation and canonicalization (`00700.HK` / `00700`) enforced
  - normalization fields and constants align with contract (`HK`, `stock`, `HKD`, `HKEX`, `9999-12-31`, `is_active=True`, schema from registry)
- Required boundaries are covered by deterministic offline tests:
  - malformed payload, missing required fields, invalid symbol/date/exchange/text, duplicate vs conflicting duplicate, non-stock type filtering, optional `source_ts`, and unexpected source symbol
- Live-gated behavior is compliant:
  - default run skips live smoke unless `QUANT_SYSTEM_LIVE_TESTS=1`
  - enabled live smoke PASS confirmed

## Scope and Policy Checks
- Phase scope: PASS (`quant/datahub/**` and `tests/datahub/**` only for implementation; report file present).
- Forbidden module scope: PASS (no feature/strategy/backtest/scanner/portfolio/notification/ai/ui implementation added).
- Default network behavior: PASS (offline tests remain offline-safe; live test explicitly gated).
- Mandatory live smoke requirement: PASS (enabled run executed and passed).

## Verification Performed By Review
1. `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- PASS (20 tests)

2. `python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`
- PASS (3 tests; live smoke skipped by default)

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`
- PASS (3 tests; live smoke PASS)

4. Code/report consistency spot-check:
- Reviewed `quant/datahub/adapters/akshare.py`, package exports, and both TASK-032 test files against handoff acceptance criteria.
- `coordination/reports/TASK-032_REPORT.md` content is consistent with observed implementation and rerun results.

## Decision
- ACCEPTED

## Follow-up Requirements
- None blocking for integration.
