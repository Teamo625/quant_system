# TASK-046 执行报告（5.3 Execution）

## 1) 任务完成结论
已完成 `TASK-046`：实现 AKShare A 股公司公告适配器（窄切片），补充离线测试与默认跳过的 live smoke，更新 DataHub source capability/source catalog 对应事实。

## 2) 变更文件
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_company_announcements_adapter.py` (new)
- `tests/datahub/test_akshare_a_share_company_announcements_live.py` (new)
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## 3) 实现摘要
- 新增 `AkshareAShareCompanyAnnouncementsAdapter`：
  - source: `akshare_cn_hk_public_family`
  - dataset: `DatasetName.COMPANY_ANNOUNCEMENTS`
  - market: `A_SHARE`
  - 支持符号：`600000.SH/000001.SZ/430047.BJ`、`SH600000/SZ000001`、裸六码
  - 明确拒绝 HK/ETF/基金/指数/格式错误/多符号/空符号
  - 支持 DataFrame-like 与 `list[Mapping]` payload
  - 归一化字段：`announcement_id/publish_time/announcement_type/title/url/source/source_ts/ingested_at/schema_version`
  - 默认稳定排序：`publish_time, symbol, announcement_id`
  - 重复去重：同 `announcement_id` 非冲突合并并优先更新较新 `source_ts`；冲突则硬失败
  - 路由签名兼容错误（required arg 不存在）保持硬失败，不归类为 live 环境不可用
  - 环境/网络不可用分类器：仅覆盖代理、DNS、TLS、连接等外部问题
- capability truth 更新：
  - `a_share_company_announcements` 从 `planned` 调整为 `partial`
  - source family 加入 `akshare_cn_hk_public_family`
- source catalog 对齐：
  - `akshare_cn_hk_public_family` 增加 `COMPANY_ANNOUNCEMENTS` dataset 覆盖
  - 增加 `InformationDomain.ANNOUNCEMENT` 对应稳定数据集映射
  - 增加 `AssetDomain.ANNOUNCEMENT` 覆盖

## 4) 测试执行记录

### 4.1 聚焦离线测试
1. `python3 -m unittest tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- 结果：`Ran 14 tests ... OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`
- 结果：`Ran 4 tests ... OK (skipped=1)`（默认 live 关闭）

3. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- 结果：`Ran 10 tests ... OK`

4. `python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py`
- 结果：`Ran 19 tests ... OK`

5. `python3 -m unittest tests/datahub/test_source.py tests/datahub/test_source_capabilities.py tests/datahub/test_source_catalog.py`
- 结果：`Ran 37 tests ... OK`

### 4.2 默认离线全量
6. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- 结果：`Ran 716 tests ... OK (skipped=31)`

### 4.3 live-enabled 冒烟（必需）
7. 首次运行：
- 命令：`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`
- 结果：`ERROR`
- 根因证据：
  - 抛错：`ValueError: ... date range exceeds bounded limit: range_days=181, max_route_days=180`
  - 性质：仓库内可修复边界错误（off-by-one），非网络/代理/DNS/TLS/upstream 问题
- 处理：将 live 测试窗口调整为 `179` 天差（含首尾共 180 天）

8. 修复后复跑：
- 命令：`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`
- 结果：`Ran 4 tests ... OK`
- live 结论：`PASS`

## 5) 默认网络行为说明
- 默认测试路径不触发真实网络：
  - 新增离线适配器测试中使用注入 fetch 函数与本地 fixture，并在关键用例 patch `socket.create_connection` 防止网络访问。
  - live 测试使用 `@skipUnless(QUANT_SYSTEM_LIVE_TESTS=1)`，默认跳过。

## 6) 与 handoff 的偏差
- 无功能性越界偏差。
- 新增 `max_route_days` 边界控制（默认 120 天）以保持窄切片与可控请求规模；与 handoff 的“bounded route”要求一致。

## 7) 风险与后续建议
- 当前能力为 `partial`：
  - 仅覆盖单符号窄切片与有界时间窗，不包含全市场/全历史回补。
  - AKShare 上游字段或路由形态未来变化仍可能触发适配器硬失败（这是预期的契约保护行为）。
- 后续可在后续 handoff 中扩展：
  - 批量符号分页能力
  - 更广日期策略与增量同步策略
  - 针对上游路由形态差异的可选降级策略
