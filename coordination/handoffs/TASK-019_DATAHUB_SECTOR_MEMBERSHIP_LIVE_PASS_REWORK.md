# TASK-019: DataHub Sector Membership Live PASS Rework

## Task ID

TASK-019

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

`TASK-019` 已完成 sector membership 适配器主体实现，并完成一轮 live-evidence rework。当前最新结论：

- review decision: `CHANGES_REQUESTED`
- integration decision: `Not Integrated (CHANGES_REQUESTED)`

现状要点：

- 报告真实性问题已修复（不再把 live-enabled 误报为 `PASS`）
- 已实现仓库级可行尝试（EM 失败后 THS fallback）
- 但当前环境下 live-enabled 仍为 `SKIP`，关键证据：
  - EM route `ProxyError`（`17.push2.eastmoney.com`、`79.push2.eastmoney.com`）
  - THS fallback chained `SSLCertVerificationError`（`CERTIFICATE_VERIFY_FAILED`）

在当前 gate 下（live-enabled 必须 PASS 才能收口），仍不可关闭 TASK-019，必须继续 rework 并走 fresh review/integration。

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-019_DATAHUB_SECTOR_MEMBERSHIP_LIVE_PASS_REWORK.md`
- `coordination/reports/TASK-019_REPORT.md`
- `coordination/reviews/TASK-019_REVIEW.md`
- `coordination/integrations/TASK-019_INTEGRATION.md`

## Goal

在保持 `SECTOR_MEMBERSHIP` 契约边界与默认离线策略不退化的前提下，使以下命令在当前环境达到 `PASS`：

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`

目标结果：

- `Ran 1 test`
- `OK`
- `test_live_akshare_sector_membership_smoke ... ok`

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

- 当前 live skip 的完整异常链（EM 主路由 + THS fallback）
- 是否存在可在当前环境通过的候选 sector 类型/标识与路由顺序
- 是否存在不破坏安全边界的可行仓库级改进（例如新增可用 route/fallback、更稳健的候选顺序、网络不可用分类边界优化）
- 若 TLS/证书链为主阻断，明确“仓库内可改 / 不可改”的边界与 operator action

## Required Rework Behavior

可接受修复方向包括：

- 在保持契约完整性的前提下增加可行 route/fallback，使 live-enabled 在当前环境可成功返回至少一条有效 membership 记录
- 优化 live smoke 候选 sector 顺序，优先使用当前环境已验证可通的路径
- 加强网络不可用判定的精确性，避免误判

必须保持：

- 非网络类 adapter/schema 错误仍 hard-fail
- duplicate 边界策略不退化（benign dedupe / conflicting hard-fail）
- 默认测试路径离线安全

不得通过“放宽测试语义”规避问题（例如将本应失败的契约/解析问题改成 skip）。

## Required PASS Evidence

报告中必须包含成功 live-enabled 命令证据：

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`

若仍无法 PASS，必须如实记录，并明确 `TASK-019` 在当前 strict PASS gate 下仍不可收口。

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

本轮 rework 可进入 closure-ready 审核的条件：

- 默认测试保持离线且通过
- live 测试默认仍为 gated skip
- live-enabled sector membership 冒烟在当前环境 `PASS`
- 报告包含本次 live-enabled 命令与结果证据
- 任何仓库级修复有离线回归覆盖
- adapter/schema bug 仍 hard-fail
- 无 future-phase 模块改动
- `coordination/reports/TASK-019_REPORT.md` 已更新完整

## Report Path

`coordination/reports/TASK-019_REPORT.md`

## Review Path

`coordination/reviews/TASK-019_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-019_INTEGRATION.md`

## Out of Scope

Everything outside TASK-019 sector-membership live PASS rework is out of scope.
