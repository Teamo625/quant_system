# TASK-038 Integration

## Task
- `TASK-038_DATAHUB_AKSHARE_ETF_DAILY_BAR_LIVE_NETWORK_REWORK`

## Inputs Read
- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-038_DATAHUB_AKSHARE_ETF_DAILY_BAR_LIVE_NETWORK_REWORK.md`
- `coordination/reports/TASK-038_REPORT.md`
- `coordination/reviews/TASK-038_REVIEW.md`
- current worktree status and TASK-038 code changes

## Review Decision
- Review result: PASS / Accepted for integration
- Blocking findings: none
- Follow-up requirements: integration may proceed for TASK-038 rework
- Review note: controller closure should still respect `AGENTS.md` live-smoke gate semantics for closure-time truth in the target environment.

## Integration Result
- Integrated the accepted TASK-038 live-network rework by recording this integration pass.
- The reviewed rework is present in the worktree and remains within the Phase 2 DataHub boundary.
- The accepted scope remains limited to AKShare-backed China ETF `DatasetName.DAILY_BARS` behavior with `market=ETF_CN` and `source=akshare_cn_hk_public_family`.
- No architectural direction change was made by integration.
- No controller-owned project state files were edited by this Integration Agent.

## Files Touched By TASK-038 Work
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
- `tests/datahub/test_akshare_etf_daily_bar_live.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-038_REPORT.md`
- `coordination/reviews/TASK-038_REVIEW.md`
- `coordination/integrations/TASK-038_INTEGRATION.md`

## Integrated Behavior Summary
- Preserved `AkshareETFDailyBarAdapter` under the existing AKShare CN/HK public source family.
- Adapter remains constrained to one requested China ETF symbol, `DatasetName.DAILY_BARS`, `market=ETF_CN`, and canonical `XXXXXX.ETF_CN` output symbols.
- Rework keeps `fund_etf_hist_em` as the preferred AKShare route.
- Rework adds bounded fallback to `fund_etf_hist_sina` only for classified route/network/proxy/DNS/TLS/source-unavailability failures.
- Fallback uses deterministic Sina symbol conversion: `5xxxxx -> shxxxxxx`, otherwise `szxxxxxx`.
- Primary-route payload, schema, normalization, malformed data, invalid symbol, invalid date, invalid numeric, and conflicting duplicate errors remain hard failures and do not trigger fallback.
- Normalization still uses the existing `DAILY_BARS` contract and source identity; no placeholder price/volume values are invented.
- Source catalog coverage for `InformationDomain.ETF_FUND_FULL_DATA` includes `DatasetName.DAILY_BARS` for the AKShare source family.
- Default tests remain offline-safe; live smoke remains gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- No broad ETF universe ingestion, non-ETF fund behavior, storage orchestration, trading strategy logic, scanner, AI, notification, UI, or automated trading behavior was added.

## Verification Performed During Integration
- `python3 -m unittest tests/datahub/test_akshare_etf_daily_bar_adapter.py`
  - PASS, 27 tests
- `QUANT_SYSTEM_LIVE_TESTS=0 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`
  - PASS with 1 default-gated live skip
- `python3 -m unittest tests/datahub/test_source_catalog.py`
  - PASS, 6 tests
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`
  - PASS, 1 live-enabled test

## Live Smoke Evidence From Report And Review
- Rework report records pre-change reproduction of the reviewer-side failure as `OK (skipped=1)` caused by `ProxyError` to `push2his.eastmoney.com`.
- Rework report records route diagnosis: `fund_etf_hist_em` failed through Eastmoney in the local environment, while `fund_etf_hist_sina(symbol='sh510300')` returned valid OHLCV plus amount fields.
- Rework report records the implemented repository-level fix: primary Eastmoney route retained, bounded Sina fallback added for classified source unavailability.
- Rework report records mandatory live-enabled status as PASS with command `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`.
- Review independently accepted the rework and records live-enabled PASS.
- Integration independently reran the live-enabled smoke and observed PASS.

## Conflicts Or Gaps
- No TASK-038 rework integration conflicts found.
- No blocking implementation gap was identified by the accepted review.
- Residual external-source risk remains if both Eastmoney and Sina public routes are unavailable in a future environment; the report records this as a follow-up risk rather than a repository defect.
- Workspace note: controller-owned coordination files and `tools/run_agent_pipeline.py` were already modified outside this Integration Agent's allowed integration edit scope according to the provided baseline/current evidence; this integration pass did not alter them.

## State Update Recommendations For Controller
- Mark `TASK-038` as Done / integrated in `coordination/TASK_BOARD.md` if closure-time live-smoke gate evidence remains acceptable.
- Add `TASK-038` to completed Phase 2 work in `coordination/PROJECT_STATE.md` and `coordination/CONTEXT_SNAPSHOT.md`.
- Record that China ETF exchange-traded `DAILY_BARS` coverage now exists under `akshare_cn_hk_public_family`, with deterministic offline tests, a gated live smoke test, and bounded live-network fallback resilience.
- Evaluate `coordination/PHASE_GATE.md` to decide whether Phase 2 is complete.
- If Phase 2 remains open, dispatch the next executable DataHub source-coverage or local-warehouse task.
- If Phase 2 is complete, switch to the next phase and dispatch that phase's first executable task.
