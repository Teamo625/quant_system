import os
import unittest

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareFundProfileAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class AkshareFundProfileLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: [])
        self.assertTrue(
            adapter._is_fund_profile_network_unavailable(
                OSError(111, "connection refused to fund_individual_basic_info_xq endpoint")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        adapter = AkshareFundProfileAdapter(fetch_fund_profile=lambda **kwargs: [])
        self.assertFalse(
            adapter._is_fund_profile_network_unavailable(
                ValueError("Invalid fund profile source code value")
            )
        )


class AkshareFundProfileLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_fund_profile_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareFundProfileAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.FUND_PROFILE,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("000001.FUND_CN",),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if adapter._is_fund_profile_network_unavailable(exc):
                self.skipTest(
                    "live AKShare fund profile source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live AKShare fund profile source returned no usable bounded sample records"
            )

        first_record = result.normalized_records[0]
        issues = registry.validate_record(DatasetName.FUND_PROFILE, first_record)
        self.assertEqual(issues, ())
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "CN")
        self.assertEqual(first_record["fund_code"], "000001.FUND_CN")
        self.assertIn("fund_name", first_record)
        self.assertIn("management_company", first_record)
        self.assertIn("fund_type", first_record)


if __name__ == "__main__":
    unittest.main()
