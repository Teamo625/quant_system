# TASK-021 Integration (Global Equity Sina KeyError Rework)

## Task
- Task ID: `TASK-021`
- Handoff: `coordination/handoffs/TASK-021_DATAHUB_GLOBAL_EQUITY_SINA_KEYERROR_REWORK.md`
- Review Input: `coordination/reviews/TASK-021_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Integrated (Accepted)**
- 当前 review 结论为 `ACCEPTED (CLOSURE-READY UNDER LIVE PASS GATE)`，满足集成前置条件。

## Scope and Compliance Check
- 按 handoff/report/review 与实际代码核查，本轮实现位于允许范围：
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_akshare_global_equity_snapshot_adapter.py`
  - `tests/datahub/test_akshare_global_equity_snapshot_live.py`
  - `coordination/reports/TASK-021_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。
- 备注：当前目录无可用 Git 工作树元信息，本次“本轮代码改动”按 handoff/report/review 与实际文件内容逐项核对。

## Verification During Integration
1. `python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py`
   - 结果：`Ran 25 tests`，`OK`

2. `python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py tests/datahub/test_akshare_index_adapter.py tests/datahub/test_akshare_hk_adapter.py tests/datahub/test_akshare_fund_nav_adapter.py tests/datahub/test_akshare_adapter.py`
   - 结果：`Ran 88 tests`，`OK`

3. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - 结果：`Ran 276 tests`，`OK (skipped=10)`

4. `python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`
   - 结果：`Ran 3 tests`，`OK (skipped=1)`（默认 gate 行为正确）

5. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`
   - 结果：`Ran 3 tests in 513.817s`，`OK`
   - 观察：命令执行期间存在较慢的实时分页拉取路径，但 live-enabled gate 已达到 `PASS`。

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻断缺口：**None**

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-021_INTEGRATION.md`

## State Update Recommendations (for Controller)
1. `TASK-021` 已具备收口条件，可按流程标记完成并关闭。
2. Phase 2 仍未完成（不切 phase），请派发当前 phase 的下一个可执行任务。
3. 后续同类 live 波动场景可复用本轮边界：仅将 `stock_us_spot + KeyError('data')` 视作 route-unavailable，避免误吞 DataHub 契约错误。
