from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareIndexDailyBarAdapter,
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


class _ProxyError(Exception):
    pass


class AkshareIndexDailyBarAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_multi_index_daily_bars(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 9, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_index_daily(symbol, start_date="", end_date=""):
            calls.append(
                {
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
            if symbol == "sh000300":
                return [
                    {
                        "date": "2024-01-03",
                        "open": "3300.00",
                        "high": 3350.0,
                        "low": "3280.00",
                        "close": 3320.0,
                        "volume": "123456",
                        "amount": "123456789.5",
                        "source_ts": "2024-01-03T15:00:00",
                    },
                    {
                        "date": "2024-01-03",
                        "open": "3300.00",
                        "high": 3350.0,
                        "low": "3280.00",
                        "close": 3320.0,
                        "volume": "123456",
                        "amount": "123456789.5",
                        "source_ts": "2024-01-03T16:00:00",
                    },
                ]
            if symbol == "sz399001":
                return [
                    {
                        "date": "2024-01-02",
                        "open": 9600.0,
                        "high": 9700.0,
                        "low": 9580.0,
                        "close": 9680.0,
                    }
                ]
            raise AssertionError(f"unexpected symbol: {symbol!r}")

        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=fake_fetch_index_daily,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.INDEX_DAILY_BARS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
            symbols=("399001.CN_INDEX", "000300.CN_INDEX", "000300"),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                request,
                fetched_at=datetime(2024, 1, 9, 10, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(
            calls,
            [
                {
                    "symbol": "sz399001",
                    "start_date": "20240102",
                    "end_date": "20240105",
                },
                {
                    "symbol": "sh000300",
                    "start_date": "20240102",
                    "end_date": "20240105",
                },
            ],
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [record["index_code"] for record in result.normalized_records],
            ["000300.CN_INDEX", "399001.CN_INDEX"],
        )
        first_record = result.normalized_records[0]
        self.assertEqual(first_record["index_name"], "CSI 300")
        self.assertEqual(first_record["market"], "CN_INDEX")
        self.assertEqual(first_record["trade_date"], "2024-01-03")
        self.assertEqual(first_record["open"], 3300.0)
        self.assertEqual(first_record["high"], 3350.0)
        self.assertEqual(first_record["low"], 3280.0)
        self.assertEqual(first_record["close"], 3320.0)
        self.assertEqual(first_record["volume"], 123456.0)
        self.assertEqual(first_record["amount"], 123456789.5)
        self.assertEqual(first_record["source_ts"], "2024-01-03T16:00:00")
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["source_route"], "fake_fetch_index_daily")
        self.assertEqual(first_record["schema_version"], "v1")
        self.assertEqual(first_record["ingested_at"], now.isoformat())

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.INDEX_DAILY_BARS, record),
                (),
            )

    def test_adapter_accepts_common_bare_codes_with_expected_source_symbol_mapping(self) -> None:
        samples = (
            ("000300", "sh000300", "000300.CN_INDEX"),
            ("000001", "sh000001", "000001.CN_INDEX"),
            ("000688", "sh000688", "000688.CN_INDEX"),
            ("000852", "sh000852", "000852.CN_INDEX"),
            ("000905", "sh000905", "000905.CN_INDEX"),
            ("000906", "sh000906", "000906.CN_INDEX"),
            ("399001", "sz399001", "399001.CN_INDEX"),
            ("399005", "sz399005", "399005.CN_INDEX"),
            ("399006", "sz399006", "399006.CN_INDEX"),
        )
        for user_symbol, expected_ak_symbol, expected_canonical in samples:
            calls: list[dict] = []

            def fake_fetch_index_daily(symbol, start_date="", end_date=""):
                calls.append(
                    {
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                )
                return [
                    {
                        "date": "2024-01-03",
                        "open": 3300.0,
                        "high": 3350.0,
                        "low": 3280.0,
                        "close": 3320.0,
                    }
                ]

            adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=fake_fetch_index_daily)
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=(user_symbol,),
                ),
            )
            with self.subTest(symbol=user_symbol):
                self.assertEqual(calls[0]["symbol"], expected_ak_symbol)
                self.assertEqual(calls[0]["start_date"], "20240102")
                self.assertEqual(calls[0]["end_date"], "20240105")
                self.assertEqual(
                    result.normalized_records[0]["index_code"],
                    expected_canonical,
                )

    def test_adapter_accepts_source_native_symbol_and_normalizes_output_code(self) -> None:
        calls: list[dict] = []

        def fake_fetch_index_daily(symbol, start_date="", end_date=""):
            calls.append(
                {
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
            return [
                {
                    "date": "2024-01-03",
                    "open": 3300.0,
                    "high": 3350.0,
                    "low": 3280.0,
                    "close": 3320.0,
                }
            ]

        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=fake_fetch_index_daily)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
                symbols=("sh000300",),
            ),
        )

        self.assertEqual(calls[0]["symbol"], "sh000300")
        self.assertEqual(result.normalized_records[0]["index_code"], "000300.CN_INDEX")
        self.assertEqual(result.normalized_records[0]["source_route"], "fake_fetch_index_daily")

    def test_adapter_accepts_hk_index_symbols_and_emits_hk_route_truth(self) -> None:
        hk_calls: list[dict] = []

        def fake_fetch_hk_index_daily(symbol):
            hk_calls.append({"symbol": symbol})
            return [
                {
                    "date": "2024-01-03",
                    "open": 17000.0,
                    "high": 17120.0,
                    "low": 16880.0,
                    "close": 17055.0,
                    "volume": 12345,
                    "amount": 67890,
                }
            ]

        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=lambda **kwargs: [],
            fetch_hk_index_daily=fake_fetch_hk_index_daily,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
                symbols=("HSI.HK_INDEX", "HSTECH.HK_INDEX"),
            ),
        )

        self.assertEqual(
            hk_calls,
            [{"symbol": "HSI"}, {"symbol": "HSTECH"}],
        )
        self.assertEqual(
            [record["index_code"] for record in result.normalized_records],
            ["HSI.HK_INDEX", "HSTECH.HK_INDEX"],
        )
        self.assertTrue(all(record["market"] == "HK_INDEX" for record in result.normalized_records))
        self.assertTrue(
            all(record["source_route"] == "fake_fetch_hk_index_daily" for record in result.normalized_records)
        )
        self.assertEqual(result.normalized_records[0]["index_name"], "Hang Seng Index")

    def test_adapter_uses_bare_code_for_index_zh_a_hist_route(self) -> None:
        calls: list[dict] = []

        def index_zh_a_hist(symbol, period, start_date="", end_date=""):
            calls.append(
                {
                    "symbol": symbol,
                    "period": period,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
            return [
                {
                    "date": "2024-01-03",
                    "open": 3300.0,
                    "high": 3350.0,
                    "low": 3280.0,
                    "close": 3320.0,
                }
            ]

        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=index_zh_a_hist)
        fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
                symbols=("000300",),
            ),
        )

        self.assertEqual(
            calls,
            [
                {
                    "symbol": "000300",
                    "period": "daily",
                    "start_date": "20240102",
                    "end_date": "20240105",
                }
            ],
        )

    def test_adapter_filters_wide_history_locally_when_source_ignores_date_arguments(self) -> None:
        calls: list[dict] = []

        def fake_fetch_index_daily(symbol):
            calls.append({"symbol": symbol})
            return [
                {"date": "2024-01-01", "open": 1, "high": 2, "low": 1, "close": 2},
                {"date": "2024-01-03", "open": 2, "high": 3, "low": 2, "close": 3},
                {"date": "2024-01-06", "open": 3, "high": 4, "low": 3, "close": 4},
            ]

        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=fake_fetch_index_daily)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
                symbols=("000300",),
            ),
        )

        self.assertEqual(calls, [{"symbol": "sh000300"}])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-03")

    def test_adapter_only_includes_optional_fields_when_values_are_valid(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": "3300",
                    "high": "3350",
                    "low": "3280",
                    "close": "3320",
                    "volume": "",
                    "amount": None,
                    "source_ts": "  ",
                }
            ],
            now_fn=lambda: datetime(2024, 1, 9, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
                symbols=("000300",),
            ),
        )
        record = result.normalized_records[0]
        self.assertNotIn("volume", record)
        self.assertNotIn("amount", record)
        self.assertNotIn("source_ts", record)

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(
            [
                {
                    "date": "20240103",
                    "open": 3300,
                    "high": 3350,
                    "low": 3280,
                    "close": 3320,
                    "volume": 1000,
                }
            ]
        )
        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=lambda **kwargs: payload,
            now_fn=lambda: datetime(2024, 1, 9, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
                symbols=("000300",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-03")
        self.assertEqual(result.normalized_records[0]["volume"], 1000.0)

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300",),
                ),
            )

    def test_adapter_requires_bounded_date_window(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        requests = (
            SourceRequest(
                dataset=DatasetName.INDEX_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000300",),
            ),
            SourceRequest(
                dataset=DatasetName.INDEX_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                symbols=("000300",),
            ),
            SourceRequest(
                dataset=DatasetName.INDEX_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                end_date=date(2024, 1, 5),
                symbols=("000300",),
            ),
        )
        for request in requests:
            with self.subTest(request=request), self.assertRaisesRegex(
                ValueError,
                "bounded date window|both start_date and end_date",
            ):
                fetch_source_result(adapter, request)

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires at least one index symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

    def test_adapter_rejects_stock_like_and_non_index_symbols_clearly(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        samples = (
            ("000300.SH", "stock-like symbol"),
            ("sh600000", "stock-like symbol"),
            ("510300", "ETF/fund symbol"),
            ("510300.ETF_CN", "ETF/fund symbol"),
            ("00700.HK", "Hong Kong stock symbol"),
            ("ABCDEF", "Unsupported index code format"),
            ("FTSE.GLOBAL_INDEX", "Unsupported index market suffix"),
        )
        for symbol, expected_message in samples:
            with self.subTest(symbol=symbol), self.assertRaisesRegex(
                ValueError,
                expected_message,
            ):
                fetch_source_result(
                    adapter,
                    SourceRequest(
                        dataset=DatasetName.INDEX_DAILY_BARS,
                        source_name=AKSHARE_SOURCE_ID,
                        start_date=date(2024, 1, 2),
                        end_date=date(2024, 1, 5),
                        symbols=(symbol,),
                    ),
                )

    def test_adapter_rejects_mismatched_source_native_symbol(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        with self.assertRaisesRegex(
            ValueError,
            "Unsupported or mismatched source-native index symbol",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("sz000300",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=lambda **kwargs: {"date": "2024-01-03"}
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_missing_required_source_field(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 3300,
                    "high": 3350,
                    "low": 3280,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_invalid_trade_date_value(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=lambda **kwargs: [
                {
                    "date": "2024-13-03",
                    "open": 3300,
                    "high": 3350,
                    "low": 3280,
                    "close": 3320,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid trade date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_value(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": "bad",
                    "high": 3350,
                    "low": 3280,
                    "close": 3320,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid numeric value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_invalid_optional_numeric_value(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 3300,
                    "high": 3350,
                    "low": 3280,
                    "close": 3320,
                    "volume": "bad",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid numeric value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_invalid_optional_source_ts_value(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 3300,
                    "high": 3350,
                    "low": 3280,
                    "close": 3320,
                    "source_ts": "not-a-datetime",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid source_ts value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_invalid_ohlc_semantics(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 3300,
                    "high": 3270,
                    "low": 3280,
                    "close": 3320,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid OHLC range"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300",),
                ),
            )

    def test_adapter_fails_when_any_requested_symbol_has_no_usable_rows(self) -> None:
        def fake_fetch_index_daily(symbol, start_date="", end_date=""):
            if symbol == "sh000300":
                return [
                    {
                        "date": "2024-01-03",
                        "open": 3300,
                        "high": 3350,
                        "low": 3280,
                        "close": 3320,
                    }
                ]
            return [
                {
                    "date": "2024-01-01",
                    "open": 9600,
                    "high": 9700,
                    "low": 9580,
                    "close": 9680,
                }
            ]

        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=fake_fetch_index_daily)
        with self.assertRaisesRegex(ValueError, "no usable rows"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300", "399001"),
                ),
            )

    def test_adapter_wraps_route_unavailable_network_failures(self) -> None:
        def stock_zh_index_daily_tx(symbol, start_date="", end_date=""):
            raise _ProxyError("proxy down")

        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=stock_zh_index_daily_tx)
        with self.assertRaisesRegex(RuntimeError, "route unavailable") as context:
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300",),
                ),
            )

        message = str(context.exception)
        self.assertIn("stock_zh_index_daily_tx", message)
        self.assertIn("sh000300", message)

    def test_adapter_keeps_signature_incompatibility_as_hard_failure(self) -> None:
        def stock_zh_index_daily_tx(not_symbol):
            return []

        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=stock_zh_index_daily_tx)
        with self.assertRaisesRegex(
            RuntimeError,
            "does not accept required argument: route=stock_zh_index_daily_tx, field=symbol",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_unmapped_hk_index_symbol(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_hk_index_daily=lambda **kwargs: [])
        with self.assertRaisesRegex(
            ValueError,
            "Unsupported or unmapped Hong Kong benchmark index code",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                    symbols=("VHSI.HK_INDEX",),
                ),
            )

    def test_route_distinct_records_remain_distinguishable(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        records = adapter._dedupe_and_sort_records(
            [
                {
                    "index_code": "000300.CN_INDEX",
                    "index_name": "CSI 300",
                    "market": "CN_INDEX",
                    "trade_date": "2024-01-03",
                    "open": 1.0,
                    "high": 2.0,
                    "low": 1.0,
                    "close": 2.0,
                    "source": AKSHARE_SOURCE_ID,
                    "source_route": "route_a",
                    "ingested_at": "2024-01-09T10:00:00+00:00",
                    "schema_version": "v1",
                },
                {
                    "index_code": "000300.CN_INDEX",
                    "index_name": "CSI 300",
                    "market": "CN_INDEX",
                    "trade_date": "2024-01-03",
                    "open": 1.0,
                    "high": 2.0,
                    "low": 1.0,
                    "close": 2.0,
                    "source": AKSHARE_SOURCE_ID,
                    "source_route": "route_b",
                    "ingested_at": "2024-01-09T10:00:00+00:00",
                    "schema_version": "v1",
                },
            ]
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(
            {record["source_route"] for record in records},
            {"route_a", "route_b"},
        )


if __name__ == "__main__":
    unittest.main()
