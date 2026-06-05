import os
import unittest
from datetime import date

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFFundHoldingsAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class AkshareETFFundHoldingsLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=lambda **kwargs: [])
        self.assertTrue(
            adapter._is_fund_holdings_network_unavailable(
                OSError(111, "connection refused to fundf10.eastmoney.com endpoint")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        adapter = AkshareETFFundHoldingsAdapter(fetch_fund_holdings=lambda **kwargs: [])
        self.assertFalse(
            adapter._is_fund_holdings_network_unavailable(
                ValueError("Invalid report_date value")
            )
        )


class AkshareETFFundHoldingsLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_fund_holdings_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareETFFundHoldingsAdapter(max_records_per_slice=30)
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.FUND_HOLDINGS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            symbols=("510300.ETF_CN", "159915.ETF_CN"),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if adapter._is_fund_holdings_network_unavailable(exc):
                self.skipTest(
                    "live AKShare ETF/fund holdings source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare ETF/fund holdings source returned insufficient bounded "
                "sample records for requested multi-symbol batch"
            )

        returned_symbols = {record["fund_code"] for record in result.normalized_records}
        self.assertEqual(returned_symbols, {"159915.ETF_CN", "510300.ETF_CN"})
        self.assertTrue(
            all(
                request.start_date
                <= date.fromisoformat(record["report_date"])
                <= request.end_date
                for record in result.normalized_records
            )
        )
        first_record = result.normalized_records[0]
        issues = registry.validate_record(DatasetName.FUND_HOLDINGS, first_record)
        self.assertEqual(issues, ())
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertIn("fund_code", first_record)
        self.assertIn("symbol", first_record)
        self.assertIn("report_date", first_record)


if __name__ == "__main__":
    unittest.main()
