# TASK-028 Integration (DataHub AKShare A-share Valuation Live-Network Rework)

## Task
- Task ID: `TASK-028`
- Handoff: `coordination/handoffs/TASK-028_DATAHUB_AKSHARE_A_SHARE_VALUATION_LIVE_NETWORK_REWORK.md`
- Review Input: `coordination/reviews/TASK-028_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Integrated (Accepted)**
- 当前 review 结论为 `ACCEPTED (CLOSURE-READY UNDER LIVE PASS GATE)`，满足集成前置条件。

## Scope and Compliance Check
- 本轮实现/测试变更位于 handoff 允许范围：
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/datasets.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
  - `tests/datahub/test_datasets.py`
  - `coordination/reports/TASK-028_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。
- 备注：当前目录无可用 Git 工作树元信息，本次“本轮代码改动”按 handoff/report/review 与实际文件内容逐项核对。

## Integrated Content Summary
- 已集成 TASK-028 live-network rework，核心结果是移除 live 对补充路由的硬阻断依赖并保留 source-truth：
  - `DatasetName.VALUATION_SNAPSHOT` 中 `float_market_cap` 调整为 optional（`ps_ttm`、`dividend_yield` 仍保持 optional）；
  - 适配器仍要求 `pe_ttm`、`pb`、`market_cap` 等核心字段，`float_market_cap` 仅在真实可得时输出；
  - 未引入占位值（不将 `float_market_cap` 伪造为 `market_cap`）；
  - `stock_individual_info_em` 在网络不可用时不再阻断可用核心记录，契约/归一化错误仍为 hard fail。
- 范围保持为单标的 A-share `VALUATION_SNAPSHOT`，未扩展到其他数据集或非 DataHub 模块。

## Verification During Integration
1. `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
   - 结果：`Ran 24 tests`，`OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
   - 结果：`Ran 3 tests`，`OK (skipped=1)`（默认 gate 行为正确）

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
   - 结果：`Ran 3 tests`，`OK`（live-enabled `PASS`）

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻断缺口：**None**

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-028_INTEGRATION.md`

## State Update Recommendations (for Controller)
1. `TASK-028` 已满足收口条件，可按流程标记完成并关闭。
2. 建议在 controller 侧状态文件中记录本次 `float_market_cap` optionality 的 source-truth 背景与回收条件（若未来出现稳定、可达、可信的 bounded 来源）。
3. Phase 2 仍未完成（不切 phase），请按 `coordination/PHASE_GATE.md` 派发当前 phase 下一个可执行任务。
