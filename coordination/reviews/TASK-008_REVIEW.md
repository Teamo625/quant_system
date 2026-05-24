# TASK-008 Review

## Review Scope
- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-008_DATAHUB_EXPANDED_CONTRACT_SEMANTIC_VALIDATION.md`
- `coordination/reports/TASK-008_REPORT.md`
- 本轮实现与测试文件（`quant/datahub/datasets.py`, `tests/datahub/test_datasets.py`, `tests/datahub/test_source_catalog.py`）

## Findings

### P1 (Blocking)
- None.

### P2 (Major)
- None.

### P3 (Minor)
- `quant/datahub/datasets.py:743` 通过字段名关键字包含判断（`id/code/symbol/title/name`）识别“标识/标题字段”，当前实现满足 handoff 目标，但该规则对未来新增字段命名较敏感。建议后续在不扩展业务语义的前提下，将该规则沉淀为更显式的字段名单或 schema-level 元数据，以降低命名耦合风险（不阻塞本次验收）。

## Handoff Compliance Check
- Phase scope: 通过。实现与测试均位于 `quant/datahub/**`、`tests/datahub/**`，未发现未来阶段模块逻辑扩展。
- Allowed/forbidden files: 通过。改动与报告声明一致，且未触及 controller-only 协调真相文件。
- Semantic validation requirements: 通过。已新增轻量语义校验并保留既有 required-field / dtype 校验路径：
  - `schema_version` 一致性校验
  - 必填标识/标题字符串非空校验
  - OHLC `high < low` 拒绝
  - 常见非负字段负值拒绝
  - `weight` 范围校验（`[0,100]`）
  - `in_date/out_date` 日期范围校验
- Expanded invalid-sample priorities: 通过。已覆盖宏观、政策、新闻、公告、行业成员、基金 NAV/持仓、指数日线、全球简要股票快照等优先域。
- TASK-007 P3 fix: 通过。`tests/datahub/test_source_catalog.py` 已将 NEWS 来源断言改为 contains-style，不再依赖“唯一来源”。

## Testing and Network Policy Check
- 复核命令：`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- 复核结果：`Ran 45 tests`，`OK`
- 补充复核：
  - `python3 -m unittest tests/datahub/test_datasets.py` -> `Ran 19 tests`，`OK`
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> `Ran 6 tests`，`OK`
- 网络策略：通过。默认测试离线；未发现新增实时网络访问逻辑；目录测试中保留 `socket.create_connection` 防护型 patch。

## Decision
- **Accepted**（可进入 integration 阶段）

## Follow-up Requirements
- 后续在 adapter 任务前，建议补充一轮“字段命名变更鲁棒性”测试，确保语义校验规则在 schema 扩展时不出现误报或漏报。
- 后续可在保持离线前提下，逐步增加“组合语义”校验（例如多字段一致性），但应继续避免引入策略/研究逻辑耦合。
