from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareTradingCalendarAdapter,
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


class AkshareAShareTradingCalendarAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareAShareTradingCalendarAdapter(fetch_trade_dates=lambda: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_calendar(self) -> None:
        registry = DatasetRegistry()
        now = datetime(2024, 1, 8, 9, 30, 0, tzinfo=timezone.utc)

        def fake_fetch_trade_dates():
            return [
                {"trade_date": "2024-01-02"},
                {"trade_date": date(2024, 1, 3)},
                {"trade_date": "2024-01-05"},
            ]

        adapter = AkshareAShareTradingCalendarAdapter(
            fetch_trade_dates=fake_fetch_trade_dates,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.TRADING_CALENDAR,
            source_name=AKSHARE_SOURCE_ID,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(result.record_count, 3)
        records = list(result.normalized_records)

        self.assertEqual(records[0]["trade_date"], "2024-01-02")
        self.assertEqual(records[0]["previous_trade_date"], "2024-01-02")
        self.assertEqual(records[0]["next_trade_date"], "2024-01-03")

        self.assertEqual(records[1]["trade_date"], "2024-01-03")
        self.assertEqual(records[1]["previous_trade_date"], "2024-01-02")
        self.assertEqual(records[1]["next_trade_date"], "2024-01-05")

        self.assertEqual(records[2]["trade_date"], "2024-01-05")
        self.assertEqual(records[2]["previous_trade_date"], "2024-01-03")
        self.assertEqual(records[2]["next_trade_date"], "2024-01-05")

        for record in records:
            self.assertEqual(record["market"], "CN")
            self.assertTrue(record["is_open"])
            self.assertEqual(record["session_type"], "full")
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(
                registry.validate_record(DatasetName.TRADING_CALENDAR, record),
                (),
            )

    def test_calendar_date_filtering_is_deterministic(self) -> None:
        adapter = AkshareAShareTradingCalendarAdapter(
            fetch_trade_dates=lambda: [
                {"trade_date": "2024-01-02"},
                {"trade_date": "2024-01-03"},
                {"trade_date": "2024-01-05"},
            ],
            now_fn=lambda: datetime(2024, 1, 8, 9, 30, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.TRADING_CALENDAR,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 3),
                end_date=date(2024, 1, 5),
            ),
        )
        records = list(result.normalized_records)

        self.assertEqual([row["trade_date"] for row in records], ["2024-01-03", "2024-01-05"])
        self.assertEqual(records[0]["previous_trade_date"], "2024-01-03")
        self.assertEqual(records[0]["next_trade_date"], "2024-01-05")
        self.assertEqual(records[1]["previous_trade_date"], "2024-01-03")
        self.assertEqual(records[1]["next_trade_date"], "2024-01-05")

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        fake_payload = _FakeDataFrame(
            [
                {"trade_date": "20240102"},
                {"trade_date": "20240103"},
            ]
        )
        adapter = AkshareAShareTradingCalendarAdapter(
            fetch_trade_dates=lambda: fake_payload,
            now_fn=lambda: datetime(2024, 1, 8, 9, 30, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.TRADING_CALENDAR,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-02")

    def test_adapter_handles_list_of_date_values(self) -> None:
        adapter = AkshareAShareTradingCalendarAdapter(
            fetch_trade_dates=lambda: [date(2024, 1, 2), "2024-01-03", "20240105"],
            now_fn=lambda: datetime(2024, 1, 8, 9, 30, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.TRADING_CALENDAR,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 3)
        self.assertEqual(result.normalized_records[2]["trade_date"], "2024-01-05")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareAShareTradingCalendarAdapter(fetch_trade_dates=lambda: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SZ",),
                ),
            )

    def test_adapter_rejects_symbols_input(self) -> None:
        adapter = AkshareAShareTradingCalendarAdapter(fetch_trade_dates=lambda: [])
        with self.assertRaisesRegex(ValueError, "does not accept symbols input"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SZ",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareAShareTradingCalendarAdapter(
            fetch_trade_dates=lambda: {"trade_date": "2024-01-02"}
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like, list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_missing_trade_date_field(self) -> None:
        adapter = AkshareAShareTradingCalendarAdapter(
            fetch_trade_dates=lambda: [{"date_str": "2024-01-02"}]
        )
        with self.assertRaisesRegex(ValueError, "Missing required trade-date field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_trade_date_value(self) -> None:
        adapter = AkshareAShareTradingCalendarAdapter(
            fetch_trade_dates=lambda: [{"trade_date": "not-a-date"}]
        )
        with self.assertRaisesRegex(ValueError, "Invalid trade date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_empty_dates_after_filtering(self) -> None:
        adapter = AkshareAShareTradingCalendarAdapter(
            fetch_trade_dates=lambda: [{"trade_date": "2024-01-02"}]
        )
        with self.assertRaisesRegex(ValueError, "no usable trade dates"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 10),
                    end_date=date(2024, 1, 11),
                ),
            )
