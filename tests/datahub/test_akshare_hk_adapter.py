from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareHKDailyBarAdapter,
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


class AkshareHKDailyBarAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareHKDailyBarAdapter(fetch_hk_hist=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_hk_daily_bars(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 8, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_hk_hist(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "日期": "2024-01-03",
                    "开盘": "320.0",
                    "最高": 325.0,
                    "最低": "318.5",
                    "收盘": 324.0,
                    "成交量": "123456",
                    "成交额": "987654321",
                }
            ]

        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=fake_fetch_hk_hist,
            now_fn=lambda: now,
            price_adjustment="raw",
        )
        request = SourceRequest(
            dataset=DatasetName.DAILY_BARS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
            symbols=("00700.HK",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                request,
                fetched_at=datetime(2024, 1, 8, 10, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["symbol"], "00700")
        self.assertEqual(calls[0]["period"], "daily")
        self.assertEqual(calls[0]["start_date"], "20240102")
        self.assertEqual(calls[0]["end_date"], "20240105")
        self.assertEqual(calls[0]["adjust"], "")

        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "00700.HK")
        self.assertEqual(record["market"], "HK")
        self.assertEqual(record["trade_date"], "2024-01-03")
        self.assertEqual(record["adj_factor"], 1.0)
        self.assertEqual(record["price_adjustment"], "raw")
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(
            registry.validate_record(DatasetName.DAILY_BARS, record),
            (),
        )

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        fake_payload = _FakeDataFrame(
            [
                {
                    "date": "20240103",
                    "open": 320.0,
                    "high": 325.0,
                    "low": 318.5,
                    "close": 324.0,
                    "volume": 123456,
                    "amount": 987654321,
                }
            ]
        )
        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=lambda **kwargs: fake_payload,
            now_fn=lambda: datetime(2024, 1, 8, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00005.HK",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "00005.HK")
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-03")

    def test_adapter_supports_multi_symbol_batch_with_deduped_sorted_records(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()

        def fake_fetch_hk_hist(**kwargs):
            calls.append(kwargs)
            if kwargs["symbol"] == "00700":
                return [
                    {
                        "date": "2024-01-03",
                        "open": 320.0,
                        "high": 325.0,
                        "low": 318.5,
                        "close": 324.0,
                        "volume": 123456,
                        "amount": 987654321,
                    },
                    {
                        "date": "2024-01-02",
                        "open": 318.0,
                        "high": 320.0,
                        "low": 317.0,
                        "close": 319.0,
                        "volume": 1000,
                        "amount": 1000000,
                    },
                    {
                        "date": "2024-01-03",
                        "open": 320.0,
                        "high": 325.0,
                        "low": 318.5,
                        "close": 324.0,
                        "volume": 123456,
                        "amount": 987654321,
                    },
                ]
            return [
                {
                    "date": "2024-01-02",
                    "open": 60.0,
                    "high": 61.0,
                    "low": 59.5,
                    "close": 60.5,
                    "volume": 45678,
                    "amount": 34567890,
                }
            ]

        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=fake_fetch_hk_hist,
            now_fn=lambda: datetime(2024, 1, 8, 10, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 3),
                symbols=("00700.HK", "00005.HK", "00700.HK"),
            ),
        )

        self.assertEqual(
            calls,
            [
                {
                    "symbol": "00700",
                    "period": "daily",
                    "start_date": "20240102",
                    "end_date": "20240103",
                    "adjust": "",
                },
                {
                    "symbol": "00005",
                    "period": "daily",
                    "start_date": "20240102",
                    "end_date": "20240103",
                    "adjust": "",
                },
            ],
        )
        self.assertEqual(result.record_count, 3)
        self.assertEqual(
            [(record["symbol"], record["trade_date"]) for record in result.normalized_records],
            [
                ("00005.HK", "2024-01-02"),
                ("00700.HK", "2024-01-02"),
                ("00700.HK", "2024-01-03"),
            ],
        )
        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.DAILY_BARS, record),
                (),
            )

    def test_adapter_supports_qfq_adjustment_mapping(self) -> None:
        calls: list[dict] = []

        def fake_fetch_hk_hist(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "date": "2024-01-03",
                    "open": 320.0,
                    "high": 325.0,
                    "low": 318.5,
                    "close": 324.0,
                    "volume": 123456,
                    "amount": 987654321,
                }
            ]

        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=fake_fetch_hk_hist,
            price_adjustment="qfq",
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(calls[0]["adjust"], "qfq")
        self.assertEqual(result.normalized_records[0]["price_adjustment"], "qfq")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareHKDailyBarAdapter(fetch_hk_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareHKDailyBarAdapter(fetch_hk_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires at least one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_validates_full_symbol_batch_before_source_calls(self) -> None:
        calls: list[dict] = []

        def fake_fetch_hk_hist(**kwargs):
            calls.append(kwargs)
            return []

        adapter = AkshareHKDailyBarAdapter(fetch_hk_hist=fake_fetch_hk_hist)
        with self.assertRaisesRegex(ValueError, "Unsupported HK market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK", "600000.SH"),
                ),
            )
        self.assertEqual(calls, [])

    def test_adapter_rejects_invalid_hk_symbol_without_suffix(self) -> None:
        adapter = AkshareHKDailyBarAdapter(fetch_hk_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported HK symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700",),
                ),
            )

    def test_adapter_rejects_invalid_hk_symbol_suffix(self) -> None:
        adapter = AkshareHKDailyBarAdapter(fetch_hk_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported HK market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.SH",),
                ),
            )

    def test_adapter_rejects_invalid_hk_symbol_code(self) -> None:
        adapter = AkshareHKDailyBarAdapter(fetch_hk_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Expected 5-digit code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("700.HK",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareHKDailyBarAdapter(fetch_hk_hist=lambda **kwargs: {"date": "2024-01-03"})
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_missing_required_source_field(self) -> None:
        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 320.0,
                    "high": 325.0,
                    "low": 318.5,
                    "close": 324.0,
                    "volume": 123456,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_value(self) -> None:
        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": "320.0",
                    "high": "bad",
                    "low": 318.5,
                    "close": 324.0,
                    "volume": 123456,
                    "amount": 987654321,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid numeric value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_invalid_date_range(self) -> None:
        calls: list[dict] = []

        def fake_fetch_hk_hist(**kwargs):
            calls.append(kwargs)
            return []

        adapter = AkshareHKDailyBarAdapter(fetch_hk_hist=fake_fetch_hk_hist)
        with self.assertRaisesRegex(ValueError, "Invalid date range"):
            adapter.fetch(
                DatasetName.DAILY_BARS,
                start_date=date(2024, 1, 5),
                end_date=date(2024, 1, 2),
                symbols=["00700.HK"],
            )
        self.assertEqual(calls, [])

    def test_adapter_rejects_unsupported_price_adjustment(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported price_adjustment"):
            AkshareHKDailyBarAdapter(
                fetch_hk_hist=lambda **kwargs: [],
                price_adjustment="invalid",
            )

    def test_adapter_falls_back_to_hk_daily_when_hist_network_unavailable(self) -> None:
        hist_calls: list[dict] = []
        daily_calls: list[dict] = []

        class ProxyError(Exception):
            pass

        def fake_fetch_hk_hist(**kwargs):
            hist_calls.append(kwargs)
            raise ProxyError("Unable to connect to proxy")

        def fake_fetch_hk_daily(**kwargs):
            daily_calls.append(kwargs)
            return [
                {
                    "date": "2024-01-01",
                    "open": 318.0,
                    "high": 320.0,
                    "low": 317.0,
                    "close": 319.0,
                    "volume": 1000,
                    "amount": 1000000,
                },
                {
                    "date": "2024-01-03",
                    "open": 320.0,
                    "high": 325.0,
                    "low": 318.5,
                    "close": 324.0,
                    "volume": 123456,
                    "amount": 987654321,
                },
                {
                    "date": "2024-01-06",
                    "open": 326.0,
                    "high": 327.0,
                    "low": 323.0,
                    "close": 324.5,
                    "volume": 150000,
                    "amount": 1000000000,
                },
            ]

        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=fake_fetch_hk_hist,
            fetch_hk_daily=fake_fetch_hk_daily,
            now_fn=lambda: datetime(2024, 1, 8, 10, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
                symbols=("00700.HK",),
            ),
        )

        self.assertEqual(len(hist_calls), 1)
        self.assertEqual(hist_calls[0]["symbol"], "00700")
        self.assertEqual(len(daily_calls), 1)
        self.assertEqual(daily_calls[0]["symbol"], "00700")
        self.assertEqual(daily_calls[0]["adjust"], "")
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-03")
        self.assertEqual(result.normalized_records[0]["symbol"], "00700.HK")

    def test_adapter_falls_back_to_hk_daily_when_hist_returns_no_rows(self) -> None:
        hist_calls: list[dict] = []
        daily_calls: list[dict] = []

        def fake_fetch_hk_hist(**kwargs):
            hist_calls.append(kwargs)
            return []

        def fake_fetch_hk_daily(**kwargs):
            daily_calls.append(kwargs)
            return [
                {
                    "date": "2019-01-01",
                    "open": 315.0,
                    "high": 316.0,
                    "low": 314.0,
                    "close": 315.5,
                    "volume": 1000,
                    "amount": 1000000,
                },
                {
                    "date": "2019-01-02",
                    "open": 316.0,
                    "high": 317.0,
                    "low": 315.5,
                    "close": 316.5,
                    "volume": 2000,
                    "amount": 2000000,
                },
                {
                    "date": "2019-01-15",
                    "open": 330.0,
                    "high": 331.0,
                    "low": 329.0,
                    "close": 330.5,
                    "volume": 3000,
                    "amount": 3000000,
                },
                {
                    "date": "2019-01-16",
                    "open": 331.0,
                    "high": 332.0,
                    "low": 330.0,
                    "close": 331.5,
                    "volume": 4000,
                    "amount": 4000000,
                },
            ]

        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=fake_fetch_hk_hist,
            fetch_hk_daily=fake_fetch_hk_daily,
            now_fn=lambda: datetime(2024, 1, 8, 10, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2019, 1, 2),
                end_date=date(2019, 1, 15),
                symbols=("00700.HK",),
            ),
        )

        self.assertEqual(len(hist_calls), 1)
        self.assertEqual(len(daily_calls), 1)
        self.assertEqual(daily_calls[0]["symbol"], "00700")
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [record["trade_date"] for record in result.normalized_records],
            ["2019-01-02", "2019-01-15"],
        )

    def test_adapter_does_not_mask_non_network_hist_errors(self) -> None:
        daily_calls: list[dict] = []

        def fake_fetch_hk_daily(**kwargs):
            daily_calls.append(kwargs)
            return []

        def fake_fetch_hk_hist(**kwargs):
            raise ValueError("bad period")

        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=fake_fetch_hk_hist,
            fetch_hk_daily=fake_fetch_hk_daily,
        )

        with self.assertRaisesRegex(ValueError, "bad period"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )
        self.assertEqual(daily_calls, [])

    def test_adapter_does_not_mask_non_network_hk_daily_errors_after_empty_hist(self) -> None:
        def fake_fetch_hk_hist(**kwargs):
            return []

        def fake_fetch_hk_daily(**kwargs):
            raise ValueError("bad daily payload")

        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=fake_fetch_hk_hist,
            fetch_hk_daily=fake_fetch_hk_daily,
        )

        with self.assertRaisesRegex(ValueError, "bad daily payload"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_fetch_source_result_normalizes_hk_turnover_liquidity_snapshot(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 8, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_hk_hist(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "日期": "2024-01-03",
                    "成交量": "123456",
                    "成交额": "987654321",
                }
            ]

        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=fake_fetch_hk_hist,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
            symbols=("00700.HK",),
        )

        result = fetch_source_result(adapter, request)

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["symbol"], "00700")
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "00700.HK")
        self.assertEqual(record["market"], "HK")
        self.assertEqual(record["trade_date"], "2024-01-03")
        self.assertEqual(record["metric_granularity"], "daily")
        self.assertEqual(record["volume"], 123456.0)
        self.assertEqual(record["amount"], 987654321.0)
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["source_route"], "stock_hk_hist")
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertNotIn("turnover_rate", record)
        self.assertEqual(
            registry.validate_record(DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT, record),
            (),
        )

    def test_hk_turnover_liquidity_fallback_preserves_fallback_source_route(self) -> None:
        hist_calls: list[dict] = []
        daily_calls: list[dict] = []
        registry = DatasetRegistry()

        class ProxyError(Exception):
            pass

        def fake_fetch_hk_hist(**kwargs):
            hist_calls.append(kwargs)
            raise ProxyError("Unable to connect to proxy")

        def fake_fetch_hk_daily(**kwargs):
            daily_calls.append(kwargs)
            return [
                {
                    "date": "2019-01-01",
                    "volume": 1000,
                    "amount": 1000000,
                },
                {
                    "date": "2019-01-03",
                    "volume": 123456,
                    "amount": 987654321,
                },
                {
                    "date": "2019-01-06",
                    "volume": 150000,
                    "amount": 1000000000,
                },
            ]

        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=fake_fetch_hk_hist,
            fetch_hk_daily=fake_fetch_hk_daily,
            now_fn=lambda: datetime(2024, 1, 8, 10, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2019, 1, 2),
                end_date=date(2019, 1, 5),
                symbols=("00700.HK",),
            ),
        )

        self.assertEqual(len(hist_calls), 1)
        self.assertEqual(hist_calls[0]["symbol"], "00700")
        self.assertEqual(len(daily_calls), 1)
        self.assertEqual(daily_calls[0]["symbol"], "00700")
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["trade_date"], "2019-01-03")
        self.assertEqual(record["symbol"], "00700.HK")
        self.assertEqual(record["source_route"], "stock_hk_daily")
        self.assertEqual(
            registry.validate_record(DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT, record),
            (),
        )
