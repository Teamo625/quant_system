# TASK-019: DataHub Sector Membership Live Evidence Rework

## Task ID

TASK-019

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

`TASK-019` 已完成 `AkshareSectorMembershipAdapter` 的主体实现与离线测试覆盖，但当前 review/integration 结果显示：

- review decision: `CHANGES_REQUESTED`
- integration decision: `Not Integrated (CHANGES_REQUESTED)`

阻断点：live-enabled 结果与报告不一致。

- report 声明：
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py` 为 `PASS`
- review/integration 复核：
  - 同命令结果为 `OK (skipped=1)`
  - skip 证据为网络/代理不可用（`ProxyError`，含 Eastmoney 主机如 `17.push2.eastmoney.com`、`79.push2.eastmoney.com`）

根据 AGENTS 规则：live-enabled fail/skip 必须 truthfully recorded，并在可行时执行仓库级修复后进入 fresh review/integration cycle，才能判断是否收口。

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-019_DATAHUB_SECTOR_MEMBERSHIP_LIVE_EVIDENCE_REWORK.md`
- `coordination/reports/TASK-019_REPORT.md`
- `coordination/reviews/TASK-019_REVIEW.md`
- `coordination/integrations/TASK-019_INTEGRATION.md`

## Goal

修复 TASK-019 的 live evidence gate：

1. 报告中的 live-enabled 结果必须与实际命令一致（truthfully recorded）。
2. 若可行，实施仓库级改进以争取 live-enabled `PASS`。
3. 若当前环境仍仅能 `SKIP`，需提供充分根因证据与可行操作建议，不得伪报 `PASS`。

## Allowed Files

The execution window may create or modify:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`（仅当导出调整确有必要）
- `quant/datahub/__init__.py`（仅当导出调整确有必要）
- `tests/datahub/test_akshare_sector_membership_adapter.py`
- `tests/datahub/test_akshare_sector_membership_live.py`
- `tests/datahub/test_source_catalog.py`（仅当断言需窄范围修正）
- `coordination/reports/TASK-019_REPORT.md`

## Forbidden Files

The execution window must not modify:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Required Investigation

至少完成以下核查并记录证据：

- live-enabled `SKIP` 的完整异常链与关键 host/token 证据
- 当前 membership 数据路由是否存在可行 fallback 路径（在不掩盖契约错误前提下）
- 若无法在仓库内消除 skip，明确说明“不可行点”与 operator 可执行动作

## Required Rework Behavior

- 首要要求：修正 `coordination/reports/TASK-019_REPORT.md` 中 live-enabled 结论，确保与实际一致。
- 在可行范围内尝试 repository-level 修复（例如路由/fallback 优化、候选路径顺序优化、网络不可用分类完善）。
- 不得把非网络类 adapter/schema 错误降级为 `skip`。
- 保持 `SECTOR_MEMBERSHIP` 契约边界与默认离线策略不退化。

## Required Test Commands

Default tests must remain offline.

Run:

`python3 -m unittest tests/datahub/test_akshare_sector_membership_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run relevant regressions if shared AKShare behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_sector_master_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`

## Acceptance Criteria

本次 rework 可进入下一轮 review 的条件：

- live-enabled 结果在报告中 truthfully recorded（PASS/SKIP/FAIL 与实际一致）
- 若为 SKIP/FAIL，包含网络/代理/DNS/TLS/上游证据与可行修复尝试说明
- 默认测试仍离线且通过
- `SECTOR_MEMBERSHIP` 契约与 duplicate 边界不退化
- 无 future-phase 模块改动
- `coordination/reports/TASK-019_REPORT.md` 已更新完整

注意：若 live-enabled 仍非 `PASS`，报告必须明确 TASK-019 在当前 gate 下是否 closure-ready。

## Report Path

`coordination/reports/TASK-019_REPORT.md`

## Review Path

`coordination/reviews/TASK-019_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-019_INTEGRATION.md`

## Out of Scope

Everything outside TASK-019 sector-membership live-evidence rework is out of scope.
