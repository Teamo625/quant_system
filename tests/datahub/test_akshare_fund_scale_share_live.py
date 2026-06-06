import os
import unittest
from datetime import date, datetime, timedelta, timezone

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFFundFlowAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class AkshareFundScaleShareLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_fund_scale_share_historical_etf_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareETFFundFlowAdapter()
        registry = DatasetRegistry()
        history_request = SourceRequest(
            dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 4),
            end_date=date(2024, 1, 5),
            symbols=("510300.ETF_CN", "159915.ETF_CN"),
        )

        try:
            result = fetch_source_result(adapter, history_request)
        except Exception as exc:
            if adapter._is_fund_flow_route_unavailable(exc):  # pylint: disable=protected-access
                self.skipTest(
                    "live AKShare ETF/fund scale/share source unavailable in current "
                    f"environment: {type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare ETF/fund scale/share source returned insufficient "
                "historical ETF records for requested batch"
            )

        returned_symbols = {record["fund_code"] for record in result.normalized_records}
        self.assertEqual(returned_symbols, {"159915.ETF_CN", "510300.ETF_CN"})
        self.assertTrue(
            all(
                history_request.start_date
                <= date.fromisoformat(record["observation_date"])
                <= history_request.end_date
                for record in result.normalized_records
            )
        )
        first_record = result.normalized_records[0]
        issues = registry.validate_record(DatasetName.FUND_SCALE_SHARE_SNAPSHOT, first_record)
        self.assertEqual(issues, ())
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["metric_code"], "shares_outstanding")
        self.assertIn(first_record["source_route"], {"fund_etf_scale_sse", "fund_scale_daily_szse"})

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_fund_scale_share_fund_snapshot_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareETFFundFlowAdapter()
        registry = DatasetRegistry()
        today = datetime.now(timezone.utc).date()
        snapshot_request = SourceRequest(
            dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=today - timedelta(days=30),
            end_date=today,
            symbols=("000001.FUND_CN", "161725.FUND_CN"),
        )

        try:
            result = fetch_source_result(adapter, snapshot_request)
        except Exception as exc:
            if adapter._is_fund_flow_route_unavailable(exc):  # pylint: disable=protected-access
                self.skipTest(
                    "live AKShare ETF/fund scale/share snapshot source unavailable in "
                    f"current environment: {type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare ETF/fund scale/share snapshot source returned insufficient "
                "records for requested fund batch"
            )

        returned_symbols = {record["fund_code"] for record in result.normalized_records}
        self.assertEqual(returned_symbols, {"000001.FUND_CN", "161725.FUND_CN"})
        self.assertTrue(
            all(
                snapshot_request.start_date
                <= date.fromisoformat(record["observation_date"])
                <= snapshot_request.end_date
                for record in result.normalized_records
            )
        )
        first_record = result.normalized_records[0]
        issues = registry.validate_record(DatasetName.FUND_SCALE_SHARE_SNAPSHOT, first_record)
        self.assertEqual(issues, ())
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertIn(first_record["metric_code"], {"shares_outstanding", "total_raised_scale"})
        self.assertTrue(first_record["source_route"].startswith("fund_scale_"))


if __name__ == "__main__":
    unittest.main()
