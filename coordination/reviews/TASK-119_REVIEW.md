# TASK-119 Review

## Findings

1. Blocking: `AkshareETFDailyBarAdapter` now treats all `16`/`18`/`150`/`501` prefixes as supported listed-fund daily-bar families ([akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:29), [akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:18720)), but this task only adds evidence and tests for `161725.FUND_CN` via the LOF route and Sina fallback ([test_akshare_etf_daily_bar_adapter.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_etf_daily_bar_adapter.py:130), [test_akshare_etf_daily_bar_adapter.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_etf_daily_bar_adapter.py:446), [test_akshare_etf_daily_bar_adapter.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_etf_daily_bar_adapter.py:813)). That overextends accepted symbol truth beyond what was proven, and it conflicts with the prior conservative boundary that broader listed-fund families needed separate validation before expansion ([TASK-082_REPORT.md](/Users/chenziheng/Documents/量化分析代码/quant_system/coordination/reports/TASK-082_REPORT.md:45)). Rework should either narrow accepted fund families to the actually proven family/path or add explicit route evidence and regression coverage for every newly accepted prefix family.

## Decision

REWORK REQUIRED.

## Closure Readiness

- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: PASS
- Rework required: YES
- Phase/scope/contract/test blockers: YES - contract/truthfulness blocker on newly accepted listed-fund code families beyond proven evidence
