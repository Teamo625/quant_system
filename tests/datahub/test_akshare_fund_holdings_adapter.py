from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFFundHoldingsAdapter,
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


class AkshareETFFundHoldingsAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_records(self) -> None:
        calls: list[dict] = []
        now = datetime(2025, 5, 1, 9, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_fund_holdings(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "股票代码": "600519",
                    "占净值比例": "4.74%",
                    "持股数": "1029.29",
                    "持仓市值": "1606717.16",
                    "季度": "2025年1季度股票投资明细",
                    "source_ts": "2025-04-21T15:30:00",
                },
                {
                    "股票代码": "300750",
                    "占净值比例": 3.23,
                    "持股数": 4320.86,
                    "持仓市值": 1092918.96,
                    "季度": "2025年1季度股票投资明细",
                },
            ]

        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=fake_fetch_fund_holdings,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.FUND_HOLDINGS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            symbols=("510300.ETF_CN",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["symbol"], "510300")
        self.assertEqual(calls[0]["date"], "2025")

        self.assertEqual(result.record_count, 2)
        by_symbol = {record["symbol"]: record for record in result.normalized_records}

        maotai = by_symbol["600519.SH"]
        self.assertEqual(maotai["fund_code"], "510300.ETF_CN")
        self.assertEqual(maotai["market"], "CN")
        self.assertEqual(maotai["report_date"], "2025-03-31")
        self.assertEqual(maotai["weight"], 4.74)
        self.assertEqual(maotai["shares"], 1029.29)
        self.assertEqual(maotai["position_value"], 1606717.16)
        self.assertEqual(maotai["source_ts"], "2025-04-21T15:30:00")
        self.assertEqual(maotai["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(maotai["schema_version"], "v1")
        self.assertEqual(maotai["ingested_at"], now.isoformat())

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.FUND_HOLDINGS, record),
                (),
            )

    def test_adapter_accepts_bare_fund_code_and_normalizes_output_code(self) -> None:
        calls: list[dict] = []

        def fake_fetch_fund_holdings(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "symbol": "000001",
                    "weight": 1.1,
                    "report_date": "2025-03-31",
                }
            ]

        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=fake_fetch_fund_holdings)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_HOLDINGS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )
        self.assertEqual(calls[0]["symbol"], "510300")
        self.assertEqual(result.normalized_records[0]["fund_code"], "510300.ETF_CN")

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(
            [
                {
                    "股票代码": "920000",
                    "占净值比例": "2.00",
                    "季度": "20250331",
                }
            ]
        )
        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=lambda **kwargs: payload,
            now_fn=lambda: datetime(2025, 5, 1, 9, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_HOLDINGS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "920000.BJ")
        self.assertEqual(result.normalized_records[0]["report_date"], "2025-03-31")

    def test_adapter_filters_by_date_and_keeps_one_latest_reporting_slice(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=lambda **kwargs: [
                {
                    "股票代码": "600519",
                    "占净值比例": 4.0,
                    "季度": "2024年4季度股票投资明细",
                },
                {
                    "股票代码": "300750",
                    "占净值比例": 3.0,
                    "季度": "2025年1季度股票投资明细",
                },
                {
                    "股票代码": "000001",
                    "占净值比例": 2.0,
                    "季度": "2025年1季度股票投资明细",
                },
            ],
            now_fn=lambda: datetime(2025, 5, 1, 9, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_HOLDINGS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                symbols=("510300",),
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            {record["report_date"] for record in result.normalized_records},
            {"2025-03-31"},
        )

    def test_adapter_does_not_pass_date_when_function_signature_lacks_it(self) -> None:
        calls: list[dict] = []

        def fake_fetch(symbol):
            calls.append({"symbol": symbol})
            return [{"股票代码": "600519", "占净值比例": 4.0, "季度": "2025年1季度股票投资明细"}]

        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=fake_fetch)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_HOLDINGS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
            ),
        )
        self.assertEqual(calls, [{"symbol": "510300"}])
        self.assertEqual(result.record_count, 1)

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires exactly one fund code, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_multiple_symbols(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "exactly one fund code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300", "159915"),
                ),
            )

    def test_adapter_rejects_invalid_fund_code_suffix(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported ETF/fund market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                ),
            )

    def test_adapter_rejects_invalid_fund_code_format(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Expected 6-digit code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("ABCDEF",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=lambda **kwargs: {"股票代码": "600519"}
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=lambda **kwargs: [1])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=lambda **kwargs: [{"股票代码": "600519", "季度": "2025年1季度股票投资明细"}]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_invalid_report_date_value(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=lambda **kwargs: [
                {"股票代码": "600519", "占净值比例": 4.0, "季度": "BAD-DATE"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid report_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_or_weight_value(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=lambda **kwargs: [
                {"股票代码": "600519", "占净值比例": "bad", "季度": "2025年1季度股票投资明细"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid weight value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_out_of_range_weight(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=lambda **kwargs: [
                {"股票代码": "600519", "占净值比例": 120.0, "季度": "2025年1季度股票投资明细"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Expected range"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_invalid_optional_numeric_value(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=lambda **kwargs: [
                {
                    "股票代码": "600519",
                    "占净值比例": 4.0,
                    "持股数": -1,
                    "季度": "2025年1季度股票投资明细",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Expected nonnegative"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_dedupes_exact_duplicates_preferring_latest_source_ts(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=lambda **kwargs: [
                {
                    "股票代码": "600519",
                    "占净值比例": 4.0,
                    "季度": "2025年1季度股票投资明细",
                    "source_ts": "2025-04-20T09:00:00",
                },
                {
                    "股票代码": "600519",
                    "占净值比例": 4.0,
                    "季度": "2025年1季度股票投资明细",
                    "source_ts": "2025-04-20T10:00:00",
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_HOLDINGS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["source_ts"], "2025-04-20T10:00:00")

    def test_adapter_rejects_conflicting_duplicates(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(
            fetch_fund_holdings=lambda **kwargs: [
                {"股票代码": "600519", "占净值比例": 4.0, "季度": "2025年1季度股票投资明细"},
                {"股票代码": "600519", "占净值比例": 4.1, "季度": "2025年1季度股票投资明细"},
            ]
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate ETF/fund holdings row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_HOLDINGS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )


if __name__ == "__main__":
    unittest.main()

