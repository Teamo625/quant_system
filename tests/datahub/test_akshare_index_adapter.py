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


class AkshareIndexDailyBarAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_index_daily_bars(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 9, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_index_daily(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "date": "2024-01-03",
                    "open": "3300.00",
                    "high": 3350.0,
                    "low": "3280.00",
                    "close": 3320.0,
                    "volume": "123456",
                    "amount": "123456789.5",
                    "source_ts": "2024-01-03T16:00:00",
                }
            ]

        adapter = AkshareIndexDailyBarAdapter(
            fetch_index_daily=fake_fetch_index_daily,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.INDEX_DAILY_BARS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
            symbols=("000300.CN_INDEX",),
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

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["symbol"], "sh000300")
        self.assertEqual(calls[0]["start_date"], "20240102")
        self.assertEqual(calls[0]["end_date"], "20240105")

        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["index_code"], "000300.CN_INDEX")
        self.assertEqual(record["index_name"], "CSI 300")
        self.assertEqual(record["market"], "CN_INDEX")
        self.assertEqual(record["trade_date"], "2024-01-03")
        self.assertEqual(record["open"], 3300.0)
        self.assertEqual(record["high"], 3350.0)
        self.assertEqual(record["low"], 3280.0)
        self.assertEqual(record["close"], 3320.0)
        self.assertEqual(record["volume"], 123456.0)
        self.assertEqual(record["amount"], 123456789.5)
        self.assertEqual(record["source_ts"], "2024-01-03T16:00:00")
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(
            registry.validate_record(DatasetName.INDEX_DAILY_BARS, record),
            (),
        )

    def test_adapter_accepts_common_bare_codes_with_expected_source_symbol_mapping(self) -> None:
        samples = (
            ("000300", "sh000300", "000300.CN_INDEX"),
            ("000001", "sh000001", "000001.CN_INDEX"),
            ("399001", "sz399001", "399001.CN_INDEX"),
            ("399006", "sz399006", "399006.CN_INDEX"),
        )
        for user_symbol, expected_ak_symbol, expected_canonical in samples:
            calls: list[dict] = []

            def fake_fetch_index_daily(**kwargs):
                calls.append(kwargs)
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
                    symbols=(user_symbol,),
                ),
            )
            with self.subTest(symbol=user_symbol):
                self.assertEqual(calls[0]["symbol"], expected_ak_symbol)
                self.assertEqual(
                    result.normalized_records[0]["index_code"],
                    expected_canonical,
                )

    def test_adapter_accepts_source_native_symbol_and_normalizes_output_code(self) -> None:
        calls: list[dict] = []

        def fake_fetch_index_daily(**kwargs):
            calls.append(kwargs)
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
                symbols=("sh000300",),
            ),
        )

        self.assertEqual(calls[0]["symbol"], "sh000300")
        self.assertEqual(result.normalized_records[0]["index_code"], "000300.CN_INDEX")

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
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires exactly one index code, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_multiple_symbols(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "exactly one index code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300", "000001"),
                ),
            )

    def test_adapter_rejects_invalid_market_suffix(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported index market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300.SH",),
                ),
            )

    def test_adapter_rejects_invalid_index_code_format(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported index code format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("ABCDEF",),
                ),
            )

    def test_adapter_rejects_unmapped_index_code(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported or unmapped index code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000905",),
                ),
            )

    def test_adapter_rejects_unmapped_source_native_index_code(self) -> None:
        adapter = AkshareIndexDailyBarAdapter(fetch_index_daily=lambda **kwargs: [])
        with self.assertRaisesRegex(
            ValueError,
            "Unsupported or unmapped source-native index code",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
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
                    symbols=("000300",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
