# TASK-109 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- `tests/datahub/test_datasets.py`

## implementation summary
- Hardened `AkshareAShareMajorActivityEventsAdapter` from single-day `stock_dzjy_mrmx` detail-only coverage to bounded date-window coverage that merges:
  - detail route `stock_dzjy_mrmx` as `event_type=block_trade`
  - symbol-date summary route `stock_dzjy_mrtj` as `event_type=block_trade_summary`
- Added explicit `source_route` truth on normalized `MAJOR_ACTIVITY_EVENTS` records.
- Preserved hard-fail behavior for unsupported dataset/symbols, malformed payloads, missing fields, invalid numerics, route signature mismatches, and normalization errors.
- Added summary-route unit normalization: `成交总量` and `成交总额` are converted from route-scale values to raw-share/raw-currency units so they stay contract-consistent with detail rows.
- Kept capability truth conservative at `partial`; updated capability/catalog wording to reflect bounded multi-day detail + summary route coverage without over-promoting breadth/history completeness.

## tests run
- `python3 -m unittest tests/datahub/test_akshare_a_share_major_activity_events_adapter.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py` -> PASS (`live` smoke skipped by default)
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
- `python3 -m unittest tests/datahub/test_datasets.py` -> PASS
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py` -> PASS

## default network behavior
- Default tests remain offline-safe.
- Adapter tests use injected fetch callables / local fixtures only.
- Live network stays gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Evidence:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py` finished `OK` on 2026-06-06.
  - Follow-up probe with the adapter fetched bounded window `2026-06-03` through `2026-06-05` and returned:
    - `record_count=548`
    - `routes=['stock_dzjy_mrmx', 'stock_dzjy_mrtj']`
    - `event_types=['block_trade', 'block_trade_summary']`
    - `date_min=2026-06-03`, `date_max=2026-06-05`
    - first sample: `symbol=000060.SZ`, `event_type=block_trade`, `source_route=stock_dzjy_mrmx`

## capability truth changed
- `a_share_major_activity_events` remains `partial`.
- Wording changed to reflect validated bounded date-window detail + symbol-date summary coverage with explicit route provenance.

## source route coverage and known limitations
- Implemented routes:
  - `stock_dzjy_mrmx`: participant-level block-trade detail rows
  - `stock_dzjy_mrtj`: symbol-date aggregate block-trade summary rows
- Current limitations:
  - still no broader non-block-trade major-activity taxonomy
  - still no proven no-credential second-source redundancy
  - longer-history continuity and broader venue/participant analytics remain incomplete
  - capability must stay `partial`

## deviations
- None.

## risks/follow-up
- Public AKShare / Eastmoney route availability may still vary by day/environment; live smoke now probes a bounded recent multi-day window and still hard-fails contract defects.
- If future work expands beyond block-trade routes, keep `MAJOR_ACTIVITY_EVENTS` taxonomy and `source_route` truth explicit instead of coalescing heterogeneous source facts.
