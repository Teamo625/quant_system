# TASK-023 Integration (HKEX Symbol Filter Rework)

## Task
- Task ID: `TASK-023`
- Handoff: `coordination/handoffs/TASK-023_DATAHUB_HKEX_SYMBOL_FILTER_REWORK.md`
- Review Input: `coordination/reviews/TASK-023_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Integrated (Accepted)**
- 当前 review 结论为 `ACCEPTED (CLOSURE-READY UNDER LIVE PASS GATE)`，满足集成前置条件。

## Scope and Compliance Check
- 本轮实现/测试变更位于 handoff 允许范围：
  - `quant/datahub/adapters/hkex.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `tests/datahub/test_hkex_company_announcements_adapter.py`
  - `tests/datahub/test_hkex_company_announcements_live.py`
  - `coordination/reports/TASK-023_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。
- 备注：当前目录无可用 Git 工作树元信息，本次“本轮代码改动”按 handoff/report/review 与实际文件内容逐项核对。

## Integrated Content Summary
- 已集成 HKEX `COMPANY_ANNOUNCEMENTS` 符号过滤 rework：
  - 请求侧与源行侧符号归一化逻辑拆分；
  - 请求侧严格校验，仅接受 `700` / `00700` / `00700.HK`（及等价 1-5 位纯数字）；
  - 明确拒绝 `foo700`、`A700.HK`、`00700HK` 等无效过滤值；
  - 保留源行 `Stock Code: 00700` 等标签前缀容错，不将该容错泄漏到请求入参路径。

## Verification During Integration
1. `python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py`
   - 结果：`Ran 19 tests`，`OK`

2. `python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`
   - 结果：`Ran 3 tests`，`OK (skipped=1)`（默认 gate 行为正确）

3. `python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py tests/datahub/test_akshare_global_equity_snapshot_adapter.py tests/datahub/test_akshare_hk_adapter.py tests/datahub/test_source.py`
   - 结果：`Ran 76 tests`，`OK`

4. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - 结果：`Ran 316 tests`，`OK (skipped=12)`

5. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`
   - 结果：`Ran 3 tests in 5.804s`，`OK`

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻断缺口：**None**

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-023_INTEGRATION.md`

## State Update Recommendations (for Controller)
1. `TASK-023` 已具备收口条件，可按流程标记完成并关闭。
2. Phase 2 仍未完成（不切 phase），请派发当前 phase 的下一个可执行任务。
3. 后续同类任务可复用“请求入参严格校验 + 源行解析容错隔离”模式，避免回归到宽松推断。
