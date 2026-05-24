# TASK-022 Integration (AKShare News Events Adapter)

## Task
- Task ID: `TASK-022`
- Handoff: `coordination/handoffs/TASK-022_DATAHUB_AKSHARE_NEWS_EVENTS_ADAPTER.md`
- Review Input: `coordination/reviews/TASK-022_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Integrated (Accepted)**
- 当前 review 结论为 `ACCEPTED (CLOSURE-READY UNDER LIVE PASS GATE)`，满足集成前置条件。

## Scope and Compliance Check
- 本轮实现/测试变更位于 handoff 允许范围：
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `tests/datahub/test_akshare_news_events_adapter.py`
  - `tests/datahub/test_akshare_news_events_live.py`
  - `coordination/reports/TASK-022_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。
- 备注：当前目录无可用 Git 工作树元信息，本次“本轮代码改动”按 handoff/report/review 与实际文件内容逐项核对。

## Integrated Content Summary
- 已集成 `AkshareNewsEventsAdapter`（仅 `DatasetName.NEWS_EVENTS`）：
  - 选择无凭据公共路由 `futures_news_shmet`；
  - 对所选路由不支持 `symbols` 的边界做显式拒绝；
  - `publish_time`、可选字段、`news_id`（缺省时稳定生成）、去重与冲突边界已覆盖；
  - 默认测试保持离线安全，live 冒烟门控完整。

## Verification During Integration
1. `python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py`
   - 结果：`Ran 15 tests`，`OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_news_events_live.py`
   - 结果：`Ran 3 tests`，`OK (skipped=1)`（默认 gate 行为正确）

3. `python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py tests/datahub/test_akshare_index_constituents_adapter.py tests/datahub/test_akshare_index_adapter.py tests/datahub/test_akshare_hk_adapter.py tests/datahub/test_akshare_fund_nav_adapter.py tests/datahub/test_akshare_adapter.py`
   - 结果：`Ran 113 tests`，`OK`

4. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - 结果：`Ran 294 tests`，`OK (skipped=11)`

5. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_news_events_live.py`
   - 结果：`Ran 3 tests in 0.855s`，`OK`

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻断缺口：**None**

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-022_INTEGRATION.md`

## State Update Recommendations (for Controller)
1. `TASK-022` 已具备收口条件，可按流程标记完成并关闭。
2. Phase 2 保持进行中（不切 phase），请派发当前 phase 的下一个可执行任务。
3. 后续若需 symbol-scoped 新闻能力，建议在独立任务中扩展路由与 symbol contract，避免破坏当前显式拒绝边界。
