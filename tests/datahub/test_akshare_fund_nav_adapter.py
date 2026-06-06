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

    def test_adapter_accepts_explicit_fund_cn_code_and_uses_open_fund_history_route(
        self,
    ) -> None:
        calls: list[dict] = []

        def fake_fetch_open_fund_nav(**kwargs):
            calls.append(kwargs)
            if kwargs["indicator"] == "单位净值走势":
                return [
                    {"净值日期": "2001-12-18", "单位净值": 1.0},
                    {"净值日期": "2001-12-21", "单位净值": 1.01},
                ]
            if kwargs["indicator"] == "累计净值走势":
                return [
                    {"净值日期": "2001-12-18", "累计净值": 1.0},
                    {"净值日期": "2001-12-21", "累计净值": 1.01},
                ]
            raise AssertionError(f"unexpected indicator: {kwargs['indicator']}")

        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: (_ for _ in ()).throw(
                AssertionError("primary ETF route should not be used for FUND_CN")
            ),
            fetch_open_fund_nav=fake_fetch_open_fund_nav,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_NAV_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2001, 12, 18),
                end_date=date(2001, 12, 31),
                symbols=("000001.FUND_CN",),
            ),
        )

        self.assertEqual(
            calls,
            [
                {"symbol": "000001", "indicator": "单位净值走势", "period": "成立来"},
                {"symbol": "000001", "indicator": "累计净值走势", "period": "成立来"},
            ],
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(result.normalized_records[0]["fund_code"], "000001.FUND_CN")
        self.assertEqual(result.normalized_records[0]["market"], "FUND_CN")
        self.assertEqual(result.normalized_records[0]["trade_date"], "2001-12-18")
        self.assertEqual(result.normalized_records[1]["accumulated_nav"], 1.01)

    def test_adapter_infers_fund_cn_for_non_etf_listed_fund_code(self) -> None:
        calls: list[dict] = []

        def fake_fetch_open_fund_nav(**kwargs):
            calls.append(kwargs)
            if kwargs["indicator"] == "单位净值走势":
                return [{"净值日期": "2024-01-09", "单位净值": 1.0}]
            return [{"净值日期": "2024-01-09", "累计净值": 1.2}]

        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_open_fund_nav=fake_fetch_open_fund_nav,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_NAV_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("161725",),
            ),
        )

        self.assertEqual(calls[0]["symbol"], "161725")
        self.assertEqual(result.normalized_records[0]["fund_code"], "161725.FUND_CN")
        self.assertEqual(result.normalized_records[0]["market"], "FUND_CN")

    def test_adapter_supports_multi_symbol_batch_with_bounded_date_window(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()

        def fake_fetch_fund_nav(**kwargs):
            calls.append(kwargs)
            if kwargs["fund"] == "510300":
                return [
                    {
                        "trade_date": "2024-01-07",
                        "nav": 1.000,
                    },
                    {
                        "trade_date": "2024-01-09",
                        "nav": 1.001,
                        "accumulated_nav": 1.201,
                    },
                ]
            if kwargs["fund"] == "159915":
                return [
                    {
                        "date": "20240109",
                        "unit_nav": 2.002,
                    },
                    {
                        "date": "20240108",
                        "unit_nav": 2.001,
                        "source_ts": "2024-01-08T18:00:00",
                    },
                ]
            raise AssertionError(f"unexpected fund code: {kwargs['fund']}")

        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=fake_fetch_fund_nav)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_NAV_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 8),
                end_date=date(2024, 1, 9),
                symbols=("510300.ETF_CN", "159915", "510300"),
            ),
        )

        self.assertEqual(
            calls,
            [
                {"fund": "510300", "start_date": "20240108", "end_date": "20240109"},
                {"fund": "159915", "start_date": "20240108", "end_date": "20240109"},
            ],
        )
        self.assertEqual(
            [
                (record["fund_code"], record["trade_date"])
                for record in result.normalized_records
            ],
            [
                ("159915.ETF_CN", "2024-01-08"),
                ("159915.ETF_CN", "2024-01-09"),
                ("510300.ETF_CN", "2024-01-09"),
            ],
        )
        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.FUND_NAV_SNAPSHOT, record),
                (),
            )

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
            return [
                {"date": "2023-12-31", "nav": 0.99},
                {"date": "2024-01-09", "nav": 1.0},
            ]

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
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-09")

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
        with self.assertRaisesRegex(ValueError, "requires at least one ETF/fund symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_requires_bounded_date_window_for_multi_symbol_requests(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires bounded date window"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300", "510500"),
                ),
            )

    def test_adapter_requires_both_dates_for_multi_symbol_requests(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires both start_date and end_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 1),
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

    def test_adapter_rejects_index_like_fund_code(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "overlaps index namespace"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_ambiguous_bare_zero_prefix_fund_code(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Use explicit '\\.FUND_CN'"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001",),
                ),
            )

    def test_adapter_rejects_a_share_stock_like_fund_code(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "A-share stock code is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000",),
                ),
            )

    def test_adapter_rejects_fund_suffix_for_etf_code_family(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Use '\\.ETF_CN' instead"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.FUND_CN",),
                ),
            )

    def test_adapter_rejects_unsupported_fund_prefix(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported ETF/fund code prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("200001",),
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

    def test_adapter_fails_when_any_requested_symbol_yields_no_usable_rows(self) -> None:
        def fake_fetch_fund_nav(**kwargs):
            if kwargs["fund"] == "510300":
                return [{"trade_date": "2024-01-09", "nav": 1.0}]
            if kwargs["fund"] == "159915":
                return []
            raise AssertionError(f"unexpected fund code: {kwargs['fund']}")

        adapter = AkshareETFFundNavSnapshotAdapter(fetch_fund_nav=fake_fetch_fund_nav)
        with self.assertRaisesRegex(ValueError, "yielded no usable rows.*159915\\.ETF_CN"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 9),
                    end_date=date(2024, 1, 10),
                    symbols=("510300.ETF_CN", "159915.ETF_CN"),
                ),
            )

    def test_adapter_dedupes_duplicate_rows_deterministically(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: [
                {
                    "trade_date": "2024-01-09",
                    "nav": 1.0,
                    "source_ts": "2024-01-09T18:00:00",
                },
                {
                    "trade_date": "2024-01-09",
                    "nav": 1.0,
                    "accumulated_nav": 1.2,
                    "source_ts": "2024-01-09T18:01:00",
                },
            ]
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
        record = result.normalized_records[0]
        self.assertEqual(record["accumulated_nav"], 1.2)
        self.assertEqual(record["source_ts"], "2024-01-09T18:01:00")

    def test_adapter_skips_rows_with_missing_required_values_when_other_rows_are_usable(self) -> None:
        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=lambda **kwargs: [
                {
                    "trade_date": "2024-01-08",
                    "nav": float("nan"),
                },
                {
                    "trade_date": "2024-01-09",
                    "nav": 1.0,
                },
            ]
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

    def test_adapter_falls_back_to_open_fund_history_when_primary_etf_window_is_empty(
        self,
    ) -> None:
        primary_calls: list[dict] = []
        open_calls: list[dict] = []

        def fake_fetch_fund_nav(**kwargs):
            primary_calls.append(kwargs)
            raise ValueError("No objects to concatenate")

        def fake_fetch_open_fund_nav(**kwargs):
            open_calls.append(kwargs)
            if kwargs["indicator"] == "单位净值走势":
                return [{"净值日期": "2012-05-04", "单位净值": 1.007}]
            return [{"净值日期": "2012-05-04", "累计净值": 1.007}]

        adapter = AkshareETFFundNavSnapshotAdapter(
            fetch_fund_nav=fake_fetch_fund_nav,
            fetch_open_fund_nav=fake_fetch_open_fund_nav,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_NAV_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2012, 5, 1),
                end_date=date(2012, 5, 10),
                symbols=("510300.ETF_CN",),
            ),
        )

        self.assertEqual(
            primary_calls,
            [{"fund": "510300", "start_date": "20120501", "end_date": "20120510"}],
        )
        self.assertEqual(
            open_calls,
            [
                {"symbol": "510300", "indicator": "单位净值走势", "period": "成立来"},
                {"symbol": "510300", "indicator": "累计净值走势", "period": "成立来"},
            ],
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["fund_code"], "510300.ETF_CN")
        self.assertEqual(result.normalized_records[0]["market"], "ETF_CN")
        self.assertEqual(result.normalized_records[0]["trade_date"], "2012-05-04")


if __name__ == "__main__":
    unittest.main()
