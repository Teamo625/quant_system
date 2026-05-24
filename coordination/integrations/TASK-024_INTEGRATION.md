# TASK-024 Integration (China Macro `is_preliminary` Rework)

## Task
- Task ID: `TASK-024`
- Handoff: `coordination/handoffs/TASK-024_DATAHUB_CHINA_MACRO_PRELIMINARY_REWORK.md`
- Review Input: `coordination/reviews/TASK-024_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Integrated (Accepted)**
- 当前 review 结论为 `ACCEPTED (CLOSURE-READY UNDER LIVE PASS GATE)`，满足集成前置条件。

## Scope and Compliance Check
- 本轮实现/测试变更位于 handoff 允许范围：
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_akshare_china_macro_adapter.py`
  - `coordination/reports/TASK-024_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。
- 备注：当前目录无可用 Git 工作树元信息，本次“本轮代码改动”按 handoff/report/review 与实际文件内容逐项核对。

## Integrated Content Summary
- 已集成 `AkshareChinaMacroAdapter` 的 `is_preliminary` 定向修复：
  - 不再从 `初值` / `预测值` / `预告` 等数值语义字段推断 `is_preliminary`；
  - 仅接受显式 `is_preliminary` 字段并保留既有布尔语义归一化；
  - 显式但非法的 `is_preliminary` 取值仍保持硬失败。
- 已集成离线回归覆盖，验证：
  - 评审复现实例 `{"日期":"2024-01-10","今值":"0.2","初值":"0.1"}` 可成功归一化且不写入 `is_preliminary`；
  - 数值 `预测值` / `预告` 字段不触发 `is_preliminary`；
  - 显式布尔型 `is_preliminary` 正常保留。

## Verification During Integration
1. `python3 -m unittest tests/datahub/test_akshare_china_macro_adapter.py`
   - 结果：`Ran 18 tests`，`OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
   - 结果：`Ran 3 tests`，`OK (skipped=1)`（默认 gate 行为正确）

3. `python3 -m unittest tests/datahub/test_source.py`
   - 结果：`Ran 20 tests`，`OK`

4. 来自 report/review 的 mandatory live-enabled 证据（本轮 rework）：
   - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
   - 结果：PASS（report: `Ran 3 tests in 4.816s`, review: `Ran 3 tests in 4.926s`，均 `OK`）

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻断缺口：**None**

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-024_INTEGRATION.md`

## State Update Recommendations (for Controller)
1. `TASK-024` 已具备收口条件，可按流程标记完成并关闭。
2. Phase 2 仍未完成（不切 phase），请派发当前 phase 的下一个可执行任务。
3. 后续 macro 扩展中如需新增 preliminary 语义键，建议坚持“仅显式可靠布尔信号可映射”的边界并同步补齐离线回归测试。
