# TASK-094 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-094_REPORT.md`

## tests run
- `python3 -m unittest tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py` -> PASS in this shell because inherited `QUANT_SYSTEM_LIVE_TESTS='1'`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py` -> PASS, live smoke `SKIP (disabled)`; confirms code remains default-offline
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py` -> PASS

## default network behavior
- Default/unit adapter and capability tests remain offline-only.
- Live smoke file is still environment-gated via `QUANT_SYSTEM_LIVE_TESTS == "1"`.
- This execution shell already had `QUANT_SYSTEM_LIVE_TESTS='1'`, so the handoff’s plain `python3 -m unittest -v ...live.py` command executed live instead of skipping.
- Extra verification with `env -u QUANT_SYSTEM_LIVE_TESTS ...` showed the live smoke is skipped when the env var is absent.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py`
- Evidence:
  - live smoke returned normalized records for `000001.SZ`
  - live smoke also verified an SSE lifecycle sample from `stock_info_sh_delist()` with both `listing_suspended` and `delisted` records present
  - full live test file result: `Ran 4 tests ... OK`

## source routes investigated and route-level findings
- `stock_info_sh_delist(全部)`: stable public route; exposes `公司代码/上市日期/暂停上市日期`; implemented as source-backed `listing_suspended` lifecycle evidence while preserving existing `delisted` output for continuity with prior behavior.
- `stock_info_sz_delist(暂停上市公司)`: callable and no-credential; current live result was empty `(0, 0)`; adapter now supports it if future rows appear, emitting `listing_suspended` only when dated rows exist.
- `stock_info_sz_delist(终止上市公司)`: stable public route; still used for dated SZ terminal delisting records.
- `stock_info_sz_change_name(简称变更)`: still the only dated public route found for SZ ST/*ST transition deltas.
- `stock_info_change_name(symbol=...)`: investigated from local AKShare source; provides former names without reliable event dates, so not used for historical continuity.
- `stock_zh_a_st_em` / `stock_zh_a_stop_em`: investigated from local AKShare source and live probe; both hit Eastmoney `ProxyError` in this environment and are current-only snapshots, so they were not integrated into dated continuity logic.

## capability truth changes
- `a_share_listing_delisting_st_status` remains `partial`.
- Wording updated to acknowledge dated suspension-to-delist lifecycle evidence where public exchange tables expose it.
- No promotion to `covered`.

## remaining public-source limitations
- Full dated ST/*ST continuity is still not available from stable public no-credential routes.
- SH public route still exposes `暂停上市日期` rather than a distinct terminal delist date.
- SZ pause-lifecycle route is currently empty, so broader dated pause/resume breadth remains unproven.
- Eastmoney current-only risk-warning / stop-board routes were not reliable in this environment and would not solve dated continuity even if reachable.

## deviations
- Added one extra verification command with `env -u QUANT_SYSTEM_LIVE_TESTS ...` to prove the live file still skips by default, because the inherited shell environment had the live flag preset.
- No forbidden files were modified.

## risks/follow-up
- Review should check whether preserving the pre-existing SH `delisted@暂停上市日期` behavior is acceptable alongside the new explicit `listing_suspended` record; this task kept it intentionally to avoid regression under the handoff’s preserve-existing-behavior requirement.
- A future hardening task would need a source with real dated ST removal/addition history across both exchanges before this capability can approach trading-grade continuity.
