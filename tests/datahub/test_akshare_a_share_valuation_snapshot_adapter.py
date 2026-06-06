from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareValuationSnapshotAdapter,
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


def _build_symbol_indicator_baidu_fetch(symbol_indicator_payload_map):
    def _fetch(**kwargs):
        symbol = kwargs.get("symbol")
        indicator = kwargs.get("indicator")
        key = (symbol, indicator)
        if key not in symbol_indicator_payload_map:
            raise AssertionError(f"Unexpected fixture lookup: {key!r}")
        payload = symbol_indicator_payload_map[key]
        if isinstance(payload, BaseException):
            raise payload
        return payload

    return _fetch


def _build_adapter(
    *,
    fetch_valuation_baidu=None,
    fetch_individual_info=None,
    fetch_valuation_comparison=None,
    now_fn=None,
) -> AkshareAShareValuationSnapshotAdapter:
    return AkshareAShareValuationSnapshotAdapter(
        fetch_valuation_baidu=fetch_valuation_baidu,
        fetch_individual_info=fetch_individual_info,
        fetch_valuation_comparison=fetch_valuation_comparison,
        now_fn=now_fn,
    )


def _default_indicator_payload_map():
    return {
        "市盈率(TTM)": [{"date": "2024-06-12", "value": 6.2}],
        "市净率": [{"date": "2024-06-12", "value": 0.95}],
        "总市值": [{"date": "2024-06-12", "value": 2984.2}],
        "市销率(TTM)": TypeError("'NoneType' object is not subscriptable"),
        "股息率(TTM)": TypeError("'NoneType' object is not subscriptable"),
    }


def _default_individual_info_payload():
    return [
        {"item": "总市值", "value": "300000000000"},
        {"item": "流通市值", "value": "210000000000"},
        {"item": "更新时间", "value": "2024-06-12 15:00:00"},
    ]


class AkshareAShareValuationSnapshotAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_valuation_snapshot(self) -> None:
        valuation_calls: list[dict[str, str]] = []
        comparison_calls: list[dict[str, str]] = []
        now = datetime(2024, 6, 12, 16, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["市销率(TTM)"] = [{"date": "2024-06-12", "value": 1.23}]
        indicator_payload_map["股息率(TTM)"] = [{"date": "2024-06-12", "value": "3.50"}]

        def fake_fetch_valuation_baidu(**kwargs):
            valuation_calls.append(kwargs)
            indicator = kwargs["indicator"]
            return indicator_payload_map[indicator]

        def fake_fetch_comparison(**kwargs):
            comparison_calls.append(kwargs)
            return [
                {
                    "代码": "600000",
                    "市销率-TTM": 9.99,
                    "股息率(TTM)": 9.99,
                }
            ]

        adapter = _build_adapter(
            fetch_valuation_baidu=fake_fetch_valuation_baidu,
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
            fetch_valuation_comparison=fake_fetch_comparison,
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
                    symbols=("600000.SH",),
                ),
                fetched_at=datetime(2024, 6, 12, 16, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "600000.SH")
        self.assertEqual(record["market"], "CN")
        self.assertEqual(record["trade_date"], "2024-06-12")
        self.assertEqual(record["pe_ttm"], 6.2)
        self.assertEqual(record["pb"], 0.95)
        self.assertEqual(record["ps_ttm"], 1.23)
        self.assertEqual(record["dividend_yield"], 3.5)
        self.assertEqual(record["market_cap"], 300000000000.0)
        self.assertEqual(record["float_market_cap"], 210000000000.0)
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(record["source_ts"], "2024-06-12T15:00:00")
        self.assertEqual(
            registry.validate_record(DatasetName.VALUATION_SNAPSHOT, record),
            (),
        )

        self.assertGreaterEqual(len(valuation_calls), 3)
        self.assertTrue(all(call["symbol"] == "600000" for call in valuation_calls))
        self.assertTrue(all(call["period"] == "近一年" for call in valuation_calls))
        self.assertEqual(comparison_calls, [{"symbol": "SH600000"}])

    def test_adapter_supports_dataframe_like_payloads(self) -> None:
        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["市盈率(TTM)"] = _FakeDataFrame(
            [{"date": "2024-06-12", "value": 6.2}]
        )
        indicator_payload_map["市净率"] = _FakeDataFrame(
            [{"date": "2024-06-12", "value": 0.95}]
        )
        indicator_payload_map["总市值"] = _FakeDataFrame(
            [{"date": "2024-06-12", "value": 2984.2}]
        )

        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: _FakeDataFrame(_default_individual_info_payload()),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "000001.SZ")

    def test_symbol_normalization_accepts_canonical_and_raw_6_digit(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )

        result_canonical = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(result_canonical.normalized_records[0]["symbol"], "600000.SH")

        result_raw = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000",),
            ),
        )
        self.assertEqual(result_raw.normalized_records[0]["symbol"], "600000.SH")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_requires_at_least_one_symbol(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        with self.assertRaisesRegex(ValueError, "requires at least one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_supports_multi_symbol_latest_snapshot_batches(self) -> None:
        valuation_calls: list[tuple[str, str]] = []
        comparison_calls: list[dict[str, str]] = []

        indicator_payload_map = {
            ("600000", "市盈率(TTM)"): [{"date": "2024-06-12", "value": 6.2}],
            ("600000", "市净率"): [{"date": "2024-06-12", "value": 0.95}],
            ("600000", "总市值"): [{"date": "2024-06-12", "value": 2984.2}],
            ("600000", "市销率(TTM)"): [{"date": "2024-06-12", "value": 1.23}],
            ("600000", "股息率(TTM)"): [{"date": "2024-06-12", "value": 3.5}],
            ("000001", "市盈率(TTM)"): [{"date": "2024-06-11", "value": 11.2}],
            ("000001", "市净率"): [{"date": "2024-06-11", "value": 1.55}],
            ("000001", "总市值"): [{"date": "2024-06-11", "value": 1450.0}],
            ("000001", "市销率(TTM)"): TypeError("'NoneType' object is not subscriptable"),
            ("000001", "股息率(TTM)"): TypeError("'NoneType' object is not subscriptable"),
        }

        def fake_fetch_valuation_baidu(**kwargs):
            valuation_calls.append((kwargs["symbol"], kwargs["indicator"]))
            return _build_symbol_indicator_baidu_fetch(indicator_payload_map)(**kwargs)

        def fake_fetch_individual_info(**kwargs):
            symbol = kwargs["symbol"]
            if symbol == "600000":
                return _default_individual_info_payload()
            return [
                {"item": "总市值", "value": "155000000000"},
                {"item": "流通市值", "value": "90000000000"},
                {"item": "更新时间", "value": "2024-06-11 15:00:00"},
            ]

        def fake_fetch_comparison(**kwargs):
            comparison_calls.append(kwargs)
            if kwargs["symbol"] == "SH600000":
                return [{"代码": "600000", "市销率-TTM": 9.99}]
            return [{"代码": "000001", "股息率(TTM)": 2.25}]

        adapter = _build_adapter(
            fetch_valuation_baidu=fake_fetch_valuation_baidu,
            fetch_individual_info=fake_fetch_individual_info,
            fetch_valuation_comparison=fake_fetch_comparison,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ", "600000.SH"),
            ),
        )

        self.assertEqual(result.record_count, 2)
        records = list(result.normalized_records)
        self.assertEqual(
            [record["symbol"] for record in records],
            ["000001.SZ", "600000.SH"],
        )
        self.assertEqual(records[0]["trade_date"], "2024-06-11")
        self.assertEqual(records[0]["market_cap"], 155000000000.0)
        self.assertEqual(records[0]["float_market_cap"], 90000000000.0)
        self.assertEqual(records[0]["dividend_yield"], 2.25)
        self.assertEqual(records[1]["trade_date"], "2024-06-12")
        self.assertEqual(records[1]["market_cap"], 300000000000.0)
        self.assertEqual(records[1]["ps_ttm"], 1.23)
        self.assertEqual(
            sorted(valuation_calls),
            sorted(
                [
                    ("600000", "市盈率(TTM)"),
                    ("600000", "市净率"),
                    ("600000", "总市值"),
                    ("600000", "市销率(TTM)"),
                    ("600000", "股息率(TTM)"),
                    ("000001", "市盈率(TTM)"),
                    ("000001", "市净率"),
                    ("000001", "总市值"),
                    ("000001", "市销率(TTM)"),
                    ("000001", "股息率(TTM)"),
                ]
            ),
        )
        self.assertEqual(
            comparison_calls,
            [{"symbol": "SZ000001"}, {"symbol": "SH600000"}],
        )

    def test_adapter_rejects_invalid_hk_etf_and_index_like_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )

        with self.assertRaisesRegex(ValueError, "market suffix|Invalid symbol filter format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "code prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Index symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("399001.SZ",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SZ",),
                ),
            )

    def test_start_end_date_filtering_uses_normalized_trade_date(self) -> None:
        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["市盈率(TTM)"] = [{"date": "2024-06-11", "value": 6.2}]
        indicator_payload_map["市净率"] = [{"date": "2024-06-11", "value": 0.95}]
        indicator_payload_map["总市值"] = [{"date": "2024-06-11", "value": 2984.2}]
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )

        in_range = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2024, 6, 11),
                end_date=date(2024, 6, 11),
            ),
        )
        self.assertEqual(in_range.record_count, 1)

        out_range = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2024, 6, 12),
                end_date=date(2024, 6, 12),
            ),
        )
        self.assertEqual(out_range.record_count, 0)

    def test_older_start_date_selects_broader_primary_route_period(self) -> None:
        valuation_calls: list[dict[str, str]] = []
        now = datetime(2024, 6, 12, 16, 0, 0, tzinfo=timezone.utc)
        indicator_payload_map = {
            "市盈率(TTM)": [
                {"date": "2022-06-01", "value": 5.8},
                {"date": "2024-06-12", "value": 6.2},
            ],
            "市净率": [
                {"date": "2022-06-01", "value": 0.88},
                {"date": "2024-06-12", "value": 0.95},
            ],
            "总市值": [
                {"date": "2022-06-01", "value": 2500.0},
                {"date": "2024-06-12", "value": 2984.2},
            ],
            "市销率(TTM)": TypeError("'NoneType' object is not subscriptable"),
            "股息率(TTM)": TypeError("'NoneType' object is not subscriptable"),
        }

        def fake_fetch_valuation_baidu(**kwargs):
            valuation_calls.append(kwargs)
            payload = indicator_payload_map[kwargs["indicator"]]
            if isinstance(payload, BaseException):
                raise payload
            return payload

        adapter = _build_adapter(
            fetch_valuation_baidu=fake_fetch_valuation_baidu,
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
            now_fn=lambda: now,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2022, 6, 1),
                end_date=date(2024, 6, 12),
            ),
        )

        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [record["trade_date"] for record in result.normalized_records],
            ["2022-06-01", "2024-06-12"],
        )
        self.assertGreaterEqual(len(valuation_calls), 3)
        self.assertTrue(all(call["period"] == "近三年" for call in valuation_calls))

    def test_older_end_date_without_start_date_still_selects_broader_period(self) -> None:
        valuation_calls: list[dict[str, str]] = []
        now = datetime(2024, 6, 12, 16, 0, 0, tzinfo=timezone.utc)
        indicator_payload_map = {
            "市盈率(TTM)": [
                {"date": "2022-06-01", "value": 5.8},
                {"date": "2024-06-12", "value": 6.2},
            ],
            "市净率": [
                {"date": "2022-06-01", "value": 0.88},
                {"date": "2024-06-12", "value": 0.95},
            ],
            "总市值": [
                {"date": "2022-06-01", "value": 2500.0},
                {"date": "2024-06-12", "value": 2984.2},
            ],
            "市销率(TTM)": TypeError("'NoneType' object is not subscriptable"),
            "股息率(TTM)": TypeError("'NoneType' object is not subscriptable"),
        }

        def fake_fetch_valuation_baidu(**kwargs):
            valuation_calls.append(kwargs)
            payload = indicator_payload_map[kwargs["indicator"]]
            if isinstance(payload, BaseException):
                raise payload
            return payload

        adapter = _build_adapter(
            fetch_valuation_baidu=fake_fetch_valuation_baidu,
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
            now_fn=lambda: now,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                end_date=date(2022, 6, 1),
            ),
        )

        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2022-06-01")
        self.assertGreaterEqual(len(valuation_calls), 3)
        self.assertTrue(all(call["period"] == "近三年" for call in valuation_calls))

    def test_bounded_date_window_returns_series_and_latest_only_fields_stay_bounded(self) -> None:
        indicator_payload_map = {
            "市盈率(TTM)": [
                {"date": "2024-06-10", "value": 6.0},
                {"date": "2024-06-11", "value": 6.1},
                {"date": "2024-06-12", "value": 6.2},
            ],
            "市净率": [
                {"date": "2024-06-10", "value": 0.9},
                {"date": "2024-06-11", "value": 0.92},
                {"date": "2024-06-12", "value": 0.95},
            ],
            "总市值": [
                {"date": "2024-06-10", "value": 2900.0},
                {"date": "2024-06-11", "value": 2950.0},
                {"date": "2024-06-12", "value": 2984.2},
            ],
            "市销率(TTM)": [
                {"date": "2024-06-10", "value": 1.1},
                {"date": "2024-06-11", "value": 1.15},
                {"date": "2024-06-12", "value": 1.23},
            ],
            "股息率(TTM)": TypeError("'NoneType' object is not subscriptable"),
        }
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: [
                {"item": "总市值", "value": "300000000000"},
                {"item": "流通市值", "value": "210000000000"},
                {"item": "更新时间", "value": "2024-06-12 15:00:00"},
            ],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2024, 6, 10),
                end_date=date(2024, 6, 12),
            ),
        )

        self.assertEqual(result.record_count, 3)
        records = list(result.normalized_records)
        self.assertEqual(
            [record["trade_date"] for record in records],
            ["2024-06-10", "2024-06-11", "2024-06-12"],
        )
        self.assertNotIn("float_market_cap", records[0])
        self.assertNotIn("source_ts", records[0])
        self.assertEqual(records[0]["market_cap"], 290000000000.0)
        self.assertEqual(records[1]["market_cap"], 295000000000.0)
        self.assertEqual(records[2]["market_cap"], 300000000000.0)
        self.assertEqual(records[2]["float_market_cap"], 210000000000.0)
        self.assertEqual(records[2]["source_ts"], "2024-06-12T15:00:00")

    def test_duplicate_requested_symbols_are_deduplicated_before_fetch(self) -> None:
        valuation_calls: list[tuple[str, str]] = []

        def fake_fetch_valuation_baidu(**kwargs):
            valuation_calls.append((kwargs["symbol"], kwargs["indicator"]))
            return _build_baidu_fetch(_default_indicator_payload_map())(**kwargs)

        adapter = _build_adapter(
            fetch_valuation_baidu=fake_fetch_valuation_baidu,
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH", "600000", "600000.SH"),
            ),
        )

        self.assertEqual(result.record_count, 1)
        self.assertEqual(len(valuation_calls), 5)

    def test_market_cap_precedence_prefers_individual_info_over_baidu(self) -> None:
        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["总市值"] = [{"date": "2024-06-12", "value": 1.0}]
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: [
                {"item": "总市值", "value": "500000000000"},
                {"item": "流通市值", "value": "200000000000"},
            ],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        record = result.normalized_records[0]
        self.assertEqual(record["market_cap"], 500000000000.0)
        self.assertEqual(record["float_market_cap"], 200000000000.0)

    def test_source_unit_conversion_for_market_cap_fields_is_deterministic(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: [
                {"item": "总市值", "value": "3000亿"},
                {"item": "流通市值", "value": "1800亿元"},
            ],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        record = result.normalized_records[0]
        self.assertEqual(record["market_cap"], 300000000000.0)
        self.assertEqual(record["float_market_cap"], 180000000000.0)

    def test_optional_metrics_can_be_omitted_without_placeholder_values(self) -> None:
        now = datetime(2024, 6, 12, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: [
                {"item": "总市值", "value": 300000000000},
                {"item": "流通市值", "value": 200000000000},
            ],
            now_fn=lambda: now,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertNotIn("ps_ttm", record)
        self.assertNotIn("dividend_yield", record)
        self.assertEqual(
            registry.validate_record(DatasetName.VALUATION_SNAPSHOT, record),
            (),
        )

    def test_adapter_deduplicates_benign_duplicate_indicator_rows(self) -> None:
        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["市盈率(TTM)"] = [
            {"date": "2024-06-12", "value": 6.2},
            {"date": "2024-06-12", "value": 6.2},
        ]
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["pe_ttm"], 6.2)

    def test_adapter_rejects_conflicting_duplicate_indicator_rows(self) -> None:
        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["市盈率(TTM)"] = [
            {"date": "2024-06-12", "value": 6.2},
            {"date": "2024-06-12", "value": 6.3},
        ]
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share valuation source row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(
                {
                    "市盈率(TTM)": {"date": "2024-06-12", "value": 6.2},
                    "市净率": [{"date": "2024-06-12", "value": 0.95}],
                    "总市值": [{"date": "2024-06-12", "value": 2984.2}],
                    "市销率(TTM)": TypeError("'NoneType' object is not subscriptable"),
                    "股息率(TTM)": TypeError("'NoneType' object is not subscriptable"),
                }
            ),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["市盈率(TTM)"] = [1]
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["市盈率(TTM)"] = [{"date": "2024-06-12"}]
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_invalid_trade_date(self) -> None:
        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["市盈率(TTM)"] = [{"date": "2024/06/12", "value": 6.2}]
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        with self.assertRaisesRegex(ValueError, "Invalid trade_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_values(self) -> None:
        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["市净率"] = [{"date": "2024-06-12", "value": "bad"}]
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        with self.assertRaisesRegex(ValueError, "Invalid pb value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_allows_missing_float_market_cap_without_placeholder(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: [
                {"item": "总市值", "value": 300000000000},
            ],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertNotIn("float_market_cap", record)
        self.assertEqual(record["market_cap"], 300000000000.0)

    def test_adapter_rejects_conflicting_duplicate_comparison_rows(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
            fetch_valuation_comparison=lambda **kwargs: [
                {"代码": "600000", "市销率-TTM": 1.1},
                {"代码": "600000", "市销率-TTM": 1.2},
            ],
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share valuation comparison row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_keeps_record_when_network_related_individual_route_fails(self) -> None:
        class ProxyError(Exception):
            pass

        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down")),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "600000.SH")
        self.assertEqual(record["market"], "CN")
        self.assertIn("market_cap", record)
        self.assertNotIn("float_market_cap", record)

    def test_adapter_rejects_missing_required_market_cap_after_merge(self) -> None:
        indicator_payload_map = _default_indicator_payload_map()
        indicator_payload_map["总市值"] = [{"date": "2024-06-12"}]

        class ProxyError(Exception):
            pass

        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(indicator_payload_map),
            fetch_individual_info=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down")),
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_does_not_mask_non_network_primary_route_errors(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=lambda **kwargs: (_ for _ in ()).throw(ValueError("bad payload")),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        with self.assertRaisesRegex(ValueError, "bad payload"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.VALUATION_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_network_unavailable_classifier_boundaries(self) -> None:
        adapter = _build_adapter(
            fetch_valuation_baidu=_build_baidu_fetch(_default_indicator_payload_map()),
            fetch_individual_info=lambda **kwargs: _default_individual_info_payload(),
        )
        self.assertTrue(
            adapter._is_valuation_network_unavailable(  # pylint: disable=protected-access
                OSError(111, "connection refused to push2.eastmoney.com")
            )
        )
        self.assertFalse(
            adapter._is_valuation_network_unavailable(  # pylint: disable=protected-access
                ValueError("schema parsing failed")
            )
        )


if __name__ == "__main__":
    unittest.main()
