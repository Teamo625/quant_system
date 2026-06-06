import os
import unittest
from datetime import date, timedelta

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareAdjustmentFactorsAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class AkshareAShareAdjustmentFactorsLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        adapter = AkshareAShareAdjustmentFactorsAdapter(fetch_daily_factor=lambda **kwargs: [])
        self.assertTrue(
            adapter._is_adjustment_factors_network_unavailable(  # pylint: disable=protected-access
                OSError(111, "connection refused to finance.sina.com.cn endpoint")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        adapter = AkshareAShareAdjustmentFactorsAdapter(fetch_daily_factor=lambda **kwargs: [])
        self.assertFalse(
            adapter._is_adjustment_factors_network_unavailable(  # pylint: disable=protected-access
                ValueError("Invalid adjustment_factor value")
            )
        )


class AkshareAShareAdjustmentFactorsLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_adjustment_factors_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareAdjustmentFactorsAdapter()
        registry = DatasetRegistry()
        window_end = date.today()
        window_start = window_end - timedelta(days=4000)
        request = SourceRequest(
            dataset=DatasetName.ADJUSTMENT_FACTORS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH", "000001.SZ"),
            start_date=window_start,
            end_date=window_end,
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if adapter._is_adjustment_factors_network_unavailable(exc):  # pylint: disable=protected-access
                self.skipTest(
                    "live AKShare A-share adjustment-factor source unavailable in current "
                    f"environment: {type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 4:
            self.skipTest(
                "live AKShare A-share adjustment-factor source returned insufficient "
                "bounded sample records for requested multi-symbol qfq/hfq batch"
            )

        returned_symbols = {record["symbol"] for record in result.normalized_records}
        returned_bases = {record["adjustment_basis"] for record in result.normalized_records}
        self.assertEqual(returned_symbols, {"000001.SZ", "600000.SH"})
        self.assertEqual(returned_bases, {"hfq", "qfq"})
        self.assertTrue(
            all(
                request.start_date
                <= date.fromisoformat(record["factor_date"])
                <= request.end_date
                for record in result.normalized_records
            )
        )

        first_record = result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.ADJUSTMENT_FACTORS, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "CN")
        self.assertIn(first_record["adjustment_basis"], {"qfq", "hfq"})
        self.assertTrue(str(first_record["raw_payload_ref"]).startswith("AKAF|"))


if __name__ == "__main__":
    unittest.main()
