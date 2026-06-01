# TASK-049 Review

## Scope and Inputs Reviewed

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-049_DATAHUB_AKSHARE_A_SHARE_MAJOR_ACTIVITY_EVENTS_ADAPTER.md`
- `coordination/reports/TASK-049_REPORT.md`
- 本轮改动范围（先验）:
  - `git status --short`
  - `git diff --stat`
- 本轮代码与测试改动（按最小必要读取）:
  - `quant/datahub/adapters/akshare.py`（新增 `AkshareAShareMajorActivityEventsAdapter` 及相关可用性分类分支）
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
  - `tests/datahub/test_akshare_a_share_major_activity_events_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

未读取 `coordination/agent_runs/**`（当前证据已足够完成审查判断）。

## Findings

### Blocking Findings

- 无。

### Non-blocking Observations

- 变更范围保持在 Phase 2.5 允许目录（`quant/datahub/**`、`tests/datahub/**`、`coordination/reports/TASK-049_REPORT.md`），未触碰 controller-only 文件。
- `MAJOR_ACTIVITY_EVENTS` 能力真值已从 `planned` 更新为 `partial`，且 `gap_reason` 保持了“仅公共源窄切片、广度/历史不足”的保守表述，符合 handoff。
- 默认测试离线安全：新增 adapter 测试均通过注入 fetch 函数完成，无隐式 live 网络调用；live smoke 仍由 `QUANT_SYSTEM_LIVE_TESTS=1` 显式门控。
- live-enabled 结果为 `SKIP`（AKShare 上游 route-shape 不可用），证据与复验一致；按 `AGENTS.md`，controller 关闭任务前仍需遵循 live 失败/跳过处置流程（是否继续 rework 由 controller 决策）。

## Independent Verification

已在本地独立复验以下命令（均通过，结果与执行报告一致）：

1. `python3 -m unittest tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- 结果：`Ran 15 tests ... OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- 结果：`Ran 4 tests ... OK (skipped=1)`（默认 live 禁用）

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- 结果：`Ran 4 tests ... OK (skipped=1)`
- 复验到的 skip 证据：
  - `RuntimeError: AKShare A-share major-activity route unavailable: stock_dzjy_mrmx(start_date=20260531, end_date=20260531) -> TypeError: 'NoneType' object is not subscriptable`

4. `python3 -m unittest tests/datahub/test_source_capabilities.py tests/datahub/test_source_catalog.py`
- 结果：`Ran 19 tests ... OK`

5. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- 结果：`Ran 756 tests ... OK (skipped=33)`

## Handoff Compliance Check

- 已实现 `DatasetName.MAJOR_ACTIVITY_EVENTS` 的 AKShare A-share 窄切片适配器与 deterministic 离线测试。
- 请求边界（单交易日、拒绝无界/多日）、符号校验、payload 形状校验、数值/日期解析、排序去重、route 签名兼容错误硬失败边界均有覆盖。
- 新增 gated live smoke，默认跳过，显式启用后给出真实 `SKIP` 证据与根因链。
- 未发现越界到 scanner/strategy/backtest/portfolio/risk/AI/UI 等未来阶段实现。

## Decision

- **ACCEPTED**

## Required Follow-up

- Integration Agent 可按现状集成本轮代码与报告。
- Controller 在任务关闭判定时需遵循 `AGENTS.md` 的 live skip/fail 处置门禁：当前 live-enabled 为 `SKIP`，不可按 live-pass 标准直接闭环。
