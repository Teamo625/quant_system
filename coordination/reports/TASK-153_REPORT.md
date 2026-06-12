# TASK-153 Report

## files changed

- `quant/portfolio/risk_rules.py`
- `tests/portfolio/test_signal_risk.py`
- `coordination/reports/TASK-153_REPORT.md`

## review finding addressed

- Fixed the Review-blocking gap where `ENTER` / `INCREASE` signals without sizing guidance were being evaluated as zero-change risk for exposure and concentration, and could silently pass market lot-size checks.

## exact risk-rule behavior for missing sizing guidance

- For actionable `ENTER` / `INCREASE` signals, if no applicable `PositionSizingRule` / sizing guidance exists:
  - `ExposureRiskRule` now returns `BLOCK` with reason code `exposure_missing_sizing_guidance`.
  - `ConcentrationRiskRule` now returns `BLOCK` with reason code `concentration_missing_sizing_guidance`.
  - `MarketConstraintRiskRule` now returns `BLOCK` with reason code `market_constraint_missing_sizing_guidance` when lot-size evaluation depends on missing sizing guidance.
- Existing behavior is preserved when sizing guidance exists.
- Existing non-actionable/no-new-risk paths continue to avoid this new block path.

## tests run

- `python3 -m unittest tests.portfolio.test_signal_risk` -> PASS (`Ran 8 tests`)
- `python3 -m unittest discover -s tests/portfolio -p 'test_*.py'` -> PASS (`Ran 18 tests`)

## default network behavior

- Offline-safe only.
- No live network calls, warehouse reads, credentials, upstream runtime execution, browser/session state, or hidden clock dependency were added.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence

- `SKIP`
- Root-cause / evidence: this handoff is explicitly local/offline-only and forbids live-enabled tests.

## deviations

- None.

## risks / follow-up

- This rework is intentionally minimal and limited to the Review finding.
- Phase 6 still has the later offline regression batch for conflicting signals, staleness depth, risk-block depth, and lifecycle workflows.
