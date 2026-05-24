# TASK-020 Integration (Index Constituents Adapter)

## Task
- Task ID: `TASK-020`
- Handoff: `coordination/handoffs/TASK-020_DATAHUB_AKSHARE_INDEX_CONSTITUENTS_ADAPTER.md`
- Review Input: `coordination/reviews/TASK-020_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Integrated (Accepted)**
- 当前 review 结论为 `ACCEPTED (CLOSURE-READY UNDER LIVE PASS GATE)`，满足集成前置条件。

## Scope and Compliance Check
- 本轮实现/测试变更位于 handoff 允许范围：
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `tests/datahub/test_akshare_index_constituents_adapter.py`
  - `tests/datahub/test_akshare_index_constituents_live.py`
  - `coordination/reports/TASK-020_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。

## Integrated Content Summary
- 已集成 `AkshareIndexConstituentsAdapter`（仅 `DatasetName.INDEX_CONSTITUENTS`）：
  - index 标识输入支持 canonical / bare / source-native 变体并归一化；
  - 输出字段按 `INDEX_CONSTITUENTS` 契约归一化；
  - `in_date` 缺失时采用 `1900-01-01` 回退；
  - duplicate 边界保留（benign dedupe / conflicting hard-fail）。
- 已集成有界路由 fallback 顺序与 live 门控测试。

## Verification During Integration
1. `python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py`
   - 结果：`Ran 24 tests`，`OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py`
   - 结果：`Ran 1 test`，`OK (skipped=1)`（默认门控行为符合预期）

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py`
   - 结果：`test_live_akshare_index_constituents_smoke ... ok`
   - `Ran 1 test in 1.132s`
   - `OK`

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻断缺口：**None**
- 备注：当前目录无可用 Git 工作树元信息，本次“本轮代码改动”按 handoff/report/review 与实际文件内容逐项核对。

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-020_INTEGRATION.md`

## State Update Recommendations (for Controller)
1. `TASK-020` 已具备收口条件，可按流程标记完成并关闭。
2. Phase 2 保持进行中（不切 phase），派发当前 phase 下一个可执行任务。
3. 后续 index 数据相关任务建议复用当前路由 fallback 顺序与 duplicate 边界策略。

