# TASK-027 Integration (DataHub AKShare A-share Corporate Actions Adapter)

## Task
- Task ID: `TASK-027`
- Handoff: `coordination/handoffs/TASK-027_DATAHUB_AKSHARE_A_SHARE_CORPORATE_ACTIONS_ADAPTER.md`
- Review Input: `coordination/reviews/TASK-027_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Integrated (Accepted)**
- 当前 review 结论为 `ACCEPTED (CLOSURE-READY UNDER LIVE PASS GATE)`，满足集成前置条件。

## Scope and Compliance Check
- 本轮实现/测试变更位于 handoff 允许范围：
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
  - `tests/datahub/test_akshare_a_share_corporate_actions_live.py`
  - `coordination/reports/TASK-027_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。
- 备注：当前目录无可用 Git 工作树元信息，本次“本轮代码改动”按 handoff/report/review 与实际文件内容逐项核对。

## Integrated Content Summary
- 已集成 `AkshareAShareCorporateActionsAdapter`（`DatasetName.CORPORATE_ACTIONS` 的单标的 A-share 分红事件切片）：
  - 单 symbol 强约束，支持 canonical/raw 6位形式并拒绝无效/歧义符号；
  - 以 `stock_dividend_cninfo` 为主路由，并在网络不可用场景下可使用 `stock_history_dividend_detail(indicator=分红)` 有界回退；
  - 规范化 `symbol/market/event_date/event_type/value/raw_payload_ref/source/ingested_at/schema_version`；
  - `event_date` 使用“除权除息 > 股权登记 > 公告日期”确定性回退；
  - `value` 结构化承载派息、送股、转增、进度、报告期和说明等字段；
  - `raw_payload_ref` 使用稳定序列化+哈希，具备确定性。
- 已集成边界行为：
  - malformed payload / required field / invalid date/value / non-serializable 值硬失败；
  - 重复记录可去重，冲突重复硬失败；
  - 默认离线安全，live 路径门控且不掩盖契约错误。

## Verification During Integration
1. `python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
   - 结果：`Ran 19 tests`，`OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`
   - 结果：`Ran 3 tests`，`OK (skipped=1)`（默认 gate 行为正确）

3. `python3 -m unittest tests/datahub/test_source.py`
   - 结果：`Ran 20 tests`，`OK`

4. `python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_adapter.py`
   - 结果：`Ran 21 tests`，`OK`

5. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - 结果：`Ran 390 tests`，`OK (skipped=15)`

6. mandatory live-enabled 证据（来自 report/review）：
   - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`
   - 结果：PASS（report: `Ran 3 tests in 0.752s`, review: `Ran 3 tests in 0.750s`，均 `OK`）

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻断缺口：**None**

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-027_INTEGRATION.md`

## State Update Recommendations (for Controller)
1. `TASK-027` 已具备收口条件，可按流程标记完成并关闭。
2. Phase 2 仍未完成（不切 phase），请派发当前 phase 的下一个可执行任务。
3. 后续维护建议：AKShare 上游字段和依赖告警可能变化，需随版本同步更新映射与离线回归用例。
