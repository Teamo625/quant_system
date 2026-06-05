# TASK-096 Review

## Findings

- No new code or contract blockers were found in the requested rework scope. The fixed `10`-calendar-day guard is gone; `1`-minute retention now resolves the latest `5` trade dates first and only falls back to a conservative weekday-plus-holiday cushion when trade-date resolution is unavailable, in [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:912).
- The previously missing holiday / long-closure regression is now covered in [tests/datahub/test_akshare_a_share_minute_bars_adapter.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_a_share_minute_bars_adapter.py:303), while the stale-window rejection still proves neither primary nor fallback fetch is hit for unsupported old `1`-minute requests in [tests/datahub/test_akshare_a_share_minute_bars_adapter.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_a_share_minute_bars_adapter.py:267).
- Live evidence is still environment-blocked rather than schema/contract-blocked. I independently reproduced the gated `SKIP` with `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`, and a manual `requests` GET to Eastmoney failed with the same `ProxyError` reported in [coordination/reports/TASK-096_REPORT.md](/Users/chenziheng/Documents/量化分析代码/quant_system/coordination/reports/TASK-096_REPORT.md:43).

## Decision

Accepted for the requested rework scope, but Controller closure is not allowed yet.

## Closure Readiness

- Controller closure allowed: No
- Default tests offline-safe: Yes. I independently verified `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py`, `python3 -m unittest tests/datahub/test_source_capabilities.py`, and `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`; the live file remained default-skipped.
- Live-enabled result: SKIP. Rework required: Yes. A fresh execution rerun from an environment that can reach Eastmoney is still required before Controller closure; this review did not find an additional repository-side defect beyond the diagnosed connectivity block.
- Phase/scope/contract/test blockers: Yes. Phase scope stayed within allowed DataHub adapter/test/report files and capability truth remains conservative, but the mandatory live PASS gate is still open.

## Required Follow-up

- Re-dispatch TASK-096 only for a live-environment rerun from a host that can reach Eastmoney or a working configured proxy path.
- No further repository code change is required before that rerun unless new live evidence reveals a repository-side failure.
