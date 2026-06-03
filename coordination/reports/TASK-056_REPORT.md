# TASK-056 Report

## files changed
- `quant/datahub/adapters/tushare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_tushare_index_weight_history_adapter.py`
- `tests/datahub/test_tushare_index_weight_history_live.py`

## tests run
- `python3 -m unittest tests/datahub/test_tushare_index_weight_history_adapter.py`
  - `Ran 21 tests ... OK`
- `python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`
  - `Ran 3 tests ... OK (skipped=1)`
- `python3 -m unittest tests/datahub/test_source.py`
  - `Ran 20 tests ... OK`
- `python3 -m unittest tests/datahub/test_datasets.py`
  - `Ran 38 tests ... OK`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - `Ran 17 tests ... OK`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
  - `Ran 7 tests ... OK`
- `python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py`
  - `Ran 24 tests ... OK`
- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
  - `Ran 846 tests ... OK (skipped=37)`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`
  - `Ran 3 tests ... OK (skipped=1)`

## default network behavior
- Default tests remain offline-safe.
- Offline adapter tests use injected callables / local fixtures only.
- The live smoke test is gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skipped by default.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: `SKIP`
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`
- Root-cause evidence: `test_live_tushare_index_weight_history_smoke ... skipped 'TUSHARE_TOKEN is not set. Operator action required: export TUSHARE_TOKEN and rerun the live smoke test.'`
- Local prerequisite status checked during execution:
  - `TUSHARE_TOKEN_SET False`
  - local `tushare` SDK probe returned `MISSING`
- Interpretation:
  - repository code now has gated live smoke coverage
  - real-source coverage is not proven in this environment
  - capability truth was intentionally left conservative; `index_weight_history` was not moved from planned to partial

## deviations
- None.

## risks/follow-up
- Operator action required: install local `tushare` SDK and export `TUSHARE_TOKEN`, then rerun `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`.
- If the live smoke passes with real credentials, a follow-up execution/review cycle can update `index_weight_history` capability truth from `planned` to conservative `partial`.
- Current bounded adapter scope supports CSI 300 / `000300` aliases only; broader index-universe coverage remains future work.
