# TASK-022 Execution Report (AKShare News Events Adapter)

## Task

- Task ID: `TASK-022`
- Active Handoff: `coordination/handoffs/TASK-022_DATAHUB_AKSHARE_NEWS_EVENTS_ADAPTER.md`
- Dataset Scope: `DatasetName.NEWS_EVENTS` only
- Module Scope: DataHub only

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_news_events_adapter.py`
- `tests/datahub/test_akshare_news_events_live.py`
- `coordination/reports/TASK-022_REPORT.md`

## Implementation Summary

Implemented `AkshareNewsEventsAdapter` with narrow `NEWS_EVENTS` scope and no-credential AKShare public route (`futures_news_shmet`).

Key behaviors delivered:

1. `DatasetName.NEWS_EVENTS` only; unsupported datasets hard-fail.
2. Symbol filter behavior is explicit for selected route:
   - non-empty `symbols` is rejected with clear error (route does not support symbol-scoped news in this task design).
3. Payload handling:
   - supports DataFrame-like and list-of-mapping payloads;
   - malformed payload shape and malformed rows hard-fail.
4. Normalization:
   - required fields normalized: `news_id`, `region`, `publish_time`, `title`, `source_name`, `source`, `ingested_at`, `schema_version`;
   - optional fields normalized when present: `related_symbol`, `sentiment_label`, `summary`, `url`, `source_ts`;
   - `publish_time` supports datetime/date/date-string inputs; date-only values normalize to deterministic midnight.
5. Deterministic id:
   - when source id is missing, `news_id` is deterministically generated from stable fields (`title`, `publish_time`, `source_name`, `url`, `related_symbol`) using stable SHA1 digest prefix.
6. Duplicate boundary:
   - benign duplicate rows are deduped;
   - conflicting rows for same `news_id` hard-fail.
7. Date window filter:
   - `start_date` / `end_date` filtering is applied by normalized `publish_time` date.
8. Live smoke test:
   - added gated live test with environment-unavailable classifier and schema validation.

## Tests Run

1. `python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py`  
   - Result: PASS (`Ran 15 tests`)

2. `python3 -m unittest -v tests/datahub/test_akshare_news_events_live.py`  
   - Result: PASS (`Ran 3 tests`, `OK (skipped=1)` default live gate behavior)

3. `python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py tests/datahub/test_akshare_index_constituents_adapter.py tests/datahub/test_akshare_index_adapter.py tests/datahub/test_akshare_hk_adapter.py tests/datahub/test_akshare_fund_nav_adapter.py tests/datahub/test_akshare_adapter.py`  
   - Result: PASS (`Ran 113 tests`)

4. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`  
   - Result: PASS (`Ran 294 tests`, `OK (skipped=11)`)

5. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_news_events_live.py`  
   - Result: PASS (`Ran 3 tests in 0.841s`, `OK`)

## Default Network Behavior

- Default tests remain offline-safe.
- New adapter tests use injected payload callables only.
- Live smoke is explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.

## Live-Enabled Result (Mandatory)

- Live-enabled status: `PASS`
- Evidence:
  - command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_news_events_live.py`
  - output tail: `Ran 3 tests in 0.841s` and `OK`

## Deviations From Handoff

- None.
- Scope remained within DataHub and `NEWS_EVENTS`.

## Risks / Follow-Up

1. Current adapter intentionally uses one bounded no-credential public route (`futures_news_shmet`); source field variability may evolve with upstream changes.
2. Symbol-scoped news for equities is intentionally out of scope for this task and currently rejected; if future handoff requires symbol-scoped behavior, route strategy and symbol contract should be extended in a dedicated task.
