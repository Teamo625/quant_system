from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareHKValuationSnapshotAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceAdapter, SourceRequest, fetch_source_result


class _FakeDataFrame:
    def __init__(self, records):
        self._records = list(records)

    def to_dict(self, orient="records"):
        if orient != "records":
            raise ValueError("Only orient='records' is supported in test fixture.")
        return list(self._records)


def _build_eniu_fetch(indicator_payload_map):
    def _fetch(**kwargs):
        indicator = kwargs.get("indicator")
        if indicator not in indicator_payload_map:
            raise AssertionError(f"Unexpected indicator in fixture: {indicator!r}")
        payload = indicator_payload_map[indicator]
        if isinstance(payload, BaseException):
            raise payload
        return payload

    return _fetch


def _build_baidu_fetch(indicator_payload_map):
    def _fetch(**kwargs):
        indicator = kwargs.get("indicator")
        if indicator not in indicator_payload_map:
            raise AssertionError(f"Unexpected indicator in fixture: {indicator!r}")
        payload = indicator_payload_map[indicator]
        if isinstance(payload, BaseException):
            raise payload
        return payload

    return _fetch


def _default_eniu_payload_map():
    return {
        "市盈率": [{"date": "2026-05-20", "pe": 14.73}],
        "市净率": [{"date": "2026-05-20", "pb": 3.03}],
        "市值": [{"date": "2026-05-20", "market_value": 32182.1}],
        "股息率": [{"date": "2026-05-20", "dv": 0.67}],
    }


def _default_baidu_payload_map():
    return {
        "市盈率(TTM)": [{"date": "2026-05-20", "value": 13.1}],
        "市净率": [{"date": "2026-05-20", "value": 2.8}],
        "总市值": [{"date": "2026-05-20", "value": 30000.0}],
        "市销率(TTM)": [{"date": "2026-05-20", "value": 4.5}],
        "股息率(TTM)": [{"date": "2026-05-20", "value": 0.6}],
        "流通市值": [{"date": "2026-05-20", "value": 22000.0}],
    }


def _default_comparison_payload():
    return [
        {
            "代码": "00700",
            "市盈率-TTM": 20.0,
            "市净率-MRQ": 5.0,
            "市销率-TTM": 4.51,
        }
    ]


def _build_adapter(
    *,
    fetch_valuation_comparison=None,
    fetch_indicator_eniu=None,
    fetch_valuation_baidu=None,
    now_fn=None,
) -> AkshareHKValuationSnapshotAdapter:
    return AkshareHKValuationSnapshotAdapter(
        fetch_valuation_comparison=fetch_valuation_comparison,
        fetch_indicator_eniu=fetch_indicator_eniu,
        fetch_valuation_baidu=fetch_valuation_baidu,
        now_fn=now_fn,
    )


class AkshareHKValuationSnapshotAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(_default_eniu_payload_map()),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_valuation_snapshot(self) -> None:
        comparison_calls: list[dict[str, str]] = []
        eniu_calls: list[dict[str, str]] = []
        baidu_calls: list[dict[str, str]] = []
        now = datetime(2026, 5, 29, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_comparison(**kwargs):
            comparison_calls.append(kwargs)
            return [
                {
                    "代码": "00700",
                    "市盈率-TTM": 20.0,
                    "市净率-MRQ": 5.0,
                    "市销率-TTM": 4.5073,
                }
            ]

        def fake_eniu(**kwargs):
            eniu_calls.append(kwargs)
            payload = _default_eniu_payload_map()[kwargs["indicator"]]
            return payload

        def fake_baidu(**kwargs):
            baidu_calls.append(kwargs)
            payload = _default_baidu_payload_map()[kwargs["indicator"]]
            return payload

        adapter = _build_adapter(
            fetch_valuation_comparison=fake_comparison,
            fetch_indicator_eniu=fake_eniu,
            fetch_valuation_baidu=fake_baidu,
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
                fetched_at=datetime(2026, 5, 29, 10, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "00700.HK")
        self.assertEqual(record["market"], "HK")
        self.assertEqual(record["trade_date"], "2026-05-20")
        self.assertEqual(record["pe_ttm"], 14.73)
        self.assertEqual(record["pb"], 3.03)
        self.assertEqual(record["market_cap"], 3218210000000.0)
        self.assertEqual(record["dividend_yield"], 0.67)
        self.assertEqual(record["ps_ttm"], 4.5073)
        self.assertEqual(record["float_market_cap"], 2200000000000.0)
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(
            registry.validate_record(DatasetName.VALUATION_SNAPSHOT, record),
            (),
        )

        self.assertEqual(comparison_calls, [{"symbol": "00700"}])
        self.assertEqual(
            [item["symbol"] for item in eniu_calls],
            ["hk00700", "hk00700", "hk00700", "hk00700"],
        )
        self.assertTrue(all(item["symbol"] == "00700" for item in baidu_calls))

    def test_adapter_supports_dataframe_like_payloads(self) -> None:
        eniu_map = _default_eniu_payload_map()
        eniu_map["市盈率"] = _FakeDataFrame(eniu_map["市盈率"])
        eniu_map["市净率"] = _FakeDataFrame(eniu_map["市净率"])
        eniu_map["市值"] = _FakeDataFrame(eniu_map["市值"])
        eniu_map["股息率"] = _FakeDataFrame(eniu_map["股息率"])

        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _FakeDataFrame(_default_comparison_payload()),
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00005.HK",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "00005.HK")

    def test_symbol_normalization_accepts_canonical_and_raw_hk_code(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(_default_eniu_payload_map()),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        result_canonical = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(result_canonical.normalized_records[0]["symbol"], "00700.HK")

        result_raw = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700",),
            ),
        )
        self.assertEqual(result_raw.normalized_records[0]["symbol"], "00700.HK")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(_default_eniu_payload_map()),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_requires_exactly_one_symbol(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(_default_eniu_payload_map()),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        with self.assertRaisesRegex(ValueError, "requires exactly one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )
        with self.assertRaisesRegex(ValueError, "exactly one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK", "00005.HK"),
                ),
            )

    def test_adapter_rejects_invalid_a_share_etf_and_index_like_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(_default_eniu_payload_map()),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )
        with self.assertRaisesRegex(ValueError, "Unsupported HK symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("HSI.HK",),
                ),
            )
        with self.assertRaisesRegex(ValueError, "Unsupported HK symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.HK",),
                ),
            )

    def test_start_end_date_filtering_uses_normalized_trade_date(self) -> None:
        eniu_map = _default_eniu_payload_map()
        eniu_map["市盈率"] = [{"date": "2026-05-21", "pe": 14.73}]
        eniu_map["市净率"] = [{"date": "2026-05-21", "pb": 3.03}]
        eniu_map["市值"] = [{"date": "2026-05-21", "market_value": 32182.1}]
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )

        in_range = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
                start_date=date(2026, 5, 21),
                end_date=date(2026, 5, 21),
            ),
        )
        self.assertEqual(in_range.record_count, 1)

        out_range = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
                start_date=date(2026, 5, 22),
                end_date=date(2026, 5, 22),
            ),
        )
        self.assertEqual(out_range.record_count, 0)

    def test_source_unit_conversion_for_market_cap_is_deterministic(self) -> None:
        eniu_map = _default_eniu_payload_map()
        eniu_map["市值"] = [{"date": "2026-05-20", "market_value": "32182.1"}]
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["market_cap"], 3218210000000.0)

    def test_route_precedence_prefers_eniu_for_required_fields(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: [
                {"代码": "00700", "市盈率-TTM": 99.0, "市净率-MRQ": 99.0, "市销率-TTM": 9.9}
            ],
            fetch_indicator_eniu=_build_eniu_fetch(_default_eniu_payload_map()),
            fetch_valuation_baidu=_build_baidu_fetch(
                {
                    **_default_baidu_payload_map(),
                    "市盈率(TTM)": [{"date": "2026-05-20", "value": 88.0}],
                    "市净率": [{"date": "2026-05-20", "value": 88.0}],
                    "总市值": [{"date": "2026-05-20", "value": 1000.0}],
                }
            ),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        record = result.normalized_records[0]
        self.assertEqual(record["pe_ttm"], 14.73)
        self.assertEqual(record["pb"], 3.03)
        self.assertEqual(record["market_cap"], 3218210000000.0)
        self.assertEqual(record["ps_ttm"], 9.9)

    def test_optional_fields_can_be_omitted_without_placeholder_values(self) -> None:
        class ProxyError(Exception):
            pass

        eniu_map = _default_eniu_payload_map()
        eniu_map["股息率"] = ProxyError("optional indicator unavailable")
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: [{"代码": "00700"}],
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=_build_baidu_fetch(
                {
                    "市盈率(TTM)": ProxyError("optional route unavailable"),
                    "市净率": ProxyError("optional route unavailable"),
                    "总市值": ProxyError("optional route unavailable"),
                    "市销率(TTM)": ProxyError("optional route unavailable"),
                    "股息率(TTM)": ProxyError("optional route unavailable"),
                    "流通市值": ProxyError("optional route unavailable"),
                }
            ),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        record = result.normalized_records[0]
        self.assertNotIn("ps_ttm", record)
        self.assertNotIn("dividend_yield", record)
        self.assertNotIn("float_market_cap", record)

    def test_adapter_deduplicates_benign_duplicate_eniu_rows(self) -> None:
        eniu_map = _default_eniu_payload_map()
        eniu_map["市盈率"] = [
            {"date": "2026-05-20", "pe": 14.73},
            {"date": "2026-05-20", "pe": 14.73},
        ]
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["pe_ttm"], 14.73)

    def test_adapter_rejects_conflicting_duplicate_eniu_rows(self) -> None:
        eniu_map = _default_eniu_payload_map()
        eniu_map["市盈率"] = [
            {"date": "2026-05-20", "pe": 14.73},
            {"date": "2026-05-20", "pe": 14.80},
        ]
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate HK valuation source row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_comparison_rows(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: [
                {"代码": "00700", "市销率-TTM": 4.5},
                {"代码": "00700", "市销率-TTM": 4.6},
            ],
            fetch_indicator_eniu=_build_eniu_fetch(_default_eniu_payload_map()),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate HK valuation comparison row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        eniu_map = _default_eniu_payload_map()
        eniu_map["市值"] = {"date": "2026-05-20", "market_value": 32182.1}
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        eniu_map = _default_eniu_payload_map()
        eniu_map["市值"] = [1]
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields_in_required_metric_route(self) -> None:
        eniu_map = _default_eniu_payload_map()
        eniu_map["市值"] = [{"date": "2026-05-20"}]
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: [{"代码": "00700", "市销率-TTM": 4.5}],
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=lambda **kwargs: (_ for _ in ()).throw(ValueError("empty_payload")),
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_invalid_trade_date(self) -> None:
        eniu_map = _default_eniu_payload_map()
        eniu_map["市盈率"] = [{"date": "2026/13/40", "pe": 14.73}]
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        with self.assertRaisesRegex(ValueError, "Invalid trade_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_values(self) -> None:
        eniu_map = _default_eniu_payload_map()
        eniu_map["市净率"] = [{"date": "2026-05-20", "pb": "bad"}]
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(eniu_map),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        with self.assertRaisesRegex(ValueError, "Invalid pb value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_keeps_record_when_optional_routes_network_unavailable(self) -> None:
        class ProxyError(Exception):
            pass

        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down")),
            fetch_indicator_eniu=_build_eniu_fetch(_default_eniu_payload_map()),
            fetch_valuation_baidu=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down")),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "00700.HK")

    def test_adapter_wraps_required_route_unavailability_with_evidence(self) -> None:
        class ProxyError(Exception):
            pass

        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down")),
            fetch_indicator_eniu=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down")),
            fetch_valuation_baidu=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down")),
        )
        with self.assertRaisesRegex(RuntimeError, "routes unavailable for required metrics"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_does_not_mask_non_network_errors(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=lambda **kwargs: (_ for _ in ()).throw(ValueError("bad payload")),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        with self.assertRaisesRegex(ValueError, "bad payload"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_network_unavailable_classifier_boundaries(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_comparison=lambda **kwargs: _default_comparison_payload(),
            fetch_indicator_eniu=_build_eniu_fetch(_default_eniu_payload_map()),
            fetch_valuation_baidu=_build_baidu_fetch(_default_baidu_payload_map()),
        )
        self.assertTrue(
            adapter._is_hk_valuation_network_unavailable(  # pylint: disable=protected-access
                OSError(111, "connection refused to eastmoney route")
            )
        )
        self.assertFalse(
            adapter._is_hk_valuation_network_unavailable(  # pylint: disable=protected-access
                ValueError("schema parsing failed")
            )
        )


if __name__ == "__main__":
    unittest.main()
