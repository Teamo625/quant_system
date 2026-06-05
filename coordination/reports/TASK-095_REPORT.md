# TASK-095 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-095_REPORT.md`

## tests run
- `python3 -m unittest tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py` -> PASS in this shell because inherited `QUANT_SYSTEM_LIVE_TESTS='1'`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py` -> PASS, live smoke `SKIP (disabled)`; confirms code remains default-offline
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py` -> PASS

## default network behavior
- Default adapter and capability tests remain offline-only; no hidden network calls were added.
- The live smoke file remains environment-gated by `QUANT_SYSTEM_LIVE_TESTS == "1"`.
- This execution shell already had `QUANT_SYSTEM_LIVE_TESTS='1'`, so the handoff's plain `python3 -m unittest -v ...live.py` command executed live instead of skipping.
- Extra verification with `env -u QUANT_SYSTEM_LIVE_TESTS ...` confirmed the live smoke is skipped when the env var is absent.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py`
- Evidence:
  - full live test file result: `Ran 4 tests ... OK`
  - manual route probe on `20260602` returned `stock_tfp_em=24` rows and `news_trade_notify_suspend_baidu=5` rows, with `4` SH/SZ overlap codes: `000668`, `000736`, `002200`, `300175`
  - the Baidu overlap rows exposed exact `复牌时间=2026-06-03` plus reasons such as `撤销退市风险警示` / `撤销其他风险警示`, confirming explicit public resumption truth is available for some A-share reminder rows

## source routes investigated and route-level findings
- `stock_tfp_em(date=YYYYMMDD)`: stable no-credential Eastmoney route; still the primary source for bounded suspension-table rows with `停牌时间/停牌截止时间/停牌期限/停牌原因/所属市场/预计复牌时间`.
- `news_trade_notify_suspend_baidu(date=YYYYMMDD)`: stable no-credential route in this environment; auto-cookie flow worked; provides reminder-style `停牌时间/复牌时间/停牌事项说明/公告日期/公告时间`.
- `news_trade_notify_suspend_baidu` findings:
  - SH/SZ rows can expose exact `复牌时间`, so the adapter now normalizes explicit `resumption` events from those rows.
  - Some A-share reminder rows may exist only in Baidu; when they are SH/SZ/BJ stocks and no Eastmoney row matches the same `symbol + start_date`, the adapter now adds a conservative generic `suspension` event.
  - HK and `NQ` rows also appear in the route; they are filtered out because they are outside the A-share dataset contract and cannot be safely mapped to SH/SZ/BJ suspension truth.
  - Rows with `复牌时间` placeholders like `-` / `--` are treated as missing exact resume truth, not inferred resumption.
- Signature compatibility policy remains strict for both routes: missing `date`/`trade_date` support still raises a hard failure instead of being misclassified as environmental unavailability.

## capability truth changes
- `a_share_suspension_resumption` remains `partial`.
- Capability wording now reflects dual public-route evidence: Eastmoney bounded suspension-table coverage plus Baidu exact announced SH/SZ resumption dates and some Baidu-only reminder breadth.
- No promotion to `covered`.

## remaining public-source limitations
- Public-source coverage is still not exchange-wide or continuity-complete; Baidu is a reminder-style day slice, not a full audited suspension/resumption history.
- Exact completed resumption confirmation is only available when the public row explicitly exposes `复牌时间`; this is not guaranteed for every event and was not proven broadly for BJ.
- Deeper taxonomy remains incomplete because Baidu does not expose a reliable `停牌期限`-style status taxonomy, so Baidu-only suspension rows stay conservatively generic.
- The adapter intentionally does not overwrite Eastmoney-provided bounded behavior with synthesized or text-inferred resume events.

## deviations
- Added one extra verification command with `env -u QUANT_SYSTEM_LIVE_TESTS ...` because the inherited shell environment had the live flag preset.
- No forbidden files were modified.

## risks/follow-up
- A future hardening task could look for a stable public BJ-specific reminder or exchange route that exposes exact `复牌时间`; this task did not prove BJ resumption breadth.
- If future public sources expose authoritative completed resumption histories instead of day reminders, the current `partial` truth should be re-reviewed rather than promoted from the present reminder-based evidence.
