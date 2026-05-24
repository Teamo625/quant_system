# TASK-018: DataHub Sector Master Live Duplicate Rework

## Task ID

TASK-018

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

`TASK-018` 已完成 `AkshareSectorMasterAdapter` 的初版实现，并在 review 环节给出 `ACCEPTED (CLOSURE-READY UNDER LIVE PASS GATE)`。但在后续集成复核（`2026-05-21`）中，live-enabled 冒烟出现新的非网络类失败：

- command:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_master_live.py`
- observed error:
  - `ValueError: Duplicate canonical sector_id detected: 'INDUSTRY:广告媒体'`

该失败不属于网络不可用 `skip` 路径，属于当前数据/归一化一致性冲突，会阻断 `TASK-018` 最终收口。

本 handoff 继续 `TASK-018`，仅做 live duplicate 问题诊断与可行修复，不得扩展到 `SECTOR_MEMBERSHIP` 或其他阶段能力。

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-018_DATAHUB_SECTOR_MASTER_LIVE_DUPLICATE_REWORK.md`
- `coordination/reports/TASK-018_REPORT.md`
- `coordination/reviews/TASK-018_REVIEW.md`
- `coordination/integrations/TASK-018_INTEGRATION.md`

## Goal

在保持 `SECTOR_MASTER` 契约与默认离线策略不退化的前提下，使当前环境下的 live-enabled 冒烟恢复为 `PASS`：

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_master_live.py`

目标结果应为：

- `Ran 1 test`
- `OK`
- `test_live_akshare_sector_master_smoke ... ok`

## Allowed Files

The execution window may create or modify:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`（仅当导出调整确有必要）
- `quant/datahub/__init__.py`（仅当导出调整确有必要）
- `tests/datahub/test_akshare_sector_master_adapter.py`
- `tests/datahub/test_akshare_sector_master_live.py`
- `tests/datahub/test_source_catalog.py`（仅当断言需窄范围修正）
- `coordination/reports/TASK-018_REPORT.md`

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

至少完成以下定位并记录证据：

- 触发 `Duplicate canonical sector_id` 的具体源路由与原始行特征：
  - 来自 `EM` 主路由、`THS` fallback，或两者之一
  - 重复是否为完全同名重复、空白/大小写/符号差异重复，或语义冲突重复
- 重复出现于 `INDUSTRY`、`CONCEPT`，或二者
- 当前重复是否是可安全去重的数据噪声，还是应保持硬失败的契约冲突

## Required Rework Behavior

实现 repository-level 可行修复。可接受方向包括：

- 对“可判定为同一 canonical `sector_id` 的重复行”进行确定性去重（例如保留第一条或保留带有效 `source_ts` 的一条），并保证行为稳定可测试
- 对“不可判定一致或存在冲突字段语义”的重复保持明确硬失败
- 必须保留：
  - 非网络异常不被网络 fallback/skip 掩盖
  - schema/contract bug 仍然作为失败暴露
  - 默认测试路径无隐式网络调用

不得通过弱化 live test 语义来规避真实适配器问题（例如把非网络的数据一致性错误直接改成 `skip`）。

## Required PASS Evidence

报告中必须包含成功的 live-enabled 运行结果：

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_master_live.py`

若仍为 `SKIP` 或 `FAIL`，必须如实记录，并明确 `TASK-018` 在当前 gate 下仍不可收口。

## Required Test Commands

Default tests must remain offline.

Run:

`python3 -m unittest tests/datahub/test_akshare_sector_master_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_sector_master_live.py`

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run relevant regressions if shared AKShare behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_master_live.py`

## Acceptance Criteria

本次 rework 可进入 closure-ready 审核的条件：

- 默认测试保持离线且通过
- live 测试默认仍为 gated skip
- live-enabled sector-master 冒烟在当前环境 `PASS`
- 报告包含本次 live-enabled 命令与结果证据
- duplicate 问题的修复有离线回归测试覆盖
- adapter/data-contract bug 仍为硬失败
- 无 future-phase 模块改动
- `coordination/reports/TASK-018_REPORT.md` 已更新并包含：
  - files changed
  - tests run
  - default network behavior
  - live-enabled PASS/SKIP/FAIL result
  - root-cause evidence
  - fix details
  - risks/follow-up

## Report Path

`coordination/reports/TASK-018_REPORT.md`

## Review Path

`coordination/reviews/TASK-018_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-018_INTEGRATION.md`

## Out of Scope

Everything outside TASK-018 sector-master live duplicate rework is out of scope.
