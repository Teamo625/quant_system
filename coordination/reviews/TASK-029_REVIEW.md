# TASK-029 Review

## Review Metadata

- Task ID: `TASK-029`
- Reviewer Role: Review Agent
- Reviewed Handoff: `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_SNAPSHOT_ADAPTER.md`
- Reviewed Report: `coordination/reports/TASK-029_REPORT.md`
- Review Output: `coordination/reviews/TASK-029_REVIEW.md`
- Review Date: `2026-05-24`

## Inputs Reviewed

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_SNAPSHOT_ADAPTER.md`
- `coordination/reports/TASK-029_REPORT.md`
- 本轮实现代码与测试文件（DataHub 范围内）

Note: 当前目录无 Git 元信息可用（不是可识别的 Git 工作树），本次“本轮代码改动”按 handoff/report 声明涉及文件逐项核查。

## Findings (By Severity)

### P1 - Live closure gate is not met (`SKIP` instead of live-enabled `PASS`)

- Handoff 明确要求：任务闭环需要 live-enabled `PASS`；若 live-enabled `SKIP/FAIL`，需进入 rework/review gate（`coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_SNAPSHOT_ADAPTER.md` acceptance criteria）。
- 执行报告记录 live-enabled 结果为 `SKIP`，并给出主路由 `push2his.eastmoney.com` 代理链路不可达证据（`coordination/reports/TASK-029_REPORT.md`）。
- 审查复测一致：`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` 结果为 `OK (skipped=1)`，skip 原因为 `ProxyError` 连接 `push2his.eastmoney.com` 失败。
- 按仓库规则，出现此类 live `SKIP` 后，下一步必须是 5.3 执行窗口 live-network rework，再进入新一轮 review/integration（`AGENTS.md` Data and Network Rules）。

### No additional blocking code-quality findings

- 范围边界、默认离线网络策略、契约可选性调整（`net_inflow`/`northbound_net_buy`/`turnover_rate` optional，`main_net_inflow` required）、以及覆盖面总体符合 handoff 要求。

## Open Questions / Assumptions

1. 假设当前环境代理/出网限制是本次 live `SKIP` 的主因，而非该适配器核心归一化逻辑回归；该假设与复测错误链、报告证据一致。

## Handoff Compliance Check

- Scope compliance (allowed files only): PASS
- Dataset scope limited to one-symbol A-share `DatasetName.CAPITAL_FLOW_SNAPSHOT`: PASS
- Source identity kept as `akshare_cn_hk_public_family`: PASS
- Symbol normalization/rejection boundaries: PASS
- Duplicate/conflict/malformed/date/numeric/unit boundaries: PASS
- Default tests remain offline-safe: PASS
- Mandatory live smoke exists and default gate behavior is correct: PASS
- Live-enabled closure gate (`PASS` required for closure): **FAIL (current result = SKIP)**
- Phase boundary respected (DataHub only): PASS

## Test Evidence (Reproduced in Review)

1. `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- Result: `Ran 22 tests`, `OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- Result: `Ran 3 tests`, `OK (skipped=1)`（默认 live gate 生效）

3. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- Result: `Ran 10 tests`, `OK`

4. `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- Result: `Ran 24 tests`, `OK`

5. `python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- Result: `Ran 19 tests`, `OK`

6. `python3 -m unittest tests/datahub/test_datasets.py`
- Result: `Ran 27 tests`, `OK`

7. `python3 -m unittest tests/datahub/test_source.py`
- Result: `Ran 20 tests`, `OK`

8. `python3 -m unittest tests/datahub/test_quality.py`
- Result: `Ran 7 tests`, `OK`

9. `python3 -m unittest tests/datahub/test_source_catalog.py`
- Result: `Ran 6 tests`, `OK`

10. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- Result: `Ran 442 tests`, `OK (skipped=17)`

11. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- Result: `Ran 3 tests`, `OK (skipped=1)`
- Skip evidence: `ProxyError ... host='push2his.eastmoney.com' ... Unable to connect to proxy ... Remote end closed connection without response`

## Review Decision

- Decision: **CHANGES REQUESTED (LIVE REWORK REQUIRED BEFORE INTEGRATION/CLOSURE)**
- Rationale: 实现与离线回归整体达标，但 live-enabled 结果仍为 `SKIP`，尚未满足 handoff 的 closure 条件；需按 `AGENTS.md` 进入显式 live-network rework 流程后再评审。

## Follow-up Requirements For Controller / Next Execution Window

1. Controller 需按 `AGENTS.md` 派发 `TASK-029` live-failure rework handoff（5.3 execution window）。
2. Rework 需在允许文件范围内继续完成可行诊断/修复，并重新提交执行报告（含 live-enabled 结果与证据）。
3. 在网络/代理路径可用后复跑：`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`，目标为 live-enabled `PASS`。
4. Integration Agent 在收到 accepted review 之前不应执行最终集成闭环。
