# TASK-026 Integration (DataHub AKShare A-share Instrument Master Adapter)

## Task
- Task ID: `TASK-026`
- Handoff: `coordination/handoffs/TASK-026_DATAHUB_AKSHARE_A_SHARE_INSTRUMENT_MASTER_ADAPTER.md`
- Review Input: `coordination/reviews/TASK-026_REVIEW.md`
- Integration Role: Integration Agent

## Integration Decision
- **Integrated (Accepted)**
- 当前 review 结论为 `ACCEPTED (CLOSURE-READY UNDER LIVE PASS GATE)`，满足集成前置条件。

## Scope and Compliance Check
- 本轮实现/测试变更位于 handoff 允许范围：
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `tests/datahub/test_akshare_a_share_instrument_master_adapter.py`
  - `tests/datahub/test_akshare_a_share_instrument_master_live.py`
  - `coordination/reports/TASK-026_REPORT.md`
- 未触达 controller 专属协调文件、future-phase 模块或 handoff 禁止路径。
- 备注：当前目录无可用 Git 工作树元信息，本次“本轮代码改动”按 handoff/report/review 与实际文件内容逐项核对。

## Integrated Content Summary
- 已集成 `AkshareAShareInstrumentMasterAdapter`（`DatasetName.INSTRUMENT_MASTER` 的 A-share 活跃标的切片）：
  - 路由顺序限定为 SH 主板、SH 科创、SZ A股、BJ A股；
  - 规范化输出到 `INSTRUMENT_MASTER` 合同字段，固定 `market=CN`、`asset_type=stock`、`currency=CNY`、`source=akshare_cn_hk_public_family`；
  - 生成规范 symbol（如 `600000.SH` / `000001.SZ` / `920000.BJ`），并支持规范/6位/raw-prefixed 的 symbols 过滤；
  - 活跃列表默认 `delist_date=9999-12-31`、`is_active=True`；
  - 保留重复去重与冲突重复硬失败边界，以及 malformed payload / required field / code prefix / date/source_ts 边界。
- 已集成 live gate 路径：
  - 默认 `QUANT_SYSTEM_LIVE_TESTS` 未开启时 skip；
  - live-enabled 下可执行真实源冒烟并保留契约失败为 hard fail。

## Verification During Integration
1. `python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_adapter.py`
   - 结果：`Ran 21 tests`，`OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_master_live.py`
   - 结果：`Ran 3 tests`，`OK (skipped=1)`（默认 gate 行为正确）

3. `python3 -m unittest tests/datahub/test_source.py`
   - 结果：`Ran 20 tests`，`OK`

4. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - 结果：`Ran 368 tests`，`OK (skipped=14)`

5. mandatory live-enabled 证据（来自 report/review）：
   - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_master_live.py`
   - 结果：PASS（report: `Ran 3 tests in 6.718s`, review: `Ran 3 tests in 8.492s`，均 `OK`）

## Conflicts and Gaps
- 代码集成冲突：**None**
- 阻断缺口：**None**

## Files Touched in This Integration Pass
- `coordination/integrations/TASK-026_INTEGRATION.md`

## State Update Recommendations (for Controller)
1. `TASK-026` 已具备收口条件，可按流程标记完成并关闭。
2. Phase 2 仍未完成（不切 phase），请派发当前 phase 的下一个可执行任务。
3. 后续维护建议保留：若 AKShare 上游列名发生漂移，需要同步更新字段候选键与离线用例，防止契约回归。
