from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareDailyBarAdapter,
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


class AkshareAShareDailyBarAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareAShareDailyBarAdapter(fetch_daily_hist=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_daily_bars(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 3, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_daily_hist(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "日期": "2024-01-02",
                    "开盘": "10.00",
                    "最高": 10.2,
                    "最低": "9.80",
                    "收盘": 10.1,
                    "成交量": "1000",
                    "成交额": "10000",
                }
            ]

        adapter = AkshareAShareDailyBarAdapter(
            fetch_daily_hist=fake_fetch_daily_hist,
            now_fn=lambda: now,
            price_adjustment="raw",
        )
        request = SourceRequest(
            dataset=DatasetName.DAILY_BARS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
            symbols=("600000.SH",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                request,
                fetched_at=datetime(2024, 1, 3, 10, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["symbol"], "600000")
        self.assertEqual(calls[0]["period"], "daily")
        self.assertEqual(calls[0]["start_date"], "20240101")
        self.assertEqual(calls[0]["end_date"], "20240102")
        self.assertEqual(calls[0]["adjust"], "")

        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "600000.SH")
        self.assertEqual(record["market"], "CN")
        self.assertEqual(record["trade_date"], "2024-01-02")
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
                    "date": "20240102",
                    "open": 10.0,
                    "high": 10.2,
                    "low": 9.8,
                    "close": 10.1,
                    "volume": 1000,
                    "amount": 10000,
                }
            ]
        )
        adapter = AkshareAShareDailyBarAdapter(
            fetch_daily_hist=lambda **kwargs: fake_payload,
            now_fn=lambda: datetime(2024, 1, 3, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-02")
        self.assertEqual(result.normalized_records[0]["symbol"], "000001.SZ")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareAShareDailyBarAdapter(fetch_daily_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SZ",),
                ),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareAShareDailyBarAdapter(fetch_daily_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires exactly one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_multiple_symbols(self) -> None:
        adapter = AkshareAShareDailyBarAdapter(fetch_daily_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "exactly one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SZ", "600000.SH"),
                ),
            )

    def test_adapter_rejects_invalid_symbol_format(self) -> None:
        adapter = AkshareAShareDailyBarAdapter(fetch_daily_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("BAD_SYMBOL",),
                ),
            )

    def test_adapter_rejects_malformed_source_row(self) -> None:
        def fake_fetch_daily_hist(**kwargs):
            return [
                {
                    "日期": "2024-01-02",
                    "开盘": 10.0,
                    "最高": 10.2,
                    "最低": 9.8,
                    "成交量": 1000,
                    "成交额": 10000,
                }
            ]

        adapter = AkshareAShareDailyBarAdapter(fetch_daily_hist=fake_fetch_daily_hist)
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SZ",),
                ),
            )

    def test_adapter_supports_qfq_adjustment_mapping(self) -> None:
        calls: list[dict] = []

        def fake_fetch_daily_hist(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "date": "2024-01-02",
                    "open": 10.0,
                    "high": 10.2,
                    "low": 9.8,
                    "close": 10.1,
                    "volume": 1000,
                    "amount": 10000,
                }
            ]

        adapter = AkshareAShareDailyBarAdapter(
            fetch_daily_hist=fake_fetch_daily_hist,
            price_adjustment="qfq",
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
            ),
        )
        self.assertEqual(calls[0]["adjust"], "qfq")
        self.assertEqual(result.normalized_records[0]["price_adjustment"], "qfq")

    def test_adapter_rejects_unsupported_price_adjustment(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported price_adjustment"):
            AkshareAShareDailyBarAdapter(
                fetch_daily_hist=lambda **kwargs: [],
                price_adjustment="invalid",
            )
