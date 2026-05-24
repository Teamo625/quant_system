# TASK-015 Integration (AKShare ETF/Fund NAV Adapter)

## Task
- Task ID: `TASK-015`
- Handoff: `coordination/handoffs/TASK-015_DATAHUB_AKSHARE_ETF_FUND_NAV_ADAPTER.md`
- Review Input: `coordination/reviews/TASK-015_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Integrated (Accepted)**
- 本轮 review 结论为 `ACCEPTED`，未发现阻塞项，满足集成前置条件。

## Scope and Compliance Check
- 本轮实现与测试变更位于 handoff 允许范围：
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `tests/datahub/test_akshare_fund_nav_adapter.py`
  - `tests/datahub/test_akshare_fund_nav_live.py`
  - `coordination/reports/TASK-015_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。

## Integrated Content Summary
- 已集成 `AkshareETFFundNavSnapshotAdapter`，覆盖 `DatasetName.FUND_NAV_SNAPSHOT` 的窄切片（单基金代码）。
- 已集成代码规范化与契约对齐能力：
  - 支持 `510300` 与 `510300.ETF_CN` 输入，输出规范化为 `XXXXXX.ETF_CN`
  - 必填字段、`source`、`schema_version`、`ingested_at` 正常写入
  - DataFrame-like 与 list-of-mapping payload 均可归一化
  - 异常路径（数据集不支持、代码格式错误、payload 异常、日期/数值非法）明确失败
- 已集成离线与 live 门控测试：
  - 默认离线测试不触网
  - live smoke 默认跳过，`QUANT_SYSTEM_LIVE_TESTS=1` 时可显式启用

## Verification During Integration
- `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`
  - 结果：`Ran 17 tests`，`OK`
- `python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py`
  - 结果：`Ran 1 test`，`OK (skipped=1)`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py`
  - 结果：`test_live_akshare_fund_nav_snapshot_smoke ... ok`，`Ran 1 test`，`OK`

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻塞缺口：**None**
- 备注：当前目录不可用 Git 工作树元信息，本次按 handoff/report/review 与实际文件内容逐项核对后集成。

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-015_INTEGRATION.md`

## State Update Recommendations (for Controller)
- 可将 `TASK-015` 标记为已完成并关闭。
- Phase 2 保持进行中（不切 phase），派发下一个 DataHub real-source 适配器任务（如 index 或 sector/concept 方向）。
- 后续继续沿用“默认离线 + 显式 live 门控 + 网络不可用证据化”的交付模板。
