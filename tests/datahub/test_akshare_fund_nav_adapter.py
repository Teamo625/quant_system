from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFFundNavSnapshotAdapter,
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


class AkshareETFFundNavSnapshotAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_fund_nav_records(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 10, 9, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_fund_nav(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "净值日期": "2024-01-09",
                    "单位净值": "1.0010",
                    "累计净值": "1.2010",
                    "shares_outstanding": "123456789",
                    "fund_scale": "321.88",
                    "source_ts": "2024-01-09T18:00:00",
                }
            ]

        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=fake_fetch_fund_nav,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.FUND_NAV_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 9),
            symbols=("510300.ETF_CN",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                request,
                fetched_at=datetime(2024, 1, 10, 9, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["fund"], "510300")
        self.assertEqual(calls[0]["start_date"], "20240101")
        self.assertEqual(calls[0]["end_date"], "20240109")

        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["fund_code"], "510300.ETF_CN")
        self.assertEqual(record["market"], "ETF_CN")
        self.assertEqual(record["trade_date"], "2024-01-09")
        self.assertEqual(record["nav"], 1.001)
        self.assertEqual(record["accumulated_nav"], 1.201)
        self.assertEqual(record["shares_outstanding"], 123456789.0)
        self.assertEqual(record["fund_scale"], 321.88)
        self.assertEqual(record["source_ts"], "2024-01-09T18:00:00")
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(
            registry.validate_record(DatasetName.FUND_NAV_SNAPSHOT, record),
            (),
        )

    def test_adapter_accepts_bare_fund_code_and_normalizes_output_code(self) -> None:
        calls: list[dict] = []

        def fake_fetch_fund_nav(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "trade_date": "2024-01-09",
                    "nav": 1.001,
                }
            ]

        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=fake_fetch_fund_nav)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_NAV_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )

        self.assertEqual(calls[0]["fund"], "510300")
        self.assertEqual(result.normalized_records[0]["fund_code"], "510300.ETF_CN")

    def test_adapter_only_includes_optional_fields_when_values_are_valid(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: [
                {
                    "date": "2024-01-09",
                    "unit_nav": "1.0010",
                    "累计净值": "",
                    "基金份额": None,
                    "fund_scale": "  ",
                    "source_ts": "",
                }
            ],
            now_fn=lambda: datetime(2024, 1, 10, 9, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_NAV_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )
        record = result.normalized_records[0]
        self.assertNotIn("accumulated_nav", record)
        self.assertNotIn("shares_outstanding", record)
        self.assertNotIn("fund_scale", record)
        self.assertNotIn("source_ts", record)

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(
            [
                {
                    "date": "20240109",
                    "nav": 1.001,
                    "accumulated_nav": 1.201,
                }
            ]
        )
        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: payload,
            now_fn=lambda: datetime(2024, 1, 10, 9, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_NAV_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-09")
        self.assertEqual(result.normalized_records[0]["accumulated_nav"], 1.201)

    def test_adapter_does_not_pass_unsupported_date_args_when_function_signature_lacks_them(
        self,
    ) -> None:
        calls: list[dict] = []

        def fake_fetch_fund_nav(fund):
            calls.append({"fund": fund})
            return [{"date": "2024-01-09", "nav": 1.0}]

        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=fake_fetch_fund_nav)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_NAV_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 9),
                symbols=("510300",),
            ),
        )
        self.assertEqual(calls, [{"fund": "510300"}])
        self.assertEqual(result.record_count, 1)

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires exactly one fund code, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_multiple_symbols(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "exactly one fund code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300", "510500"),
                ),
            )

    def test_adapter_rejects_invalid_fund_code_suffix(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported ETF/fund market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                ),
            )

    def test_adapter_rejects_invalid_fund_code_format(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Expected 6-digit code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("ABCDEF",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: {"date": "2024-01-09", "nav": 1.0}
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: [
                {
                    "trade_date": "2024-01-09",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_invalid_trade_date_value(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: [
                {
                    "trade_date": "2024-13-09",
                    "nav": 1.0,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid trade date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_value(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: [
                {
                    "trade_date": "2024-01-09",
                    "nav": "bad",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid numeric value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_invalid_optional_numeric_value(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: [
                {
                    "trade_date": "2024-01-09",
                    "nav": 1.0,
                    "accumulated_nav": "bad",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid numeric value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_invalid_optional_source_ts_value(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: [
                {
                    "trade_date": "2024-01-09",
                    "nav": 1.0,
                    "source_ts": "not-a-datetime",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid source_ts value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
