# TASK-029 Integration (DataHub AKShare A-share Capital Flow Snapshot Adapter)

## Task
- Task ID: `TASK-029`
- Handoff: `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_SNAPSHOT_ADAPTER.md`
- Review Input: `coordination/reviews/TASK-029_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Not Integrated (Blocked by Review Gate)**
- 当前 review 结论为 `CHANGES REQUESTED (LIVE REWORK REQUIRED BEFORE INTEGRATION/CLOSURE)`，尚不满足“已接受后再集成”的前置条件。

## Scope and Compliance Check
- 本轮实现/测试变更位于 handoff 允许范围（按 report 与实文件核对）：
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
  - `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
  - `tests/datahub/test_datasets.py`
  - `tests/datahub/test_source_catalog.py`
  - `coordination/reports/TASK-029_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。
- 备注：当前目录无可用 Git 工作树元信息，本次“本轮代码改动”按 handoff/report/review 与实际文件内容逐项核对。

## Integration Assessment Summary
- 实现与离线回归整体符合 TASK-029 范围目标（A-share 单标的 `CAPITAL_FLOW_SNAPSHOT`、符号边界、归一化、默认离线安全）。
- `DatasetName.CAPITAL_FLOW_SNAPSHOT` 已做最小 source-truth optionality 硬化：
  - `net_inflow` / `northbound_net_buy` / `turnover_rate` 为 optional；
  - `main_net_inflow` 保持 required。
- 但 mandatory live gate 仍未满足：live-enabled 结果为 `SKIP`（主路由 `push2his.eastmoney.com` 代理链路不可达），与 review 结论一致。

## Verification During Integration
1. `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
   - 结果：`Ran 22 tests`，`OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
   - 结果：`Ran 3 tests`，`OK (skipped=1)`（默认 gate 行为正确）

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
   - 结果：`Ran 3 tests`，`OK (skipped=1)`
   - skip 证据：`ProxyError ... host='push2his.eastmoney.com' ... Unable to connect to proxy ... RemoteDisconnected(...)`

4. `python3 -m unittest tests/datahub/test_datasets.py tests/datahub/test_source_catalog.py`
   - 结果：`Ran 33 tests`，`OK`

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻断缺口：**Live-enabled PASS gate 未达成（当前为 SKIP）**

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-029_INTEGRATION.md`

## State Update Recommendations (for Controller)
1. 按 `AGENTS.md` 为 `TASK-029` 派发一次 live-failure rework handoff（5.3 execution window），要求在允许范围内继续完成可行诊断/修复并提交新报告。
2. 在可用网络/代理路径下复跑：
   - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
   目标为 live-enabled `PASS`。
3. 收到“review accepted”后，再进行下一轮 integration 以完成 TASK-029 收口。
