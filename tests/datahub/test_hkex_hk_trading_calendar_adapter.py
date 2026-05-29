from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.hkex import (
    HKEX_SOURCE_ID,
    HkexHKTradingCalendarAdapter,
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


_ICS_PAYLOAD = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART;VALUE=DATE:20240101
SUMMARY:Hong Kong Public Holidays - New Year's Day
DESCRIPTION:Hong Kong Market is closed
END:VEVENT
BEGIN:VEVENT
DTSTART:20240103T000000Z
SUMMARY:Trading Information: Securities & Derivatives - Half-Day Trading Day - Afternoon Session is Closed
END:VEVENT
BEGIN:VEVENT
DTSTART;VALUE=DATE:20240105
SUMMARY:HKEX Events - Synthetic Fixture Marker
END:VEVENT
END:VCALENDAR
"""


class HkexHKTradingCalendarAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(fetch_trading_calendar=lambda: _ICS_PAYLOAD)
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_calendar_from_ics(self) -> None:
        registry = DatasetRegistry()
        now = datetime(2024, 1, 8, 9, 30, 0, tzinfo=timezone.utc)
        adapter = HkexHKTradingCalendarAdapter(
            fetch_trading_calendar=lambda: _ICS_PAYLOAD,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.TRADING_CALENDAR,
            source_name=HKEX_SOURCE_ID,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(result.record_count, 4)
        records = list(result.normalized_records)
        self.assertEqual(
            [row["trade_date"] for row in records],
            ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        )

        self.assertEqual(records[0]["previous_trade_date"], "2024-01-02")
        self.assertEqual(records[0]["next_trade_date"], "2024-01-03")

        self.assertEqual(records[1]["previous_trade_date"], "2024-01-02")
        self.assertEqual(records[1]["next_trade_date"], "2024-01-04")
        self.assertEqual(records[1]["session_type"], "half-day")

        self.assertEqual(records[3]["previous_trade_date"], "2024-01-04")
        self.assertEqual(records[3]["next_trade_date"], "2024-01-05")

        for record in records:
            self.assertEqual(record["market"], "HK")
            self.assertTrue(record["is_open"])
            self.assertEqual(record["source"], HKEX_SOURCE_ID)
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(
                registry.validate_record(DatasetName.TRADING_CALENDAR, record),
                (),
            )

    def test_calendar_date_filtering_is_deterministic(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(
            fetch_trading_calendar=lambda: _ICS_PAYLOAD,
            now_fn=lambda: datetime(2024, 1, 8, 9, 30, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.TRADING_CALENDAR,
                source_name=HKEX_SOURCE_ID,
                start_date=date(2024, 1, 3),
                end_date=date(2024, 1, 4),
            ),
        )
        records = list(result.normalized_records)

        self.assertEqual([row["trade_date"] for row in records], ["2024-01-03", "2024-01-04"])
        self.assertEqual(records[0]["previous_trade_date"], "2024-01-03")
        self.assertEqual(records[0]["next_trade_date"], "2024-01-04")
        self.assertEqual(records[1]["previous_trade_date"], "2024-01-03")
        self.assertEqual(records[1]["next_trade_date"], "2024-01-04")

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        fake_payload = _FakeDataFrame(
            [
                {
                    "calendarDate": "20240103",
                    "session_type": "half-day",
                    "source_ts": "2024-01-03 08:55:00",
                },
                {
                    "trade_date": "2024-01-02",
                    "source_ts": "2024-01-02T09:00:00",
                },
            ]
        )
        adapter = HkexHKTradingCalendarAdapter(
            fetch_trading_calendar=lambda: fake_payload,
            now_fn=lambda: datetime(2024, 1, 8, 9, 30, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.TRADING_CALENDAR,
                source_name=HKEX_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-02")
        self.assertEqual(result.normalized_records[1]["trade_date"], "2024-01-03")
        self.assertEqual(result.normalized_records[1]["session_type"], "half-day")
        self.assertEqual(result.normalized_records[1]["source_ts"], "2024-01-03T08:55:00")

    def test_adapter_handles_list_of_date_values(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(
            fetch_trading_calendar=lambda: [date(2024, 1, 2), "2024-01-03", "20240105"],
            now_fn=lambda: datetime(2024, 1, 8, 9, 30, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.TRADING_CALENDAR,
                source_name=HKEX_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 3)
        self.assertEqual(
            [row["trade_date"] for row in result.normalized_records],
            ["2024-01-02", "2024-01-03", "2024-01-05"],
        )

    def test_adapter_sorts_and_deduplicates_trade_dates_deterministically(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(
            fetch_trading_calendar=lambda: [
                {
                    "trade_date": "2024-01-03",
                    "session_type": "full",
                },
                {
                    "trade_date": "2024-01-02",
                    "source_ts": "2024-01-02T09:00:00",
                },
                {
                    "trade_date": "2024-01-03",
                    "session_type": "half-day",
                    "source_ts": "2024-01-03T09:10:00",
                },
                "2024-01-02",
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.TRADING_CALENDAR,
                source_name=HKEX_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-02")
        self.assertEqual(result.normalized_records[1]["trade_date"], "2024-01-03")
        self.assertEqual(result.normalized_records[1]["session_type"], "half-day")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(fetch_trading_calendar=lambda: _ICS_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_symbols_input(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(fetch_trading_calendar=lambda: _ICS_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "does not accept symbols input"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=HKEX_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_invalid_date_range(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(fetch_trading_calendar=lambda: _ICS_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "Invalid SourceRequest date range"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=HKEX_SOURCE_ID,
                    start_date=date(2024, 1, 10),
                    end_date=date(2024, 1, 1),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(
            fetch_trading_calendar=lambda: {"trade_date": "2024-01-02"}
        )
        with self.assertRaisesRegex(ValueError, "payload must be ICS str, DataFrame-like"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_missing_trade_date_field(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(
            fetch_trading_calendar=lambda: [{"date_value": "2024-01-02"}]
        )
        with self.assertRaisesRegex(ValueError, "Missing required trade-date field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_trade_date_value(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(
            fetch_trading_calendar=lambda: [{"trade_date": "not-a-date"}]
        )
        with self.assertRaisesRegex(ValueError, "Invalid trade date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_source_ts_value(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(
            fetch_trading_calendar=lambda: [{"trade_date": "2024-01-02", "source_ts": "bad-ts"}]
        )
        with self.assertRaisesRegex(ValueError, "Invalid source_ts value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_session_type_value(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(
            fetch_trading_calendar=lambda: [{"trade_date": "2024-01-02", "session_type": "night"}]
        )
        with self.assertRaisesRegex(ValueError, "Invalid session_type value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_empty_dates_after_filtering(self) -> None:
        adapter = HkexHKTradingCalendarAdapter(fetch_trading_calendar=lambda: _ICS_PAYLOAD)
        with self.assertRaisesRegex(ValueError, "no usable trade dates"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TRADING_CALENDAR,
                    source_name=HKEX_SOURCE_ID,
                    start_date=date(2024, 2, 1),
                    end_date=date(2024, 2, 2),
                ),
            )


if __name__ == "__main__":
    unittest.main()
