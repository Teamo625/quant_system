# TASK-072 Review - DataHub A-share Daily Bars Batch Hardening

## Findings

No blocking findings.

## Decision

ACCEPTED.

The implementation satisfies the handoff by expanding `AkshareAShareDailyBarAdapter` from one-symbol-only behavior to caller-provided multi-symbol batch fetching, while preserving default offline-safe tests and providing live-enabled PASS evidence.

## Scope And Phase Compliance

- Scope compliance: PASS.
- Files changed are within the handoff's allowed write list.
- No downstream modules were touched.
- No controller-owned project state files were changed by the execution window.
- No credentials were used.

## Contract And Behavior Review

- Multi-symbol requests now flow through the existing `SourceRequest.symbols` contract.
- Single-symbol requests remain supported.
- Missing or empty symbol inputs still fail clearly.
- Invalid symbols are validated before source fetch.
- Each requested symbol uses the existing public AKShare daily-bar route.
- Output is normalized to `DatasetName.DAILY_BARS`, deduplicated by `(symbol, trade_date, source)`, and sorted deterministically.
- Existing price-adjustment and date-bound behavior is preserved.

The `a_share_daily_bars` capability promotion to `CapabilityStatus.COVERED` is justified because the specific TASK-071 gap was one-symbol-only access, and TASK-072 now has offline multi-symbol coverage plus live-enabled two-symbol PASS evidence.

## Tests And Network Behavior

Default tests offline-safe: YES.

Reviewed execution evidence:

- `python3 -m unittest tests/datahub/test_akshare_adapter.py`
  - PASS: `Ran 10 tests ... OK`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - PASS: `Ran 18 tests ... OK`
- `python3 -m unittest -v tests/datahub/test_akshare_live.py`
  - PASS with default skip: `OK (skipped=1)`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_live.py`
  - PASS: `test_live_akshare_daily_bars_smoke ... ok`

Live-enabled result: PASS.

No live-network rework is required.

## Closure Readiness

- Controller closure allowed: YES, for TASK-072.
- Phase 2.5 closure allowed: NO.

Reason: TASK-072 closes the A-share daily-bars batch-access gap, but TASK-071 identified many remaining DataHub trading-usable gaps. The controller should dispatch the next DataHub hardening task.

## Follow-Up Recommendation

Dispatch the next DataHub hardening handoff for A-share listing/delisting/ST lifecycle history, because scanner and strategy workflows need reliable exclusion/status data before downstream work can safely consume broad daily bars.
