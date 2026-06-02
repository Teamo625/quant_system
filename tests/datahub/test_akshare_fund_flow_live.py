import os
import unittest
from datetime import date

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFFundFlowAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class AkshareETFFundFlowLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_fund_flow_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareETFFundFlowAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.FUND_FLOW,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 5),
            symbols=("510300.ETF_CN",),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if adapter._is_fund_flow_route_unavailable(exc):  # pylint: disable=protected-access
                self.skipTest(
                    "live AKShare ETF/fund flow source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live AKShare ETF/fund flow source returned no usable bounded sample records"
            )

        first_record = result.normalized_records[0]
        issues = registry.validate_record(DatasetName.FUND_FLOW, first_record)
        self.assertEqual(issues, ())
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "ETF_FUND")
        self.assertEqual(first_record["fund_code"], "510300.ETF_CN")
        self.assertEqual(first_record["trade_date"], "2024-01-05")
        self.assertIn("shares_change", first_record)


if __name__ == "__main__":
    unittest.main()
