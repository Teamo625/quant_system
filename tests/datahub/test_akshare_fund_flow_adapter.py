from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFFundFlowAdapter,
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


def _sse_row(**overrides):
    row = {
        "基金代码": "510300",
        "基金简称": "沪深300ETF",
        "统计日期": "2024-01-05",
        "基金份额": "1.25亿份",
    }
    row.update(overrides)
    return row


class AkshareETFFundFlowAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareETFFundFlowAdapter(fetch_sse_scale=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_fund_flow(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 6, 9, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_sse(**kwargs):
            calls.append(kwargs)
            return [
                _sse_row(source_ts="2024-01-05T18:00:00"),
                _sse_row(基金代码="510500", 基金份额=1000),
            ]

        adapter = AkshareETFFundFlowAdapter(
            fetch_sse_scale=fake_fetch_sse,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.FUND_FLOW,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 5),
            symbols=("510300.ETF_CN",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                request,
                fetched_at=datetime(2024, 1, 6, 9, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(calls, [{"date": "20240105"}])
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["fund_code"], "510300.ETF_CN")
        self.assertEqual(record["market"], "ETF_FUND")
        self.assertEqual(record["trade_date"], "2024-01-05")
        self.assertEqual(record["shares_change"], 125000000.0)
        self.assertNotIn("net_inflow", record)
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["source_ts"], "2024-01-05T18:00:00")
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(registry.validate_record(DatasetName.FUND_FLOW, record), ())

    def test_adapter_accepts_bare_code_and_szse_route(self) -> None:
        calls: list[dict] = []

        def fake_fetch_szse(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "日期": "2024-01-05",
                    "基金代码": "159001",
                    "基金简称": "货币ETF",
                    "基金份额": 12345.0,
                }
            ]

        adapter = AkshareETFFundFlowAdapter(fetch_szse_scale=fake_fetch_szse)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_FLOW,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 5),
                end_date=date(2024, 1, 5),
                symbols=("159001",),
            ),
        )
        self.assertEqual(
            calls,
            [{"start_date": "20240105", "end_date": "20240105", "symbol": "ETF"}],
        )
        self.assertEqual(result.normalized_records[0]["fund_code"], "159001.ETF_CN")
        self.assertEqual(result.normalized_records[0]["shares_change"], 12345.0)

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame([_sse_row(统计日期="20240105", 基金份额="12,345")])
        adapter = AkshareETFFundFlowAdapter(fetch_sse_scale=lambda **kwargs: payload)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_FLOW,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 5),
                end_date=date(2024, 1, 5),
                symbols=("510300",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["shares_change"], 12345.0)

    def test_adapter_preserves_source_truth_optional_metrics(self) -> None:
        adapter = AkshareETFFundFlowAdapter(
            fetch_sse_scale=lambda **kwargs: [
                _sse_row(
                    shares_change="1000",
                    net_inflow="88.5",
                    subscription_amount="120.5",
                    redemption_amount="32.0",
                    source_ts="20240105",
                )
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_FLOW,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 5),
                end_date=date(2024, 1, 5),
                symbols=("510300",),
            ),
        )
        record = result.normalized_records[0]
        self.assertEqual(record["net_inflow"], 88.5)
        self.assertEqual(record["subscription_amount"], 120.5)
        self.assertEqual(record["redemption_amount"], 32.0)
        self.assertEqual(record["source_ts"], "2024-01-05T00:00:00")

    def test_adapter_sorts_and_deduplicates_exact_duplicate_rows(self) -> None:
        adapter = AkshareETFFundFlowAdapter(
            fetch_sse_scale=lambda **kwargs: [
                _sse_row(统计日期="2024-01-05", 基金份额=2000),
                _sse_row(统计日期="2024-01-05", 基金份额=2000),
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_FLOW,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 5),
                end_date=date(2024, 1, 5),
                symbols=("510300",),
            ),
        )
        self.assertEqual(result.record_count, 1)

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = AkshareETFFundFlowAdapter(
            fetch_sse_scale=lambda **kwargs: [
                _sse_row(统计日期="2024-01-05", 基金份额=2000),
                _sse_row(统计日期="2024-01-05", 基金份额=3000),
            ]
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate ETF/fund flow row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_FLOW,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 5),
                    end_date=date(2024, 1, 5),
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareETFFundFlowAdapter(fetch_sse_scale=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_PROFILE,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 5),
                    end_date=date(2024, 1, 5),
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_unbounded_and_invalid_date_ranges(self) -> None:
        adapter = AkshareETFFundFlowAdapter(fetch_sse_scale=lambda **kwargs: [])
        invalid_requests = (
            (None, None, "requires bounded trade_date"),
            (date(2024, 1, 5), None, "requires both start_date and end_date"),
            (None, date(2024, 1, 5), "requires both start_date and end_date"),
            (date(2024, 1, 4), date(2024, 1, 5), "exactly one trade_date"),
        )
        for start_date, end_date, message in invalid_requests:
            with self.subTest(start_date=start_date, end_date=end_date):
                with self.assertRaisesRegex(ValueError, message):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.FUND_FLOW,
                            source_name=AKSHARE_SOURCE_ID,
                            start_date=start_date,
                            end_date=end_date,
                            symbols=("510300",),
                        ),
                    )

    def test_adapter_rejects_invalid_fund_code_inputs(self) -> None:
        adapter = AkshareETFFundFlowAdapter(fetch_sse_scale=lambda **kwargs: [])
        invalid_cases = (
            (None, "requires exactly one ETF/fund code"),
            ((), "requires exactly one ETF/fund code"),
            (("510300", "510500"), "exactly one ETF/fund code"),
            (("",), "non-empty string"),
            (("600000.SH",), "Unsupported ETF/fund flow market suffix"),
            (("00700.HK",), "Unsupported ETF/fund flow market suffix"),
            (("399001",), "Index code is unsupported"),
            (("600000",), "A-share stock code is unsupported"),
            (("000001",), "A-share stock code is unsupported"),
            (("ETF510300",), "Expected 6-digit code"),
        )
        for symbols, message in invalid_cases:
            with self.subTest(symbols=symbols):
                with self.assertRaisesRegex(ValueError, message):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.FUND_FLOW,
                            source_name=AKSHARE_SOURCE_ID,
                            start_date=date(2024, 1, 5),
                            end_date=date(2024, 1, 5),
                            symbols=symbols,
                        ),
                    )

    def test_adapter_rejects_malformed_payloads_and_missing_fields(self) -> None:
        bad_payloads = (
            {"基金代码": "510300"},
            [1],
            [{"基金代码": "510300", "统计日期": "2024-01-05"}],
        )
        for payload in bad_payloads:
            with self.subTest(payload=payload):
                adapter = AkshareETFFundFlowAdapter(fetch_sse_scale=lambda **kwargs: payload)
                with self.assertRaisesRegex(ValueError, "payload|Missing required source field"):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.FUND_FLOW,
                            source_name=AKSHARE_SOURCE_ID,
                            start_date=date(2024, 1, 5),
                            end_date=date(2024, 1, 5),
                            symbols=("510300",),
                        ),
                    )

    def test_adapter_rejects_invalid_dates_and_numeric_values(self) -> None:
        invalid_rows = (
            (_sse_row(统计日期="2024-99-05"), "Invalid trade_date value"),
            (_sse_row(基金份额="not-a-number"), "Invalid shares_change value"),
        )
        for row, message in invalid_rows:
            with self.subTest(row=row):
                adapter = AkshareETFFundFlowAdapter(fetch_sse_scale=lambda **kwargs: [row])
                with self.assertRaisesRegex(ValueError, message):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.FUND_FLOW,
                            source_name=AKSHARE_SOURCE_ID,
                            start_date=date(2024, 1, 5),
                            end_date=date(2024, 1, 5),
                            symbols=("510300",),
                        ),
                    )

    def test_route_signature_incompatibility_is_not_live_unavailable(self) -> None:
        def bad_signature():
            return []

        adapter = AkshareETFFundFlowAdapter(fetch_sse_scale=bad_signature)
        with self.assertRaisesRegex(RuntimeError, "does not accept date argument") as context:
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_FLOW,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 5),
                    end_date=date(2024, 1, 5),
                    symbols=("510300",),
                ),
            )
        self.assertFalse(adapter._is_fund_flow_route_unavailable(context.exception))

    def test_network_classifier_marks_route_environment_errors_only(self) -> None:
        adapter = AkshareETFFundFlowAdapter(fetch_sse_scale=lambda **kwargs: [])
        self.assertTrue(
            adapter._is_fund_flow_route_unavailable(
                OSError(111, "connection refused to sse.com.cn endpoint")
            )
        )
        self.assertFalse(
            adapter._is_fund_flow_route_unavailable(
                ValueError("Invalid shares_change value")
            )
        )


if __name__ == "__main__":
    unittest.main()
