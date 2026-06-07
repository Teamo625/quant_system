import os
import unittest
from datetime import date

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFFundPremiumDiscountAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class AkshareETFFundPremiumDiscountLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        adapter = AkshareETFFundPremiumDiscountAdapter(fetch_fund_daily=lambda: [])
        self.assertTrue(
            adapter._is_fund_premium_discount_route_unavailable(
                OSError(111, "connection refused to fund.eastmoney.com endpoint")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        adapter = AkshareETFFundPremiumDiscountAdapter(fetch_fund_daily=lambda: [])
        self.assertFalse(
            adapter._is_fund_premium_discount_route_unavailable(
                ValueError("Invalid premium_discount_rate value")
            )
        )

    def test_classifier_marks_sina_history_network_failures_as_environment_unavailable(
        self,
    ) -> None:
        adapter = AkshareETFFundPremiumDiscountAdapter(fetch_fund_daily=lambda: [])
        self.assertTrue(
            adapter._is_fund_premium_discount_route_unavailable(
                ConnectionError("hq.sinajs.cn connection reset")
            )
        )


class AkshareETFFundPremiumDiscountLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_fund_premium_discount_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareETFFundPremiumDiscountAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 4),
            end_date=date(2024, 1, 10),
            symbols=("510300.ETF_CN", "161725.FUND_CN"),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if adapter._is_fund_premium_discount_route_unavailable(exc):
                self.skipTest(
                    "live AKShare ETF/fund premium-discount source unavailable in current "
                    f"environment: {type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare ETF/fund premium-discount source returned insufficient "
                "bounded sample records for requested multi-symbol batch"
            )

        returned_symbols = {record["fund_code"] for record in result.normalized_records}
        self.assertEqual(returned_symbols, {"161725.FUND_CN", "510300.ETF_CN"})
        self.assertTrue(
            all(
                request.start_date
                <= date.fromisoformat(record["trade_date"])
                <= request.end_date
                for record in result.normalized_records
            )
        )
        self.assertTrue(
            any(
                record["source_route"] == "fund_etf_hist_sina+fund_open_fund_info_em"
                for record in result.normalized_records
            ),
            "live bounded history should include explicit proven FUND_CN composite coverage",
        )

        first_record = result.normalized_records[0]
        issues = registry.validate_record(DatasetName.FUND_PREMIUM_DISCOUNT, first_record)
        self.assertEqual(issues, ())
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "ETF_FUND")
        self.assertIn("premium_discount_rate", first_record)
        self.assertIn("source_route", first_record)
        self.assertTrue(
            "nav" in first_record or "iopv" in first_record,
            "premium-discount record should preserve a route-local reference valuation field",
        )


if __name__ == "__main__":
    unittest.main()
