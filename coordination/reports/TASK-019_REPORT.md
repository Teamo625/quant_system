# TASK-019 Report (Live PASS Rework)

## Task

- Task ID: `TASK-019`
- Handoff: `coordination/handoffs/TASK-019_DATAHUB_SECTOR_MEMBERSHIP_LIVE_PASS_REWORK.md`
- Role: 5.3 execution window

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `coordination/reports/TASK-019_REPORT.md`

## Rework Summary

### 1) Live PASS blocker fixed at repository level

对 `AkshareSectorMembershipAdapter` 的 THS fallback 页面抓取实现做了最小且针对性的修复：

- 将 THS detail page 抓取从 `urllib` 路径改为 `requests.get(...)` 路径
- 保留超时与 UA 设置
- 保留 HTTP 状态检查（`raise_for_status()`）
- 保留编码稳健性（`response.encoding` / `apparent_encoding`）

该改动的目的：规避当前环境下 `urllib` 链路出现的 TLS 证书校验失败，确保 EM 主路由失败后 THS fallback 仍可在当前环境拿到成分数据，从而让 live-enabled 冒烟达成 `PASS`。

### 2) Contract and safety boundaries preserved

本轮未放宽测试语义，且保持以下边界不退化：

- 非网络类 adapter/schema 错误仍 hard-fail
- `SECTOR_MEMBERSHIP` 契约归一化逻辑未放宽
- duplicate 边界策略未放宽（benign dedupe / conflicting hard-fail）
- 默认测试路径仍离线安全，live 仍需 `QUANT_SYSTEM_LIVE_TESTS=1`

## Required Investigation Evidence

### A. Previous skip chain reproduction (before fix)

在本轮修复前复现实测（同环境）可见：

- EM industry membership: `ProxyError` (`17.push2.eastmoney.com`)
- EM concept membership: `ProxyError` (`79.push2.eastmoney.com`)
- THS fallback (old urllib path): chained `SSLCertVerificationError` (`CERTIFICATE_VERIFY_FAILED`)

### B. Candidate route feasibility in current environment

本轮复核结果：

- EM 成分主路由在当前环境仍失败（`ProxyError`）
- THS fallback 路由在当前环境可成功取回 membership rows（示例 `INDUSTRY:小金属` 返回 20 条）

说明当前环境下“可通过路径”明确存在：

- 主路由失败 -> THS fallback（requests fetch + HTML extract）-> 归一化通过

### C. Required PASS evidence

命令：

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`

结果：

- `test_live_akshare_sector_membership_smoke ... ok`
- `Ran 1 test in 6.701s`
- `OK`

满足本次 handoff 的 strict PASS gate。

## Tests Run

### Required tests

1. `python3 -m unittest tests/datahub/test_akshare_sector_membership_adapter.py`
- Result: `Ran 26 tests`, `OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`
- Result: `Ran 1 test`, `OK (skipped=1)`

3. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- Result: `Ran 223 tests`, `OK (skipped=8)`

4. `python3 -m unittest tests/datahub/test_akshare_sector_master_adapter.py`
- Result: `Ran 18 tests`, `OK`

5. `python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`
- Result: `Ran 25 tests`, `OK`

6. `python3 -m unittest tests/datahub/test_akshare_index_adapter.py`
- Result: `Ran 21 tests`, `OK`

7. `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`
- Result: `Ran 17 tests`, `OK`

8. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- Result: `Ran 10 tests`, `OK`

9. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`
- Result: `Ran 1 test`, `OK`

## Default Network Behavior

- 默认测试路径保持离线（未新增隐式网络调用）。
- live 路径仍显式门控：`QUANT_SYSTEM_LIVE_TESTS=1`。

## Live Smoke Status

- default run status: `SKIP`（门控关闭，预期）
- live-enabled run status: `PASS`

## Deviations From Handoff

- No deviations.

## Risks / Follow-up

1. EM 成分接口在当前环境仍受代理链路影响（`push2.eastmoney.com` 相关 `ProxyError`）。
2. 当前 live PASS 依赖 THS fallback 可用性；若 THS 上游页面结构显著变化，可能需要窄范围解析维护。

## Closure-Ready Assessment

- 在当前 strict PASS gate 下：**Closure-ready**。
