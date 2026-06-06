# TASK-098 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_hk_corporate_actions_live.py`
- `coordination/reports/TASK-098_REPORT.md`

## tests run
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest tests/datahub/test_datasets.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py` -> PASS (`live` smoke skipped by default; classifier tests passed)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_adapter.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py` -> PASS (`live` smoke skipped by default; classifier tests passed)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py` -> PASS

## default network behavior
- Default/offline tests remain network-safe.
- Adapter tests use injected fixtures only.
- A-share and HK live smoke tests still skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
- HK corporate-actions live-enabled result: PASS.
- Evidence:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py` passed end to end.
  - Direct live sample via `AkshareHKCorporateActionsAdapter` for `00700.HK`, `start_date=2000-01-01`, `end_date=<today>` returned `record_count=27`.
  - First normalized live record validated against `DatasetName.CORPORATE_ACTIONS` with `validation=()`.
  - First live record fields observed:
    - `event_type=dividend`
    - `action_family=dividend_distribution`
    - `source_route=stock_hk_dividend_payout_em`
    - `event_date=2005-04-19`
    - `symbol=00700.HK`
- No network/proxy/DNS/TLS/upstream skip occurred in the enabled HK rerun.
- A-share live-enabled result in this rework: not rerun. Reason: shared schema requirement was preserved unchanged and the A-share adapter path was not modified by this handoff. Prior TASK-098 review context already recorded A-share live PASS, and the required default-gated A-share live test still passed with the smoke skipped by default.

## regression and fix
- Review regression: shared `DatasetName.CORPORATE_ACTIONS` schema globally required top-level `action_family` and `source_route`, but HK corporate-actions records still emitted neither field.
- Chosen fix: keep the shared schema globally required and make HK records satisfy it truthfully.
- Implementation:
  - HK fetch now carries the actual route name (`stock_hk_dividend_payout_em` or fallback `stock_hk_fhpx_detail_ths`) into normalization.
  - HK normalized records now emit top-level `action_family=dividend_distribution` and route-backed `source_route`.
  - HK value payload now also carries the same taxonomy fields for parity with the A-share path.
  - HK top-level `announcement_date` and `ex_date` are copied only when source-backed; no synthetic `record_date` or other event details were fabricated.

## schema status and validation outcome
- Shared `CORPORATE_ACTIONS` schema remains globally required for top-level `action_family` and `source_route`.
- A-share TASK-098 taxonomy evidence remains intact; no A-share adapter or schema logic changed in this rework.
- HK corporate-actions records now validate under the shared schema in both fixture-backed tests and live-enabled smoke.

## deviations
- None.

## risks/follow-up
- HK coverage in this adapter remains dividend-focused; this rework fixed the shared-contract rollout only and did not expand HK corporate-action family breadth.
- Live HK sample showed source-backed `announcement_date` can be later than the first returned `event_date`; this was preserved as upstream truth and not normalized away.
