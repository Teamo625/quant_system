# TASK-132 Review

## Findings

1. `a_share_northbound_flow` 的 capability/catalog 文案仍然过度表述了 fallback truth。`quant/datahub/source_capabilities.py:276-288` 和 `quant/datahub/source_catalog.py:443-446` 都把 `stock_hsgt_individual_detail_em` 写成已成立的 fallback coverage，但执行报告同时明确记录该路由当前 live 仍因 upstream `TypeError: 'NoneType' object is not subscriptable` 而未能证明可用，只能算“尝试 fallback / 当前未证实”的保守 truth（`coordination/reports/TASK-132_REPORT.md:37`, `coordination/reports/TASK-132_REPORT.md:64`）。这会让 source truth 强于实际 live evidence，不满足 handoff 要求的“cannot be silently treated as complete”。

## Decision

- Rejected pending a focused truth rework for northbound fallback wording.
- Independent verification passed for `python3 -m unittest tests.datahub.test_datasets tests.datahub.test_source_capabilities tests.datahub.test_source_catalog tests.datahub.test_akshare_a_share_northbound_flow_adapter tests.datahub.test_akshare_a_share_limit_up_down_adapter tests.datahub.test_akshare_a_share_financial_data_adapter`.
- Independent verification passed for `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_northbound_flow_live tests.datahub.test_akshare_a_share_limit_up_down_live tests.datahub.test_akshare_a_share_financial_data_live`.

## Closure Status

- decision: rejected_or_blocked
- controller_closure_allowed: no
- default_tests_offline_safe: yes
- live_enabled_result: SKIP
- rework_required: yes

## Closure Readiness

- Controller 现在不应收口；需先修正文案，使 northbound fallback truth 与 live evidence 一致。
- 默认测试离线安全；本次复核复跑的离线/默认门控测试通过。
- live-enabled 结果整体记为 `SKIP`：`limit_up_down` 与 `financial_statements` 为 PASS，但 `northbound_flow` 的 material route change 仍只拿到 upstream-broken SKIP。
- 当前阻塞项是 source truth 过度表述，不是 phase 越界或默认测试联网；完成 focused truth rework 后需要新的 Review 再决定是否允许 Controller 收口。

## Required Follow-up

- 将 `a_share_northbound_flow` 在 capability/catalog 中改写为“primary route plus attempted/unproven bounded fallback; fallback currently upstream-broken in accepted live evidence”，不要表述为已成立 coverage。
