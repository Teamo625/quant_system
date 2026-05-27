# TASK-029 Integration (DataHub AKShare A-share Capital Flow Live-Network Rework)

## Task
- Task ID: `TASK-029`
- Handoff: `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_LIVE_NETWORK_REWORK.md`
- Review Input: `coordination/reviews/TASK-029_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Integrated (Accepted)**
- 当前 review 结论为 `ACCEPTED (CLOSURE-READY UNDER LIVE PASS GATE)`，满足集成前置条件。

## Scope and Compliance Check
- 本轮实现/测试变更位于 handoff 允许范围：
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
  - `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
  - `coordination/reports/TASK-029_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。
- 备注：当前目录无可用 Git 工作树元信息，本次“本轮代码改动”按 handoff/report/review 与实际文件内容逐项核对。

## Integration Assessment Summary
- 已集成 TASK-029 live-network rework，核心结果是在保持 one-symbol 边界前提下实现 primary-first + bounded fallback：
  - 保持 AKShare 主路由 `stock_individual_fund_flow` 为优先；
  - 当主路由出现网络/代理/DNS/TLS/upstream 不可用时，启用有界 datacenter fallback（`RPT_FUNDFLOW_SECUCODE` one-symbol 过滤）；
  - 保持 `DatasetName.CAPITAL_FLOW_SNAPSHOT` 的 source-truth optionality（`net_inflow` / `northbound_net_buy` / `turnover_rate` optional，`main_net_inflow` required）；
  - 不引入 full-market workaround，不引入占位值。
- 范围保持 DataHub 内一标的 A-share `CAPITAL_FLOW_SNAPSHOT` 切片，未越界到其他模块/数据集。

## Verification During Integration
1. `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
   - 结果：`Ran 26 tests`，`OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
   - 结果：`Ran 3 tests`，`OK (skipped=1)`（默认 gate 行为正确）

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
   - 结果：`Ran 3 tests`，`OK`（live-enabled `PASS`）

4. `python3 -m unittest tests/datahub/test_datasets.py tests/datahub/test_source_catalog.py tests/datahub/test_akshare_adapter.py tests/datahub/test_source.py tests/datahub/test_quality.py`
   - 结果：`Ran 70 tests`，`OK`

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻断缺口：**None**

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-029_INTEGRATION.md`

## State Update Recommendations (for Controller)
1. `TASK-029` 已满足收口条件，可按流程标记完成并关闭。
2. 建议在 controller 状态文件记录“primary route unavailable 时启用 bounded datacenter fallback，且保持 one-symbol scope”的边界说明。
3. Phase 2 仍未完成（不切 phase），请按 `coordination/PHASE_GATE.md` 派发当前 phase 下一个可执行任务。
